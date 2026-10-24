# Hugging Face

```json
{
  "tool": "Hugging Face",
  "homepage": "https://huggingface.co/docs/huggingface_hub/guides/manage-cache",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/.cache/huggingface/hub"],
      "linux": ["~/.cache/huggingface/hub"],
      "env": ["HF_HUB_CACHE"],
      "model_depth": 1,
      "cleanup": "hf cache scan, then hf cache delete (older versions: huggingface-cli scan-cache / delete-cache)",
      "after_delete": "Model is re-downloaded the next time any library loads it."
    },
    {
      "kind": "cache",
      "macos": ["~/.cache/huggingface/xet"],
      "linux": ["~/.cache/huggingface/xet"],
      "after_delete": "Download chunk cache, rebuilt automatically."
    },
    {
      "kind": "models",
      "macos": ["~/.cache/huggingface/datasets"],
      "linux": ["~/.cache/huggingface/datasets"],
      "env": ["HF_DATASETS_CACHE"],
      "after_delete": "Datasets are re-downloaded and re-processed when used again."
    }
  ]
}
```

## What it stores

The Hugging Face cache is shared by `transformers`, `diffusers`, `mlx-lm`, `sentence-transformers` and many other tools. They all download into the same place.

- **`hub/models--<org>--<name>`:** one folder per model. Inside, `blobs/` holds the data and `snapshots/` holds symlinks to it.
- **`hub/datasets--...`, `hub/spaces--...`:** datasets and Spaces downloaded through the hub.
- **`xet/`:** chunk cache for the Xet download backend.
- **`datasets/`:** processed datasets from the `datasets` library.
- **`token`:** the user's login token. Never delete it.

`HF_HOME` moves everything. `HF_HUB_CACHE` moves only `hub/`.

## Safe to delete

- `xet/`.
- Individual `models--*` folders the user no longer uses.

## Never delete

- `~/.cache/huggingface/token` and `stored_tokens`.

## How to clean

1. `hf cache scan` lists every model with its size and last-used date.
2. `hf cache delete` opens an interactive picker. Older versions use `huggingface-cli delete-cache`.
3. Or remove `hub/models--<org>--<name>` folders directly. Measure them without following symlinks, or sizes double-count.
