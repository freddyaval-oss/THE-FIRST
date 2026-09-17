# Generic Logic Engines

Reusable, domain-neutral Python components extracted from recurring software patterns:

1. **Record-to-document pipeline** — load, normalize, validate, calculate, and render structured records.
2. **Time-series pipeline** — clean samples, smooth values, extract rolling features, and evaluate data quality.
3. **Synchronized sensor pipeline** — timestamp independent measurements, align them to a common clock, and package telemetry frames.
4. **Multiscale state engine** — aggregate a series at several scales, build state vectors, and label future outcomes for reproducible research.

The repository contains no institutional names, operational procedures, proprietary templates, real measurements, credentials, or product-specific parameters. Examples use synthetic data.

## Requirements

- Python 3.11 or newer
- No runtime dependencies outside the Python standard library

## Quick start

```bash
python -m generic_engines.demo
python -m unittest discover -s tests -v
```

## Package layout

```text
generic_engines/
  documents.py       generic record-to-document workflow
  timeseries.py      numerical cleaning and feature extraction
  synchronization.py clock alignment and telemetry frames
  multiscale.py      multiscale state vectors and future labels
  demo.py            complete synthetic demonstration
tests/               unit tests
docs/architecture.md design and extension points
```

## Design rules

- Domain meaning stays outside the engine. Callers provide field mappings, validation rules, feature functions, scale definitions, and renderers.
- Every stage receives plain Python data and returns plain Python data.
- Inputs are copied before transformation to avoid hidden mutation.
- Validation errors include the affected field and reason.
- Numerical routines are deterministic and suitable for unit testing.
- Time synchronization exposes residual error instead of hiding it.

## Example uses

- Generate standardized reports, certificates, summaries, or forms from structured records.
- Clean and characterize telemetry, environmental, industrial, financial, or laboratory series.
- Merge measurements from independent devices that share reference timestamps.
- Compare state features across time scales and test their relationship with later observations.

## Public-use boundary

Only generic code and synthetic examples belong in this repository. Keep private datasets, real reports, internal procedures, equipment configurations, customer identifiers, access tokens, and third-party copyrighted templates outside the repository.

## License

MIT. See `LICENSE`.
