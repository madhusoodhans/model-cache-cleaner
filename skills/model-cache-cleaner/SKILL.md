---
name: model-cache-cleaner
description: Scan the machine for storage used by local AI tools (LM Studio, Ollama, Hugging Face, MLX tools, Jan, Unsloth, PyTorch, pip, uv and others), show the raw results and a numbered list of suggested deletions, let the user pick and review what to remove, then move only that to the Trash. Use when the user says their disk or laptop is full, asks where their storage went, wants to clean up models or caches, or wants to add a new AI tool to the cleaner.
---

# model-cache-cleaner

Show the user where local AI tools are using their disk, suggest what could go, and delete only what they pick.

## Layout

```
model-cache-cleaner/
├── SKILL.md            # this file
├── scripts/scan.py     # read-only scanner
├── scripts/trash.py    # moves approved paths to the Trash, with guard rails
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

**Never call two models the same, or suggest that one makes another redundant, because their names match.** A different quantization (4-bit and 8-bit, Q4_K_M and Q8_0, GPTQ, QAT), format (GGUF and MLX), variant (MTP, speed-optimised, instruct and base) or fine-tune is a different model, with different quality, speed and memory use. Only the scanner's `duplicates`, which are byte-identical files, count as duplicates. If you mention that two models share a base model, say how they differ, and leave the choice to the user. Don't recommend keeping one.

End with the total that could be freed by each group, then ask:

> Which numbers should I delete? (for example "1, 2, 4-7", "all safe", or "none")

Stop and wait. Do not delete anything in this step.

### 4. Review: always, before anything moves

For the picked numbers:

1. Read each tool's `TOOL.md` (the path is in the tool's `doc` field). Follow its "Never delete" and "How to clean" sections. If it says to quit the app first or to use the tool's own command (for example `ollama rm` or `hf cache delete`), plan for that.
2. Run a dry run with the exact paths:
   ```bash
   python3 -I <skill-dir>/scripts/trash.py --dry-run "<path1>" "<path2>"
   ```
3. Show the user a review table: each path, its size, the tool, the method (Trash or the tool's own command), and what happens after (rebuilt, re-downloaded, lost). Show the total.
4. Ask: "Move these to the Trash? (yes / change the list)". **Stop and wait.** Continue only on an explicit yes to this exact list. If the user changes the list, run the dry run and show the review again.

This review step is never skipped, whatever the size or risk, and even if the user said "delete all" earlier.

### 5. Move to Trash

After the user says yes:

- For items whose `TOOL.md` names a cleanup command, run that command. These commands delete directly, so say so in the review.
- Move everything else to the Trash with the bundled script:
  ```bash
  python3 -I <skill-dir>/scripts/trash.py "<path1>" "<path2>"
  ```
  It uses macOS's built-in `trash` command (Finder's Put Back works), or the freedesktop Trash on Linux. It refuses the home folder, user folders, paths outside home and symlinks.

Never use `rm -rf` on picked items. Never use wildcards, `sudo`, or system folders. If the script refuses a path, tell the user why. Don't work around the refusal.

### 6. Report

Show:
- A table of what was moved to the Trash or removed by a tool command, with sizes.
- That the space is freed only after the Trash is emptied (on macOS, Finder → Empty Trash). Items can be restored with Put Back until then. Don't empty the Trash yourself unless the user explicitly asks.
- Free space before and after (`df -h /`). Note that space from items in the Trash won't show until it's emptied.
- What will be re-downloaded on next use.
- The largest remaining suggestions, in case the user wants to go further.

## Safety rules

1. Move only numbers or paths the user picked in this conversation, and only after they've said yes to the review in step 4.
2. Move to the Trash with `scripts/trash.py`. Never `rm -rf`.
3. Never delete or suggest deleting user folders: Documents, Desktop, Downloads, Pictures, Movies, Music.
4. Never delete a single file from inside an app's bundle or model folder. Delete the whole model or bundle, or use the tool's own command.
5. If a pick is ambiguous ("delete the cache"), and more than one path could match, ask which.
6. Models with similar names are different models unless the scanner found them byte-identical. Never suggest that one replaces another.
7. Follow each tool's "Never delete" list even when the user picked its parent folder. Remove the allowed contents and say what was kept.

## Adding a tool

When the user wants to add a tool, or you identify a large unknown AI folder:

1. Copy `tools/_template/` to `tools/<tool-id>/` (lowercase, hyphens).
2. Fill in the `json` block: paths for each OS, `kind` for each location, `model_depth` if models are in per-model folders, the cleanup command and `after_delete`.
3. Fill in "What it stores", "Safe to delete", "Ask first", "Never delete" and "How to clean" from what you saw on disk and the tool's docs. Mark anything you inferred rather than confirmed.
4. Set `verified` to today's date if you checked the paths on this machine. Otherwise use `null`.
5. Run the scanner again to confirm the tool is picked up.
