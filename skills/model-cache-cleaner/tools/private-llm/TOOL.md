# Private LLM

```json
{
  "tool": "Private LLM",
  "homepage": "https://privatellm.app",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/Library/Containers/ie.numen.personalgpt/Data/Library/Application Support/ie.numen.personalgpt/models"],
      "model_depth": 1,
      "cleanup": "Private LLM app → Settings → delete downloaded models",
      "after_delete": "Model is re-downloaded from inside the app."
    }
  ]
}
```

## What it stores

- **`models/`:** models downloaded inside the Mac app. The app's bundle ID is `ie.numen.personalgpt`, so it lives in a sandbox container that Finder doesn't show.

## Safe to delete

- Models the user no longer uses. Prefer deleting them in the app.

## How to clean

1. Open Private LLM, go to **Settings**, then delete models there.
2. If the app has been uninstalled, remove `~/Library/Containers/ie.numen.personalgpt`.
