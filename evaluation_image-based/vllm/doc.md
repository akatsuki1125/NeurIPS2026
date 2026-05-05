# Image-based Evaluation (vLLM)

This directory provides image-based evaluation against a vLLM-compatible OpenAI endpoint.

## Recommended one-command pipeline

Use this script to run **server startup + evaluation** in one command:

```bash
bash evaluation_image-based/vllm/scripts/run_vllm_pipeline_evaluation.sh \
  --model Qwen/Qwen3.5-4B \
  --input_path data/image_metadata.jsonl \
  --output_path evaluation_image-based/vllm/runs/example/output.jsonl \
  --gpu_id 0 \
  --port 8080 \
  --tensor_parallel_size 1
```

## Important options

- `--skip_server`: use an already-running vLLM server
- `--enable_thinking`: enable thinking mode
- `--hosts` and `--ports`: inference target endpoints
- `--num_processes_per_server`: worker processes per endpoint

## Input requirement

Input JSONL must reference local image paths resolvable on this machine.
URL pass-through is disabled.
