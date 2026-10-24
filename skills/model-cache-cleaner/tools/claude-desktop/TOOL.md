# Claude desktop app

```json
{
  "tool": "Claude desktop",
  "homepage": "https://claude.ai/download",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "app-data",
      "macos": ["~/Library/Application Support/Claude/vm_bundles", "~/Library/Application Support/Claude-3p/vm_bundles"],
      "after_delete": "Virtual machine image used for sandboxed work. The app downloads it again when needed."
    },
    {
      "kind": "cache",
      "macos": ["~/Library/Application Support/Claude/Cache", "~/Library/Application Support/Claude-3p/Cache"],
      "after_delete": "Web cache, rebuilt automatically."
    }
  ]
}
```

## What it stores

- **`vm_bundles/claudevm.bundle`:** a Linux virtual machine image (about 10 GB) that the app uses to run code in a sandbox.
- **`Cache/`, `Partitions/`:** web caches and storage for the app's interface.
- **`claude-code/`, `claude-code-vm/`:** Claude Code components bundled with the app.

`Claude` and `Claude-3p` are two separate app installs (for example a personal and a work build). Each keeps its own copy of the VM image. On the machine this was verified on, both held the same 10 GB `rootfs.img`.

## Safe to delete

- `Cache/`, with the app quit.

## Ask first

- `vm_bundles/` of an install the user no longer uses. The app re-downloads it if needed.
- The whole `Claude-3p` folder, if the second app has been uninstalled.

## Never delete

- Anything while the app is running.
- `Partitions/` and config files, unless the user wants to sign out and reset the app.

## How to clean

1. Quit every Claude app.
2. Ask which install the user still uses.
3. Remove `vm_bundles/` or `Cache/` from the one that isn't used.
