# pip

```json
{
  "tool": "pip",
  "homepage": "https://pip.pypa.io/en/stable/topics/caching/",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "cache",
      "macos": ["~/Library/Caches/pip"],
      "linux": ["~/.cache/pip"],
      "env": ["PIP_CACHE_DIR"],
      "cleanup": "pip cache purge",
      "after_delete": "Download and wheel cache, refilled on next install."
    }
  ]
}
```

## What it stores

- Downloaded packages and built wheels. AI work makes it large because of PyTorch, CUDA and MLX wheels.

## Safe to delete

- All of it. Installed packages in environments are not affected.

## How to clean

1. `pip cache purge`, or
2. Remove the folder.
