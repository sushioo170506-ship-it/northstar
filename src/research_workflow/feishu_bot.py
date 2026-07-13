"""Feishu bot adapter for creating and operating research workflows."""

from __future__ import annotations

import argparse
import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .models import WorkflowStatus
from .orchestrator import QualityGateRejected, ResearchReportOrchestrator
from .renderers import FeishuApiClient


class FeishuBotClient:
    """Send text messages through the Feishu bot messaging API."""

    def __init__(self, api: FeishuApiClient) -> None:
        self.api = api

    def send_text(self, chat_id: str, text: str) -> dict[str, Any]:
        return self.api.request(
            "POST",
            "/open-apis/im/v1/messages?receive_id_type=chat_id",
            {
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json.dumps({"text": text}, ensure_ascii=False),
            },
        )


class FeishuWorkflowBot:
    """Map Feishu text commands to stateful workflow operations."""

    HELP = (
        "研究报告机器人命令：\n"
        "研究 <主题>：创建并运行报告\n"
        "确认 <workflow_id>：确认当前节点并继续\n"
        "状态 <workflow_id>：查看当前状态\n"
        "修改 <workflow_id> <意见>：按意见选择性重跑\n"
        "帮助：显示本说明"
    )

    def __init__(
        self,
        orchestrator: ResearchReportOrchestrator,
        sender: FeishuBotClient,
        *,
        verification_token: str,
        default_profile: str = "standard",
        default_length: int = 5000,
        target_tenant_confirmed: bool = False,
        data_residency_approved: bool = False,
        max_workers: int = 4,
    ) -> None:
        if not verification_token:
            raise ValueError("飞书事件回调必须配置 verification_token")
        self.orchestrator = orchestrator
        self.sender = sender
        self.verification_token = verification_token
        self.default_profile = default_profile
        self.default_length = default_length
        self.target_tenant_confirmed = target_tenant_confirmed
        self.data_residency_approved = data_residency_approved
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._event_ids: set[str] = set()
        self._event_lock = threading.Lock()

    def handle_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Validate one callback and schedule message processing."""
        if payload.get("type") == "url_verification":
            if payload.get("token") != self.verification_token:
                raise PermissionError("飞书回调 verification_token 不匹配")
            return {"challenge": payload.get("challenge", "")}
        if "encrypt" in payload:
            raise ValueError("当前服务不接收加密事件；请使用HTTPS并关闭飞书事件加密")

        header = payload.get("header") or {}
        if header.get("token") != self.verification_token:
            raise PermissionError("飞书回调 verification_token 不匹配")
        if header.get("event_type") != "im.message.receive_v1":
            return {"ok": True, "ignored": True}
        event_id = str(header.get("event_id") or "")
        if event_id and not self._mark_event(event_id):
            return {"ok": True, "duplicate": True}

        event = payload.get("event") or {}
        message = event.get("message") or {}
        if message.get("message_type") != "text":
            return {"ok": True, "ignored": True}
        sender = event.get("sender") or {}
        sender_id = sender.get("sender_id") or {}
        open_id = str(sender_id.get("open_id") or "")
        chat_id = str(message.get("chat_id") or "")
        try:
            content = json.loads(message.get("content") or "{}")
            text = str(content.get("text") or "").strip()
        except json.JSONDecodeError as exc:
            raise ValueError("飞书文本消息 content 不是合法JSON") from exc
        if not chat_id or not open_id or not text:
            return {"ok": True, "ignored": True}
        self.executor.submit(self._process_and_send, chat_id, open_id, text)
        return {"ok": True, "accepted": True}

    def process_text(self, text: str, *, chat_id: str, open_id: str) -> str:
        """Process a command synchronously; useful for tests and workers."""
        command = text.strip()
        if command in {"帮助", "help", "/help"}:
            return self.HELP
        match = re.match(r"^(?:研究|/research)\s+(.+)$", command, re.S)
        if match:
            return self._create_and_run(match.group(1).strip(), chat_id, open_id)
        match = re.match(r"^(?:确认|/confirm)\s+(\S+)$", command)
        if match:
            workflow_id = match.group(1)
            self._assert_owner(workflow_id, open_id)
            snapshot = self.orchestrator.state.snapshot(workflow_id)
            waiting = self._waiting_checkpoint(snapshot)
            if not waiting:
                return f"工作流 {workflow_id} 当前没有待确认节点。"
            self.orchestrator.confirm(workflow_id, waiting, f"飞书用户 {open_id} 确认")
            return self._run_and_describe(workflow_id)
        match = re.match(r"^(?:状态|/status)\s+(\S+)$", command)
        if match:
            workflow_id = match.group(1)
            self._assert_owner(workflow_id, open_id)
            return self._describe_snapshot(workflow_id)
        match = re.match(r"^(?:修改|/revise)\s+(\S+)\s+(.+)$", command, re.S)
        if match:
            workflow_id, feedback = match.group(1), match.group(2).strip()
            self._assert_owner(workflow_id, open_id)
            target, affected = self.orchestrator.request_revision(workflow_id, feedback)
            result = self._run_and_describe(workflow_id)
            return (
                f"已将修改路由到 {target}，失效节点："
                f"{', '.join(sorted(affected))}\n{result}"
            )
        return "无法识别命令。\n\n" + self.HELP

    def _create_and_run(self, topic: str, chat_id: str, open_id: str) -> str:
        workflow_id = self.orchestrator.create(
            {
                "topic": topic,
                "expected_length": self.default_length,
                "output_format": "feishu",
                "output_type": "研究报告",
                "audience": "企业专业读者",
                "workflow_profile": self.default_profile,
                "confidentiality_level": "internal",
                "extra": {
                    "feishu_target_tenant_confirmed": self.target_tenant_confirmed,
                    "feishu_data_residency_approved": self.data_residency_approved,
                },
            }
        )
        self.orchestrator.state.record_operation(
            workflow_id,
            "feishu_owner",
            {"open_id": open_id, "chat_id": chat_id},
            "requirements_analysis",
        )
        return f"已创建工作流 {workflow_id}。\n" + self._run_and_describe(workflow_id)

    def _run_and_describe(self, workflow_id: str) -> str:
        try:
            outcome = self.orchestrator.run(workflow_id)
        except QualityGateRejected as exc:
            return f"工作流 {workflow_id} 未通过质量门：{exc}"
        if outcome.status == WorkflowStatus.WAITING_CONFIRMATION:
            return (
                f"工作流 {workflow_id} 等待确认：{outcome.waiting_at}\n"
                f"回复：确认 {workflow_id}"
            )
        if outcome.status == WorkflowStatus.COMPLETED:
            report = self.orchestrator.final_report(workflow_id)
            return f"工作流 {workflow_id} 已完成：\n{report}"
        return self._describe_snapshot(workflow_id)

    def _describe_snapshot(self, workflow_id: str) -> str:
        snapshot = self.orchestrator.state.snapshot(workflow_id)
        waiting = self._waiting_checkpoint(snapshot)
        status = snapshot.get("workflow", {}).get("status", "unknown")
        message = f"工作流 {workflow_id} 状态：{status}"
        if waiting:
            message += f"\n等待确认：{waiting}\n回复：确认 {workflow_id}"
        return message

    def _assert_owner(self, workflow_id: str, open_id: str) -> None:
        operations = self.orchestrator.state.operations(workflow_id, "feishu_owner")
        owner = next(
            (
                item.get("payload", {}).get("open_id")
                for item in operations
                if item.get("payload", {}).get("open_id")
            ),
            None,
        )
        if owner != open_id:
            raise PermissionError("你无权操作该工作流")

    @staticmethod
    def _waiting_checkpoint(snapshot: dict[str, Any]) -> str | None:
        for node in snapshot.get("nodes", []):
            status = node.get("status")
            status_value = getattr(status, "value", status)
            if status_value == "waiting_confirmation":
                return str(node["node_id"])
        return None

    def _mark_event(self, event_id: str) -> bool:
        with self._event_lock:
            if event_id in self._event_ids:
                return False
            self._event_ids.add(event_id)
            if len(self._event_ids) > 10_000:
                self._event_ids = set(list(self._event_ids)[-5_000:])
            return True

    def _process_and_send(self, chat_id: str, open_id: str, text: str) -> None:
        try:
            reply = self.process_text(text, chat_id=chat_id, open_id=open_id)
        except Exception as exc:
            reply = f"处理失败：{exc}"
        self.sender.send_text(chat_id, reply)


def make_callback_handler(bot: FeishuWorkflowBot) -> type[BaseHTTPRequestHandler]:
    """Build a small HTTP callback handler bound to one bot."""

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/feishu/events":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                response = bot.handle_event(payload)
                self._json(200, response)
            except PermissionError as exc:
                self._json(403, {"error": str(exc)})
            except (ValueError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
            except Exception:
                self._json(500, {"error": "internal_error"})

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/healthz":
                self._json(200, {"ok": True})
            else:
                self.send_error(404)

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return CallbackHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-workflow-feishu-bot")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--data-dir", default=".research-workflow")
    args = parser.parse_args(argv)

    from .cli import _renderer_from_env

    verification_token = os.environ.get("FEISHU_VERIFICATION_TOKEN", "")
    api = FeishuApiClient(
        access_token=os.environ.get("FEISHU_USER_ACCESS_TOKEN"),
        app_id=os.environ.get("FEISHU_APP_ID"),
        app_secret=os.environ.get("FEISHU_APP_SECRET"),
        auth_mode=(
            "user_oauth" if os.environ.get("FEISHU_USER_ACCESS_TOKEN") else "tenant"
        ),
    )
    orchestrator = ResearchReportOrchestrator(
        args.data_dir, document_renderer=_renderer_from_env()
    )
    bot = FeishuWorkflowBot(
        orchestrator,
        FeishuBotClient(api),
        verification_token=verification_token,
        default_profile=os.environ.get("RESEARCH_WORKFLOW_PROFILE", "standard"),
        default_length=int(os.environ.get("RESEARCH_WORKFLOW_LENGTH", "5000")),
        target_tenant_confirmed=(
            os.environ.get("FEISHU_TARGET_TENANT_CONFIRMED") == "true"
        ),
        data_residency_approved=(
            os.environ.get("FEISHU_DATA_RESIDENCY_APPROVED") == "true"
        ),
    )
    server = ThreadingHTTPServer(
        (args.host, args.port), make_callback_handler(bot)
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
