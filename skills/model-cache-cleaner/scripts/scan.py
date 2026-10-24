#!/usr/bin/env python3
"""Read-only disk scan for local AI tools.

Reads the tool definitions in ../tools/*/TOOL.md, measures every location it
finds, lists the largest folders in the home directory, flags duplicate model
files, and prints a numbered list of suggested deletions. It never deletes
anything.

Usage:
    python3 -I scan.py              # table
    python3 -I scan.py --json       # JSON for Claude to read
    python3 -I scan.py --no-dupes   # skip duplicate detection (faster)
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
SKILL_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = SKILL_DIR / "tools"
GB = 1024 ** 3
USER_FOLDERS = ["~/Documents", "~/Desktop", "~/Downloads", "~/Pictures", "~/Movies", "~/Music"]
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.S)

# Suggestion groups, safest first.
RISK_ORDER = {"safe": 0, "duplicate": 1, "re-download": 2, "inspect": 3}


def platform_key():
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    return "windows"


def expand(path):
    return Path(os.path.expandvars(os.path.expanduser(path)))


def short(path):
    s = str(path)
    return "~" + s[len(str(HOME)):] if s.startswith(str(HOME)) else s


def disk_usage(root, seen=None):
    """Bytes allocated under root. Doesn't follow symlinks; counts hard links once."""
    seen = set() if seen is None else seen
    try:
        st = os.lstat(root)
    except OSError:
        return 0
    if not os.path.isdir(root) or os.path.islink(root):
        return st.st_blocks * 512
    total = 0
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    key = (st.st_dev, st.st_ino)
                    if key in seen:
                        continue
                    seen.add(key)
                    total += st.st_blocks * 512
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)
        except OSError:
            continue
    return total


def load_tools():
    """Parse the first ```json block of each tools/<name>/TOOL.md."""
    tools = []
    for tool_md in sorted(TOOLS_DIR.glob("*/TOOL.md")):
        if tool_md.parent.name.startswith("_"):
            continue
        match = JSON_BLOCK.search(tool_md.read_text())
        if not match:
            print(f"warning: no json block in {tool_md}", file=sys.stderr)
            continue
        try:
            spec = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            print(f"warning: bad json in {tool_md}: {e}", file=sys.stderr)
            continue
        spec["id"] = tool_md.parent.name
        spec["doc"] = str(tool_md.relative_to(SKILL_DIR))
        tools.append(spec)
    return tools


def location_paths(loc):
    paths = [expand(p) for p in loc.get(platform_key(), [])]
    for var in loc.get("env", []):
        if os.environ.get(var):
            paths.append(expand(os.environ[var]))
    return [p for p in dict.fromkeys(paths) if p.exists()]


def model_items(root, depth):
    """Folders `depth` levels below root, e.g. publisher/model for depth 2."""
    level = [root]
    for _ in range(depth):
        nxt = []
        for folder in level:
            try:
                nxt += [c for c in folder.iterdir() if c.is_dir() and not c.is_symlink() and not c.name.startswith(".")]
            except OSError:
                continue
        level = nxt
    return level


def scan_tools(tools):
    found = []
    for tool in tools:
        locations = []
        for loc in tool.get("locations", []):
            for path in location_paths(loc):
                entry = {k: v for k, v in loc.items() if k not in ("macos", "linux", "windows", "env")}
                entry["path"] = path
                entry["bytes"] = disk_usage(path)
                if loc.get("model_depth"):
                    entry["items"] = sorted(
                        ({"path": p, "bytes": disk_usage(p)} for p in model_items(path, loc["model_depth"])),
                        key=lambda i: i["bytes"], reverse=True)
                locations.append(entry)
        if locations:
            found.append({
                "id": tool["id"], "tool": tool["tool"], "doc": tool["doc"],
                "bytes": sum(l["bytes"] for l in locations),
                "locations": sorted(locations, key=lambda l: l["bytes"], reverse=True),
            })
    return sorted(found, key=lambda t: t["bytes"], reverse=True)


def is_within(path, parents):
    return any(path == p or p in path.parents for p in parents)


def top_level(min_bytes, known_paths, user_folders):
    """Largest folders under home, ~/.cache and Application Support, labelled."""
    roots = [HOME, HOME / ".cache", HOME / "Library" / "Application Support"]
    results = []
    for root in roots:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            try:
                is_dir = child.is_dir() and not child.is_symlink()
            except OSError:  # macOS privacy protection blocks some folders
                continue
            if not is_dir or (root == HOME and child in roots):
                continue
            size = disk_usage(child)
            if size < min_bytes:
                continue
            if is_within(child, user_folders):
                label = "user"
            elif is_within(child, known_paths) or any(child in p.parents for p in known_paths):
                label = "known-tool"
            else:
                label = "unknown"
            results.append({"path": child, "bytes": size, "label": label})
    return sorted(results, key=lambda r: r["bytes"], reverse=True)


