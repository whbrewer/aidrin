# Task 4 Report: SKILL.md

## Verification outputs

### Frontmatter name
```
$ awk '/^name:/{print $2}' .claude/skills/assessing-dataset-readiness/SKILL.md
assessing-dataset-readiness
```
- Matches `^[a-z0-9-]+$`: YES
- Contains `claude`: NO
- Contains `anthropic`: NO

### Description length
```
$ python3 -c "..."
description chars: 508
OK
```
508 chars <= 1024 limit.

### Line count
```
$ wc -l .claude/skills/assessing-dataset-readiness/SKILL.md
     112
```
112 lines < 500 limit.

### Markdown links
```
$ grep -oE "\]\([^)]+\)" SKILL.md
](reference/installation.md)
](reference/metrics.md)
](assets/report-template.md)
```
All three links: one level deep, all files exist.

## Self-review

- Frontmatter valid: name `assessing-dataset-readiness`, description 508 chars.
- Length: 112 lines (well under 500).
- References resolve: all three linked files present.
- No contradiction with metrics.md: `aidrin run` metric names use dash form per the consistency requirement (the intent table uses readable names only as labels, not as CLI invocations). SKILL.md defers to `reference/metrics.md` and `aidrin run <metric> -h` for exact syntax.
- `differential_privacy` is absent from the metric list and the workflow; `aidrin list` is cited as source of truth.
- Non-CSV inspection uses `read_file((path, name, ext))` per the requirement (not generic pandas).
- No ready/not-ready verdict declared.
- `aidrin`/`pip install -e .` used as general form; `uv run` not hardcoded.
- No Co-Authored-By trailer in commit.

## Commit
SHA: d934f59 — feat(skill): add SKILL.md core workflow and intent map

---

## Fix report

### Changes made

**SKILL.md** (`/Users/jlbez/Documents/repositories/AIDRIN-skill/.claude/skills/assessing-dataset-readiness/SKILL.md`):

1. **CRITICAL — Gotcha rewrite (dash-named keys):** Replaced the misleading "Dash-named keys are batch-config only" line with an accurate explanation: metric names under `aidrin run` must use dash form; underscore forms are rejected; per-metric args are positional; batch config keys are also dash form but live in the config file not in a `run` command.

2. **IMPORTANT — Intent table caveat:** Added a `_Names above are readable labels…_` note immediately after the "Always-run baseline" line below the intent table, directing agents to use dash form under `aidrin run` and linking to reference/metrics.md.

3. **IMPORTANT — Invocation portability gotcha:** Added a new gotcha bullet at the top of the Gotchas section: "If `aidrin` is not on your PATH, see reference/installation.md for the invocation form (e.g. `python -m aidrin.headless.cli` or, in a uv setup, `uv run aidrin`)."

4. **MINOR — data-quality clause:** Clarified `--detail` gotcha to explicitly name `aidrin data-quality` as the separate command that summarizes unless `--detail` is passed to it.

5. **MINOR — read_file snippet comment:** Clarified the tuple comment to `path = full file path, name = filename, ext = e.g. ".csv"`.

**reference/metrics.md** (`/Users/jlbez/Documents/repositories/AIDRIN-skill/.claude/skills/assessing-dataset-readiness/reference/metrics.md`):

6. **IMPORTANT — Invocation generalization:** Replaced "The working invocation on this repo is `uv run aidrin <args>` (a uv venv with Python 3.13 is used; bare `aidrin` may not resolve)." with "Examples use bare `aidrin`. If `aidrin` is not on PATH, see reference/installation.md for the invocation form (e.g. `uv run aidrin`)."

7. **Consistency:** All `uv run aidrin run` examples in metrics.md updated to bare `aidrin run` to match the new convention (all 9 example blocks).

### Verification outputs

**Line count:** 121 lines (< 500 limit)

**Description length:** 521 chars (≤ 1024 limit)

**Links resolve:**
- `reference/installation.md` ✓
- `reference/metrics.md` ✓
- `assets/report-template.md` ✓

**metrics.md TOC:** present (11 TOC bullet items); no `<paste>` placeholders found.

**`aidrin run class-imbalance -h` (dash form) → exit 0:**
```
usage: aidrin run class-imbalance [-h] [-v] file_path target-column
```

**`aidrin run class_imbalance -h` (underscore form) → exit 2:**
```
aidrin run: error: argument metric: invalid choice: 'class_imbalance'
(choose from completeness, duplicity, ... class-imbalance, ...)
```

### Commit
SHA: (see below) — fix(skill): correct run-name guidance and invocation consistency
