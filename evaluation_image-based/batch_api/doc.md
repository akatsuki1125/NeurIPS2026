# Image-based Evaluation (Batch API)

This directory provides image-based evaluation through provider Batch APIs.

Supported judge providers:
- OpenAI (GPT family)
- Google (Gemini family)
- Anthropic (Claude family)

## Entry points

You can run this pipeline in two ways:
- Unified wrapper: `python eval.py image-batch ...` (recommended)
- Direct step scripts under `steps/`

## Pipeline steps

1. Generate provider input JSONL from metadata/config.
2. Submit batch requests and wait for completion.
3. Extract score fields to CSV.

## Example (recommended)

```bash
python eval.py image-batch pipeline \
  --config evaluation_image-based/batch_api/configs/example.toml \
  --config-name example_experiment
```

## Equivalent direct commands

```bash
python evaluation_image-based/batch_api/steps/01_generate_jsonl.py \
  --config evaluation_image-based/batch_api/configs/example.toml \
  --config-name example_experiment

python evaluation_image-based/batch_api/steps/02_run_batch.py \
  --config evaluation_image-based/batch_api/configs/example.toml \
  --config-name example_experiment

python evaluation_image-based/batch_api/steps/03_extract_scores.py \
  --config evaluation_image-based/batch_api/configs/example.toml \
  --config-name example_experiment
```

## Reproducibility and privacy notes

- Keep metadata and config paths relative to the repository root.
- Avoid embedding private user information or environment-specific absolute paths.
- Share only sanitized configs and logs.


## Batch size split

`steps/02_run_batch.py` (and `eval.py image-batch ... run/pipeline`) now split input JSONL into **3 parts by default**, submit them sequentially, and merge outputs into one JSONL.

- Default: `--num-splits 3`
- You can override: `--num-splits <N>`

This helps avoid provider request-size limits (for example HTTP 413).

- URL pass-through is disabled. Image inputs are sent from local files only (base64/inlineData by provider).

- Claude only: run once in normal mode first. Failed items are then retried automatically with image resize (long edge <= 8000px), and retry outputs override the failed originals in final output.
