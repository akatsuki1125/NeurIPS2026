# Image-based Evaluation (OpenRouter)

This directory contains the OpenRouter runner for image-based evaluation.

## Entry points

- Unified wrapper: `python eval.py image-openrouter ...` (recommended)
- Direct script: `python evaluation_image-level/openrouter/evaluate.py ...`

## Required input

- `OPENROUTER_API_KEY` environment variable
- Metadata JSONL passed with `--metadata-path`
- Edited model key passed with `--edited-model-type`
- Judge model id passed with `--model` (OpenRouter model id)

The script resolves each row using:

- `question_id` (or fallback `key`)
- `img_org_url` or `org_image_path`
- `img_visual_url` or `visual_instruction_image_path`
- `img_edited_url` or `edited_image_paths[edited_input_type][edited_model_type]`

## Example

```bash
python eval.py image-openrouter \
  --metadata-path data/metadata.jsonl \
  --edited-model-type gpt-image-1.5 \
  --model Qwen/Qwen3.5-397B-A17B \
  --output evaluation_image-level/openrouter/runs/example/output.jsonl
```

Image sending is local-only: all images are sent as base64 from local files (URL pass-through is disabled).

## Output

- Full output JSONL at `--output`
- Score-only JSONL at `score.jsonl` (or `--score-output`)

## Reproducibility and privacy notes

- Do not hard-code user-specific absolute paths.
- Keep secrets in environment variables only.

- URL pass-through is disabled. If metadata contains URLs, they must be resolvable to local files before sending.

- To change judge model, set `--model` to any OpenRouter model id (for example `openai/gpt-4.1` or `anthropic/claude-3.5-sonnet`).
