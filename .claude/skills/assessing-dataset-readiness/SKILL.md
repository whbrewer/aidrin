---
name: assessing-dataset-readiness
description: Assess whether a dataset is AI/ML-ready by running AIDRIN's CLI metrics for data quality, fairness/bias, privacy, and governance, then producing an interpreted readiness report. Supports CSV, Excel (.xls/.xlsb/.xlsx/.xlsm), JSON, NumPy (.npz), HDF5 (.h5), and Parquet files. Use when the user asks "is my data AI ready", "is my dataset ready to be used by AI", "what is the quality of my data", whether data is good enough to train or publish, to check a dataset for bias or privacy risk, or mentions AIDRIN.
---

# Assessing dataset AI-readiness with AIDRIN

Drive the `aidrin` CLI to assess a dataset and produce an interpreted markdown
report. The CLI runs the metrics; you choose what to run based on the user's
intent, interpret the results, and report scores with their meaning. You do NOT
declare a final ready/not-ready verdict — that judgment is the user's.

## Workflow

Copy this checklist and work through it in order:

```
- [ ] 1. Preflight: `aidrin list` (confirm CLI works; read which metrics exist)
- [ ] 2. Elicit intent: how will the user use this dataset?
- [ ] 3. Inspect: read the AIDRIN-parsed schema + a small sample
- [ ] 4. Plan: map intent + columns -> metrics + exact commands (with rationale)
- [ ] 5. Confirm plan with the user (HARD gate on column roles)
- [ ] 6. Validate planned column names against the schema
- [ ] 7. Run metrics (per-metric `aidrin run`; batch only for arg-identical groups)
- [ ] 8. Write the report from assets/report-template.md; save raw JSON alongside
```

### 1. Preflight
Run `aidrin list`. If it fails, see [reference/installation.md](reference/installation.md).
The listed metrics are the source of truth — never run a metric that is not
listed (e.g. `differential_privacy` is currently absent; skip it).

### 2. Elicit intent
Ask how the user plans to use the dataset. Examples that change the plan:
train a supervised model (and on what target?), ensure fairness across groups,
publish/share the dataset, general quality check, or "it contains PII". Real
answers are often blended (train AND publish) — handle the union.

### 3. Inspect the dataset
Get the schema AIDRIN itself will see — do NOT rely on a generic pandas read for
non-CSV files (AIDRIN's JSON/NPZ/H5 readers reshape data differently). Use:

```python
from aidrin.file_handling.file_parser import read_file
df = read_file((path, name, ext))   # ext like ".csv"; name is the filename
print(df.columns.tolist()); print(df.dtypes); print(df.head())
```

For CSV, `head <file>` is equivalent. Use this to identify candidate roles:
target, sensitive attributes, quasi-identifiers, id column, categorical vs
numerical.

### 4. Build the plan
Map intent + columns to metrics using the table below. For each chosen metric,
write the exact `aidrin run` command (positional args — see
[reference/metrics.md](reference/metrics.md) for syntax/order). Give a one-line
rationale per metric. Always include the zero-arg quality baseline.

| User intent | Metrics | Columns needed |
|---|---|---|
| Train supervised model | completeness, duplicity, outliers, feature_relevance, class_imbalance, correlations | target; categorical/numerical features; correlations & feature_relevance need columns |
| Ensure fairness across groups | class_imbalance, statistical_rates, representation_rate | target + sensitive attribute(s) |
| Publish / share externally | k_anonymity, l_diversity, t_closeness, entropy_risk, single_attribute_risk, multiple_attribute_risk | quasi-identifiers, sensitive column, id column + eval columns |
| General quality / exploration | completeness, duplicity, outliers, correlations | correlations needs columns |
| Contains PII / sensitive data | governance + privacy set above | quasi-identifiers, sensitive column |

Always-run baseline (zero-arg): completeness, duplicity, outliers.

### 5. Confirm the plan (HARD gate)
Present the plan AND explicitly list every inferred column role — target /
sensitive / quasi-identifiers / id — each with a one-line reason. Add: "I may
have missed indirect identifiers (e.g. zip, birthdate, rare categories) — please
confirm or correct these." Do not run anything until the user confirms. Wrong
quasi-identifiers produce a falsely reassuring privacy result.

### 6. Validate column names
Check every column name in the plan against the schema from Step 3. Fix typos /
casing / non-existent columns before running.

### 7. Run the metrics
- Default: one `aidrin run <metric> <file> <args...>` per metric. This isolates
  errors and lets each metric use its own columns.
- Batch only an arg-identical group. The zero-arg baseline is the natural batch:
  `aidrin batch <config>` with `{"file_path": "...", "metrics": ["completeness","duplicity","outliers"]}`.
- If a metric errors, record it as "Not run: <reason>" and continue with the rest.

### 8. Write the report
Fill in [assets/report-template.md](assets/report-template.md). Report each
score with its directional meaning (from reference/metrics.md). Flag extremes.
Keep privacy/fairness findings explicitly conditional on the confirmed roles.
Do not state a ready/not-ready verdict — give findings + suggested next steps and
let the user decide. Save each metric's raw JSON next to the report and list the
commands run.

## Gotchas
- `aidrin run` args are POSITIONAL in `required_args` order, not `--flags`. Quote
  comma-separated column lists: `"zip,age"`. Dash-named keys are batch-config only.
- Confirm exact per-metric arg order with `aidrin run <metric> -h` or
  reference/metrics.md. `feature_relevance` needs at least one of
  categorical/numerical columns plus the target, or it exits 2.
- `aidrin list` is the source of truth for available metrics; `differential_privacy`
  is currently absent — skip it, don't assume it exists.
- For non-CSV (JSON/NPZ/H5), derive the schema via `read_file`, not a plain pandas
  read — column sets differ.
- `--detail` is already the default for `run`/`batch` (full JSON, viz stripped);
  no need to add it. `data-quality` summarizes unless `--detail`.
- `statistical_rates` is label-distribution, not model-output fairness.
- Run produces no ready/not-ready verdict — that is the user's call.

## Scope
This skill covers metric assessment only. Out of scope: the `aidrin agentic`
pipeline, the web UI, custom-metric authoring, and remediation.
