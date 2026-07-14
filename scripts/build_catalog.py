#!/usr/bin/env python3
"""Build docs/assets/catalog.json, data-manifest.json for GitHub Pages search."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = ROOT / "docs" / "assets"

PUBLIC_FIELDS = {
    "part_number",
    "manufacturer",
    "manufacturer_id",
    "product_class",
    "category",
    "category_slug",
    "sub_category",
    "sub_category_slug",
    "package",
    "origin",
    "datasheet_url",
    "description",
    "status",
    "attributes",
    "tags",
    "updated_at",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def public_item(obj: dict) -> dict:
    return {k: obj[k] for k in PUBLIC_FIELDS if k in obj}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    data_files = []
    if DATA.is_dir():
        for path in sorted(DATA.rglob("*.json")):
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            data_files.append(rel)
            try:
                data = load_json(path)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, list):
                continue
            for obj in data:
                if isinstance(obj, dict):
                    items.append(public_item(obj))

    catalog = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(items),
        "items": items,
    }
    (OUT_DIR / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "source": "https://raw.githubusercontent.com/zhanhuiinhk/world-electronic-components/main/",
        "files": data_files,
        "count_files": len(data_files),
    }
    (OUT_DIR / "data-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
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

    print(f"Built catalog: {len(items)} items, {len(data_files)} files → {OUT_DIR}")


if __name__ == "__main__":
    main()
