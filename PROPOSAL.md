# Proposal: model-cache-cleaner

A generic Claude skill that scans every local AI tool's caches, models and app data, shows the user the raw results and a numbered list of suggested deletions, and deletes only what the user picks.

## 1. Problem

People who experiment with local models (LM Studio, Ollama, MLX, Hugging Face, Unsloth, ComfyUI and others) pile up hundreds of gigabytes without noticing. They notice only when macOS reports "disk full".

Three things make this hard to see:

1. **The data is hidden.** Most of it sits in dot-folders (`~/.cache`, `~/.ollama`, `~/.omlx`) or in `~/Library/Application Support`. Finder doesn't show these, and macOS Storage settings lumps them into "System Data".
2. **Every tool keeps its own copy.** The same model is often downloaded separately into LM Studio, the Hugging Face hub and an MLX server, because each tool uses its own folder.
3. **Caches and models look alike.** A 40 GB `cache` folder can be deleted with no cost, but a 40 GB `models` folder costs hours of re-downloading. Generic disk tools show sizes and nothing more, so people either delete nothing or delete the wrong thing.

## 2. Evidence: one real session (24 Oct 2026)

On a 460 GB MacBook with 3.7 GB free, the home folder held 337 GB:

| Folder | Size | What it was |
|---|---|---|
| `~/.omlx` | 89 GB | oMLX: 47 GB of models plus a 41 GB cache |
| `~/.cache` | 79 GB | LM Studio models (42 GB), Hugging Face hub (25 GB), uv (6.6 GB) |
| `~/Library/Application Support` | 50 GB | Claude, AI Edge Gallery (12 GB), others |
| `~/.mlx-serve` | 18 GB | MLX server models |
| `~/.mtplx`, `~/.hermes`, `~/.unsloth` | 20 GB | Other model and experiment folders |

About 250 GB of the 337 GB was local AI data, and almost none of it was visible in Finder.

After a guided cleanup (clear three caches, delete three unused tool folders) free space rose from **3.7 GB to 112 GB in about ten minutes**, with no loss of anything the user still needed. Doing it took knowing what each folder was, and that knowledge is what this project packages.

## 3. Who it's for

- Developers and researchers who try many local models and tools.
- Mac users on 256 GB to 1 TB laptops, where model weights fill space fastest. Linux workstations are the second target.
- People who already use Claude Code or another agent that supports skills.

## 4. Proposed solution

An open-source **Claude skill** published on GitHub. The user says "my disk is full" or "where did my space go?". The skill then runs a fixed workflow:

1. **Scan.** Measure every known AI tool location, plus the largest folders in the home directory.
2. **Show the raw results.** Largest folders, each AI tool found with its locations and sizes, and duplicate files. Nothing is hidden or pre-filtered.
3. **Suggest.** A numbered list of deletions, grouped by risk:
   - `safe`: caches, rebuilt automatically.
   - `duplicate`: a second copy of the same file.
   - `re-download`: individual models, listed one by one, that cost a download to get back.
   - `inspect`: app data; look before deleting.
4. **The user picks.** They reply with numbers ("1, 2, 4-7", "all safe"). The tool never decides for them.
5. **Delete.** Remove only the picked items. Follow that tool's own instructions, and prefer its cleanup command (`ollama rm`, `uv cache clean`, `hf cache delete`) over `rm -rf`.
6. **Report.** Show what was removed, free space before and after, and what will be re-downloaded on next use.

### Generic and extensible by design

Each tool is a folder, `tools/<tool-id>/TOOL.md`. It holds a small JSON block the scanner reads (paths, kinds, cleanup command), followed by plain-language guidance Claude reads before deleting (what it stores, safe to delete, ask first, never delete, how to clean).

Adding a tool means copying `tools/_template/` and filling it in. The scanner needs no code change. Users can add their own tools locally, or ask Claude to do it, and can contribute them back.

### Why a skill and not just a script

The hard part is judgment, not measuring. Whether `~/.unsloth` is safe to delete depends on whether the user still fine-tunes. Whether two 15 GB folders are duplicates depends on file names, quantizations and formats. A skill lets Claude ask, interpret and adapt, while the bundled script does the fast, deterministic measuring.

A standalone CLI built on the same locations map is a possible later step (see section 9).

## 5. Design

```
model-cache-cleaner/
├── PROPOSAL.md
├── README.md
└── skills/model-cache-cleaner/
    ├── SKILL.md                  # workflow and safety rules Claude follows
    ├── scripts/scan.py           # read-only scanner
    └── tools/
        ├── _template/TOOL.md     # copy this to add a tool
        ├── lm-studio/TOOL.md
        ├── omlx/TOOL.md
        ├── huggingface/TOOL.md
        └── ...                   # one folder per tool
```

### Tool folders

The tool folders are the main asset and the place where contributions matter most. Each `TOOL.md` has two parts.

