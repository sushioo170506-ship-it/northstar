"""Built-in skills; each module can be imported and executed independently."""

from .evidence_governance import EvidenceGovernanceSkill
from .formatting import FormattingSkill
from .issue_tree import IssueTreeSkill
from .outline import OutlineSkill
from .pressure_test import PressureTestSkill
from .quality_gate import QualityGateSkill
from .research import ResearchSkill
from .review import ReviewSkill
from .writing import WritingSkill

__all__ = [
    "ResearchSkill",
    "IssueTreeSkill",
    "EvidenceGovernanceSkill",
    "OutlineSkill",
    "WritingSkill",
    "PressureTestSkill",
    "FormattingSkill",
    "ReviewSkill",
    "QualityGateSkill",
]
