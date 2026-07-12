"""Built-in skills; each module can be imported and executed independently."""

from .formatting import FormattingSkill
from .outline import OutlineSkill
from .research import ResearchSkill
from .review import ReviewSkill
from .writing import WritingSkill

__all__ = [
    "ResearchSkill",
    "OutlineSkill",
    "WritingSkill",
    "FormattingSkill",
    "ReviewSkill",
]
