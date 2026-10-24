# Jan

```json
{
  "tool": "Jan",
  "homepage": "https://jan.ai",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "app-data",
      "macos": ["~/Library/Application Support/Jan/data"],
      "linux": ["~/.config/Jan/data", "~/.local/share/Jan/data"],
      "cleanup": "Jan app → Settings → Model Providers → delete models",
      "after_delete": "Models, chat threads and settings. Models can be re-downloaded; threads cannot."
    }
  ]
}
```

## What it stores

- **`data/`:** Jan's data folder, holding downloaded models, chat threads, assistants and settings. The location can be changed in **Settings → Advanced → Data folder**.

On the machine this was verified on, it was 61 MB, so no large models were downloaded.

## Safe to delete

- Models, deleted from inside the app.

## Never delete

- `threads/`: the user's chat history.

## How to clean

1. In Jan, delete models from the model settings.
2. If Jan is uninstalled, remove its data folder.
