"""Run the whole pipeline: Extract -> Transform -> Load -> EDA."""
import logging

from eda import eda
from extract import extract
from load import load
from transform import transform

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
    extract()
    load(transform())
    eda()
