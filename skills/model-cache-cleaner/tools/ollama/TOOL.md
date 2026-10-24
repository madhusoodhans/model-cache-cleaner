# Ollama

```json
{
  "tool": "Ollama",
  "homepage": "https://ollama.com",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/.ollama/models"],
      "linux": ["~/.ollama/models", "/usr/share/ollama/.ollama/models"],
      "env": ["OLLAMA_MODELS"],
      "cleanup": "ollama list, then ollama rm <model>",
      "after_delete": "Model is re-pulled with ollama pull."
    }
  ]
}
```

## What it stores

- **`models/blobs/`:** model layers, named by hash. Several models can share layers.
- **`models/manifests/`:** which blobs make up each model.

On the machine this was verified on, `~/.ollama` held only `manifests/` and `backup/` (12 KB), so no models were downloaded.

## Safe to delete

- Models removed with `ollama rm`.

## Never delete

- Files inside `blobs/` or `manifests/` by hand. This breaks Ollama's index, and shared layers may belong to models the user keeps.

## How to clean

1. `ollama list` shows each model and its size.
2. `ollama rm <model>` removes one model and any layers no other model uses.
3. To remove Ollama entirely, uninstall the app, then delete `~/.ollama`.
