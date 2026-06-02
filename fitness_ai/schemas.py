from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class ExerciseLevel(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"

    @classmethod
    def coerce(cls, value: str | "ExerciseLevel") -> "ExerciseLevel":
        if isinstance(value, cls):
            return value
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"unsupported exercise level: {value}")


@dataclass(frozen=True)
class Exercise:
    title: str
    desc: str
    type: str
    body_part: str
    equipment: str
    level: ExerciseLevel | str
    rating: float
    excluded_injuries: tuple[str, ...] | list[str] | str = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for attr in ("title", "desc", "type", "body_part", "equipment"):
            if not str(getattr(self, attr)).strip():
                raise ValueError(f"{attr} is required")
        rating = float(self.rating)
        if not 0.0 <= rating <= 10.0:
            raise ValueError("rating must be between 0.0 and 10.0")
        object.__setattr__(self, "rating", rating)
        object.__setattr__(self, "level", ExerciseLevel.coerce(self.level))
        object.__setattr__(self, "excluded_injuries", normalize_injuries(self.excluded_injuries))


@dataclass
class ParsedIntent:
    body_part: str | None = None
    equipment: list[str] = field(default_factory=list)
    level: ExerciseLevel | None = None
    injuries: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    requested_titles: list[str] = field(default_factory=list)


@dataclass
class SafetyBlock:
    reason: str
    blocked_injuries: list[str]
    requested_title: str | None = None


@dataclass
class RecommendationRequest:
    message: str
    max_results: int = 5

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("message is required")
        if not 1 <= int(self.max_results) <= 20:
            raise ValueError("max_results must be between 1 and 20")


@dataclass
class RecommendationItem:
    title: str
    desc: str
    type: str
    body_part: str
    equipment: str
    level: ExerciseLevel
    rating: float
    safety_notes: list[str] = field(default_factory=list)


@dataclass
class RecommendationResponse:
    status: Literal["ok", "no_match", "safety_block"]
    message_th: str
    parsed_intent: ParsedIntent
    safety_blocks: list[SafetyBlock] = field(default_factory=list)
    recommendations: list[RecommendationItem] = field(default_factory=list)


def normalize_injuries(value: tuple[str, ...] | list[str] | set[str] | str | None) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        clean = value.strip().lower()
        if not clean or clean == "none":
            return ()
        return tuple(part.strip().lower() for part in clean.split(",") if part.strip())
    return tuple(str(part).strip().lower() for part in value if str(part).strip())