
"""Automated ingestion pipeline.

Run with:
    python -m src.ingest

Takes raw CSVs in data/ and produces data/documents.json, ready for
the retrieval layer. This is the single entry point a reviewer (or a
scheduled job) would run to (re)build the knowledge base from scratch.
"""

import sys
import time
import json
from pathlib import Path

from src.load_data import load_raw
from src.build_documents import build_all_documents

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def validate_raw_data():
    """Basic sanity checks before we trust the data."""

    data = load_raw()

    required = {
        "customers": ["customer_id"],
        "products": ["product_id", "category", "brand"],
        "transactions": [
            "transaction_id",
            "product_id",
            "customer_id",
            "gross_revenue",
        ],
        "campaigns": ["campaign_id"],
    }

    for name, cols in required.items():
        df = data[name]

        missing = [c for c in cols if c not in df.columns]

        if missing:
            raise ValueError(
                f"{name}.csv is missing required columns: {missing}"
            )

        if df.empty:
            raise ValueError(f"{name}.csv loaded but is empty")

    print("Validation passed: all required files and columns present.")
    return data


def run_ingestion():
    start = time.time()

    print("Starting ingestion pipeline...")

    validate_raw_data()

    documents = build_all_documents()

    out_path = DATA_DIR / "documents.json"

    with open(out_path, "w") as f:
        json.dump(documents, f, indent=2)

    elapsed = time.time() - start

    print(
        f"Ingestion complete: {len(documents)} documents written to {out_path}"
    )
    print(f"Elapsed: {elapsed:.2f}s")

    return documents


if __name__ == "__main__":
    try:
        run_ingestion()
    except Exception as e:
        print(f"Ingestion failed: {e}", file=sys.stderr)
        sys.exit(1)
