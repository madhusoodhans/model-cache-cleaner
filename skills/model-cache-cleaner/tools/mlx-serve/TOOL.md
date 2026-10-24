# mlx-serve

```json
{
  "tool": "mlx-serve",
  "verified": "2026-10-24",
  "locations": [
    {
      "kind": "models",
      "macos": ["~/.mlx-serve"],
      "after_delete": "Models served by mlx-serve. Re-downloaded if the server is set up again."
    }
  ]
}
```

## What it stores

- **`~/.mlx-serve`:** data for a local MLX model server, mostly downloaded models. It was 18 GB on the machine this was verified on.

## Safe to delete

- The whole folder, if the user no longer runs mlx-serve.

## How to clean

1. Stop the server.
2. Look inside with `du -hd 2 ~/.mlx-serve` to see which models it holds.
3. Remove unused models, or the whole folder.
