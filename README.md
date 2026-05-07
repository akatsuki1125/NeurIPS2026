# NeurIPS2026 Evaluation & Editing Runbook

This repository provides two unified entry points for reproducible experiments:

- **`eval.py`** — evaluation of edited diagrams
- **`edit.py`** — diagram editing (TikZ generation from instructions)

`eval.py` supports:

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

Base fields per row (initial dataset, before editing):

- `id`
- `source_image` — path to the original diagram image
- `visual_instruction` — path to the annotated instruction image
- `target_image` — path to the reference/target image
- `uri` — source URL of the original diagram
- `source_tikz` — original TikZ code (inline string)
- `target_tikz` — target TikZ code (inline string)
- `edit_type` — type of edit operation (e.g., `STRUCTURE`, `STYLE`)
- `edit_operation` — edit operation index

After editing, `edited_image_paths` is appended per row to record model outputs:

```json
"edited_image_paths": {
  "w_org_image_w_org_tikz": {
    "gpt-image-1.5": "data/images/edited/gpt-image-1.5/sample.png"
  }
}
```

Example base row:

```json
{
    "id": "00000069_STRUCTURE_1_edit_0",
    "source_image": "source_images/00000069_STRUCTURE_1_edit_0.png",
    "visual_instruction": "visual_instructions/00000069_STRUCTURE_1_edit_0.png",
    "target_image": "target_images/00000069_STRUCTURE_1_edit_0.png",
    "uri": "https://tex.stackexchange.com/a/15180",
    "source_tikz": "...",
    "target_tikz": "...",
    "edit_type": "STRUCTURE",
    "edit_operation": 1
}
```

Important:

- URL passthrough is disabled for image evaluation paths.
- Images are resolved and sent from local files.

## 4. Config Files (TOML)

- Code batch config: `evaluation_code-level/batch_api/configs/*.toml`
- Image batch config: `evaluation_image-level/batch_api/configs/*.toml`

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
  --config evaluation_code-level/batch_api/configs/example.toml \
  --config-name <config_name>
```

### 5.2 Image Batch API (pipeline)

```bash
uv run python eval.py image-batch pipeline \
  --config evaluation_image-level/batch_api/configs/example.toml \
  --config-name <config_name>
```

Notes:

- Batch input is split into 3 parts by default.
- For Claude image-batch, failed samples are retried with automatic resize (long edge <= 8000px), then merged.

### 5.3 Image OpenRouter

```bash
uv run python eval.py image-openrouter \
  --input data/image_metadata.jsonl \
  --output evaluation_image-level/openrouter/runs/example/output.jsonl \
  --score-output evaluation_image-level/openrouter/runs/example/score.jsonl \
  --model Qwen/Qwen3.5-397B-A17B
```

Optional:

- `--enable-thinking`

### 5.4 Image vLLM (single-command pipeline)

First build the container image:

```bash
bash evaluation_image-level/vllm/apptainer/build.sh
```

Then run:

```bash
bash evaluation_image-level/vllm/scripts/run_vllm_pipeline_evaluation.sh \
  --model Qwen/Qwen3.5-4B \
  --input_path data/image_metadata.jsonl \
  --output_path evaluation_image-level/vllm/runs/example/output.jsonl \
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
apptainer exec evaluation_image-level/vllm/apptainer/vllm.sif \
  sh -c "grep -n 'guided-decoding-backend' /opt/setup_dir/entrypoint.sh || echo 'not found'"
