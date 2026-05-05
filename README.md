# NeurIPS2026 Evaluation Runbook

This repository provides a single entry point (`eval.py`) for reproducible evaluation.
It supports:

- Code-based evaluation: Batch API only (OpenAI / Gemini / Claude)
- Image-based evaluation: Batch API, vLLM, and OpenRouter

## 1. Quick Start

Run from repository root:

```bash
uv sync
uv run python eval.py -h
```

Expected commands:

- `code-batch`
- `image-batch`
- `image-vllm`
- `image-openrouter`

## 2. Prerequisites and API Keys

Create `.env` at repository root.

```bash
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
HF_TOKEN=your_huggingface_token
```

Which key is required:

- `code-batch` / `image-batch`
    - `judge_provider=openai` -> `OPENAI_API_KEY`
    - `judge_provider=google` -> `GOOGLE_API_KEY`
    - `judge_provider=anthropic` -> `ANTHROPIC_API_KEY`
- `image-openrouter` -> `OPENROUTER_API_KEY`
- `image-vllm` -> no API key required for local server; `HF_TOKEN` may be required for gated models

## 3. Metadata Files (Required)

Create a `data/` directory and place JSONL metadata files there.

```bash
mkdir -p data
```

### 3.1 Code Metadata (`data/code_metadata.jsonl`)

Required fields per row:

- `key`
- `org_tikz_code_path`
- `reference_tikz_code_path` or `reference_tikz_path`
- one generated code field:
    - `generated_tikz_code_path`, or
    - `edited_tikz_code_path`, or
    - `generated_code_path`, or
    - `edited_code_path`

Fallback structure is also supported:

- `edited_tikz_code_paths[edited_input_type][edited_model_type]`

Example row:

```json
{
    "key": "20260101_AAA_1_edit_1",
    "question_id": "q_0001",
    "org_tikz_code_path": "data/code/org/20260101_AAA_1_edit_1.tex",
    "reference_tikz_code_path": "data/code/ref/20260101_AAA_1_edit_1.tex",
    "generated_tikz_code_path": "data/code/gen/model_x/20260101_AAA_1_edit_1.tex"
}
```

### 3.2 Image Metadata (`data/image_metadata.jsonl`)

Recommended fields per row:

- `key`
- `question_id`
- `org_image_path`
- `visual_instruction_image_path`
- `org_tikz_code_path` (if TikZ-based judging is used)
- `edited_image_paths`

Example `edited_image_paths`:

```json
"edited_image_paths": {
  "w_org_image_w_org_tikz": {
    "gpt-image-1": "data/images/edited/gpt-image-1/sample.png"
  }
}
```

Important:

- URL passthrough is disabled for image evaluation paths.
- Images are resolved and sent from local files.

## 4. Config Files (TOML)

- Code batch config: `evaluation_code-based/batch_api/configs/*.toml`
- Image batch config: `evaluation_image-based/batch_api/configs/*.toml`

Key fields:

- `name`
- `judge_provider`
- `judge_model`
- `judge_input_type` (image-batch)
- `edited_model_type`
- `edited_input_type`
- `metadata_path`
- `save_path`
- `append`

## 5. Execution

### 5.1 Code Batch API (pipeline)

```bash
uv run python eval.py code-batch pipeline \
  --config evaluation_code-based/batch_api/configs/example.toml \
  --config-name <config_name>
```

### 5.2 Image Batch API (pipeline)

```bash
uv run python eval.py image-batch pipeline \
  --config evaluation_image-based/batch_api/configs/example.toml \
  --config-name <config_name>
```

Notes:

- Batch input is split into 3 parts by default.
- For Claude image-batch, failed samples are retried with automatic resize (long edge <= 8000px), then merged.

### 5.3 Image OpenRouter

```bash
uv run python eval.py image-openrouter \
  --input data/image_metadata.jsonl \
  --output evaluation_image-based/openrouter/runs/example/output.jsonl \
  --score-output evaluation_image-based/openrouter/runs/example/score.jsonl \
  --model Qwen/Qwen3.5-397B-A17B
```

Optional:

- `--enable-thinking`

### 5.4 Image vLLM (single-command pipeline)

First build the container image:

```bash
bash evaluation_image-based/vllm/apptainer/build.sh
```

Then run:

```bash
bash evaluation_image-based/vllm/scripts/run_vllm_pipeline_evaluation.sh \
  --model Qwen/Qwen3.5-4B \
  --input_path data/image_metadata.jsonl \
  --output_path evaluation_image-based/vllm/runs/example/output.jsonl \
  --gpu_id 0 \
  --port 8080 \
  --tensor_parallel_size 1 \
  --hf_token your-hf-token
```

Optional:

- `--hf_token <token>`
- `--enable_thinking`
- `--skip_server` (when reusing an already running server)

## 6. Outputs

Typical outputs:

- Batch input JSONL: `.../runs/<name>/input.jsonl`
- Batch output JSONL: `.../runs/<name>/output_<name>.jsonl`
- Batch score CSV: `.../runs/<name>/scores_<name>.csv`
- OpenRouter output JSONL: path from `--output`
- OpenRouter score JSONL: path from `--score-output`

## 7. Troubleshooting

- `Config not found`:
    - Check `--config-name` against `[[configs]].name` in TOML.
- Missing file errors:
    - Verify metadata paths are valid from repository root.
- vLLM startup errors:
    - Rebuild SIF after changes to `vllm.def` or `entrypoint.sh`.
    - Confirm SIF contains the latest entrypoint:

```bash
apptainer exec evaluation_image-based/vllm/apptainer/vllm.sif \
  sh -c "grep -n 'guided-decoding-backend' /opt/setup_dir/entrypoint.sh || echo 'not found'"
```

## 8. Publication Checklist

- Do not commit API keys or access tokens.
- Do not hardcode personal absolute paths.
- Keep metadata/config/commands reproducible and project-relative.
