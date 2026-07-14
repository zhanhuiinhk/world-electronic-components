#!/usr/bin/env python3
"""Collect parts from DigiKey (or dry-run fixture) into WEC data/ layout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

COLLECTORS = Path(__file__).resolve().parent
ROOT = COLLECTORS.parents[1]
if str(COLLECTORS) not in sys.path:
    sys.path.insert(0, str(COLLECTORS))

from digikey_client import DigiKeyClient, DigiKeyConfig, extract_products  # noqa: E402
from map_to_wec import load_profiles, load_synonyms, map_product  # noqa: E402


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def merge_components(existing: list, new_items: list) -> list:
    by_key = {}
    for it in existing:
        if isinstance(it, dict) and it.get("part_number"):
            key = (
                str(it.get("manufacturer_id") or "").lower(),
                str(it["part_number"]).upper(),
            )
            by_key[key] = it
    for it in new_items:
        key = (
            str(it.get("manufacturer_id") or "").lower(),
            str(it["part_number"]).upper(),
        )
        by_key[key] = it
    return sorted(by_key.values(), key=lambda x: str(x.get("part_number", "")).upper())


def write_manufacturer(out_root: Path, mfr: dict) -> None:
    path = out_root / "manufacturers" / f"{mfr['id']}.json"
    if path.exists():
        old = load_json(path)
        if old.get("website") and "supplier-centers" not in str(old.get("website", "")):
            mfr["website"] = old["website"]
        for k in ("name_zh", "country", "aliases", "contact"):
            if old.get(k) and not mfr.get(k):
                mfr[k] = old[k]
    save_json(path, mfr)


def write_components(
    out_root: Path,
    category_slug: str,
    manufacturer_id: str,
    items: list,
    merge: bool,
) -> Path:
    path = out_root / "data" / category_slug / f"{manufacturer_id}.json"
    existing = []
    if merge and path.exists():
        try:
            existing = load_json(path)
            if not isinstance(existing, list):
                existing = []
        except json.JSONDecodeError:
            existing = []
    merged = merge_components(existing, items) if merge else items
    save_json(path, merged)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="DigiKey → WEC collector")
    parser.add_argument("--sub", required=True, help="sub_category_slug")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--env", choices=("sandbox", "production"), default=None)
    parser.add_argument(
        "--dry-run", action="store_true", help="fixture only, no network"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="output root (default: repo root; dry-run defaults to _collect_out)",
    )
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--no-merge", action="store_true")
    parser.add_argument("--keyword", default=None)
    args = parser.parse_args()

    qmap = load_json(COLLECTORS / "query_map.json")
    if args.sub not in qmap or str(args.sub).startswith("_"):
        known = [k for k in qmap if not k.startswith("_")]
        print(f"Unknown --sub {args.sub!r}. Known: {', '.join(known)}")
        return 2

    meta = qmap[args.sub]
    keywords = args.keyword or meta["keywords"][0]
    synonyms = load_synonyms()
    profiles = load_profiles()

    if args.out_dir is None:
        out_root = (ROOT / "_collect_out") if args.dry_run else ROOT
    else:
        out_root = args.out_dir
    out_root = out_root.resolve()

    print(f"Category: {meta['category_slug']} / {args.sub}")
    print(f"Keyword:  {keywords}")
    print(f"Limit:    {args.limit}")
    print(f"Out dir:  {out_root}")

    if args.dry_run:
        fixture = COLLECTORS / "fixtures" / "sample_keyword_search.json"
        print(f"Dry-run fixture: {fixture}")
        response = load_json(fixture)
    else:
        try:
            cfg = DigiKeyConfig.from_env(args.env)
        except Exception as e:
            print(f"Config error: {e}")
            print("Tip: --dry-run without keys, or docs/DIGIKEY_SETUP.md")
            return 2
        print(f"API env:  {cfg.env}")
        client = DigiKeyClient(cfg)
        try:
            response = client.keyword_search(
                keywords, record_count=min(max(args.limit * 2, 5), 50)
            )
        except Exception as e:
            print(f"API error: {e}")
            return 1

    products = extract_products(response)
    print(f"Raw products from API/fixture: {len(products)}")

    accepted: list[dict] = []
    mfrs: dict[str, dict] = {}
    skips: dict[str, int] = {}

    for prod in products:
        if len(accepted) >= args.limit:
            break
        comp, mfr, reason = map_product(
            prod,
            category_slug=meta["category_slug"],
            category=meta["category"],
            sub_category_slug=args.sub,
            sub_category=meta["sub_category"],
            product_class=meta.get("product_class", "component"),
            synonyms=synonyms,
            profiles=profiles,
        )
        if reason:
            skips[reason] = skips.get(reason, 0) + 1
            continue
        assert comp and mfr
        accepted.append(comp)
        mfrs[mfr["id"]] = mfr

    print(f"Accepted: {len(accepted)}")
    if skips:
        print("Skipped:", ", ".join(f"{k}={v}" for k, v in sorted(skips.items())))

    if not accepted:
        print("Nothing to write.")
        return 0

    merge = not args.no_merge
    by_mfr: dict[str, list] = {}
    for c in accepted:
        by_mfr.setdefault(c["manufacturer_id"], []).append(c)

    for mid, items in by_mfr.items():
        write_manufacturer(out_root, mfrs[mid])
        path = write_components(
            out_root, meta["category_slug"], mid, items, merge=merge
        )
        try:
            rel = path.relative_to(out_root)
        except ValueError:
            rel = path
        print(f"Wrote {len(items)} → {rel}")

    if args.validate:
        import subprocess

        # validate only works on repo ROOT layout; if out_dir is ROOT, run it
        if out_root == ROOT.resolve():
            rc = subprocess.call([sys.executable, str(ROOT / "scripts" / "validate.py")])
            if rc != 0:
                print("validate.py failed")
                return rc
            print("validate.py OK")
        else:
            print("Skip validate: out-dir is not repo root (copy files into data/ first)")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