```

---

# NeurIPS2026 Editing Runbook

This section covers `edit.py`, the unified entry point for diagram editing experiments.
It supports:

- TikZ editing via Batch API (OpenAI / Gemini / Claude)
- TikZ editing via vLLM server
- TikZ editing via OpenRouter
- Image editing via Diffusers (Qwen-Image-Edit-2511)

## 9. Quick Start (Editing)

```bash
uv run python edit.py -h
```

Expected sub-commands:

- `batch`
- `vllm`
- `openrouter`
- `diffusers`

## 10. Editing Metadata File (Required)

Place the base editing metadata at `data/metadata/edit_metadata.jsonl`.

Fields per row (initial dataset schema):

- `id`
- `source_image` — path to the original diagram image
- `visual_instruction` — path to the annotated instruction image
- `target_image` — path to the reference/target image
- `uri` — source URL of the original diagram
- `source_tikz` — original TikZ code (inline string)
- `target_tikz` — target TikZ code (inline string)
- `edit_type` — type of edit operation (e.g., `STRUCTURE`, `STYLE`)
- `edit_operation` — edit operation index

Example row:

```json
{
    "id": "00000069_STRUCTURE_1_edit_0",
    "source_image": "source_images/00000069_STRUCTURE_1_edit_0.png",
    "visual_instruction": "visual_instructions/00000069_STRUCTURE_1_edit_0.png",
    "target_image": "target_images/00000069_STRUCTURE_1_edit_0.png",
    "uri": "https://tex.stackexchange.com/a/15180",
    "source_tikz": "...",
    "target_tikz": "...",
    "edit_type": "STRUCTURE",
    "edit_operation": 1
}
```

## 11. Editing Config Files (TOML) — Batch Only

Config files for batch editing live in `editing/batch_api/configs/`.

Key fields:

- `name`
- `provider` (`openai` / `google` / `anthropic` / `openrouter`)
- `model`
- `system_instruction_type`
- `metadata_path`
- `save_path`

See `editing/batch_api/configs/example.toml` for a complete reference.

## 12. Execution (Editing)

### 12.1 Batch API — full pipeline

```bash
uv run python edit.py batch pipeline \
  --config editing/batch_api/configs/example.toml \
  --config-name <config_name>
```

Run individual steps instead of the full pipeline:

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

Optional flags for `generate`:

- `--limit N` — process only the first N metadata rows
- `--preview` — print the first request without saving

Optional flags for `run`:

- `--batch-output-path PATH` — override the output JSONL path
- `--poll-interval SECONDS` — polling interval (default: 120)

Optional flags for `extract`:

- `--batch-output-path PATH` — override the input JSONL path
- `--save-dir DIR` — override the output directory for `.tex` files (default: `work/editing/visual/<pattern>/<model>/tikz/`)

### 12.2 vLLM

First build the container image:

```bash
bash editing/vllm/apptainer/build.sh
```

Then start the server and run inference:

```bash
bash editing/vllm/scripts/run_vllm_pipeline_edit.sh \
  --model Qwen/Qwen3-VL-32B-Instruct \
  --gpu_id 0 \
  --port 8080
```

Or call `edit.py` directly against an already running server:

```bash
uv run python edit.py vllm \
  --mode visual_w_org_tikz \
  --input-path data/metadata/edit_metadata_before_batch_api.jsonl \
  --output-path editing/vllm/runs/example/output.jsonl \
  --hosts localhost \
  --ports 8080 \
  --model Qwen/Qwen3-VL-32B-Instruct
```

Available `--mode` values:

| Mode                | Inputs                                            |
| ------------------- | ------------------------------------------------- |
| `visual`            | original image + annotated image                  |
| `visual_w_org_tikz` | original image + annotated image + original TikZ  |
| `text_w_org_tikz`   | original image + text instruction + original TikZ |

Optional flags:

- `--num-processes-per-server N` — parallel workers per server (default: 1)
- `--seed N` — random seed (default: 42)
- `--max-tokens N` — maximum generation tokens (default: 128000)
- `--tex-output-dir DIR` — override the output directory for `.tex` files
- `--enable-thinking` — enable thinking mode

### 12.3 OpenRouter

```bash
uv run python edit.py openrouter \
  --mode visual_instruction_w_org_image_w_org_tikz \
  --jsonl-path data/metadata/edit_metadata_before_batch_api.jsonl \
  --model qwen/qwen3-vl-235b-a22b-instruct
```

Available `--mode` values:

| Mode                                        | Inputs                                            |
| ------------------------------------------- | ------------------------------------------------- |
| `visual_instruction`                        | annotated image only                              |
| `visual_instruction_w_org_image`            | original image + annotated image                  |
| `visual_instruction_w_org_tikz`             | original TikZ + annotated image                   |
| `visual_instruction_w_org_image_w_org_tikz` | original TikZ + original image + annotated image  |
| `text_instruction_w_org_image_w_org_tikz`   | original TikZ + original image + text instruction |

Optional flags:

- `--api-key KEY` — OpenRouter API key (falls back to `OPENROUTER_API_KEY`)
- `--save-dir DIR` — override output directory for `.tex` files
- `--start N` — start index (default: 0)
- `--limit N` — maximum number of records to process
- `--overwrite` — overwrite existing output files
- `--only-keys k1,k2,...` — process only specified keys
- `--max-tokens N` — maximum generation tokens (default: 128000)
- `--enable-thinking` — enable thinking mode

### 12.4 Diffusers (Qwen-Image-Edit-2511)

Requires a GPU. Install dependencies and run:

```bash
uv run python edit.py diffusers \
  --mode visual \
  --save-dir work/editing/visual/w_org_image/qwen-image-edit-2511
