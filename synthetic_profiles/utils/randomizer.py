from __future__ import annotations

import hashlib
import random
import secrets
import uuid
from dataclasses import dataclass, field
from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")


def derive_seed(base_seed: int, *parts: object) -> int:
    payload = "|".join([str(base_seed)] + [str(part) for part in parts])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


@dataclass(slots=True)
class GenerationContext:
    seed: int | None
    deterministic_mode: bool
    generation_id: str
    base_entropy: int
    rng_strategy: str = "generation_context_v2"
    usage_counts: dict[str, int] = field(default_factory=dict)
    batch_index: int = 0
    attempt: int = 0

    @classmethod
    def create(
        cls,
        *,
        seed: int | None,
        batch_index: int = 0,
        attempt: int = 0,
        usage_counts: dict[str, int] | None = None,
    ) -> "GenerationContext":
        deterministic_mode = seed is not None
        if deterministic_mode:
            base_entropy = derive_seed(seed, "context", batch_index, attempt)
            generation_id = f"seed-{derive_seed(seed, 'generation-id', batch_index, attempt):016x}"
        else:
            base_entropy = secrets.randbits(64)
            generation_id = f"gen-{uuid.uuid4().hex[:12]}"
        return cls(
            seed=seed,
            deterministic_mode=deterministic_mode,
            generation_id=generation_id,
            base_entropy=base_entropy,
            usage_counts=usage_counts or {},
            batch_index=batch_index,
            attempt=attempt,
        )

    def rng(self, *parts: object) -> random.Random:
        return random.Random(derive_seed(self.base_entropy, *parts))

    def child(self, *parts: object) -> "GenerationContext":
        return GenerationContext(
            seed=self.seed,
            deterministic_mode=self.deterministic_mode,
            generation_id=self.generation_id,
            base_entropy=derive_seed(self.base_entropy, *parts),
            rng_strategy=self.rng_strategy,
            usage_counts=self.usage_counts,
            batch_index=self.batch_index,
            attempt=self.attempt,
        )


def sample_count(
    rng: random.Random,
    values: Sequence[T],
    minimum: int,
    maximum: int,
) -> list[T]:
    if not values:
        return []
    count = min(len(values), rng.randint(minimum, maximum))
    return rng.sample(list(values), count)


def choice_with_penalty(
    rng: random.Random,
    values: Sequence[T],
    usage_counts: dict[str, int],
    key_fn: callable,
) -> T:
    weighted: list[tuple[float, T]] = []
    for item in values:
        key = key_fn(item)
        penalty = usage_counts.get(key, 0)
        weighted.append((1 / (1 + penalty), item))
    total = sum(weight for weight, _ in weighted)
    draw = rng.random() * total
    upto = 0.0
    for weight, item in weighted:
        upto += weight
        if upto >= draw:
            return item
    return weighted[-1][1]


def overlap_ratio(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 1.0
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)
