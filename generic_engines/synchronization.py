"""Clock alignment and transport-neutral telemetry framing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from statistics import fmean
from typing import Any, Iterable


@dataclass(frozen=True)
class SensorSample:
    source: str
    device_time: float
    value: float
    sequence: int


@dataclass(frozen=True)
class ClockModel:
    """Linear clock model: reference_time = offset + scale * device_time."""

    offset: float
    scale: float
    rms_error: float

    def to_reference(self, device_time: float) -> float:
        return self.offset + self.scale * device_time

    @classmethod
    def fit(cls, pairs: Iterable[tuple[float, float]]) -> "ClockModel":
        points = list(pairs)
        if len(points) < 2:
            raise ValueError("at least two synchronization pairs are required")
        xs = [float(x) for x, _ in points]
        ys = [float(y) for _, y in points]
        x_mean, y_mean = fmean(xs), fmean(ys)
        denominator = sum((x - x_mean) ** 2 for x in xs)
        if denominator == 0:
            raise ValueError("device timestamps must not all be equal")
        scale = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator
        offset = y_mean - scale * x_mean
        residuals = [y - (offset + scale * x) for x, y in zip(xs, ys)]
        rms = (fmean([residual * residual for residual in residuals])) ** 0.5
        return cls(offset=offset, scale=scale, rms_error=rms)


def align_samples(
    samples: Iterable[SensorSample], models: dict[str, ClockModel]
) -> list[dict[str, Any]]:
    aligned: list[dict[str, Any]] = []
    for sample in samples:
        if sample.source not in models:
            raise KeyError(f"missing clock model for source {sample.source!r}")
        row = asdict(sample)
        row["reference_time"] = models[sample.source].to_reference(sample.device_time)
        row["clock_rms_error"] = models[sample.source].rms_error
        aligned.append(row)
    return sorted(aligned, key=lambda row: (row["reference_time"], row["source"], row["sequence"]))


def telemetry_frame(record: dict[str, Any], schema_version: int = 1) -> bytes:
    envelope = {"schema_version": schema_version, "payload": record}
    return json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")
