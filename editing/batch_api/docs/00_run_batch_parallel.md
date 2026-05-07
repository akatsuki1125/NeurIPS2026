# Parallel Batch Runners

The parallel runner scripts have been removed. Use `edit.py batch pipeline` for each
experiment, or run multiple instances in separate terminal sessions.

## Running multiple experiments

```bash
# Run experiments one by one
uv run python edit.py batch pipeline \
  --config editing/batch_api/configs/example.toml \
  --config-name exp_a

uv run python edit.py batch pipeline \
  --config editing/batch_api/configs/example.toml \
  --config-name exp_b
```

## Notes

- Keep all paths relative to repository root for portability.
- Store API keys in environment variables only.
