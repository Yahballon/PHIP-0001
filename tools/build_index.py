#!/usr/bin/env python3
"""Generate deterministic public indexes from approved registrations."""
import json
import sys
from pathlib import Path

from validate_registry import ROOT, load_registry

def serialize(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

def main():
    records, errors = load_registry(ROOT / "registry")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    records.sort(key=lambda r: r["title_id"])
    output = ROOT / "index"
    output.mkdir(exist_ok=True)
    status = {name: sum(x["status"] == name for x in records)
              for name in ("registered", "reserved")}
    (output / "registry.json").write_text(serialize({
        "schema_version": "1.0", "count": len(records), "apps": records
    }), encoding="utf-8")
    (output / "stats.json").write_text(serialize({
        "count": len(records), "by_status": status
    }), encoding="utf-8")
    lines = ["# Registry directory", "",
             "> Generated automatically. Edit `registry/*.json`, not this file.", "",
             "| Title ID | Application | Global identity | Owner | Status |",
             "| --- | --- | --- | --- | --- |"]
    for r in records:
        source = r["source_repo"]
        lines.append(f"| `{r['title_id']}` | [{r['name']}]({source}) "
                     f"| `{r['app_id']}` | {r['owner']} | {r['status']} |")
    if not records:
        lines.append("| — | No registrations | — | — | — |")
    (ROOT / "REGISTRY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated index for {len(records)} entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
