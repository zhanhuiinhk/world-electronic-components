#!/usr/bin/env python3
"""Build docs/assets/catalog.json (+ taxonomy/profiles copy) for GitHub Pages search."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = ROOT / "docs" / "assets"


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    if DATA.is_dir():
        for path in sorted(DATA.rglob("*.json")):
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, list):
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            for obj in data:
                if isinstance(obj, dict):
                    row = dict(obj)
                    row["_source"] = rel
                    items.append(row)

    catalog = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(items),
        "items": items,
    }
    (OUT_DIR / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    tax = ROOT / "taxonomy" / "categories.json"
    if tax.exists():
        shutil.copyfile(tax, OUT_DIR / "taxonomy.json")

    profiles = ROOT / "schema" / "attribute-profiles.json"
    if profiles.exists():
        shutil.copyfile(profiles, OUT_DIR / "attribute-profiles.json")

    mfrs = []
    mdir = ROOT / "manufacturers"
    if mdir.is_dir():
        for path in sorted(mdir.glob("*.json")):
            if path.name.startswith("_"):
                continue
            try:
                mfrs.append(load_json(path))
            except json.JSONDecodeError:
                pass
    (OUT_DIR / "manufacturers.json").write_text(
        json.dumps(mfrs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Built catalog: {len(items)} items → {OUT_DIR / 'catalog.json'}")


if __name__ == "__main__":
    main()
