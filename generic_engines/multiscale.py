"""Multiscale state-vector construction and future-outcome labels."""

from __future__ import annotations

from statistics import fmean
from typing import Iterable

from .timeseries import Sample, sort_and_deduplicate


def aggregate(samples: Iterable[Sample], interval: float) -> list[Sample]:
    if interval <= 0:
        raise ValueError("interval must be positive")
    buckets: dict[int, list[float]] = {}
    for sample in sort_and_deduplicate(samples):
        bucket = int(sample.timestamp // interval)
        buckets.setdefault(bucket, []).append(sample.value)
    return [Sample(bucket * interval, fmean(values)) for bucket, values in sorted(buckets.items())]


def state_at(series: list[Sample], timestamp: float, lookback: int) -> dict[str, float] | None:
    history = [sample for sample in series if sample.timestamp <= timestamp]
    if len(history) < lookback:
        return None
    window = history[-lookback:]
    values = [sample.value for sample in window]
    mean = fmean(values)
    return {
        "level": values[-1],
        "change": values[-1] - values[0],
        "mean": mean,
        "deviation": values[-1] - mean,
        "amplitude": max(values) - min(values),
    }


def build_multiscale_dataset(
    samples: Iterable[Sample],
    scales: Iterable[float],
    lookback: int = 5,
    horizon: int = 3,
) -> list[dict[str, float]]:
    base = sort_and_deduplicate(samples)
    scale_list = sorted(set(float(scale) for scale in scales))
    if not scale_list or any(scale <= 0 for scale in scale_list):
        raise ValueError("scales must contain positive intervals")
    if lookback < 2 or horizon < 1:
        raise ValueError("lookback must be >= 2 and horizon must be >= 1")
    aggregated = {scale: aggregate(base, scale) for scale in scale_list}
    rows: list[dict[str, float]] = []
    for index in range(len(base) - horizon):
        current = base[index]
        row: dict[str, float] = {"timestamp": current.timestamp}
        complete = True
        for scale in scale_list:
            state = state_at(aggregated[scale], current.timestamp, lookback)
            if state is None:
                complete = False
                break
            prefix = f"s{scale:g}_"
            row.update({prefix + key: value for key, value in state.items()})
        if complete:
            future = base[index + horizon].value
            row["future_change"] = future - current.value
            row["future_direction"] = float((future > current.value) - (future < current.value))
            rows.append(row)
    return rows