def fingerprint(path, chunk=1024 * 1024):
    """Hash of the first and last MB. Cheap stand-in for a full hash on huge files."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(chunk))
        f.seek(max(0, os.path.getsize(path) - chunk))
        h.update(f.read(chunk))
    return h.hexdigest()


def find_duplicates(dirs, min_bytes):
    by_size = {}
    seen = set()
    for root in dirs:
        for dirpath, _, files in os.walk(root):
            for name in files:
                path = Path(dirpath) / name
                try:
                    st = path.lstat()
                except OSError:
                    continue
                if path.is_symlink() or st.st_size < min_bytes or (st.st_dev, st.st_ino) in seen:
                    continue
                seen.add((st.st_dev, st.st_ino))
                by_size.setdefault(st.st_size, []).append(path)

    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_print = {}
        for path in paths:
            try:
                by_print.setdefault(fingerprint(path), []).append(path)
            except OSError:
                continue
        for same in by_print.values():
            if len(same) > 1:
                groups.append({"bytes": size, "paths": same, "wasted": size * (len(same) - 1)})
    return sorted(groups, key=lambda g: g["wasted"], reverse=True)


def build_suggestions(tools_found, duplicates, min_bytes):
    """Numbered deletions from known tools and duplicates. Unknown folders stay in the raw list."""
    suggestions = []

    def add(risk, path, size, tool, why, cleanup=None, doc=None):
        if size >= min_bytes:
            suggestions.append({"risk": risk, "path": path, "bytes": size, "tool": tool,
                                "why": why, "cleanup": cleanup, "doc": doc})

    for tool in tools_found:
        for loc in tool["locations"]:
            kind = loc["kind"]
            if kind == "cache":
                add("safe", loc["path"], loc["bytes"], tool["tool"], loc.get("after_delete", "Cache, rebuilt on next use."),
                    loc.get("cleanup"), tool["doc"])
            elif kind == "models" and loc.get("items"):
                for item in loc["items"]:
                    add("re-download", item["path"], item["bytes"], tool["tool"],
                        loc.get("after_delete", "Model, re-downloaded if needed again."), loc.get("cleanup"), tool["doc"])
            elif kind == "models":
                add("re-download", loc["path"], loc["bytes"], tool["tool"],
                    loc.get("after_delete", "Models, re-downloaded if needed again."), loc.get("cleanup"), tool["doc"])
            else:
                add("inspect", loc["path"], loc["bytes"], tool["tool"],
                    loc.get("after_delete", "App data. Look inside before deleting."), loc.get("cleanup"), tool["doc"])

    # A duplicate inside a suggested folder becomes a note on that folder, since
    # deleting one file from inside an app bundle can break it.
    for group in duplicates:
        for extra in group["paths"][1:]:
            owner = next((s for s in suggestions if s["path"] in extra.parents), None)
            note = f"{short(extra)} is identical to {short(group['paths'][0])} ({group['bytes'] / GB:.1f} GB)."
            if owner:
                owner.setdefault("duplicates", []).append(note)
            else:
                add("duplicate", extra, group["bytes"], None, f"Same file as {short(group['paths'][0])}. Keep one copy.")

    suggestions.sort(key=lambda s: (RISK_ORDER[s["risk"]], -s["bytes"]))
    for n, s in enumerate(suggestions, 1):
        s["n"] = n
    return suggestions


def scan(min_gb, dupes, dupe_min_gb, suggest_min_gb):
    tools_found = scan_tools(load_tools())
    known_paths = [l["path"] for t in tools_found for l in t["locations"]]
    user_folders = [expand(p) for p in USER_FOLDERS]
    top = top_level(min_gb * GB, known_paths, user_folders)

    duplicates = []
    if dupes:
        dirs = [l["path"] for t in tools_found for l in t["locations"] if l["kind"] != "cache"]
        dirs += [t["path"] for t in top if t["label"] == "unknown"]
        duplicates = find_duplicates(dirs, dupe_min_gb * GB)

    return {
        "home": HOME,
        "tools": tools_found,
        "top": top,
        "duplicates": duplicates,
        "suggestions": build_suggestions(tools_found, duplicates, suggest_min_gb * GB),
    }


def gb(n):
    return f"{n / GB:6.1f} GB"


def print_table(result):
    print("RAW: largest folders")
    for item in result["top"][:20]:
        print(f"  {gb(item['bytes'])}  {item['label']:<11} {short(item['path'])}")

    print("\nRAW: local AI tools found")
    for tool in result["tools"]:
        print(f"  {gb(tool['bytes'])}  {tool['tool']}  ({tool['doc']})")
        for loc in tool["locations"]:
            print(f"    {gb(loc['bytes'])}  {loc['kind']:<9} {short(loc['path'])}")

    if result["duplicates"]:
        print("\nRAW: duplicate files")
        for group in result["duplicates"][:20]:
            print(f"  {gb(group['bytes'])} each, {len(group['paths'])} copies")
            for path in group["paths"]:
                print(f"    {short(path)}")

    print("\nSUGGESTED DELETIONS (pick by number)")
    risk = None
    for s in result["suggestions"]:
        if s["risk"] != risk:
            risk = s["risk"]
            print(f"\n  [{risk}]")
        tool = f"{s['tool']}: " if s["tool"] else ""
        print(f"  {s['n']:>3}. {gb(s['bytes'])}  {short(s['path'])}")
        print(f"       {tool}{s['why']}")
        for note in s.get("duplicates", []):
            print(f"       duplicate: {note}")


def to_json(result):
    def clean(obj):
        if isinstance(obj, Path):
            return short(obj)
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj
    return json.dumps(clean(result), indent=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument("--min-gb", type=float, default=1.0, help="smallest folder in the raw list (default 1)")
    parser.add_argument("--suggest-min-gb", type=float, default=0.2, help="smallest suggestion (default 0.2)")
    parser.add_argument("--no-dupes", action="store_true", help="skip duplicate detection")
    parser.add_argument("--dupe-min-gb", type=float, default=0.5, help="smallest file checked for duplicates (default 0.5)")
    args = parser.parse_args()

    result = scan(args.min_gb, not args.no_dupes, args.dupe_min_gb, args.suggest_min_gb)
    if args.json:
        print(to_json(result))
    else:
        print_table(result)


if __name__ == "__main__":
    main()
