# Editing Pipeline (vLLM)

This directory provides vLLM-based editing inference against OpenAI-compatible local endpoints.

## Entry points

- Unified Python runner: `run_vllm_edit_inference.py`
- Unified shell launcher: `scripts/run_vllm_pipeline_edit.sh`

## Supported modes

- `visual`
- `visual_w_org_tikz`
- `text_w_org_tikz`

## Recommended one-command run

```bash
bash editing/vllm/scripts/run_vllm_pipeline_edit.sh \
  --mode visual_w_org_tikz \
  --model qwen3-vl-32b-instruct \
  --input_path data/metadata/edit_metadata_before_batch_api.jsonl \
  --output_path work/editing/vllm/runs/example/output.jsonl \
  --gpu_id 0 \
  --port 8080
```

## Useful options

- `--skip_server`: use an already-running vLLM endpoint
- `--enable_thinking`: enable thinking mode
- `--hosts` and `--ports`: target inference endpoints
- `--num_processes_per_server`: workers per endpoint

## Notes

- Input JSONL must reference local image files.
- Output JSONL stores full model responses and metadata.
- TikZ outputs are written to the configured `--tex_output_dir`.
