#!/usr/bin/env python3
"""Portable reference helpers for YNM adaptive execution decisions."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Iterable


class Level(str, Enum):
    ROUTE = "YNM-0"
    EVALUATE = "YNM-1"
    SPECIALIZE = "YNM-2"
    ASSURE = "YNM-3"


class Mode(str, Enum):
    PORTABLE = "PORTABLE"
    ACCELERATED = "ACCELERATED"


class Rating(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


ESCALATION_REASONS = frozenset({
    "CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE", "HIGH_IMPACT",
    "AUTHORITY_AMBIGUITY", "SECURITY_RELEVANT", "SPECIALIST_DISAGREEMENT",
    "BROAD_PROPOSITION", "RELEASE_OR_PROMOTION", "USER_REQUESTED_DEEP_REVIEW",
})


@dataclass(frozen=True)
class EvidenceSufficiency:
    affirmative_support: bool
    coverage: str
    scope_bounded: bool
    contradiction_search: str = "NOT_PERFORMED"
    complete_bounded_search: bool = False

    def supports_yes(self, *, bounded_negative: bool = False) -> bool:
        if not self.scope_bounded or self.coverage != "SUFFICIENT":
            return False
        if bounded_negative:
            return self.complete_bounded_search
        return self.affirmative_support


@dataclass(frozen=True)
class Escalation:
    current_level: Level
    next_level: Level
    reasons: tuple[str, ...]
    expected_information_gain: Rating
    expected_cost: Rating

    def justified(self, *, material: bool = False) -> bool:
        if self.next_level.value <= self.current_level.value:
            return False
        if not self.reasons or any(reason not in ESCALATION_REASONS for reason in self.reasons):
            return False
        if self.expected_information_gain is Rating.LOW:
            return False
        if self.expected_information_gain is Rating.MEDIUM and self.expected_cost is Rating.HIGH and not material:
            return False
        return True


@dataclass
class SourceCache:
    fingerprints: dict[str, str] = field(default_factory=dict)
    reads: dict[str, int] = field(default_factory=dict)

    def read(self, path: Path) -> tuple[bytes, bool]:
        data = path.read_bytes()
        fingerprint = sha256(data).hexdigest()
        key = str(path.resolve())
        cache_hit = self.fingerprints.get(key) == fingerprint
        if not cache_hit:
            self.fingerprints[key] = fingerprint
            self.reads[key] = self.reads.get(key, 0) + 1
        return data, cache_hit


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source: str
    location: str
    summary: str
    provenance: str
    ancestry: str | None = None
    memory_status: str = "VERIFIED_CURRENT"

    @property
    def corroboration_key(self) -> tuple[str, str]:
        return (self.ancestry or self.source, self.summary.strip().casefold())


def deduplicate_evidence(items: Iterable[EvidenceItem]) -> list[EvidenceItem]:
    seen: set[tuple[str, str]] = set()
    result: list[EvidenceItem] = []
    for item in items:
        key = item.corroboration_key
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def historical_memory_is_material(item: EvidenceItem) -> bool:
    return item.memory_status == "VERIFIED_CURRENT"
