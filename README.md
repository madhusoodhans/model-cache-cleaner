# model-cache-cleaner

A Claude skill that finds the storage local AI tools use on your machine, shows you everything it found, and deletes only what you pick.

If you try local models, your disk fills up in places you never see: `~/.cache/lm-studio`, `~/.cache/huggingface`, `~/.ollama`, `~/.omlx`, `~/Library/Containers/...`. Finder hides them, and macOS calls them "System Data". The same model often gets downloaded by three different tools.

## How it works

1. **Scan.** A read-only script measures every known AI tool location, plus the largest folders in your home directory.
2. **Show the raw results.** Largest folders, AI tools found with their sizes, and duplicate files.
3. **Suggest.** A numbered list of deletions, grouped by risk:
   - **safe:** caches, rebuilt automatically.
   - **duplicate:** a second copy of the same file.
   - **re-download:** individual models you can get back by downloading again.
   - **inspect:** app data. Look before deleting.
4. **You pick.** Reply with numbers, for example "1, 2, 4-7".
5. **Delete and report.** Only what you picked, using each tool's own cleanup method where it has one. Then free space before and after.

## Example

On a 460 GB MacBook with 3.7 GB free, a guided cleanup took free space to 112 GB. The biggest wins were a 41 GB oMLX cache, a 25 GB Hugging Face cache, and folders from tools no longer used.

Run afterwards, the scanner found 19 more suggestions, including:

- Models listed one by one across LM Studio, oMLX, MTPLX and Private LLM, from 17 GB down.
- The same 10 GB virtual machine image stored by two installs of the Claude desktop app.

## Install

```bash
cp -r skills/model-cache-cleaner ~/.claude/skills/
```

Then ask Claude "my disk is full, where did my space go?" or "clean up my local AI models".

## Run the scanner on its own

It needs Python 3 and nothing else. It never deletes anything.

```bash
python3 -I skills/model-cache-cleaner/scripts/scan.py             # table
python3 -I skills/model-cache-cleaner/scripts/scan.py --json      # JSON
python3 -I skills/model-cache-cleaner/scripts/scan.py --no-dupes  # faster
```

## Tools covered

Each tool has its own folder in [`skills/model-cache-cleaner/tools/`](skills/model-cache-cleaner/tools/). Its `TOOL.md` lists its paths and explains what is safe to delete.

| Tool | Folder | What it covers |
|---|---|---|
| LM Studio | `lm-studio` | Models (per model), runtimes |
| oMLX | `omlx` | Cache, models (per model) |
| MTPLX | `mtplx` | Models (per model), session bank |
| Hugging Face | `huggingface` | Hub models (per model), Xet cache, datasets |
| Ollama | `ollama` | Models, via `ollama rm` |
| Jan | `jan` | Data folder |
| Private LLM | `private-llm` | Models (per model) |
| mlx-serve | `mlx-serve` | Server data and models |
| Google AI Edge Gallery | `ai-edge-gallery` | On-device models |
| Claude desktop | `claude-desktop` | VM images, web cache |
| Unsloth | `unsloth` | Studio install, llama.cpp builds |
| PyTorch Hub | `pytorch` | Checkpoints, compiled kernels |
| pip | `pip` | Wheel cache |
| uv | `uv` | Package cache, installed Pythons and tools |

All of these were found and checked on a real Mac on 2026-10-24. Linux paths come from each tool's documentation and haven't been checked yet.

### Wanted

These popular tools don't have a folder yet. Contributions welcome:

- **Chat and inference apps:** GPT4All, Msty, AnythingLLM, Open WebUI, LocalAI, KoboldCpp, text-generation-webui, vLLM, llama.cpp (`-hf` downloads), mlx-lm, Exo.
- **Image and video:** ComfyUI, Automatic1111 and Forge, InvokeAI, DiffusionBee, Draw Things, Fooocus.
- **Audio:** Whisper, whisper.cpp, MacWhisper.
- **Model hubs and environments:** ModelScope, Kaggle, conda, Docker.

## Adding a tool

1. Copy [`tools/_template`](skills/model-cache-cleaner/tools/_template/TOOL.md) to `tools/<tool-id>/`.
2. Fill in the `json` block: paths for each OS, `kind` (`cache`, `models` or `app-data`), and the cleanup command.
3. Write the guidance sections: what it stores, safe to delete, ask first, never delete, how to clean.
4. Run the scanner to check it's picked up, then open a pull request.

Or ask Claude: "add <tool> to model-cache-cleaner". The skill knows how to fill in the template.

## Safety

- The scanner only reads.
- Nothing is deleted until you pick it by number, and anything risky or large gets a final confirmation.
- User folders (Documents, Desktop, Downloads, Pictures, Movies, Music) are never suggested.
- Each tool's "Never delete" list is respected, for example chat history and login tokens.
- It never uses `sudo`.

See [PROPOSAL.md](PROPOSAL.md) for background and roadmap.

## Licence

To be decided. MIT is proposed.
