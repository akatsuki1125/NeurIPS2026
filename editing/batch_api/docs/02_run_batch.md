# 02_run_batch.py

Submits batch requests to the provider, waits for completion, and writes output JSONL.

Supported providers: `openai`, `google`, `anthropic`.

## Usage

```bash
python editing/batch_api/steps/02_run_batch.py \
  --config editing/batch_api/configs/example.toml \
  --config-name <config_name>
```

## Options

- `--config` (required): TOML config path
- `--config-name` (required): experiment name
- `--batch-output-path PATH`: output JSONL path override
- `--poll-interval SECONDS`: polling interval (default: 120)

## Output

Output JSONL is written to `<input_dir>/output_<name>.jsonl` by default.
When `image_detail` is set to a value other than `auto`, the filename becomes
`output_<detail>_<name>.jsonl`.
