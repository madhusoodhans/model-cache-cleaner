# oMLX

```json
{
  "tool": "oMLX",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "cache",
      "macos": ["~/.omlx/cache"],
      "after_delete": "Runtime cache, rebuilt on next use. Was 41 GB on the machine this was first verified on."
    },
    {
      "kind": "models",
      "macos": ["~/.omlx/models"],
      "model_depth": 2,
      "after_delete": "Model is re-downloaded if you load it again."
    }
  ]
}
```

## What it stores

- **`cache/`:** runtime cache. It can grow very large (41 GB seen).
- **`models/<publisher>/<model>`:** downloaded MLX models (for example `mlx-community/...`, `unsloth/...`).
- **`settings.json`, `model_settings.json`, `model_profiles.json`, `global_templates.json`, `stats.json`:** settings and usage stats. Small.
- **`bin/`, `logs/`.**

## Safe to delete

- `cache/`, entirely. Quit oMLX first.
- Individual model folders the user no longer uses.

## Never delete

- The settings JSON files, unless the user wants to reset oMLX.

## How to clean

1. Quit oMLX.
2. Remove `~/.omlx/cache`.
3. Remove unused models from `~/.omlx/models/<publisher>/<model>`.
