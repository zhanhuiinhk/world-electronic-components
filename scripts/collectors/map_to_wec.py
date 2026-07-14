#!/usr/bin/env python3
"""Map DigiKey product objects → WEC component + manufacturer records."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

COLLECTORS = Path(__file__).resolve().parent
ROOT = COLLECTORS.parents[1]

SLUG_RE = re.compile(r"[^a-z0-9]+")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = s.replace("&", " and ")
    s = SLUG_RE.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"


def _dig(obj: dict, *paths: str, default=None):
    for path in paths:
        cur: Any = obj
        ok = True
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur not in (None, ""):
            return cur
    return default


def _parameters_list(product: dict) -> list[dict]:
    for key in ("Parameters", "parameters", "ProductParameters"):
        val = product.get(key)
        if isinstance(val, list):
            return [p for p in val if isinstance(p, dict)]
    return []


def _param_pairs(product: dict) -> dict[str, str]:
    pairs = {}
    for p in _parameters_list(product):
        name = (
            p.get("ParameterText")
            or p.get("Parameter")
            or p.get("Name")
            or p.get("parameterText")
            or ""
        )
        value = (
            p.get("ValueText")
            or p.get("Value")
            or p.get("valueText")
            or ""
        )
        if name:
            pairs[str(name).strip()] = str(value).strip()
    return pairs


def _parse_number(text: str) -> float | int | str:
    t = text.strip().replace(",", "").replace("±", "").replace("+", "")
    t = re.sub(r"\s+", " ", t)

    # 10 kOhms / 10k / 4.7 MOhm
    m2 = re.match(
        r"^([\d.]+)\s*([kKmM])\s*(?:ohms?|Ω)?$", t, re.I
    )
    if m2:
        base = float(m2.group(1))
        mult = m2.group(2).lower()
        return base * (1000 if mult == "k" else 1_000_000)

    # capacitance: 100nF, 0.1uF, 100 nF
    m3 = re.match(r"^([\d.]+)\s*(p|n|u|µ|m)?\s*F$", t, re.I)
    if m3:
        base = float(m3.group(1))
        pref = (m3.group(2) or "").lower()
        factor = {"p": 1e-6, "n": 1e-3, "u": 1.0, "µ": 1.0, "m": 1000.0, "": 1e6}
        return base * factor.get(pref, 1.0)

    # 0.1W / 1% / 50V
    m = re.match(
        r"^([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*%?\s*[a-zA-Z°/]*$", t
    )
    if m:
        num = m.group(1)
        try:
            if "." in num or "e" in num.lower():
                return float(num)
            return int(num)
        except ValueError:
            pass

    return text


def map_parameters(product: dict, synonyms: dict) -> dict:
    attrs = {}
    pairs = _param_pairs(product)
    syn = {
        k.lower(): v
        for k, v in synonyms.items()
        if not str(k).startswith("_") and isinstance(v, str)
    }
    for name, value in pairs.items():
        key = syn.get(name.lower())
        if not key:
            nl = name.lower()
            for sk, sv in syn.items():
                if sk in nl or nl in sk:
                    key = sv
                    break
        if not key or value in ("", "-", "n/a"):
            continue
        if key in attrs:
            continue
        attrs[key] = _parse_number(value)
    return attrs


def manufacturer_record(product: dict) -> dict | None:
    name = _dig(
        product,
        "Manufacturer.Name",
        "Manufacturer.Value",
        "ManufacturerName",
        "manufacturer",
        default=None,
    )
    if isinstance(name, dict):
        name = name.get("Name") or name.get("Value")
    if not name:
        return None
    name = str(name).strip()
    mid = slugify(name)
    return {
        "id": mid,
        "name": name,
        "website": "https://www.digikey.com/en/supplier-centers",
        "notes": "Auto-registered from DigiKey collect; please set official website.",
    }


def map_product(
    product: dict,
    *,
    category_slug: str,
    category: str,
    sub_category_slug: str,
    sub_category: str,
    product_class: str,
    synonyms: dict,
    profiles: dict,
) -> tuple[dict | None, dict | None, str | None]:
    mpn = _dig(
        product,
        "ManufacturerProductNumber",
        "ManufacturerPartNumber",
        "manufacturerProductNumber",
        default=None,
    )
    if not mpn:
        mpn = product.get("DigiKeyProductNumber") or product.get("ProductNumber")
    if not mpn:
        return None, None, "missing_mpn"

    mfr = manufacturer_record(product)
    if not mfr:
        return None, None, "missing_manufacturer"

    datasheet = _dig(
        product,
        "DatasheetUrl",
        "PrimaryDatasheet",
        "datasheetUrl",
        "ProductUrl",
        default="",
    )
    if isinstance(datasheet, dict):
        datasheet = datasheet.get("Url") or datasheet.get("Value") or ""
    datasheet = str(datasheet or "").strip()
    if not datasheet.startswith("http"):
        prod_url = _dig(product, "ProductUrl", "productUrl", default="")
        datasheet = str(prod_url or "").strip()
    if not datasheet.startswith("http"):
        return None, mfr, "missing_datasheet_url"

    package = _dig(
        product,
        "PackageType",
        "Packaging.Value",
        "Package.Name",
        default="",
    )
    if isinstance(package, dict):
        package = package.get("Name") or package.get("Value") or ""

    desc = _dig(
        product,
        "Description.ProductDescription",
        "Description.DetailedDescription",
        "ProductDescription",
        default="",
    )
    if isinstance(desc, dict):
        desc = desc.get("ProductDescription") or desc.get("Value") or ""

    attrs = map_parameters(product, synonyms)
    profile = profiles.get(sub_category_slug) or profiles.get("_default") or {}
    required = profile.get("required") or []
    for req in required:
        if req not in attrs or attrs[req] in (None, ""):
            return None, mfr, f"missing_required_attr:{req}"

    status = "active"
    life = str(_dig(product, "ProductStatus.Status", "Status", default="") or "").lower()
    if "obsolete" in life or "end of life" in life:
        status = "obsolete"
    elif "nrnd" in life or "not recommended" in life:
        status = "nrnd"

    component = {
        "part_number": str(mpn).strip(),
        "manufacturer": mfr["name"],
        "manufacturer_id": mfr["id"],
        "product_class": product_class,
        "category": category,
        "category_slug": category_slug,
        "sub_category": sub_category,
        "sub_category_slug": sub_category_slug,
        "package": str(package or "").strip() or "—",
        "datasheet_url": datasheet,
        "description": str(desc or "").strip(),
        "status": status,
        "attributes": attrs,
        "tags": [sub_category_slug, "digikey-import"],
        "updated_at": date.today().isoformat(),
    }
    return component, mfr, None


def load_synonyms() -> dict:
    return load_json(COLLECTORS / "param_synonyms.json")


def load_profiles() -> dict:
    path = ROOT / "schema" / "attribute-profiles.json"
    if path.exists():
        return load_json(path)
    return {}
