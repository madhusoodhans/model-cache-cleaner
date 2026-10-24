# PyTorch Hub

```json
{
  "tool": "PyTorch Hub",
  "homepage": "https://pytorch.org/docs/stable/hub.html",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/.cache/torch/hub/checkpoints"],
      "linux": ["~/.cache/torch/hub/checkpoints"],
      "after_delete": "Weights are re-downloaded the next time code loads them."
    },
    {
      "kind": "cache",
      "macos": ["~/.cache/torch/kernels", "~/.cache/torch/inductor"],
      "linux": ["~/.cache/torch/kernels", "~/.cache/torch/inductor"],
      "after_delete": "Compiled kernels, rebuilt on next run."
    }
  ]
}
```

## What it stores

- **`hub/checkpoints/`:** model weights from `torch.hub.load`, `torchvision` and libraries built on them (TTS, vision and audio models).
- **`hub/<owner>_<repo>_<branch>/`:** source code of models loaded from GitHub. Small.

`TORCH_HOME` moves the whole folder.

## Safe to delete

- Everything in `~/.cache/torch`. All of it is re-downloaded or rebuilt on demand.

## How to clean

1. List files in `hub/checkpoints/` by size. File names usually identify the model.
2. Delete the ones the user no longer uses, or the whole folder.
