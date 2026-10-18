"""Polygon API client — handles signing, file uploads, and rate limiting."""

import hashlib
import random
import string
import sys
import time

import requests

BASE_URL = "https://polygon.codeforces.com/api"
MAX_RETRIES = 6


def _make_signature(method: str, params: dict, secret: str) -> str:
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    sig_bytes = rand.encode() + b"/" + method.encode() + b"?"
    sig_bytes += b"&".join(
        k.encode() + b"=" + (v if isinstance(v, bytes) else v.encode())
        for k, v in sorted(params.items())
    )
    sig_bytes += b"#" + secret.encode()
    return rand + hashlib.sha512(sig_bytes).hexdigest()


class PolygonAPI:
    def __init__(self, api_key: str, api_secret: str, delay: float = 0.3):
        self.api_key = api_key
        self.api_secret = api_secret
        self.delay = delay

    def _post(self, method: str, kwargs: dict) -> requests.Response:
        params = {k: v for k, v in kwargs.items() if v is not None and k != "_files"}
        params["apiKey"] = self.api_key
        params["time"] = str(int(time.time()))

        files = kwargs.get("_files")
        if files:
            # ponytail: file bytes must be in signature — Polygon verifies them
            for field_name, (_, content) in files.items():
                params[field_name] = content
            params["apiSig"] = _make_signature(method, params, self.api_secret)
            del params["file"]
            return requests.post(f"{BASE_URL}/{method}", data=params, files=files)
        params["apiSig"] = _make_signature(method, params, self.api_secret)
        return requests.post(f"{BASE_URL}/{method}", data=params)

    def call(self, method: str, fatal: bool = True, **kwargs):
        # Polygon throttles bursts with HTTP 429 and an HTML body; back off and re-sign.
        for attempt in range(MAX_RETRIES):
            resp = self._post(method, kwargs)
            if resp.status_code != 429 or attempt == MAX_RETRIES - 1:
                break
            time.sleep(2 ** attempt)

        try:
            data = resp.json()
        except Exception:
            if not fatal:
                return None
            print(f"  API error [{method}]: non-JSON response (HTTP {resp.status_code})", file=sys.stderr)
            sys.exit(1)
        if data.get("status") != "OK":
            msg = data.get("comment", data)
            print(f"  API error [{method}]: {msg}", file=sys.stderr)
            if not fatal:
                return None
            sys.exit(1)

        time.sleep(self.delay)
        if "result" not in data:
            return True
        return data.get("result")