```

Available `--mode` values:

| Mode                   | Inputs                                           |
| ---------------------- | ------------------------------------------------ |
| `visual`               | original image + annotated image                 |
| `text_instruction`     | original image + text instruction                |
| `visual_with_org_tikz` | original image + annotated image + original TikZ |

Optional flags:

- `--metadata-path PATH` — path to edit metadata JSONL (default: `data/metadata/edit_metadata.jsonl`)
- `--model MODEL` — HuggingFace model ID (default: `Qwen/Qwen-Image-Edit-2511`)
- `--device DEVICE` — target device (default: `cuda:0`)
- `--seed N` — random seed (default: 0)
- `--skip-existing` — skip keys whose output file already exists
- `--limit N` — maximum number of records to process
- `--keys k1 k2 ...` — process only the specified keys

## 13. Editing Outputs

Typical output locations:

| Backend          | Output                                                 |
| ---------------- | ------------------------------------------------------ |
| Batch API        | `editing/batch_api/runs/<name>/output_<name>.jsonl`    |
| Batch API (TikZ) | `work/editing/<modality>/<pattern>/<model>/tikz/*.tex` |
| vLLM             | path from `--output-path`                              |
| vLLM (TikZ)      | `work/editing/<modality>/<pattern>/<model>/tikz/*.tex` |
| OpenRouter       | path from `--save-dir`                                 |
| Diffusers        | path from `--save-dir`                                 |

---

## 14. Compiling TikZ to PNG

After editing, convert the generated `.tex` files to PNG images using:

```bash
python editing/compile_tikz_batch.py --base_dir work/editing/visual
```

The script recursively discovers every subdirectory named `tikz` under `--base_dir`,
compiles each `.tex` file, and writes the PNG to a sibling `images/` directory:

```
work/editing/visual/<pattern>/<model>/tikz/foo.tex
    -> work/editing/visual/<pattern>/<model>/images/foo.png
```

### 14.1 Prerequisites

The script requires the following tools to be available on `PATH`:

- `pdflatex` (e.g. TeX Live)
- `pdfcrop` (part of TeX Live)
- `pdftoppm` (part of poppler-utils)

Alternatively, provide an Apptainer/Singularity image that bundles them.

### 14.2 Local execution

```bash
python editing/compile_tikz_batch.py \
  --base_dir work/editing/visual
```

To limit to a single model:

```bash
python editing/compile_tikz_batch.py \
  --base_dir work/editing/visual/qwen3-vl-4b-instruct
```

### 14.3 Container execution (Apptainer / Singularity)

```bash
python editing/compile_tikz_batch.py \
  --base_dir work/editing/visual \
  --apptainer path/to/texlive.sif \
  --bind /path/to/work \
  --env apptainer
```

Use `--env singularity` when running under Singularity instead of Apptainer.

### 14.4 Options

| Option | Default | Description |
|--------|---------|-------------|
| `--base_dir` | (required) | Base directory to search for `tikz` subdirectories |
| `--apptainer PATH` | — | Apptainer/Singularity image; omit to use local tools |
| `--bind DIR` | — | Directory to bind-mount into the container |
| `--env` | `apptainer` | Container runtime: `apptainer` or `singularity` |
| `--dpi N` | `300` | PNG resolution in DPI |
| `--tex_dir NAME` | `tikz` | Name of the subdirectory containing `.tex` files |
| `--png_dir NAME` | `images` | Name of the output subdirectory for PNG files |
| `--overwrite` | off | Overwrite existing PNG files |

---

## 15. Publication Checklist

- Do not commit API keys or access tokens.
- Do not hardcode personal absolute paths.
- Keep metadata/config/commands reproducible and project-relative.
