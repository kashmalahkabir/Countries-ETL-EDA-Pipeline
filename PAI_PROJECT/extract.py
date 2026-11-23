"""EXTRACT: download country data from the REST Countries API (v5) and save it raw.

v5 needs a FREE API key (sign up at https://restcountries.com/sign-up).
Put the key in a file called api_key.txt (one line) next to this script,
or set the environment variable RESTCOUNTRIES_API_KEY.
"""
import json
import logging
import os
from pathlib import Path

import requests

URL = "https://api.restcountries.com/countries/v5"
FIELDS = "names.common,codes.alpha_3,capitals,region,subregion,area.kilometers,population"
PAGE_SIZE = 100                      # maximum allowed on the free plan
RAW_PATH = Path("data/raw/countries_raw.json")
KEY_FILE = Path("api_key.txt")

log = logging.getLogger(__name__)


def get_api_key() -> str:
    key = os.environ.get("RESTCOUNTRIES_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        raise SystemExit(
            "No API key found. Sign up free at https://restcountries.com/sign-up, "
            "then paste your key into a file named api_key.txt in this folder."
        )
    return key


def extract() -> list[dict]:
    """Request all countries page by page (100 per page) and save them unchanged."""
    headers = {"Authorization": f"Bearer {get_api_key()}"}
    records, offset = [], 0

    while True:
        params = {"response_fields": FIELDS, "limit": PAGE_SIZE, "offset": offset}
        log.info("Requesting %s (offset %d)", URL, offset)
        response = requests.get(URL, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            try:
                message = response.json()["errors"][0]["message"]
            except Exception:
                message = response.text[:200]
            raise SystemExit(f"API error {response.status_code}: {message}")

        data = response.json()["data"]
        records.extend(data["objects"])
        if not data["meta"]["more"]:
            break
        offset += PAGE_SIZE

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Saved %d raw records to %s", len(records), RAW_PATH)
    return records


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    extract()
