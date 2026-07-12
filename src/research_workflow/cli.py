"""Command-line interface for local and container deployments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .orchestrator import ResearchReportOrchestrator


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
    create.add_argument("--sources-json", help="包含 sources 数组的 JSON 文件")

    for name in ("run", "status", "final"):
        command = sub.add_parser(name)
        command.add_argument("workflow_id")

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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    orchestrator = ResearchReportOrchestrator(args.data_dir)
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
                    "extra": extra,
                }
            )
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
        elif args.command == "status":
            print(json.dumps(orchestrator.state.snapshot(args.workflow_id), ensure_ascii=False))
        elif args.command == "final":
            print(orchestrator.final_report(args.workflow_id))
        return 0
    except (ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
