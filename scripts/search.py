#!/usr/bin/env python3
"""Search components under data/**/*.json by part number, manufacturer, category, package, tags."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def iter_component_files():
    if not DATA_DIR.is_dir():
        return
    for path in sorted(DATA_DIR.rglob("*.json")):
        yield path


def load_items(path: Path):
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def matches(item: dict, keyword: str) -> bool:
    haystacks = [
        item.get("part_number", ""),
        item.get("manufacturer", ""),
        item.get("category", ""),
        item.get("sub_category", ""),
        item.get("package", ""),
        item.get("origin", ""),
        item.get("description", ""),
        " ".join(item.get("tags") or []),
    ]
    return any(keyword in str(h).lower() for h in haystacks)


def search(keyword: str) -> list[tuple[Path, dict]]:
    keyword = keyword.lower().strip()
    results = []
    for path in iter_component_files():
        try:
            items = load_items(path)
        except json.JSONDecodeError:
            print(f"[WARN] JSON 格式错误: {path.relative_to(ROOT)}", file=sys.stderr)
            continue
        for item in items:
            if matches(item, keyword):
                results.append((path, item))
    return results


def main():
    parser = argparse.ArgumentParser(description="搜索元器件数据库")
    parser.add_argument("keyword", nargs="?", help="型号 / 厂家 / 分类 / 封装 / 标签")
    args = parser.parse_args()
    keyword = args.keyword or input("请输入要搜索的型号/厂家/分类/封装: ").strip()
    if not keyword:
        print("请提供关键词。")
        sys.exit(1)

    results = search(keyword)
    if not results:
        print("未找到匹配元器件。")
        sys.exit(0)

    print(f"共 {len(results)} 条匹配：\n")
    for path, item in results:
        print(f"✅ {item.get('part_number')}")
        print(f"   厂家: {item.get('manufacturer')} | 产地: {item.get('origin', '未知')}")
        print(
            f"   分类: {item.get('category')} > {item.get('sub_category')} "
            f"| 封装: {item.get('package', '—')}"
        )
        print(f"   手册: {item.get('datasheet_url')}")
        print(f"   文件: {path.relative_to(ROOT)}")
        print()


if __name__ == "__main__":
    main()
