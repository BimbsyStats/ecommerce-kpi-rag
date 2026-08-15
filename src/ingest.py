"""
Builds data/documents.json from the raw CSVs.

This is the script-form of Notebooks 01 + 02's data prep, so the Streamlit app (or a Docker
container) can rebuild the document store without needing to run notebooks. Run it directly:

    python -m src.ingest
"""
import json
import os

import pandas as pd

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_raw():
    customers = pd.read_csv(os.path.join(_DATA_DIR, "customers.csv"))
    products = pd.read_csv(os.path.join(_DATA_DIR, "products.csv"))
    transactions = pd.read_csv(os.path.join(_DATA_DIR, "transactions.csv"), parse_dates=["timestamp"])
    campaigns = pd.read_csv(os.path.join(_DATA_DIR, "campaigns.csv"))
    return customers, products, transactions, campaigns


def build_merged(customers, products, transactions):
    df = transactions.merge(products, on="product_id", how="left")
    df = df.merge(customers, on="customer_id", how="left", suffixes=("", "_customer"))
    # Exclude rows missing product_id / gross_revenue in the raw source data (~10.1% of rows,
    # see Notebook 01 for the investigation confirming this is a source data issue, not a join bug)
    df = df.dropna(subset=["gross_revenue"])
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    return df


def build_documents(df, campaigns):
    documents = []
    doc_id = 0

    def add_doc(text, doc_type, **meta):
        nonlocal doc_id
        documents.append({"id": doc_id, "type": doc_type, "text": text, **meta})
        doc_id += 1

    for cat, g in df.groupby("category"):
        add_doc(
            f"Category: {cat}. Total revenue: ${g['gross_revenue'].sum():,.2f}. "
            f"Orders: {len(g):,}. Average order value: ${g['gross_revenue'].mean():,.2f}. "
            f"Refund rate: {g['refund_flag'].mean():.2%}.",
            doc_type="category", category=cat,
        )

    for country, g in df.groupby("country"):
        add_doc(
            f"Country: {country}. Total revenue: ${g['gross_revenue'].sum():,.2f}. "
            f"Orders: {len(g):,}. Average order value: ${g['gross_revenue'].mean():,.2f}. "
            f"Unique customers: {g['customer_id'].nunique():,}.",
            doc_type="country", country=country,
        )

    for tier, g in df.groupby("loyalty_tier"):
        add_doc(
            f"Loyalty tier: {tier}. Total revenue: ${g['gross_revenue'].sum():,.2f}. "
            f"Orders: {len(g):,}. Average order value: ${g['gross_revenue'].mean():,.2f}.",
            doc_type="loyalty_tier", loyalty_tier=tier,
        )

    for month, g in df.groupby("month"):
        add_doc(
            f"Month: {month}. Total revenue: ${g['gross_revenue'].sum():,.2f}. Orders: {len(g):,}.",
            doc_type="month", month=month,
        )

    df_campaigns = df[df["campaign_id"] > 0].merge(campaigns, on="campaign_id", how="left")
    for channel, g in df_campaigns.groupby("channel"):
        add_doc(
            f"Marketing channel: {channel}. Revenue attributed: ${g['gross_revenue'].sum():,.2f}. "
            f"Orders: {len(g):,}.",
            doc_type="channel", channel=channel,
        )

    add_doc(
        f"Overall summary: Total revenue across all orders is ${df['gross_revenue'].sum():,.2f} "
        f"from {len(df):,} orders. Average order value is ${df['gross_revenue'].mean():,.2f}. "
        f"Refund rate is {df['refund_flag'].mean():.2%}.",
        doc_type="overall",
    )

    return documents


def main():
    customers, products, transactions, campaigns = load_raw()
    df = build_merged(customers, products, transactions)
    df.to_csv(os.path.join(_DATA_DIR, "merged_transactions.csv"), index=False)

    documents = build_documents(df, campaigns)
    with open(os.path.join(_DATA_DIR, "documents.json"), "w") as f:
        json.dump(documents, f, indent=2)

    print(f"Built {len(documents)} documents -> data/documents.json")


if __name__ == "__main__":
    main()
