#!/usr/bin/env python3
"""Minimal DigiKey Product Information V4 client (OAuth2 client_credentials)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COLLECTORS = Path(__file__).resolve().parent

ENDPOINTS = {
    "sandbox": {
        "token": "https://sandbox-api.digikey.com/v1/oauth2/token",
        "keyword": "https://sandbox-api.digikey.com/products/v4/search/keyword",
    },
    "production": {
        "token": "https://api.digikey.com/v1/oauth2/token",
        "keyword": "https://api.digikey.com/products/v4/search/keyword",
    },
}


def _load_dotenv() -> None:
    env_path = COLLECTORS / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


@dataclass
class DigiKeyConfig:
    client_id: str
    client_secret: str
    env: str = "sandbox"

    @classmethod
    def from_env(cls, env_override: str | None = None) -> "DigiKeyConfig":
        _load_dotenv()
        env = (env_override or os.environ.get("DIGIKEY_ENV") or "sandbox").lower()
        if env not in ENDPOINTS:
            raise ValueError("DIGIKEY_ENV must be 'sandbox' or 'production'")
        cid = os.environ.get("DIGIKEY_CLIENT_ID", "").strip()
        secret = os.environ.get("DIGIKEY_CLIENT_SECRET", "").strip()
        if not cid or not secret:
            raise RuntimeError(
                "Missing DIGIKEY_CLIENT_ID / DIGIKEY_CLIENT_SECRET. "
                "See docs/DIGIKEY_SETUP.md"
            )
        return cls(client_id=cid, client_secret=secret, env=env)


class DigiKeyClient:
    def __init__(self, config: DigiKeyConfig):
        self.config = config
        self._token: str | None = None
        self._token_exp: float = 0.0

    def _request(
        self,
        method: str,
        url: str,
        *,
        data: bytes | None = None,
        headers: dict | None = None,
        form: dict | None = None,
    ) -> Any:
        hdrs = {"Accept": "application/json", "User-Agent": "wec-digikey-collector/1.0"}
        if headers:
            hdrs.update(headers)
        body = data
        if form is not None:
            body = urllib.parse.urlencode(form).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} {url}: {err_body[:800]}") from e

    def get_token(self) -> str:
        now = time.time()
        if self._token and now < self._token_exp - 60:
            return self._token
        token_url = ENDPOINTS[self.config.env]["token"]
        payload = self._request(
            "POST",
            token_url,
            form={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "grant_type": "client_credentials",
            },
        )
        self._token = payload["access_token"]
        self._token_exp = now + int(payload.get("expires_in", 600))
        return self._token

    def keyword_search(
        self,
        keywords: str,
        *,
        record_count: int = 10,
        record_start: int = 0,
        locale_site: str = "US",
        locale_language: str = "en",
        locale_currency: str = "USD",
    ) -> dict:
        """POST KeywordSearch. Response shape may include Products or products."""
        url = ENDPOINTS[self.config.env]["keyword"]
        token = self.get_token()
        body = {
            "Keywords": keywords,
            "RecordCount": max(1, min(int(record_count), 50)),
            "RecordStartPosition": max(0, int(record_start)),
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "X-DIGIKEY-Client-Id": self.config.client_id,
            "X-DIGIKEY-Locale-Site": locale_site,
            "X-DIGIKEY-Locale-Language": locale_language,
            "X-DIGIKEY-Locale-Currency": locale_currency,
            "Content-Type": "application/json",
        }
        return self._request(
            "POST", url, data=json.dumps(body).encode("utf-8"), headers=headers
        )


def extract_products(response: dict) -> list[dict]:
    """Normalize various DigiKey response envelope keys."""
    if not response:
        return []
    for key in ("Products", "products", "ProductList", "productList"):
        val = response.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
    # Some envelopes nest under ProductSearch or similar
    for key, val in response.items():
        if isinstance(val, dict):
            nested = extract_products(val)
            if nested:
                return nested
    return []
