#!/usr/bin/env python3
"""PHIP-0001 registry validator. Python 3.10+, standard library only."""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"schema_version", "title_id", "app_id", "name", "developer",
            "owner", "source_repo", "status", "created"}
OPTIONAL = {"description", "license"}
TITLE = re.compile(r"^PPSA[0-9]{5}$")
APP = re.compile(r"^io\.github\.([a-z0-9-]+)\.([a-z0-9][a-z0-9-]*)$")
OWNER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+$")


def validate_entry(data, filename):
    errors = []
    if not isinstance(data, dict):
        return ["registration must be a JSON object"]
    missing = REQUIRED - set(data)
    extra = set(data) - REQUIRED - OPTIONAL
    if missing:
        errors.append("missing fields: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unknown fields: " + ", ".join(sorted(extra)))
    if missing:
        return errors
    if data["schema_version"] != "1.0":
        errors.append("schema_version must be 1.0")
    tid = data["title_id"]
    if not isinstance(tid, str) or not TITLE.fullmatch(tid) or tid == "PPSA99999":
        errors.append("title_id must be PPSA followed by five digits (not PPSA99999)")
    if filename != tid + ".json":
        errors.append("filename must equal title_id + .json")
    app_id = data["app_id"]
    m = APP.fullmatch(app_id) if isinstance(app_id, str) else None
    if not m or len(app_id) > 150:
        errors.append("app_id must be io.github.<owner>.<slug> (lowercase)")
    for field, limit in (("name", 100), ("developer", 100)):
        value = data[field]
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            errors.append(field + " must be nonempty text, max " + str(limit))
    owner = data["owner"]
    if not isinstance(owner, str) or not OWNER.fullmatch(owner):
        errors.append("owner must be a valid GitHub username or organization")
    if m and isinstance(owner, str) and m.group(1) != owner.lower():
        errors.append("app_id owner namespace must match owner (case-insensitive)")
    source = data["source_repo"]
    if not isinstance(source, str):
        errors.append("source_repo must be a GitHub repository HTTPS URL")
    else:
        url = urlsplit(source)
        parts = url.path.strip("/").split("/")
        if (url.scheme != "https" or url.netloc != "github.com"
                or url.query or url.fragment or len(parts) != 2
                or not all(REPO.fullmatch(part) for part in parts)):
            errors.append("source_repo must be https://github.com/OWNER/REPO")
        elif isinstance(owner, str) and parts[0].lower() != owner.lower():
            errors.append("source_repo owner must match owner")
    if data["status"] not in ("reserved", "registered"):
        errors.append("status must be reserved or registered")
    try:
        if not isinstance(data["created"], str):
            raise ValueError("not a string")
        dt.date.fromisoformat(data["created"])
    except ValueError:
        errors.append("created must be a valid ISO YYYY-MM-DD date")
    for field, limit in (("description", 500), ("license", 80)):
        if field in data and (not isinstance(data[field], str)
                              or len(data[field]) > limit):
            errors.append(field + " must be text, max " + str(limit))
    return errors


def load_registry(directory):
    errors, records = [], []
    if not directory.is_dir():
        return [], ["registry directory not found"]
    seen_ids, seen_apps = {}, {}
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            errors.append(f"{path.name}: invalid JSON/UTF-8: {exc}")
            continue
        for error in validate_entry(data, path.name):
            errors.append(f"{path.name}: {error}")
        if not isinstance(data, dict):
            continue
        tid, app = data.get("title_id"), data.get("app_id")
        if isinstance(tid, str):
            key = tid.casefold()
            if key in seen_ids:
                errors.append(f"{path.name}: duplicate title_id also in {seen_ids[key]}")
            seen_ids[key] = path.name
        if isinstance(app, str):
            key = app.casefold()
            if key in seen_apps:
                errors.append(f"{path.name}: duplicate app_id also in {seen_apps[key]}")
            seen_apps[key] = path.name
        records.append(data)
    return records, errors


def changed_entries(base):
    try:
        result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=ACMR",
                                 base + "...HEAD", "--", "registry/"],
                                cwd=ROOT, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("could not compare PR with base: " + exc.stderr) from exc
    return [p for p in result.stdout.splitlines()
            if p.startswith("registry/") and p.endswith(".json")]


def check_pr_ownership(paths, actor, base):
    errors = []
    for name in paths:
        target = ROOT / name
        if not target.is_file():
            continue
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        owner = data.get("owner")
        if not isinstance(owner, str) or owner.lower() != actor.lower():
            errors.append(f"{name}: PR author '{actor}' must be the GitHub owner "
                          f"'{owner}' to request a registry change")
        old = subprocess.run(["git", "show", base + ":" + name], cwd=ROOT,
                             text=True, capture_output=True)
        if old.returncode == 0:
            old_data = json.loads(old.stdout)
            for key in ("title_id", "app_id", "owner", "source_repo", "created"):
                if data.get(key) != old_data.get(key):
                    errors.append(f"{name}: immutable field '{key}' changed; "
                                  "open a migration/transfer discussion")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "registry")
    parser.add_argument("--actor", help="PR author login, for authorization check")
    parser.add_argument("--base", default="origin/main",
                        help="Git ref used as PR comparison base")
    args = parser.parse_args(argv)
    records, errors = load_registry(args.registry)
    if args.actor:
        try:
            errors.extend(check_pr_ownership(changed_entries(args.base),
                                             args.actor, args.base))
        except (RuntimeError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    if errors:
        print("PHIP validation failed:", file=sys.stderr)
        for err in errors:
            print(" - " + err, file=sys.stderr)
        return 1
    print(f"PHIP registry OK: {len(records)} registration(s); "
          "validation does not guarantee external uniqueness or publisher ownership.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
