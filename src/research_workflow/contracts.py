"""Stable interfaces that keep skills independently replaceable."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from .models import SkillRequest, SkillResult


class Skill(ABC):
    """A versioned, side-effect-free workflow capability."""

    name: str
    version: str = "1.0.0"

    @abstractmethod
    def execute(self, request: SkillRequest) -> SkillResult:
        """Transform explicit input/context into one immutable artifact."""

    def validate(self, result: SkillResult) -> None:
        if not result.content.strip():
            raise ValueError(f"{self.name} 返回了空内容")
        if not result.artifact_type:
            raise ValueError(f"{self.name} 未声明 artifact_type")


class TextGenerator(ABC):
    """Optional LLM boundary; implementations may call any model provider."""

    @abstractmethod
    def generate(self, *, system: str, prompt: str, max_tokens: int) -> str:
        """Generate text without leaking provider details into skills."""


class FunctionGenerator(TextGenerator):
    def __init__(self, function: Callable[[str, str, int], str]) -> None:
        self.function = function

    def generate(self, *, system: str, prompt: str, max_tokens: int) -> str:
        return self.function(system, prompt, max_tokens)


class SourceRetriever(ABC):
    """External search boundary for official, academic and social sources."""

    @abstractmethod
    def retrieve(
        self, *, topic: str, questions: tuple[str, ...], categories: tuple[str, ...]
    ) -> list[dict[str, Any]]:
        """Return normalized source candidates with original URLs."""


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill 已注册: {skill.name}")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        try:
            return self._skills[name]
        except KeyError as exc:
            raise KeyError(f"Skill 未注册: {name}") from exc

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._skills))
