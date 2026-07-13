"""Command-line interface for local and container deployments."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .orchestrator import ResearchReportOrchestrator
from .office_renderers import (
    AestheticDocxRenderer,
    CompositeDocumentRenderer,
    SlidesRenderer,
)
from .renderers import FeishuApiClient, FeishuDocumentRenderer


def _renderer_from_env():
    renderers = {
        "docx": AestheticDocxRenderer(),
        "pptx": SlidesRenderer(),
        "slides_html": SlidesRenderer(),
        "slides_zip": SlidesRenderer(),
    }
    user_token = os.getenv("FEISHU_USER_ACCESS_TOKEN")
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    if user_token or (app_id and app_secret):
        client = FeishuApiClient(
            access_token=user_token,
            app_id=app_id,
            app_secret=app_secret,
            auth_mode="user_oauth" if user_token else "tenant",
        )
        renderers["feishu"] = FeishuDocumentRenderer(
            client,
            title=os.getenv("FEISHU_DOCUMENT_TITLE", "研究报告"),
            folder_token=os.getenv("FEISHU_FOLDER_TOKEN"),
        )
    return CompositeDocumentRenderer(renderers)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-workflow")
    parser.add_argument("--data-dir", default=".research-workflow")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--topic", required=True)
    create.add_argument("--length", type=int, default=5000)
    create.add_argument("--style", default="专业、客观、证据驱动")
    create.add_argument("--format", default="markdown")
    create.add_argument("--output-type", default="research_report")
    create.add_argument("--audience", default="通用专业读者")
    create.add_argument("--boundary", action="append", default=[])
    create.add_argument("--prior-thoughts", default="")
    create.add_argument("--confidentiality", default="public")
    create.add_argument(
        "--profile",
        choices=("quick", "standard", "deep", "regulatory"),
        default="deep",
    )
    create.add_argument("--sources-json", help="包含 sources 数组的 JSON 文件")

    create_config = sub.add_parser("create-config")
    create_config.add_argument("config_json", help="完整 ReportConfig JSON 文件")

    for name in ("run", "status", "final"):
        command = sub.add_parser(name)
        command.add_argument("workflow_id")

    artifact = sub.add_parser("artifact")
    artifact.add_argument("workflow_id")
    artifact.add_argument("node")
    artifact.add_argument(
        "--json", action="store_true", help="输出包含元数据的完整产物JSON"
    )

    export = sub.add_parser("export")
    export.add_argument("workflow_id")
    export.add_argument("output_path")

    confirm = sub.add_parser("confirm")
    confirm.add_argument("workflow_id")
    confirm.add_argument("checkpoint")
    confirm.add_argument("--comment", default="")

    modify = sub.add_parser("modify")
    modify.add_argument("workflow_id")
    modify.add_argument("node")
    modify.add_argument("feedback")

    update_sources = sub.add_parser("update-sources")
    update_sources.add_argument("workflow_id")
    update_sources.add_argument("sources_json", help="包含 sources 数组的 JSON 文件")
    update_sources.add_argument("--reason", default="更新研究来源")

    revise = sub.add_parser("revise")
    revise.add_argument("workflow_id")
    revise.add_argument("feedback")

    comment = sub.add_parser("comment")
    comment.add_argument("workflow_id")
    comment.add_argument("node")
    comment.add_argument("comment")
    comment.add_argument("--actor", required=True)

    comments = sub.add_parser("comments")
    comments.add_argument("workflow_id")
    comments.add_argument("--node")

    apply_learning = sub.add_parser("apply-learning")
    apply_learning.add_argument("workflow_id")
    apply_learning.add_argument("proposal_id")
    apply_learning.add_argument("--approved-by", required=True)
    apply_learning.add_argument("--skills-root", default="skills")

    evolution_report = sub.add_parser("evolution-report")
    evolution_report.add_argument("year", type=int)
    evolution_report.add_argument("quarter", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    orchestrator = ResearchReportOrchestrator(
        args.data_dir, document_renderer=_renderer_from_env()
    )
    try:
        if args.command == "create":
            extra = {}
            if args.sources_json:
                payload = json.loads(Path(args.sources_json).read_text(encoding="utf-8"))
                extra["sources"] = payload["sources"]
            workflow_id = orchestrator.create(
                {
                    "topic": args.topic,
                    "expected_length": args.length,
                    "style": args.style,
                    "output_format": args.format,
                    "output_type": args.output_type,
                    "audience": args.audience,
                    "content_boundaries": args.boundary,
                    "prior_thoughts": args.prior_thoughts,
                    "workflow_profile": args.profile,
                    "confidentiality_level": args.confidentiality,
                    "extra": extra,
                }
            )
            print(json.dumps({"workflow_id": workflow_id}, ensure_ascii=False))
        elif args.command == "create-config":
            config = json.loads(
                Path(args.config_json).read_text(encoding="utf-8")
            )
            if not isinstance(config, dict):
                raise ValueError("config_json 顶层必须是对象")
            workflow_id = orchestrator.create(config)
            print(json.dumps({"workflow_id": workflow_id}, ensure_ascii=False))
        elif args.command == "run":
            print(json.dumps(orchestrator.run(args.workflow_id).__dict__, ensure_ascii=False))
        elif args.command == "confirm":
            orchestrator.confirm(args.workflow_id, args.checkpoint, args.comment)
            print(json.dumps({"confirmed": args.checkpoint}, ensure_ascii=False))
        elif args.command == "modify":
            affected = orchestrator.modify(args.workflow_id, args.node, args.feedback)
            print(json.dumps({"affected": sorted(affected)}, ensure_ascii=False))
        elif args.command == "update-sources":
            payload = json.loads(Path(args.sources_json).read_text(encoding="utf-8"))
            affected = orchestrator.update_sources(
                args.workflow_id, payload["sources"], args.reason
            )
            print(json.dumps({"affected": sorted(affected)}, ensure_ascii=False))
        elif args.command == "revise":
            target, affected = orchestrator.request_revision(
                args.workflow_id, args.feedback
            )
            print(
                json.dumps(
                    {"target_node": target, "affected": sorted(affected)},
                    ensure_ascii=False,
                )
            )
        elif args.command == "comment":
            orchestrator.add_comment(
                args.workflow_id, args.node, args.comment, actor_id=args.actor
            )
            print(json.dumps({"commented": args.node}, ensure_ascii=False))
        elif args.command == "comments":
            print(
                json.dumps(
                    orchestrator.list_comments(args.workflow_id, args.node),
                    ensure_ascii=False,
                )
            )
        elif args.command == "apply-learning":
            path = orchestrator.apply_approved_learning(
                args.workflow_id,
                args.proposal_id,
                approved_by=args.approved_by,
                skills_root=args.skills_root,
            )
            print(json.dumps({"updated": str(path)}, ensure_ascii=False))
        elif args.command == "evolution-report":
            print(
                orchestrator.quarterly_evolution_report(
                    args.year, args.quarter
                )
            )
        elif args.command == "status":
            print(json.dumps(orchestrator.state.snapshot(args.workflow_id), ensure_ascii=False))
        elif args.command == "artifact":
            artifact = orchestrator.state.node_artifact(
                args.workflow_id, args.node
            )
            if artifact is None:
                raise ValueError(f"节点尚无产物: {args.node}")
            if args.json:
                print(json.dumps(artifact, ensure_ascii=False))
            else:
                print(artifact["content"])
        elif args.command == "final":
            print(orchestrator.final_report(args.workflow_id))
        elif args.command == "export":
            path = orchestrator.export_final(
                args.workflow_id, args.output_path
            )
            print(json.dumps({"exported": str(path)}, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
