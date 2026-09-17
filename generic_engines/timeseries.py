"""Small deterministic routines for timestamped numerical data."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import fmean
from typing import Iterable


@dataclass(frozen=True)
class Sample:
    timestamp: float
    value: float


def sort_and_deduplicate(samples: Iterable[Sample]) -> list[Sample]:
    """Sort samples and average duplicate timestamps."""
    buckets: dict[float, list[float]] = {}
    for sample in samples:
        buckets.setdefault(float(sample.timestamp), []).append(float(sample.value))
    return [Sample(t, fmean(buckets[t])) for t in sorted(buckets)]


def moving_average(values: list[float], window: int) -> list[float | None]:
    if window < 1:
        raise ValueError("window must be positive")
    result: list[float | None] = []
    for index in range(len(values)):
        start = index - window + 1
        result.append(None if start < 0 else fmean(values[start : index + 1]))
    return result


def rolling_features(samples: Iterable[Sample], window: int) -> list[dict[str, float]]:
    clean = sort_and_deduplicate(samples)
    if window < 2:
        raise ValueError("window must be at least 2")
    rows: list[dict[str, float]] = []
    for end in range(window, len(clean) + 1):
        segment = clean[end - window : end]
        values = [item.value for item in segment]
        mean = fmean(values)
        variance = fmean([(value - mean) ** 2 for value in values])
        duration = segment[-1].timestamp - segment[0].timestamp
        slope = 0.0 if duration == 0 else (values[-1] - values[0]) / duration
        rows.append(
            {
                "timestamp": segment[-1].timestamp,
                "mean": mean,
                "std": sqrt(variance),
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
                "slope": slope,
            }
        )
    return rows


def quality_summary(samples: Iterable[Sample], expected_interval: float) -> dict[str, float]:
    clean = sort_and_deduplicate(samples)
    if expected_interval <= 0:
        raise ValueError("expected_interval must be positive")
    if len(clean) < 2:
        return {"samples": float(len(clean)), "coverage": 0.0, "largest_gap": 0.0}
    gaps = [b.timestamp - a.timestamp for a, b in zip(clean, clean[1:])]
    expected_count = (clean[-1].timestamp - clean[0].timestamp) / expected_interval + 1
    return {
        "samples": float(len(clean)),
        "coverage": min(1.0, len(clean) / expected_count),
        "largest_gap": max(gaps),
    }
