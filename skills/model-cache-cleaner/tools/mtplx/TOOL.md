# MTPLX

```json
{
  "tool": "MTPLX",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/.mtplx/models"],
      "model_depth": 1,
      "after_delete": "Model is re-downloaded if you load it again."
    },
    {
      "kind": "app-data",
      "macos": ["~/.mtplx/session-bank"],
      "after_delete": "Probably saved session or prompt caches (inferred from the name and blob layout, not confirmed). Ask the user."
    }
  ]
}
```

## What it stores

- **`models/<model>`:** downloaded MLX models optimised for multi-token prediction.
- **`session-bank/blobs`, `session-bank/entries`:** stored session data. The name and layout suggest saved prompt or KV caches, but this hasn't been confirmed.
- **`bin/`:** the `mtplx` and `thermalforge` binaries.
- **`tuning.json`, `max-active.json`, `metrics/`, `logs/`.**

## Safe to delete

- Individual model folders the user no longer uses.

## Ask first

- `session-bank/`. It may hold saved sessions the user wants. If the user doesn't use saved sessions, it's likely safe.

## Never delete

- `bin/` and `tuning.json`, unless removing MTPLX entirely.

## How to clean

1. Stop any running MTPLX process.
2. Remove unused model folders from `~/.mtplx/models`.
3. If the user agrees, remove `~/.mtplx/session-bank`.
4. To remove MTPLX entirely, delete `~/.mtplx`.
