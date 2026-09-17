"""Run synthetic examples for every engine."""

from __future__ import annotations

from pprint import pprint

from .documents import DocumentPipeline, FieldRule
from .multiscale import build_multiscale_dataset
from .synchronization import ClockModel, SensorSample, align_samples, telemetry_frame
from .timeseries import Sample, quality_summary, rolling_features


def main() -> None:
    records = DocumentPipeline(
        rules={
            "item": FieldRule(required=True, converter=str),
            "quantity": FieldRule(required=True, converter=int, predicate=lambda x: x > 0, message="must be positive"),
            "unit_price": FieldRule(required=True, converter=float, predicate=lambda x: x >= 0, message="must be nonnegative"),
        },
        derived={"total": lambda row: row["quantity"] * row["unit_price"]},
    )
    print(records.render("Item: {item}\nTotal: {total:.2f}", {"item": "Synthetic A", "quantity": "3", "unit_price": "4.5"}))

    samples = [Sample(float(i), 10.0 + i * 0.2 + (i % 3) * 0.1) for i in range(30)]
    pprint(quality_summary(samples, expected_interval=1.0))
    pprint(rolling_features(samples, window=5)[-1])
    pprint(build_multiscale_dataset(samples, scales=[1, 5], lookback=3, horizon=2)[-1])

    model = ClockModel.fit([(0.0, 100.0), (10.0, 110.01), (20.0, 120.02)])
    aligned = align_samples([SensorSample("sensor-a", 5.0, 42.0, 1)], {"sensor-a": model})
    pprint(aligned[0])
    print(telemetry_frame(aligned[0]).decode())


if __name__ == "__main__":
    main()
