# 03_extract_tikz.py

Extracts final TikZ code from batch output JSONL and writes standalone `.tex` files.

Supported providers: `openai`, `google`, `anthropic`, `openrouter`.

## Usage

```bash
python editing/batch_api/steps/03_extract_tikz.py \
  --config editing/batch_api/configs/example.toml
```

## Options

- `--config` (required): TOML config path
- `--config-name`: process one config only (all configs if omitted)
- `--batch-output-path PATH`: override input JSONL path
- `--save-dir DIR`: output directory for `.tex` files

## Default output path

When `--save-dir` is omitted, TikZ files are written to:

```
work/editing/visual/<pattern>/<model>/tikz/
```

where `<pattern>` is derived from `system_instruction_type` (with the
`visual_instruction_` prefix stripped) and `<model>` is the last component
of the model identifier.

## Output

- One `.tex` file per sample key
- Standalone LaTeX/TikZ document format
