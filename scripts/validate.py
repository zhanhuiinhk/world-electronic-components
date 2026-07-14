#!/usr/bin/env python3
"""Validate manufacturers, taxonomy, and component JSON files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

REQUIRED_COMPONENT = [
    "part_number",
    "manufacturer",
    "category",
    "category_slug",
    "sub_category",
    "sub_category_slug",
    "datasheet_url",
]


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_taxonomy_index(taxonomy: dict):
    by_slug = {}
    for top in taxonomy.get("categories", []):
        by_slug[top["slug"]] = {
            "name_en": top["name_en"],
            "children": {c["slug"]: c["name_en"] for c in top.get("children", [])},
        }
    return by_slug


def validate_manufacturer(path: Path, errors: list):
    if path.name.startswith("_"):
        return
    try:
        data = load_json(path)
    except json.JSONDecodeError as e:
        errors.append(f"{path}: invalid JSON ({e})")
        return
    for field in ("id", "name", "website"):
        if field not in data or not data[field]:
            errors.append(f"{path}: missing required field '{field}'")
    mid = data.get("id", "")
    if mid and not SLUG_RE.match(mid):
        errors.append(f"{path}: id must be kebab-case slug")
    if mid and path.stem != mid:
        errors.append(f"{path}: filename stem '{path.stem}' must equal id '{mid}'")


def validate_component_file(path: Path, tax: dict, mfr_ids: set, errors: list):
    try:
        data = load_json(path)
    except json.JSONDecodeError as e:
        errors.append(f"{path}: invalid JSON ({e})")
        return
    if not isinstance(data, list):
        errors.append(f"{path}: root must be a JSON array")
        return

    parent_slug = path.parent.name
    seen_pn = set()
    for i, item in enumerate(data):
        loc = f"{path}[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{loc}: item must be object")
            continue
        for field in REQUIRED_COMPONENT:
            if field not in item or item[field] in (None, ""):
                errors.append(f"{loc}: missing required field '{field}'")
        pn = item.get("part_number")
        if pn:
            key = (str(pn).upper(), item.get("manufacturer_id") or item.get("manufacturer"))
            if key in seen_pn:
                errors.append(f"{loc}: duplicate part_number in file: {pn}")
            seen_pn.add(key)
        cat = item.get("category_slug")
        if cat and cat != parent_slug:
            errors.append(
                f"{loc}: category_slug '{cat}' must match folder '{parent_slug}'"
            )
        if cat and cat not in tax:
            errors.append(f"{loc}: unknown category_slug '{cat}' (add to taxonomy first)")
        sub = item.get("sub_category_slug")
        if cat in tax and sub and sub not in tax[cat]["children"]:
            errors.append(
                f"{loc}: unknown sub_category_slug '{sub}' under '{cat}'"
            )
        mid = item.get("manufacturer_id")
        if mid and mid not in mfr_ids:
            errors.append(
                f"{loc}: manufacturer_id '{mid}' not found in manufacturers/"
            )
        url = item.get("datasheet_url", "")
        if url and not str(url).startswith(("http://", "https://")):
            errors.append(f"{loc}: datasheet_url must be http(s) URL")


def main() -> int:
    errors: list[str] = []
    tax_path = ROOT / "taxonomy" / "categories.json"
    if not tax_path.exists():
        print("ERROR: taxonomy/categories.json missing")
        return 1
    taxonomy = load_json(tax_path)
    tax = build_taxonomy_index(taxonomy)

    mfr_dir = ROOT / "manufacturers"
    mfr_ids = set()
    if mfr_dir.is_dir():
        for path in sorted(mfr_dir.glob("*.json")):
            validate_manufacturer(path, errors)
            if not path.name.startswith("_"):
                try:
                    mfr_ids.add(load_json(path).get("id"))
                except Exception:
                    pass

    data_dir = ROOT / "data"
    if data_dir.is_dir():
        for path in sorted(data_dir.rglob("*.json")):
            validate_component_file(path, tax, mfr_ids, errors)

    if errors:
        print(f"校验失败，共 {len(errors)} 个问题：\n")
        for e in errors:
            print(f" - {e}")
        return 1

    print("校验通过：taxonomy / manufacturers / data 均符合规则。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
