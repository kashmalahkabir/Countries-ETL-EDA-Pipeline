"""TRANSFORM: clean with pandas, validate each record with Pydantic."""
import json
import logging
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, field_validator

RAW_PATH = Path("data/raw/countries_raw.json")
LOG_PATH = Path("data/rejected_records.log")

log = logging.getLogger(__name__)


class Country(BaseModel):
    """Rules every clean record must follow."""
    name: str = Field(min_length=1)
    cca3: str = Field(min_length=3, max_length=3)
    capital: str = "Unknown"          # missing capital is simply filled in
    region: str = Field(min_length=1)
    subregion: str = "Unknown"
    population: float = Field(gt=0)   # must be positive
    area: float = Field(gt=0)         # must be positive
    density: float

    @field_validator("name", "region")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v.strip()


def flatten(record: dict) -> dict:
    """Turn the nested v5 API record into one flat row."""
    capitals = record.get("capitals") or []          # list of objects (can be empty)
    first = capitals[0] if capitals else None
    capital = first.get("name") if isinstance(first, dict) else first
    return {
        "name": (record.get("names") or {}).get("common", ""),
        "cca3": (record.get("codes") or {}).get("alpha_3", ""),
        "capital": capital,
        "region": record.get("region", ""),
        "subregion": record.get("subregion") or None,
        "population": record.get("population"),
        "area": (record.get("area") or {}).get("kilometers"),
    }


def transform() -> pd.DataFrame:
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    df = pd.DataFrame([flatten(r) for r in raw])
    log.info("Loaded %d raw rows", len(df))

    # --- pandas cleaning ---
    df = df.drop_duplicates(subset="cca3")
    df["capital"] = df["capital"].fillna("Unknown")
    df["subregion"] = df["subregion"].fillna("Unknown")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["area"] = pd.to_numeric(df["area"], errors="coerce")

    # density = population / area (only where area is positive, otherwise NaN)
    df["density"] = df["population"] / df["area"].where(df["area"] > 0)

    # --- Pydantic validation, record by record ---
    good, rejected = [], []
    for row in df.to_dict(orient="records"):
        row = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        if row["area"] is None or row["area"] <= 0:
            log.warning("Zero/missing area: %s", row["name"])
        try:
            good.append(Country(**row).model_dump())
        except ValidationError as e:
            rejected.append(f"{row['name']}: {e.errors()[0]['loc']} {e.errors()[0]['msg']}")

    LOG_PATH.write_text("\n".join(rejected), encoding="utf-8")
    log.info("Valid: %d | Rejected: %d (see %s)", len(good), len(rejected), LOG_PATH)

    clean = pd.DataFrame(good)
    clean["population"] = clean["population"].astype("int64")
    return clean.sort_values("name").reset_index(drop=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    print(transform().head())
