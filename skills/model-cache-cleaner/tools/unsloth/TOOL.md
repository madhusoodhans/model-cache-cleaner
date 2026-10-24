# Unsloth

```json
{
  "tool": "Unsloth",
  "homepage": "https://unsloth.ai",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "app-data",
      "macos": ["~/.unsloth/studio"],
      "linux": ["~/.unsloth/studio"],
      "after_delete": "Unsloth Studio's Python environment and libraries. Reinstalled if Studio is set up again."
    },
    {
      "kind": "app-data",
      "macos": ["~/.unsloth/llama.cpp", "~/.unsloth/whisper.cpp"],
      "linux": ["~/.unsloth/llama.cpp", "~/.unsloth/whisper.cpp"],
      "after_delete": "llama.cpp and whisper.cpp builds Unsloth uses for exporting models. Rebuilt on next export."
    }
  ]
}
```

## What it stores

- **`studio/`:** Unsloth Studio's install: Python libraries (`unsloth_studio/lib`) and several virtual environments (`.venv_*`).
- **`llama.cpp/`, `whisper.cpp/`:** tool builds used to export or convert models to GGUF.

Fine-tuned models and checkpoints are usually saved in the user's project folder, not here. Check with the user.

## Safe to delete

- The whole `~/.unsloth` folder, if the user no longer uses Unsloth.

## Ask first

- `studio/`: needed to run Unsloth Studio.
- Old `.venv_*` folders inside `studio/` may be leftovers from earlier versions.

## How to clean

1. Ask whether the user still uses Unsloth or Unsloth Studio.
2. If not, remove `~/.unsloth`.
3. Also look for fine-tuning output (`outputs/`, `checkpoint-*`, `lora_model/`) in the user's project folders. It's often larger than the tool itself.
