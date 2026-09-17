import json
import unittest

from generic_engines.documents import DocumentPipeline, FieldRule, ValidationError
from generic_engines.multiscale import build_multiscale_dataset
from generic_engines.synchronization import ClockModel, SensorSample, align_samples, telemetry_frame
from generic_engines.timeseries import Sample, quality_summary, rolling_features


class DocumentTests(unittest.TestCase):
    def test_process_and_render(self):
        pipeline = DocumentPipeline(
            {"count": FieldRule(required=True, converter=int, predicate=lambda x: x > 0)},
            {"double": lambda row: row["count"] * 2},
        )
        self.assertEqual(pipeline.render("{double}", {"count": "4"}), "8")

    def test_validation(self):
        with self.assertRaises(ValidationError):
            DocumentPipeline({"x": FieldRule(required=True)}).process({})


class SeriesTests(unittest.TestCase):
    def setUp(self):
        self.samples = [Sample(float(i), float(i)) for i in range(20)]

    def test_features(self):
        result = rolling_features(self.samples, 4)
        self.assertEqual(len(result), 17)
        self.assertAlmostEqual(result[-1]["slope"], 1.0)

    def test_quality(self):
        self.assertEqual(quality_summary(self.samples, 1.0)["coverage"], 1.0)

    def test_multiscale(self):
        result = build_multiscale_dataset(self.samples, [1, 2], lookback=3, horizon=2)
        self.assertTrue(result)
        self.assertIn("s2_change", result[-1])


class SynchronizationTests(unittest.TestCase):
    def test_clock_alignment_and_frame(self):
        model = ClockModel.fit([(0, 10), (10, 20), (20, 30)])
        rows = align_samples([SensorSample("a", 5, 2.5, 1)], {"a": model})
        self.assertAlmostEqual(rows[0]["reference_time"], 15.0)
        envelope = json.loads(telemetry_frame(rows[0]))
        self.assertEqual(envelope["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
