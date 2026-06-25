# Installing & verifying the AIDRIN CLI

## Invocation form used by this skill

Prefer the `aidrin` console script. If it is not on PATH, use
`python -m aidrin.headless.cli` with the same arguments. Decide once and use
consistently.

If you are using the `uv`-managed environment shipped with this repo (see
[uv path](#uv-path) below), use `uv run aidrin` instead.

## Install

### Standard (Python >= 3.10 required)

From the AIDRIN repository root:

    pip install -e .

This pulls the runtime dependencies the metrics need (pandas, numpy, scipy,
scikit-learn, matplotlib, seaborn, dython, shap, h5py, openpyxl, pgeocode,
pyarrow). A partial environment (e.g. missing matplotlib) will fail at import.

> **Note:** Python 3.9 (macOS system default) is not supported. Use Python
> 3.10 or later.

### uv path

The repo ships a `uv.lock`. If you have [uv](https://github.com/astral-sh/uv)
installed, you can create a ready-to-use Python 3.13 environment without
touching your system Python:

    uv sync
    uv run aidrin list   # quick smoke test

All `aidrin` commands can then be prefixed with `uv run`:

    uv run aidrin run --dataset path/to/data.csv --metric completeness

## Verify (capability check — also the skill's Step 1 preflight)

    aidrin list
    # or, with uv:
    uv run aidrin list

Expected: JSON of available metrics grouped by category. This list is the
source of truth for which metrics exist. If a metric you intend to run is not
in this output, do not run it.

Known gap on the `cli-integration` branch: `differential_privacy` is not
registered and will NOT appear in `aidrin list`. Skip it when absent. When it
later appears in `aidrin list`, the skill picks it up automatically.

## Out of scope

The `aidrin agentic` subcommands need extra dependencies
(`pip install 'aidrin[agentic]'`), API keys, and a vector index. This skill
does not use them.
