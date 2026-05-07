# Full Pipeline

The all-in-one pipeline is now handled by `edit.py batch pipeline`.

## Usage

```bash
uv run python edit.py batch pipeline \
  --config editing/batch_api/configs/example.toml \
  --config-name <config_name>
```

## Options

- `--config` (required): TOML config path
- `--config-name` (required for pipeline): experiment name
- `--limit N`: process only the first N metadata rows
- `--preview`: print the first request without saving
- `--batch-output-path PATH`: override batch output JSONL path
- `--poll-interval SECONDS`: batch status polling interval (default: 120)
- `--save-dir DIR`: override output directory for `.tex` files

## Output

- Batch output JSONL: `editing/batch_api/runs/<name>/output_<name>.jsonl`
- Extracted `.tex` files: `work/editing/visual/<pattern>/<model>/tikz/`
