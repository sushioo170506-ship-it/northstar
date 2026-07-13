"""Workflow and quality profiles for different research depths."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowProfile:
    name: str
    confirmation_nodes: frozenset[str]
    quality_pass_score: float
    minimum_high_grade_ratio: float
    minimum_visual_assets: int


WORKFLOW_PROFILES = {
    "quick": WorkflowProfile(
        "quick",
        frozenset({
            "output_format_confirmation", "pre_review_confirmation"
        }),
        quality_pass_score=22.0,
        minimum_high_grade_ratio=0.6,
        minimum_visual_assets=3,
    ),
    "standard": WorkflowProfile(
        "standard",
        frozenset({
            "outline_confirmation", "output_format_confirmation",
            "pre_review_confirmation",
        }),
        quality_pass_score=24.0,
        minimum_high_grade_ratio=0.75,
        minimum_visual_assets=4,
    ),
    "deep": WorkflowProfile(
        "deep",
        frozenset(
            {
                "issue_tree_confirmation",
                "outline_confirmation",
                "draft_confirmation",
                "output_format_confirmation",
                "pre_review_confirmation",
            }
        ),
        quality_pass_score=24.0,
        minimum_high_grade_ratio=0.8,
        minimum_visual_assets=6,
    ),
    "regulatory": WorkflowProfile(
        "regulatory",
        frozenset(
            {
                "issue_tree_confirmation",
                "outline_confirmation",
                "draft_confirmation",
                "output_format_confirmation",
                "pre_review_confirmation",
            }
        ),
        quality_pass_score=30.0,
        minimum_high_grade_ratio=0.9,
        minimum_visual_assets=6,
    ),
}
