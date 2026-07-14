#!/usr/bin/env python3
"""Weekly multi-category DigiKey collect into the repository tree."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

COLLECTORS = Path(__file__).resolve().parent
ROOT = COLLECTORS.parents[1]
RUN = COLLECTORS / "run_collect.py"


def load_query_map() -> dict:
    data = json.loads((COLLECTORS / "query_map.json").read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not str(k).startswith("_")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly DigiKey multi-category collect")
    parser.add_argument("--limit", type=int, default=10, help="per-category limit")
    parser.add_argument(
        "--env",
        choices=("sandbox", "production"),
        default=None,
        help="passed to run_collect (default: DIGIKEY_ENV)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="fixture only, no DigiKey network"
    )
    parser.add_argument(
        "--sleep", type=float, default=1.2, help="seconds between categories"
    )
    parser.add_argument(
        "--subs",
        default="",
        help="comma-separated sub slugs (default: all in query_map.json)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT,
        help="output repo root (default: repository root)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="do not stop if one category fails",
    )
    args = parser.parse_args()

    qmap = load_query_map()
    if args.subs.strip():
        subs = [s.strip() for s in args.subs.split(",") if s.strip()]
        for s in subs:
            if s not in qmap:
                print(f"Unknown sub: {s}")
                return 2
    else:
        subs = list(qmap.keys())

    print(f"Weekly collect: {len(subs)} categories, limit={args.limit}")
    print(f"Out dir: {args.out_dir.resolve()}")

    summary = []
    failed = 0
    for i, sub in enumerate(subs, 1):
        print(f"\n=== [{i}/{len(subs)}] {sub} ===")
        cmd = [
            sys.executable,
            str(RUN),
            "--sub",
            sub,
            "--limit",
            str(args.limit),
            "--out-dir",
            str(args.out_dir.resolve()),
        ]
        if args.dry_run:
            cmd.append("--dry-run")
        elif args.env:
            cmd.extend(["--env", args.env])

        r = subprocess.run(cmd, cwd=str(ROOT))
        ok = r.returncode == 0
        summary.append((sub, r.returncode))
        if not ok:
            failed += 1
            print(f"FAILED {sub} exit={r.returncode}")
            if not args.continue_on_error:
                break
        if i < len(subs) and args.sleep > 0:
            time.sleep(args.sleep)

    print("\n=== SUMMARY ===")
    for sub, code in summary:
        print(f"  {sub}: {'OK' if code == 0 else f'FAIL({code})'}")
    print(f"Failed categories: {failed}/{len(summary)}")

    # Always try validate when writing into real tree
    if not args.dry_run and args.out_dir.resolve() == ROOT.resolve():
        print("\n=== VALIDATE ===")
        vr = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")])
        if vr.returncode != 0:
            print("validate.py failed")
            return vr.returncode
        print("\n=== BUILD CATALOG / MANIFEST ===")
        br = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_catalog.py")])
        if br.returncode != 0:
            print("build_catalog.py failed")
            return br.returncode

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
