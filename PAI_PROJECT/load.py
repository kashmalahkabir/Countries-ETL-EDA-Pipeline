"""LOAD: write the clean data into a SQLite database."""
import logging
import sqlite3

import pandas as pd

DB_PATH = "countries.db"
log = logging.getLogger(__name__)


def load(df: pd.DataFrame) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("countries", conn, if_exists="replace", index=False)
        count = conn.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    log.info("Saved %d rows to table 'countries' in %s", count, DB_PATH)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from transform import transform
    load(transform())
