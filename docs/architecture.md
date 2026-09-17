# Architecture

## Common processing contract

Each engine follows the same six-stage pattern:

1. **Acquire** plain records or timestamped samples.
2. **Normalize** types, names, ordering, and duplicate observations.
3. **Validate** required fields, ranges, time assumptions, and configuration.
4. **Transform** data with domain-supplied rules.
5. **Expose quality** through explicit errors, coverage values, or clock residuals.
6. **Export** plain dictionaries, text, or versioned byte frames.

This separation lets an application replace its data source, renderer, transport, or analysis method without modifying the central workflow.

## Engines

### Record-to-document

`DocumentPipeline` accepts field rules and derived-field functions. The engine does not know what a record represents. A separate application can later add CSV, database, spreadsheet, web-form, Word, HTML, or PDF adapters.

### Time series

The time-series module sorts samples, resolves duplicate timestamps, calculates rolling descriptive features, and reports acquisition coverage. Its output is suitable for visualization, rule engines, or statistical models.

### Synchronized sensors

`ClockModel` estimates offset and scale from device/reference time pairs. The result corrects both constant offset and linear clock drift. Every aligned sample retains the model's RMS residual so downstream logic can reject data that exceeds its own tolerance.

`telemetry_frame` supplies a minimal versioned envelope. Production systems can replace JSON with another encoding and add message authentication, encryption, retransmission, or compression at the transport boundary.

### Multiscale state

The multiscale engine aggregates a base series at configured intervals. It calculates the same state variables at each scale and attaches future-change labels. This produces a rectangular dataset for hypothesis testing or model training while keeping feature construction separate from evaluation.

## Extension points

- Input adapters: CSV, SQL, APIs, files, message queues, or device streams.
- Validation: schema libraries, units, calibration status, and business rules.
- Processing: custom filters, transforms, domain features, and uncertainty propagation.
- Outputs: text templates, office documents, dashboards, databases, or event streams.
- Evaluation: holdout sets, walk-forward tests, confidence intervals, and drift monitoring.

## Security and publication

Keep secrets in environment variables or an external secret store. Never commit raw operational data. Add anonymization before export and use synthetic fixtures in tests. Review dependencies, generated files, and Git history before changing a repository from private to public.