**A JSON block the scanner reads:**
- `tool`: the display name.
- `verified`: the date the paths were last confirmed on a real machine, or `null`.
- `locations[]`: one entry per folder, with:
  - paths per OS (`macos`, `linux`, `windows`), with `~` expansion;
  - `env`: environment variables that override the path (for example `HF_HUB_CACHE`, `OLLAMA_MODELS`);
  - `kind`: `cache`, `models` or `app-data`;
  - `model_depth`: lists each model as its own suggestion;
  - `cleanup`: the tool's own cleanup command;
  - `after_delete`: what is lost or re-downloaded.

**Guidance Claude reads before deleting:** what each folder stores, what is safe, what to ask about, what never to delete (chat history, login tokens) and the preferred cleanup steps.

The first version has 14 tools, all found on the author's Mac: LM Studio, oMLX, MTPLX, Hugging Face, Ollama, Jan, Private LLM, mlx-serve, Google AI Edge Gallery, Claude desktop, Unsloth, PyTorch Hub, pip and uv.

### The scan script

`scan.py` uses only the Python standard library, so there is nothing to install. It:

- Loads every `tools/*/TOOL.md`. Adding a tool needs no code change.
- Measures real disk usage (allocated blocks) and doesn't follow symlinks. This matters because the Hugging Face hub uses symlinks, and following them would count the same data twice.
- Lists models one by one where `model_depth` is set, so users can keep some and drop others.
- Lists large unknown folders in the raw results, so new tools still show up. They are not offered for deletion.
- Finds duplicate large files across tools: same size, plus the same hash of the first and last MB. A duplicate inside an app bundle is shown as a note, never as a single file to delete.
- Prints raw results and numbered suggestions as a table, or as JSON for Claude to read.

The script only reads. It never deletes. Deletion happens only in the skill's confirm step, one path at a time, through a command the user has approved.

## 6. Safety rules

These are hard rules in `SKILL.md`:

1. Delete only what the user picked, and confirm again before anything in `inspect` or anything over about 20 GB.
2. Never suggest deleting `user` folders (Documents, Pictures, Movies, Desktop). Suggest moving them to other storage instead.
3. Always show a folder's size and contents before proposing to delete it.
4. Prefer the tool's own cleanup command over `rm -rf`.
5. Warn before deleting the only copy of a model, and say how large the re-download would be.
6. Never use `sudo`, and never touch system folders.
7. Read the tool's `TOOL.md` before deleting from it, and respect its "Never delete" list.
8. Never delete a single file from inside an app bundle or model folder.

## 7. Scope

**Version 1:**
- macOS and Linux.
- 14 tool folders, then the popular tools in the README's "Wanted" list (GPT4All, Msty, Open WebUI, ComfyUI, Automatic1111, InvokeAI, Draw Things, Whisper and others).
- Duplicate detection by size and a partial hash.
- Use as a Claude Code skill.

**Not in version 1:**
- Windows (planned for version 2).
- Content hashing for duplicates, which is slow on hundreds of gigabytes.
- Moving models to external drives, or deduplicating them with symlinks.
- A graphical interface.

## 8. Competition and differentiation

**This needs checking before launch.** We haven't yet searched GitHub, the Claude skills directories or Homebrew for something similar.

Known neighbours:

- General disk tools: DaisyDisk, GrandPerspective, OmniDiskSweeper, `ncdu`, `dust`. They show sizes but don't know which AI folders are caches.
- Built-in tool commands: `hf cache scan`, `ollama list`, `uv cache dir`. Each covers one tool only.
- Cleaner apps: CleanMyMac and similar. These are closed, generic and not aware of models.

The difference: model-cache-cleaner spans every tool at once, knows which folders are caches and which are models, lists models one by one, finds duplicates across tools, and lets the user pick before anything is deleted.

## 9. Milestones

| Stage | Contents |
|---|---|
| **M1: working skill** | `SKILL.md`, `scan.py`, 14 tool folders, tested on the author's Mac. **Done.** |
| **M2: public release** | Tool folders for the "Wanted" list, README with before and after numbers, demo GIF, licence |
| **M3: community** | Tool folders from others, Linux paths verified, Windows paths added |
| **M4: optional CLI** | `pipx install model-cache-cleaner`, reading the same tool folders, for people without Claude |

## 10. Success measures

- Users free at least 20 GB in their first run.
- No reports of user data lost through the skill.
- Tool folders added by people other than the author.
- GitHub stars and forks, as a rough measure of reach.

## 11. Open questions

1. **Name.** "model-cache-cleaner" is chosen. It should be checked for clashes on GitHub and PyPI.
2. **Unconfirmed folders.** What MTPLX keeps in `session-bank/` is inferred, not confirmed, so it's marked "ask first". Other entries will have the same problem. Should contributions require a link to the tool's docs?
3. **Licence.** MIT is proposed.
4. **Distribution.** A plain GitHub repo, a Claude Code plugin marketplace entry, or both.
