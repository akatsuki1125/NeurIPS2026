# Editing Pipeline (Diffusers)

This directory contains local Diffusers-based editing scripts for `Qwen/Qwen-Image-Edit-2511`.

## Entry point

- Unified script: `edit_images_by_qwen-image-edit-2511.py`

## Supported modes

- `visual`: original image + visual instruction image
- `text_instruction`: original image + text instruction
- `visual_with_org_tikz`: original image + visual instruction image + original TikZ code

## Recommended launcher

```bash
bash editing/diffusers/scripts/run_qwen-image-edit-2511.sh \
  --mode visual_with_org_tikz \
  --metadata_path data/metadata/edit_metadata_before_batch_api.jsonl \
  --device cuda:0 \
  --skip_existing
```

## Direct execution

```bash
python editing/diffusers/edit_images_by_qwen-image-edit-2511.py \
  --mode visual \
  --metadata_path data/metadata/edit_metadata_before_batch_api.jsonl \
  --save_dir work/editing/visual/w_org_image/qwen-image-edit-2511
```

## Notes

- Inputs are local files from metadata JSONL.
- Output images are stored as `<key>.png` under `--save_dir`.
