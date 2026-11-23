"""EDA: SQL queries, IQR outlier flags, charts and a summary table."""
import logging
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # save charts to files, no window needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DB_PATH = "countries.db"
OUT = Path("outputs")
log = logging.getLogger(__name__)


def query(conn, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)


def iqr_flag(s: pd.Series) -> pd.Series:
    """True where a value is outside Q1 - 1.5*IQR ... Q3 + 1.5*IQR."""
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)


def eda() -> None:
    OUT.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # ---------- SQL queries ----------
    top10 = query(conn, """
        SELECT name, population FROM countries
        ORDER BY population DESC LIMIT 10""")

    regions = query(conn, """
        SELECT region,
               COUNT(*)                   AS countries,
               SUM(population)            AS total_population,
               ROUND(AVG(density), 1)     AS avg_density
        FROM countries GROUP BY region ORDER BY total_population DESC""")

    most_crowded = query(conn, """
        SELECT name, region, ROUND(density, 1) AS density FROM countries
        ORDER BY density DESC LIMIT 10""")

    least_crowded = query(conn, """
        SELECT name, region, ROUND(density, 2) AS density FROM countries
        ORDER BY density ASC LIMIT 10""")

    df = query(conn, "SELECT * FROM countries")

    # ---------- IQR outliers: flag, never delete ----------
    df["population_outlier"] = iqr_flag(df["population"])
    df["area_outlier"] = iqr_flag(df["area"])
    df.to_sql("countries_flagged", conn, if_exists="replace", index=False)
    conn.close()

    outliers = df[df["population_outlier"] | df["area_outlier"]]
    outliers[["name", "region", "population", "area",
              "population_outlier", "area_outlier"]].to_csv(OUT / "outliers.csv", index=False)

    # ---------- Summary table ----------
    summary = df[["population", "area", "density"]].describe().round(2)
    summary.to_csv(OUT / "summary_table.csv")
    regions.to_csv(OUT / "region_comparison.csv", index=False)

    # ---------- Charts ----------
    # 1. Top 10 by population
    plt.figure(figsize=(9, 5))
    plt.barh(top10["name"][::-1], top10["population"][::-1] / 1e6, color="#4c72b0")
    plt.xlabel("Population (millions)"); plt.title("Top 10 countries by population")
    plt.tight_layout(); plt.savefig(OUT / "1_top10_population.png", dpi=150); plt.close()

    # 2. Region total population
    plt.figure(figsize=(8, 5))
    plt.bar(regions["region"], regions["total_population"] / 1e6, color="#55a868")
    plt.ylabel("Total population (millions)"); plt.title("Total population by region")
    plt.xticks(rotation=30); plt.tight_layout()
    plt.savefig(OUT / "2_region_population.png", dpi=150); plt.close()

    # 3. Region average density
    plt.figure(figsize=(8, 5))
    plt.bar(regions["region"], regions["avg_density"], color="#c44e52")
    plt.ylabel("Average density (people per km²)"); plt.title("Average density by region")
    plt.xticks(rotation=30); plt.tight_layout()
    plt.savefig(OUT / "3_region_density.png", dpi=150); plt.close()

    # 4. Most and least crowded
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].barh(most_crowded["name"][::-1], most_crowded["density"][::-1], color="#c44e52")
    axes[0].set_title("10 most crowded"); axes[0].set_xlabel("People per km²")
    axes[1].barh(least_crowded["name"][::-1], least_crowded["density"][::-1], color="#8172b2")
    axes[1].set_title("10 least crowded"); axes[1].set_xlabel("People per km²")
    plt.tight_layout(); plt.savefig(OUT / "4_crowded_countries.png", dpi=150); plt.close()

    # 5. Histogram (log10 because data is very skewed)
    plt.figure(figsize=(8, 5))
    plt.hist(np.log10(df["population"].clip(lower=1)), bins=25, color="#4c72b0", edgecolor="white")
    plt.xlabel("log10(population)"); plt.ylabel("Number of countries")
    plt.title("Distribution of country population (log scale)")
    plt.tight_layout(); plt.savefig(OUT / "5_histogram_population.png", dpi=150); plt.close()

    # 6. Box plots for population and area (log scale)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].boxplot(df["population"]); axes[0].set_yscale("log")
    axes[0].set_title("Population"); axes[0].set_xticks([])
    axes[1].boxplot(df["area"]); axes[1].set_yscale("log")
    axes[1].set_title("Area (km²)"); axes[1].set_xticks([])
    plt.tight_layout(); plt.savefig(OUT / "6_boxplots.png", dpi=150); plt.close()

    # ---------- Print results ----------
    print("\nTOP 10 BY POPULATION\n", top10)
    print("\nREGIONS\n", regions)
    print("\nMOST CROWDED\n", most_crowded)
    print("\nLEAST CROWDED\n", least_crowded)
    print("\nSUMMARY\n", summary)
    print(f"\nFlagged outliers: {len(outliers)} "
          f"(population: {df['population_outlier'].sum()}, area: {df['area_outlier'].sum()})")
    log.info("Charts and tables saved in %s/", OUT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    eda()
