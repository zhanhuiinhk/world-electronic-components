#!/usr/bin/env python3
"""Convert a component CSV into data JSON array (CSV → JSON batch import)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOP_LEVEL = {
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
    "updated_at",
}


def coerce(value: str):
    v = value.strip()
    if v == "":
        return None
    low = v.lower()
    if low in ("true", "yes", "y"):
        return True
    if low in ("false", "no", "n"):
        return False
    try:
        if "." in v or "e" in low:
            return float(v)
        return int(v)
    except ValueError:
        return v


def row_to_item(row: dict) -> dict:
    item: dict = {}
    attrs: dict = {}
    for raw_key, raw_val in row.items():
        if raw_key is None:
            continue
        key = raw_key.strip()
        if not key or raw_val is None or str(raw_val).strip() == "":
            continue
        val = str(raw_val).strip()
        if key.startswith("attr.") or key.startswith("attributes."):
            akey = key.split(".", 1)[1]
            attrs[akey] = coerce(val)
        elif key == "tags":
            item["tags"] = [t.strip() for t in val.split("|") if t.strip()]
        elif key in TOP_LEVEL:
            item[key] = coerce(val) if key not in {
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
                "updated_at",
            } else val
        else:
            # unknown columns → attributes
            attrs[key] = coerce(val)
    if attrs:
        item["attributes"] = attrs
    return item


def convert(csv_path: Path) -> list:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("CSV has no header row")
        items = []
        for row in reader:
            item = row_to_item(row)
            if item.get("part_number"):
                items.append(item)
    return items


def main():
    parser = argparse.ArgumentParser(
        description="Batch import: CSV → component JSON array"
    )
    parser.add_argument("csv_file", type=Path, help="Input CSV path")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JSON path (default: stdout)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent (default 2)",
    )
    args = parser.parse_args()
    if not args.csv_file.exists():
        print(f"File not found: {args.csv_file}", file=sys.stderr)
        sys.exit(1)

    items = convert(args.csv_file)
    text = json.dumps(items, ensure_ascii=False, indent=args.indent) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote {len(items)} items → {args.output}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
