"""StickerByVIN window sticker API client. Docs and free key: https://stickerbyvin.com/developers"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

__version__ = "0.1.0"
__all__ = ["StickerByVIN", "StickerByVINError"]

BASE_URL = "https://stickerbyvin.com/api/v1"


class StickerByVINError(Exception):
    """An API error. `code` is one of missing_key, invalid_key, key_disabled, plan_required, invalid_vin,
    unknown_vin, sticker_not_available, rate_limited, quota_exceeded, upstream_unavailable, internal."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


class StickerByVIN:
    """Client for https://stickerbyvin.com/api/v1. Reads the key from SBV_KEY when api_key is not given."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL, timeout: float = 30.0):
        self.api_key = api_key or os.environ.get("SBV_KEY") or os.environ.get("STICKERBYVIN_API_KEY")
        if not self.api_key:
            raise ValueError("No API key. Pass api_key= or set SBV_KEY. Free key: https://stickerbyvin.com/developers")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        #: calls left this month, from the last response's X-Quota-Remaining header
        self.quota_remaining: Optional[int] = None

    def _get(self, endpoint: str, vin: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}?" + urllib.parse.urlencode({"vin": vin.strip().upper()})
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": f"stickerbyvin-python/{__version__}",
        })
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                self._quota(r.headers)
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            self._quota(e.headers)
            try:
                err = json.loads(e.read().decode("utf-8")).get("error", {})
            except Exception:
                err = {}
            raise StickerByVINError(e.code, err.get("code", "http_error"), err.get("message", str(e))) from None

    def _quota(self, headers: Any) -> None:
        q = headers.get("x-quota-remaining") if headers else None
        if q is not None and str(q).isdigit():
            self.quota_remaining = int(q)

    def availability(self, vin: str) -> Dict[str, Any]:
        """Decode + whether the original window sticker is on file. All plans, 1 call."""
        return self._get("availability", vin)

    def decode(self, vin: str) -> Dict[str, Any]:
        """Year, make, model, trim, engine, drivetrain, plant. All plans, 1 call."""
        return self._get("decode", vin)

    def sticker(self, vin: str) -> Dict[str, Any]:
        """The original window sticker as JSON (MSRP, options with prices, paint code) + a 1-hour PDF link.
        Starter plan and above, 1 call. Raises StickerByVINError(code='sticker_not_available') when none is on file."""
        return self._get("sticker", vin)

    def sticker_pdf(self, vin: str, path: str) -> str:
        """Fetch the sticker and save the original PDF to `path`. Returns the path. 1 call."""
        url = self.sticker(vin)["pdf"]["url"]
        req = urllib.request.Request(url, headers={"User-Agent": f"stickerbyvin-python/{__version__}"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r, open(path, "wb") as f:
            f.write(r.read())
        return path
