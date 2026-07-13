"""Feishu bot command and callback tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_workflow.feishu_bot import FeishuBotClient, FeishuWorkflowBot
from research_workflow.orchestrator import ResearchReportOrchestrator
from research_workflow.renderers import FeishuApiClient


class FakeSender:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send_text(self, chat_id: str, text: str) -> dict:
        self.messages.append((chat_id, text))
        return {"code": 0}


class FeishuBotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.orchestrator = ResearchReportOrchestrator(Path(self.temp.name))
        self.sender = FakeSender()
        self.bot = FeishuWorkflowBot(
            self.orchestrator,
            self.sender,  # type: ignore[arg-type]
            verification_token="verify-me",
            target_tenant_confirmed=True,
            data_residency_approved=True,
        )

    def tearDown(self) -> None:
        self.bot.executor.shutdown(wait=True)
        self.temp.cleanup()

    def test_url_verification_requires_matching_token(self) -> None:
        response = self.bot.handle_event(
            {
                "type": "url_verification",
                "token": "verify-me",
                "challenge": "challenge-1",
            }
        )
        self.assertEqual(response, {"challenge": "challenge-1"})
        with self.assertRaises(PermissionError):
            self.bot.handle_event(
                {
                    "type": "url_verification",
                    "token": "wrong",
                    "challenge": "challenge-2",
                }
            )

    def test_research_status_confirm_and_owner_isolation(self) -> None:
        created = self.bot.process_text(
            "研究 人工智能治理", chat_id="chat-1", open_id="user-1"
        )
        self.assertIn("等待确认：outline_confirmation", created)
        workflow_id = created.split("工作流 ", 1)[1].split("。", 1)[0]

        status = self.bot.process_text(
            f"状态 {workflow_id}", chat_id="chat-1", open_id="user-1"
        )
        self.assertIn("outline_confirmation", status)
        with self.assertRaises(PermissionError):
            self.bot.process_text(
                f"状态 {workflow_id}", chat_id="chat-1", open_id="user-2"
            )

        continued = self.bot.process_text(
            f"确认 {workflow_id}", chat_id="chat-1", open_id="user-1"
        )
        self.assertIn("pre_review_confirmation", continued)

    def test_message_event_is_deduplicated(self) -> None:
        event = {
            "header": {
                "token": "verify-me",
                "event_type": "im.message.receive_v1",
                "event_id": "event-1",
            },
            "event": {
                "sender": {"sender_id": {"open_id": "user-1"}},
                "message": {
                    "chat_id": "chat-1",
                    "message_type": "text",
                    "content": json.dumps({"text": "帮助"}, ensure_ascii=False),
                },
            },
        }
        self.assertTrue(self.bot.handle_event(event)["accepted"])
        self.assertTrue(self.bot.handle_event(event)["duplicate"])
        self.bot.executor.shutdown(wait=True)
        self.assertEqual(len(self.sender.messages), 1)
        self.assertIn("研究 <主题>", self.sender.messages[0][1])

    def test_bot_client_uses_message_endpoint(self) -> None:
        calls = []

        def transport(method, path, payload, headers):
            calls.append((method, path, payload, headers))
            return {"code": 0, "data": {}}

        api = FeishuApiClient(access_token="token", transport=transport)
        FeishuBotClient(api).send_text("chat-1", "完成")
        method, path, payload, headers = calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(
            path, "/open-apis/im/v1/messages?receive_id_type=chat_id"
        )
        self.assertEqual(payload["receive_id"], "chat-1")
        self.assertEqual(json.loads(payload["content"])["text"], "完成")
        self.assertEqual(headers["Authorization"], "Bearer token")


if __name__ == "__main__":
    unittest.main()
