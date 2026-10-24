#!/usr/bin/env python3
"""Move approved paths to the Trash instead of deleting them.

Only run this after the user has reviewed the exact paths and said yes.
Items stay recoverable until the Trash is emptied (Finder → Put Back on macOS).
Space is freed only when the Trash is emptied.

Usage:
    python3 -I trash.py --dry-run PATH [PATH ...]   # show what would move
    python3 -I trash.py PATH [PATH ...]             # move to Trash

Refuses: the home folder itself, user folders and anything inside them,
paths outside the home folder, symlinks, and paths that don't exist.
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

HOME = Path.home()
PROTECTED = [HOME / p for p in ("Documents", "Desktop", "Downloads", "Pictures", "Movies", "Music", ".ssh", ".Trash")]
GB = 1024 ** 3


def disk_usage(root):
    if not root.is_dir():
        return root.lstat().st_blocks * 512
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            try:
                total += os.lstat(os.path.join(dirpath, name)).st_blocks * 512
            except OSError:
                pass
    return total


def check(raw):
    """Return (path, None) if the path may be trashed, else (path, reason)."""
    path = Path(os.path.expanduser(raw))
    if not path.is_absolute():
        return path, "not an absolute path"
    if path.is_symlink():
        return path, "is a symlink"
    if not path.exists():
        return path, "does not exist"
    path = path.resolve()
    if path == HOME:
        return path, "is the home folder"
    if HOME not in path.parents:
        return path, "is outside the home folder"
    for p in PROTECTED:
        if path == p or p in path.parents:
            return path, f"is inside protected folder {p.name}"
    return path, None


def trash_macos(path):
    if Path("/usr/bin/trash").exists():  # built into macOS 15 and later
        subprocess.run(["/usr/bin/trash", str(path)], check=True)
    else:
        script = f'tell application "Finder" to delete (POSIX file "{path}" as alias)'
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)


def trash_linux(path):
    for cmd in (["gio", "trash"], ["trash-put"]):
        if shutil.which(cmd[0]):
            subprocess.run(cmd + [str(path)], check=True)
            return
    # Freedesktop Trash by hand, so the file manager can still restore it.
    trash = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share")) / "Trash"
    (trash / "files").mkdir(parents=True, exist_ok=True)
    (trash / "info").mkdir(parents=True, exist_ok=True)
    name, n = path.name, 1
    while (trash / "files" / name).exists() or (trash / "info" / f"{name}.trashinfo").exists():
        n += 1
        name = f"{path.name}.{n}"
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    (trash / "info" / f"{name}.trashinfo").write_text(
        f"[Trash Info]\nPath={quote(str(path))}\nDeletionDate={stamp}\n")
    shutil.move(str(path), trash / "files" / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--dry-run", action="store_true", help="list what would be moved, move nothing")
    args = parser.parse_args()

    if sys.platform == "darwin":
        trash = trash_macos
    elif sys.platform.startswith("linux"):
        trash = trash_linux
    else:
        sys.exit("Unsupported platform. Delete manually after review.")

    approved, refused = [], []
    for raw in args.paths:
        path, reason = check(raw)
        (refused if reason else approved).append((path, reason))
    for path, reason in refused:
        print(f"REFUSED  {path}: {reason}")
    if refused:
        sys.exit("Nothing moved. Remove the refused paths and run again.")

    total = 0
    for path, _ in approved:
        size = disk_usage(path)
        total += size
        if args.dry_run:
            print(f"WOULD MOVE  {size / GB:6.1f} GB  {path}")
            continue
        try:
            trash(path)
            print(f"MOVED       {size / GB:6.1f} GB  {path}")
        except (subprocess.CalledProcessError, OSError) as e:
            sys.exit(f"FAILED      {path}: {e}. Stopped; later paths were not moved.")

    verb = "Would move" if args.dry_run else "Moved"
    print(f"\n{verb} {total / GB:.1f} GB to the Trash.")
    if not args.dry_run:
        print("Space is freed when the Trash is emptied. Until then, items can be restored.")


if __name__ == "__main__":
    main()
