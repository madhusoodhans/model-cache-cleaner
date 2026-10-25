# Changelog

## 2026-10-25

- **Similar model names are no longer treated as duplicates.** Different quantizations, formats (GGUF and MLX), variants (MTP, speed-optimised) and fine-tunes of the same base model perform differently. The skill no longer suggests keeping only one of them. Only byte-identical files are flagged as duplicates.
- **Install docs:** added cloning, linking the skill so it updates with `git pull`, and a note that running sessions keep the version they loaded.

## 2026-10-24

- **Deletions go to the Trash.** Added `scripts/trash.py`. It uses macOS's built-in `trash` (Finder's Put Back works) or the freedesktop Trash on Linux. It refuses the home folder, user folders, paths outside home and symlinks.
- **Review is mandatory.** Every deletion is shown first as a dry run with exact paths and sizes, and nothing moves without an explicit yes.
- Added the MIT licence.
- First release: read-only scanner, 14 tool folders with per-tool `TOOL.md` guidance, a template for adding tools, per-model listing and duplicate detection.
