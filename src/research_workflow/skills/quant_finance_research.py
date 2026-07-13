"""Validate quantitative-finance methodology and backtest disclosure."""

from __future__ import annotations

import json
import re
from typing import Any

from ..contracts import Skill
from ..models import SkillRequest, SkillResult


REQUIRED_FIELDS = {
    "universe",
    "benchmark",
    "start_date",
    "end_date",
    "frequency",
    "data_source",
    "factor_formula",
    "rebalance",
    "transaction_cost_bps",
    "metrics",
    "out_of_sample",
    "lookahead_bias_checked",
    "survivorship_bias_checked",
}
REQUIRED_METRICS = {
    "annual_return",
    "benchmark_return",
    "excess_return",
    "volatility",
    "sharpe",
    "max_drawdown",
    "turnover",
}


class QuantFinanceResearchSkill(Skill):
    name = "quant_finance_research"
    version = "1.0.0"

    @staticmethod
    def applicable(request: SkillRequest) -> bool:
        context = (
            f"{request.config.topic} {request.config.output_type} "
            f"{request.config.extra.get('writing_standard_profile', '')}"
        ).lower()
        return any(
            keyword in context
            for keyword in (
                "量化", "金工", "因子", "回测", "择时", "组合优化",
                "指数增强", "quant", "factor", "backtest",
            )
        )

    def execute(self, request: SkillRequest) -> SkillResult:
        if not self.applicable(request):
            payload = {
                "applicable": False,
                "status": "not_applicable",
                "reason": "当前报告不是量化金融工程场景",
                "hard_gates_passed": True,
                "feedback_applied": list(request.feedback),
            }
            return SkillResult(
                json.dumps(payload, ensure_ascii=False, indent=2),
                "quant_research_validation",
                {"applicable": False, "status": "not_applicable"},
            )
        analysis = request.config.extra.get("quant_analysis", {})
        if not isinstance(analysis, dict):
            analysis = {}
        missing_fields = sorted(REQUIRED_FIELDS - analysis.keys())
        metrics = analysis.get("metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}
        missing_metrics = sorted(REQUIRED_METRICS - metrics.keys())
        metric_sources = analysis.get("metric_sources", {})
        if not isinstance(metric_sources, dict):
            metric_sources = {}
        untraced_metrics = sorted(
            metric for metric in REQUIRED_METRICS
            if metric in metrics and not metric_sources.get(metric)
        )
        issues = []
        if missing_fields:
            issues.append("缺少回测字段：" + "、".join(missing_fields))
        if missing_metrics:
            issues.append("缺少绩效指标：" + "、".join(missing_metrics))
        if untraced_metrics:
            issues.append("指标缺少来源：" + "、".join(untraced_metrics))
        if analysis.get("transaction_cost_bps", 0) in {None, ""}:
            issues.append("未披露交易成本")
        if analysis.get("out_of_sample") is not True:
            issues.append("未完成样本外验证")
        if analysis.get("lookahead_bias_checked") is not True:
            issues.append("未完成前视偏差检查")
        if analysis.get("survivorship_bias_checked") is not True:
            issues.append("未完成幸存者偏差检查")
        formula = str(analysis.get("factor_formula") or "")
        if formula and not re.search(r"[=+\-*/()]|rank|zscore", formula, re.I):
            issues.append("因子公式不可复核")
        hard_gates_passed = not issues
        payload = {
            "applicable": True,
            "status": "completed" if hard_gates_passed else "incomplete",
            "subtype": analysis.get("subtype", "factor_or_timing"),
            "data_contract": {
                key: analysis.get(key)
                for key in (
                    "universe", "benchmark", "start_date", "end_date",
                    "frequency", "data_source",
                )
            },
            "methodology": {
                "factor_formula": analysis.get("factor_formula"),
                "preprocessing": analysis.get("preprocessing", []),
                "neutralization": analysis.get("neutralization"),
                "rebalance": analysis.get("rebalance"),
                "portfolio_constraints": analysis.get(
                    "portfolio_constraints", []
                ),
            },
            "backtest": {
                "metrics": metrics,
                "metric_sources": metric_sources,
                "transaction_cost_bps": analysis.get(
                    "transaction_cost_bps"
                ),
                "slippage_bps": analysis.get("slippage_bps"),
            },
            "robustness": {
                "out_of_sample": analysis.get("out_of_sample"),
                "walk_forward": analysis.get("walk_forward"),
                "parameter_stability": analysis.get("parameter_stability"),
                "lookahead_bias_checked": analysis.get(
                    "lookahead_bias_checked"
                ),
                "survivorship_bias_checked": analysis.get(
                    "survivorship_bias_checked"
                ),
            },
            "missing_fields": missing_fields,
            "missing_metrics": missing_metrics,
            "untraced_metrics": untraced_metrics,
            "issues": issues,
            "hard_gates_passed": hard_gates_passed,
            "disclaimer": (
                "历史回测不代表未来表现；结果仅用于研究复核，不构成投资建议。"
            ),
            "reference_playbook": {
                "name": "hugo2046/QuantsPlaybook",
                "source_url": "https://github.com/hugo2046/QuantsPlaybook",
                "version": "87163521c75629a3466564c017ac734a236a9ce4",
                "license": "NOASSERTION",
                "usage": "methodological_reference_only",
                "code_executed": False,
            },
            "feedback_applied": list(request.feedback),
        }
        return SkillResult(
            json.dumps(payload, ensure_ascii=False, indent=2),
            "quant_research_validation",
            {
                "applicable": True,
                "status": payload["status"],
                "issue_count": len(issues),
                "hard_gates_passed": hard_gates_passed,
            },
        )

    def validate(self, result: SkillResult) -> None:
        super().validate(result)
        payload = json.loads(result.content)
        if not {"applicable", "status", "hard_gates_passed"} <= payload.keys():
            raise ValueError("quant_finance_research 缺少必要字段")
        if payload["applicable"] and "reference_playbook" not in payload:
            raise ValueError("量化报告必须记录参考Playbook来源与许可证")
