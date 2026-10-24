---
name: model-cache-cleaner
description: Scan the machine for storage used by local AI tools (LM Studio, Ollama, Hugging Face, MLX tools, Jan, Unsloth, PyTorch, pip, uv and others), show the raw results and a numbered list of suggested deletions, let the user pick what to remove, then remove only that. Use when the user says their disk or laptop is full, asks where their storage went, wants to clean up models or caches, or wants to add a new AI tool to the cleaner.
---

# model-cache-cleaner

Show the user where local AI tools are using their disk, suggest what could go, and delete only what they pick.

## Layout

```
model-cache-cleaner/
├── SKILL.md            # this file
├── scripts/scan.py     # read-only scanner
└── tools/
    ├── _template/TOOL.md
    └── <tool-id>/TOOL.md   # one per tool: paths, kinds, and how to clean it
```

Each `tools/<tool-id>/TOOL.md` starts with a `json` block the scanner reads (paths per OS, `kind`, cleanup command). The rest is tool-specific guidance: what each folder holds, what is safe, what to ask about, and what never to delete. **Read a tool's `TOOL.md` before deleting anything from it.**

## Workflow

### 1. Scan

```bash
python3 -I <skill-dir>/scripts/scan.py --json
df -h /
```

The scan only reads. It takes from 30 seconds to a few minutes.

The JSON has:
- `top`: the largest folders in home, `~/.cache` and `~/Library/Application Support`. Each has a `label`:
  - `user`: personal files.
  - `known-tool`: belongs to a tool in `tools/`.
  - `unknown`: not covered.
- `tools`: each tool found, with its locations, sizes and, for model folders, each model as an `item`.
- `duplicates`: identical large files stored in more than one place.
- `suggestions`: a numbered list (`n`), grouped by `risk`:
  - `safe`: caches, rebuilt automatically.
  - `duplicate`: a second copy of a file.
  - `re-download`: models that cost a download to get back.
  - `inspect`: app data; look before deleting.

  Each suggestion has `path`, `bytes`, `tool`, `why` and optional `cleanup` and `duplicates` notes.

If Python isn't available, fall back to `du -xhd 1 ~ | sort -rh | head -20` and match folders against the paths in `tools/*/TOOL.md` by hand.

### 2. Show the raw results

Present these to the user before any suggestion:

1. Free space and total used.
2. **Largest folders:** a table with rank, folder, size and label.
3. **AI tools found:** a table with tool, total size and each location with its kind.
4. **Duplicates**, if any.

Then look at the `unknown` folders. If one looks AI-related (model files such as `.gguf`, `.safetensors` or `.mlx`, or names like models, weights, checkpoints, llm or diffusion), look inside it. Run `ls`, read any README or config, and run `du -hd 2`. Tell the user what you found. If it's still unclear, say so rather than guess. Offer to add it as a new tool (see "Adding a tool").

Don't offer unknown folders for deletion unless the user asks about one.

### 3. Show the suggestions

Show the numbered `suggestions` grouped by risk, in the scanner's order. Include number, size, path, tool and what happens after deletion. Show `duplicates` notes under their suggestion.

End with the total that could be freed by each group, then ask:

> Which numbers should I delete? (for example "1, 2, 4-7", "all safe", or "none")

Stop and wait. Do not delete anything in this step.

### 4. Delete what the user picked

For each picked number:

1. Read the tool's `TOOL.md` (the path is in the tool's `doc` field). Follow its "Never delete" and "How to clean" sections.
2. If the tool's "How to clean" says to quit the app first, or to use its own command (for example `ollama rm` or `hf cache delete`), do that instead of `rm -rf`.
3. Before deleting, repeat back the exact list of paths, with sizes and the total. If the pick includes anything from `inspect`, or more than about 20 GB, wait for a final yes.
4. Delete exact paths only, showing each size in the same command:
   ```bash
   du -sh "<path>" && rm -rf "<path>"
   ```
   Never use wildcards, never use `sudo`, and never touch system folders.

### 5. Report

Run `df -h /` again. Show:
- A table of what was deleted, with sizes.
- Free space before and after.
- What will be re-downloaded on next use.
- The largest remaining suggestions, in case the user wants to go further.

## Safety rules

1. Delete only numbers or paths the user picked in this conversation.
2. Never delete or suggest deleting user folders: Documents, Desktop, Downloads, Pictures, Movies, Music.
3. Never delete a single file from inside an app's bundle or model folder. Delete the whole model or bundle, or use the tool's own command.
4. If a pick is ambiguous ("delete the cache"), and more than one path could match, ask which.
5. Follow each tool's "Never delete" list even when the user picked its parent folder. Remove the allowed contents and say what was kept.

## Adding a tool

When the user wants to add a tool, or you identify a large unknown AI folder:

1. Copy `tools/_template/` to `tools/<tool-id>/` (lowercase, hyphens).
2. Fill in the `json` block: paths for each OS, `kind` for each location, `model_depth` if models are in per-model folders, the cleanup command and `after_delete`.
3. Fill in "What it stores", "Safe to delete", "Ask first", "Never delete" and "How to clean" from what you saw on disk and the tool's docs. Mark anything you inferred rather than confirmed.
4. Set `verified` to today's date if you checked the paths on this machine. Otherwise use `null`.
5. Run the scanner again to confirm the tool is picked up.
