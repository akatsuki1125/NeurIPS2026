# 01_generate_jsonl.py

Generates provider-ready request JSONL files from metadata and experiment config.

## Usage

```bash
python editing/batch_api/steps/01_generate_jsonl.py \
  --config editing/batch_api/configs/example.toml
```

## Options

- `--config` (required): TOML config path
- `--config-name`: run only one config (default: all)
- `--limit`: process first N rows only
- `--preview`: print first request and skip file write

## Output

JSONL files are written to each config's `save_path`.
