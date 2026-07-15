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

    # Resistance with SI prefix: 22mOhm, 10 kOhms, 4.7 MOhm, 4.7Ω
    # Prefix case matters: m = milli, M = mega; k/K = kilo.
    m_ohm = re.match(r"^([\d.]+)\s*([kKmM])\s*(ohms?|Ω)$", t, re.I)
    if m_ohm:
        base = float(m_ohm.group(1))
        pref_m = re.search(r"[\d.]+\s*([kKmM])", t)
        pref = pref_m.group(1) if pref_m else ""
        if pref in ("k", "K"):
            return base * 1000
        if pref == "M":
            return base * 1_000_000
        if pref == "m":
            return base * 0.001
    m_ohm_plain = re.match(r"^([\d.]+)\s*(ohms?|Ω)$", t, re.I)
    if m_ohm_plain:
        return float(m_ohm_plain.group(1))

    # capacitance: 100nF, 0.1uF, 100 nF
    m3 = re.match(r"^([\d.]+)\s*(p|n|u|µ|m)?\s*F$", t, re.I)
    if m3:
        base = float(m3.group(1))
        pref = (m3.group(2) or "").lower()
        factor = {"p": 1e-6, "n": 1e-3, "u": 1.0, "µ": 1.0, "m": 1000.0, "": 1e6}
        return base * factor.get(pref, 1.0)

    # Current with milliamp: 160 mA → 0.16 (stored as amperes)
    m_ma = re.match(r"^([\d.]+)\s*mA$", t, re.I)
    if m_ma:
        return float(m_ma.group(1)) / 1000.0
    m_ua = re.match(r"^([\d.]+)\s*[uµ]A$", t, re.I)
    if m_ua:
        return float(m_ua.group(1)) / 1_000_000.0

    # 0.1W / 1% / 50V / 5A
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
    # Longer keys first so "current rating (amps)" beats "current rating"
    syn_fuzzy = sorted(syn.items(), key=lambda kv: len(kv[0]), reverse=True)
    for name, value in pairs.items():
        nl = name.lower().strip()
        key = syn.get(nl)
        if not key:
            for sk, sv in syn_fuzzy:
                # Avoid short names like "Type" matching "transistor type"
                if sk == nl:
                    key = sv
                    break
                if sk in nl and len(sk) >= 4:
                    key = sv
                    break
                if len(nl) >= 8 and nl in sk:
                    key = sv
                    break
        if not key or value in ("", "-", "n/a"):
            continue
        if key in attrs:
            continue
        attrs[key] = _parse_number(value)
    return attrs


def _text_blob(product: dict) -> str:
    parts: list[str] = []
    desc = _dig(
        product,
        "Description.ProductDescription",
        "Description.DetailedDescription",
        "ProductDescription",
        default="",
    )
    if isinstance(desc, dict):
        desc = desc.get("ProductDescription") or desc.get("Value") or ""
    if desc:
        parts.append(str(desc))
    for name, value in _param_pairs(product).items():
        parts.append(f"{name} {value}")
    cat = _dig(product, "Category.Name", "Category.Value", default="")
    if cat:
        parts.append(str(cat))
    return " ".join(parts).lower()


def enrich_required_attrs(
    attrs: dict,
    product: dict,
    sub_category_slug: str,
) -> dict:
    """Fill hard-required attributes DigiKey often names differently."""
    out = dict(attrs)
    blob = _text_blob(product)
    pairs = {k.lower(): v for k, v in _param_pairs(product).items()}

    if sub_category_slug == "fuses":
        if "current_rating_a" not in out:
            for src in ("current_a",):
                if src in out:
                    out["current_rating_a"] = out[src]
                    break
        if "current_rating_a" not in out:
            # Traditional fuse: Current Rating; PTC: Current - Hold (Ih)
            preferred = (
                "current rating",
                "current - hold",
                "current hold",
                "hold (ih)",
                "current - trip",
            )
            for pname, pval in pairs.items():
                pl = pname.lower()
                if any(tok in pl for tok in preferred) or (
                    "current" in pl and "rating" in pl
                ):
                    out["current_rating_a"] = _parse_number(pval)
                    break
        if "voltage_rating_v" not in out:
            for pname, pval in pairs.items():
                pl = pname.lower()
                if ("voltage" in pl and "rating" in pl) or pl in (
                    "voltage - max",
                    "voltage max",
                ):
                    out["voltage_rating_v"] = _parse_number(pval)
                    break
        if "fuse_type" not in out:
            for pname, pval in pairs.items():
                if pname in ("type", "fuse type"):
                    out["fuse_type"] = str(pval).strip()
                    break
            if "fuse_type" not in out and ("ptc" in blob or "polymeric" in blob):
                out["fuse_type"] = "PTC Resettable"

    if sub_category_slug == "discrete-transistors":
        if "transistor_type" not in out:
            for pname, pval in pairs.items():
                pl = pname.lower()
                if "fet type" in pl or "mosfet" in pl or "transistor type" in pl:
                    val = str(pval).strip()
                    if "mosfet" in pl or "fet" in pl:
                        out["transistor_type"] = (
                            f"MOSFET ({val})" if val and "mosfet" not in val.lower() else val
                        )
                    else:
                        out["transistor_type"] = val
                    break
        if "transistor_type" not in out:
            if "mosfet" in blob or "fet type" in blob:
                pol = ""
                for token in ("n-channel", "p-channel", "n channel", "p channel"):
                    if token in blob:
                        pol = token.replace(" ", "-").title()
                        break
                out["transistor_type"] = f"MOSFET {pol}".strip() if pol else "MOSFET"
            elif "bjt" in blob or "bipolar" in blob or "npn" in blob or "pnp" in blob:
                if "npn" in blob:
                    out["transistor_type"] = "BJT NPN"
                elif "pnp" in blob:
                    out["transistor_type"] = "BJT PNP"
                else:
                    out["transistor_type"] = "BJT"
            elif "igbt" in blob:
                out["transistor_type"] = "IGBT"
        if "polarity" not in out:
            for token, label in (
                ("n-channel", "N-Channel"),
                ("p-channel", "P-Channel"),
                ("npn", "NPN"),
                ("pnp", "PNP"),
            ):
                if token in blob:
                    out["polarity"] = label
                    break

    if sub_category_slug == "discrete-diodes-rectifiers":
        if "diode_type" not in out:
            for pname, pval in pairs.items():
                pl = pname.lower()
                if "diode" in pl or pl in ("technology", "type"):
                    out["diode_type"] = str(pval).strip()
                    break
        if "diode_type" not in out:
            for label in (
                "schottky",
                "zener",
                "tvs",
                "rectifier",
                "switching",
                "fast recovery",
            ):
                if label in blob:
                    out["diode_type"] = label.title()
                    break
            if "diode_type" not in out and "diode" in blob:
                out["diode_type"] = "Diode"

    return out


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
    attrs = enrich_required_attrs(attrs, product, sub_category_slug)
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
