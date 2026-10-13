# Integration guide

## Read-only registry

The published `index/registry.json` contains:

```json
{
  "schema_version": "1.0",
  "count": 1,
  "apps": [
    {
      "schema_version": "1.0",
      "title_id": "PPSA99873",
      "app_id": "io.github.yahballon.payload-launcherx",
      "name": "Payload LauncherX",
      "developer": "YAHBALLON",
      "owner": "Yahballon",
      "source_repo": "https://github.com/Yahballon/PS5_Payload_LauncherX",
      "status": "registered",
      "created": "2026-10-13",
      "description": "Native PS5 homebrew USB payload launcher.",
      "license": "GPL-3.0-or-later"
    }
  ]
}
```

Use the raw URL from README for the latest reviewed registry; pin a commit for reproducibility. `count` is the total of all entries, including reservations.

### Client recommendations

1. Parse and validate schema version before using the data.
2. Compare both `title_id` and `app_id`; a Title ID match with conflicting publisher identity should be flagged and must not become a silent update.
3. Respect `status`. `reserved` does not imply a downloadable app.
4. Do **not** infer the official package format, installation path, ZIP contents, binary integrity, firmware compatibility or app safety from this registry.
5. Verify release hashes and signatures independently and prefer the developer's reviewed source or official community listing.
6. Cache cautiously; stale data may not include a newly approved entry.

### Local checks for developers

```bash
python tools/validate_registry.py
python -m unittest discover -s tests -v
python tools/build_index.py
git diff --exit-code -- index/registry.json index/stats.json REGISTRY.md
```

### Automated process

* PR validation checks all JSON files, duplicates, namespace-to-owner consistency, immutable identity changes and the GitHub PR author's login.
* A maintainer must review claims of actual GitHub repository control and external registry collisions. A matching handle is **not proof** of control.
* A successful merge triggers the index publisher; it makes a commit only when generated index content changed. PRs that register an app should **also** regenerate and commit the index before merge, so the validation diff check passes immediately.
* No workflow runs contributed application binaries. PR validation uses read-only token permissions.

### Relationship to existing community services

PHIP-0001 is not intended to replace [the PS5 homebrew catalog](https://github.com/blackbearreloaded/ps5-homebrew-catalog). Check both before claiming a new number. A future interoperable approach might delegate ID allocations to a shared authority and mirror them; this requires explicit agreement with other maintainers.
