# Editing Pipeline (Batch API)

This directory provides a Batch-API-based editing pipeline that generates provider JSONL requests from TOML configs, runs batch jobs, and extracts final TikZ outputs.

## Recommended usage

Use the unified entry point from the repository root:

```bash
uv run python edit.py batch pipeline \
  --config editing/batch_api/configs/example.toml \
  --config-name <config_name>
```

Run individual steps:

```bash
# Step 1: generate input JSONL
uv run python edit.py batch generate \
  --config editing/batch_api/configs/example.toml \
  --config-name <config_name>

# Step 2: submit batch and wait for results
uv run python edit.py batch run \
  --config editing/batch_api/configs/example.toml \
  --config-name <config_name>

# Step 3: extract TikZ from batch output
uv run python edit.py batch extract \
  --config editing/batch_api/configs/example.toml \
  --config-name <config_name>
```

## Step overview

- `01_generate_jsonl.py`: generate request JSONL for all or a single config
- `02_run_batch.py`: submit and monitor a single batch job (OpenAI / Gemini / Claude)
- `03_extract_tikz.py`: extract standalone TikZ documents from batch output

Supported providers per step:

| Step | Providers |
|------|-----------|
| generate (01) | `openai`, `google`, `anthropic`, `openrouter` |
| run (02) | `openai`, `google`, `anthropic` |
| extract (03) | `openai`, `google`, `anthropic`, `openrouter` |

## Directory structure

```text
editing/batch_api/
├── doc.md
├── docs/
├── configs/
├── lib/
├── runs/
└── steps/
```

## Privacy and reproducibility notes

- Use repository-relative paths in configs and commands.
- Do not store API keys in files; use environment variables.
- Avoid embedding user-specific absolute paths in shared scripts.
