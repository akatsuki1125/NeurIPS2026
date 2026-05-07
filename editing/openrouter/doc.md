# Editing Pipeline (OpenRouter)

This directory contains OpenRouter-based editing scripts that generate final TikZ documents.

## Entry point

- Unified script: `edit_images.py`

## Supported modes

- `visual_instruction`
- `visual_instruction_w_org_image`
- `visual_instruction_w_org_tikz`
- `visual_instruction_w_org_image_w_org_tikz`
- `text_instruction_w_org_image_w_org_tikz`

## Example

```bash
python editing/openrouter/edit_images.py \
  --mode visual_instruction_w_org_image_w_org_tikz \
  --jsonl_path data/metadata/edit_metadata_before_batch_api.jsonl \
  --model qwen/qwen3-vl-235b-a22b-instruct
```

## Required environment variable

- `OPENROUTER_API_KEY`

## Notes

- Image inputs are local-only (base64 data URLs).
- URL pass-through is disabled in this unified script.
- Output files are saved as `<key>.tex` under the selected output directory.
