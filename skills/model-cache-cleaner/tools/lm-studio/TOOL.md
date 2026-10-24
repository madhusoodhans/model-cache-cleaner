# LM Studio

```json
{
  "tool": "LM Studio",
  "homepage": "https://lmstudio.ai",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/.cache/lm-studio/models", "~/.lmstudio/models"],
      "linux": ["~/.cache/lm-studio/models", "~/.lmstudio/models"],
      "model_depth": 2,
      "cleanup": "LM Studio app → My Models → delete, or the lms CLI",
      "after_delete": "Model is re-downloaded from Hugging Face if you load it again."
    },
    {
      "kind": "app-data",
      "macos": ["~/.cache/lm-studio/extensions", "~/.lmstudio/extensions"],
      "linux": ["~/.cache/lm-studio/extensions", "~/.lmstudio/extensions"],
      "cleanup": "LM Studio app → Runtime settings → remove old runtime versions",
      "after_delete": "Inference runtimes (llama.cpp, MLX). Old versions can go; the active one is needed to run models."
    }
  ]
}
```

## What it stores

- **`models/<publisher>/<model>`:** downloaded GGUF and MLX models. This is almost always the bulk of the space.
- **`extensions/`:** inference runtimes (llama.cpp, MLX engines). Each update adds a version, and old ones pile up.
- **`conversations/`, `chats/`, `config-presets/`, `mcp.json`, `credentials/`:** the user's chats, settings and keys. Small.

LM Studio's home folder can be moved. The file `~/.lmstudio-home-pointer` contains the real path, so read it if neither default path exists.

## Safe to delete

- Individual model folders the user no longer uses.
- `server-logs/`.

## Ask first

- Old runtime versions inside `extensions/`. Prefer removing them from the app.

## Never delete

- `conversations/`, `chats/`, `config-presets/`, `credentials/`, `mcp.json`, `settings.json`.
- The whole LM Studio folder.

## How to clean

1. In the app: **My Models**, then delete each model. This keeps LM Studio's index in sync.
2. Or delete the model folder directly. LM Studio rescans on launch.
3. Check whether the same model is also in the Hugging Face hub, oMLX or another tool. The scanner's duplicate check finds identical files.
