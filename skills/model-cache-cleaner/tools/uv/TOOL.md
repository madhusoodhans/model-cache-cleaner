# uv

```json
{
  "tool": "uv",
  "homepage": "https://docs.astral.sh/uv/concepts/cache/",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "cache",
      "macos": ["~/.cache/uv"],
      "linux": ["~/.cache/uv"],
      "env": ["UV_CACHE_DIR"],
      "cleanup": "uv cache clean (or uv cache prune to keep what's in use)",
      "after_delete": "Package cache, refilled on next install."
    },
    {
      "kind": "app-data",
      "macos": ["~/.local/share/uv"],
      "linux": ["~/.local/share/uv"],
      "cleanup": "uv python list / uv python uninstall <version>; uv tool list / uv tool uninstall <tool>",
      "after_delete": "Python versions and CLI tools installed with uv. Anything using them stops working until reinstalled."
    }
  ]
}
```

## What it stores

- **`~/.cache/uv`:** package cache shared by all uv projects. Creating many ML environments makes it large (6.6 GB seen).
- **`~/.local/share/uv/python`:** Python versions installed with `uv python install`.
- **`~/.local/share/uv/tools`:** command-line tools installed with `uv tool install`.

## Safe to delete

- `~/.cache/uv`. Run `uv cache prune` to remove only unused entries, or `uv cache clean` to remove everything.

## Ask first

- `~/.local/share/uv`. Use `uv python uninstall` and `uv tool uninstall` for specific items.

## How to clean

1. `uv cache clean`.
2. `uv python list --only-installed`, then uninstall versions the user doesn't need.
