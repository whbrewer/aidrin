# Installing & verifying AIDRIN

## Preferred invocation

**MCP (preferred):** If the `list_metrics` tool is available, use MCP tools directly — no PATH or shell setup required. See the skill's Tool path table.

**CLI (fallback):** Prefer the `aidrin` console script. If it is not on PATH, use
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
in this output, do not run it — offer to scaffold it as a custom metric instead.

Known gap on the `cli-integration` branch: `differential_privacy` is not
registered and will NOT appear in `aidrin list`. When the user requests it,
offer to implement it as a custom metric. When it later appears in `aidrin list`,
run it natively.

## Agentic dependencies

The `aidrin agentic` subcommands need extra dependencies and API keys:

    pip install 'aidrin[agentic]'

Via MCP: `agentic_build_index` and `agentic_run` tools. Use when the user asks
for literature-grounded analysis or remediation recommendations.

---

## Setting up AIDRIN with Claude Code (MCP + skill)

This section is for users who want Claude Code to drive AIDRIN assessments
directly — asking questions like "is my dataset AI-ready?" and having Claude
run the metrics, interpret the results, and write a report.

### How it works

AIDRIN ships two things that plug into Claude Code:

- **MCP server** (`aidrin-mcp`) — exposes AIDRIN's metrics as tools that Claude
  can call directly, without you writing any commands.
- **Skill** (`.claude/skills/assessing-dataset-readiness/`) — tells Claude *how*
  to use those tools: what workflow to follow, which metrics to run for which
  intent, how to interpret results, and how to write the report.

Claude Code reads `.mcp.json` from your project root to connect the MCP server,
and picks up the skill automatically when the AIDRIN repo is your working directory.

### Step 1 — Install AIDRIN

Follow the [Install](#install) section above. After `pip install -e .` (or `uv sync`),
the `aidrin-mcp` console script is available in your environment.

Verify:

    aidrin-mcp --help

### Step 2 — Open the AIDRIN repo in Claude Code

The repo already contains `.mcp.json` at the root:

```json
{
  "mcpServers": {
    "aidrin": {
      "type": "stdio",
      "command": "aidrin-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

When you open this directory in Claude Code (CLI, desktop app, or IDE extension),
Claude Code automatically starts the `aidrin-mcp` server and makes its tools
available. No manual configuration needed.

> **Using a different project directory?** Copy `.mcp.json` and the
> `.claude/skills/assessing-dataset-readiness/` folder into that project's root.
> Claude Code will pick both up on next launch.

### Step 3 — Verify the MCP connection

Start a Claude Code session in the AIDRIN directory and ask:

> "List the available AIDRIN metrics."

Claude should call `list_metrics()` and return the full metric catalogue. If it
falls back to the CLI instead, the MCP server didn't connect — check that
`aidrin-mcp` is on your PATH (run `which aidrin-mcp` in a terminal).

### Step 4 — Assess a dataset

Point Claude at your data file:

> "Is my dataset at `/path/to/data.csv` ready for training a classifier?"

Claude will follow the skill's workflow: inspect the schema, propose a metric
plan, ask you to confirm column roles, run the metrics, and write an interpreted
markdown report.

Supported formats: CSV, Excel (`.xls`/`.xlsx`/`.xlsb`/`.xlsm`), JSON, NumPy
(`.npz`), HDF5 (`.h5`), Parquet.

### Step 5 (optional) — Agentic pipeline

For literature-grounded evaluation against domain papers and standards:

1. Install extra dependencies:

       pip install 'aidrin[agentic]'

2. Set your API key:

       export OPENAI_API_KEY="sk-..."   # or any OpenAI-compatible key

3. Create an agentic config YAML (see the skill's *Agentic pipeline* section for
   the full config structure), then tell Claude:

   > "Run an agentic evaluation using my config at `/path/to/config.yaml`."

   Claude will call `agentic_build_index` (once, to index your PDFs) then
   `agentic_run` to execute the full pipeline.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `aidrin-mcp` not found | Run `pip install -e .` from the AIDRIN root, or `uv sync` |
| Claude uses CLI instead of MCP tools | `.mcp.json` missing or server failed to start — check `aidrin-mcp --help` works |
| `aidrin list` fails | See [Install](#install) — likely a missing dependency |
| Agentic run fails with credential error | Set `OPENAI_API_KEY` env var before launching Claude Code |
| Agentic run fails with `metadata_csv` error | Your config must include `paths.metadata_csv` pointing to a text description of the dataset |
