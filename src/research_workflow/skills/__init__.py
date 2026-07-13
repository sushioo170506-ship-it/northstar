"""Built-in skills; each module can be imported and executed independently."""

from .capability_sweep import CapabilitySweepSkill
from .citation_management import CitationManagementSkill
from .content_optimization import ContentOptimizationSkill
from .data_processing import DataProcessingSkill
from .evidence_governance import EvidenceGovernanceSkill
from .experience_evolution import ExperienceEvolutionSkill
from .formatting import FormattingSkill
from .issue_tree import IssueTreeSkill
from .material_integration import MaterialIntegrationSkill
from .outline import OutlineSkill
from .pressure_test import PressureTestSkill
from .publish import PublishSkill
from .quality_gate import QualityGateSkill
from .research import ResearchSkill
from .requirements_analysis import RequirementsAnalysisSkill
from .review import ReviewSkill
from .skill_research import SkillResearchSkill
from .visualization import VisualizationSkill
from .writing import WritingSkill
from .writing_standards import WritingStandardsSkill

__all__ = [
    "CapabilitySweepSkill",
    "CitationManagementSkill",
    "ContentOptimizationSkill",
    "ResearchSkill",
    "RequirementsAnalysisSkill",
    "SkillResearchSkill",
    "IssueTreeSkill",
    "EvidenceGovernanceSkill",
    "ExperienceEvolutionSkill",
    "DataProcessingSkill",
    "MaterialIntegrationSkill",
    "VisualizationSkill",
    "OutlineSkill",
    "WritingSkill",
    "WritingStandardsSkill",
    "PressureTestSkill",
    "FormattingSkill",
    "ReviewSkill",
    "QualityGateSkill",
    "PublishSkill",
]
