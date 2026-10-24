# Tool name

Copy this folder to `tools/<tool-id>/` (lowercase, hyphens), fill it in, and the scanner picks it up automatically. Folders starting with `_` are ignored.

The scanner reads only the first `json` block below. Everything else is guidance Claude reads when the user picks something from this tool.

```json
{
  "tool": "Tool Name",
  "homepage": "https://example.com",
  "verified": "YYYY-MM-DD",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/.toolname/models"],
      "linux": ["~/.toolname/models"],
      "env": ["TOOLNAME_MODELS"],
      "model_depth": 1,
      "cleanup": "toolname rm <model>",
      "after_delete": "Model is re-downloaded the next time you load it."
    },
    {
      "kind": "cache",
      "macos": ["~/Library/Caches/toolname"],
      "linux": ["~/.cache/toolname"],
      "after_delete": "Rebuilt automatically."
    }
  ]
}
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `tool` | yes | Display name |
| `homepage` | no | Project website |
| `verified` | yes | Date the paths were last checked on a real machine, or `null` if taken from docs |
| `locations[].kind` | yes | `cache`: safe to clear, rebuilt automatically. `models`: re-downloadable but large. `app-data`: settings, history, runtimes; look before deleting |
| `locations[].macos` / `linux` / `windows` | yes, at least one | Paths for each OS. `~` and `$VARS` are expanded |
| `locations[].env` | no | Environment variables that override the path |
| `locations[].model_depth` | no | Lists each model as its own suggestion. `1` for `models/<model>`, `2` for `models/<publisher>/<model>` |
| `locations[].cleanup` | no | The tool's own cleanup command or menu path; preferred over `rm -rf` |
| `locations[].after_delete` | no | What the user loses or must re-download |

## What it stores

Describe each folder in plain words.

## Safe to delete

## Ask first

## Never delete

## How to clean

The tool's own commands or menus, in order of preference.
