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
5. **Review.** Show the exact paths, sizes and consequences from a dry run. Nothing moves until the user says yes to that exact list. This step is never skipped.
6. **Move to Trash.** Move only the approved items to the Trash, so they're recoverable until it's emptied. Where a tool has its own cleanup command (`ollama rm`, `hf cache delete`), use that instead. `rm -rf` is never used.
7. **Report.** Show what was moved, that space is freed when the Trash is emptied, and what will be re-downloaded on next use.

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

1. Move only what the user picked, after they approve a dry-run review of the exact paths. Every time.
2. Move to the Trash (`scripts/trash.py`), never `rm -rf`. The script refuses the home folder, user folders, paths outside home and symlinks.
3. Never suggest deleting `user` folders (Documents, Desktop, Downloads, Pictures, Movies, Music). Suggest moving them to other storage instead.
4. Always show a folder's size and contents before proposing to delete it.
5. Prefer the tool's own cleanup command where it has one, and say in the review that it deletes directly.
6. Warn before deleting the only copy of a model, and say how large the re-download would be.
7. Never use `sudo`, and never touch system folders.
8. Read the tool's `TOOL.md` before deleting from it, and respect its "Never delete" list.
9. Never delete a single file from inside an app bundle or model folder.

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

Checked on 2026-10-24. The space is new and crowded, but nobody leads it yet. Every AI-specific project found had 0 or 1 GitHub stars, and most were created in the previous few weeks.

**AI storage cleaners:**

| Project | Type | Closest overlap |
|---|---|---|
| [LLMDoctor](https://github.com/Arthur031221/llm-doctor) | Python CLI | Dedupes weights across Ollama, LM Studio, Hugging Face and MLX; finds orphan Ollama blobs and old Hugging Face revisions |
| [macreaper](https://github.com/roopen219/macreaper) | Bun CLI, macOS | 21+ developer cache categories, tool-native cleanup, moves to Trash |
| [ai-disk-cleaner](https://github.com/nethero23/ai-disk-cleaner) | Tauri app, Windows | Ollama, Hugging Face, LM Studio, pip, conda, Docker; pick and undo |
| [cleanator](https://github.com/blackberrylabs/cleanator) | Rust CLI, Linux | Never deletes; writes a cleanup script to review |
| [llm-mem-cleaner](https://github.com/jasonhuzhensheng/llm-mem-cleaner) | macOS menu bar app | Mainly memory and GPU; has a disk tab |

**Claude skills:**
- [upkeep](https://github.com/KyleNesium/upkeep) is a general Mac disk audit and package updater.
- [disk-cleanup-skill](https://github.com/HappyLy-61/disk-cleanup-skill) is Chinese-language, with a data/ML role and a staging folder.

**Wider neighbours:**
- General disk tools (DaisyDisk, GrandPerspective, `ncdu`, `dust`) show sizes but don't know which AI folders are caches.
- Built-in commands (`hf cache scan`, `ollama list`, `uv cache dir`) each cover one tool.
- Cleaner apps (CleanMyMac and similar) are closed and not aware of models.

**Where model-cache-cleaner differs:**
1. **It's Claude-native.** It can investigate folders it doesn't recognise, instead of following fixed rules only.
2. **Tools are added as Markdown files.** Each `TOOL.md` holds both the scanner config and the guidance. No code change is needed.
3. **It covers Mac MLX tools.** oMLX, MTPLX, mlx-serve, Private LLM, AI Edge Gallery and the Claude desktop VM images aren't covered elsewhere.
4. **It lists models one by one,** with numbered picks and a mandatory review.

**Ideas taken from neighbours:**
- Move to Trash instead of deleting (macreaper). This is done.

**Still to consider:**
- Old Hugging Face revisions and orphan Ollama blobs (LLMDoctor).
- A dry-run mode that writes a reviewable script (cleanator).

Position it as "the extensible, Claude-native cleaner with Mac MLX coverage", not as the first of its kind.

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
