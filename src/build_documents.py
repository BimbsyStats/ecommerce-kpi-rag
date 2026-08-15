import json
from pathlib import Path
from src.load_data import get_merged_transactions, load_raw

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def build_category_documents(merged):
    """One document per product category: revenue, orders, avg order value."""
    docs = []
    grouped = merged.groupby("category").agg(
        total_revenue=("gross_revenue", "sum"),
        total_orders=("transaction_id", "count"),
        avg_order_value=("gross_revenue", "mean"),
    ).reset_index()
    for i, row in grouped.iterrows():
        text = (
            f"Category: {row['category']}. "
            f"Total revenue: {row['total_revenue']:.2f}. "
            f"Total orders: {int(row['total_orders'])}. "
            f"Average order value: {row['avg_order_value']:.2f}."
        )
        docs.append({"id": f"category-{i}", "type": "category_revenue", "text": text})
    return docs


def build_monthly_documents(merged):
    """One document per month: revenue and order count trend."""
    docs = []
    merged["month"] = merged["timestamp"].dt.to_period("M").astype(str)
    grouped = merged.groupby("month").agg(
        total_revenue=("gross_revenue", "sum"),
        total_orders=("transaction_id", "count"),
    ).reset_index()
    for i, row in grouped.iterrows():
        text = (
            f"Month: {row['month']}. "
            f"Total revenue: {row['total_revenue']:.2f}. "
            f"Total orders: {int(row['total_orders'])}."
        )
        docs.append({"id": f"month-{i}", "type": "monthly_revenue", "text": text})
    return docs


def build_brand_documents(merged):
    """One document per brand: revenue and order count."""
    docs = []
    grouped = merged.groupby("brand").agg(
        total_revenue=("gross_revenue", "sum"),
        total_orders=("transaction_id", "count"),
    ).reset_index()
    for i, row in grouped.iterrows():
        text = (
            f"Brand: {row['brand']}. "
            f"Total revenue: {row['total_revenue']:.2f}. "
            f"Total orders: {int(row['total_orders'])}."
        )
        docs.append({"id": f"brand-{i}", "type": "brand_revenue", "text": text})
    return docs


def build_campaign_documents(merged, campaigns):
    """One document per campaign: revenue attributed to it."""
    docs = []
    merged_c = merged.merge(campaigns, on="campaign_id", how="left")
    grouped = merged_c.groupby("campaign_id").agg(
        total_revenue=("gross_revenue", "sum"),
        total_orders=("transaction_id", "count"),
    ).reset_index()
    for i, row in grouped.iterrows():
        text = (
            f"Campaign ID: {row['campaign_id']}. "
            f"Total revenue generated: {row['total_revenue']:.2f}. "
            f"Total orders: {int(row['total_orders'])}."
        )
        docs.append({"id": f"campaign-{i}", "type": "campaign_revenue", "text": text})
    return docs


def build_summary_document(merged):
    """One overall summary document."""
    total_revenue = merged["gross_revenue"].sum()
    total_orders = merged["transaction_id"].nunique()
    refund_rate = merged["refund_flag"].mean() * 100
    text = (
        f"Overall summary: Total revenue across all transactions is "
        f"{total_revenue:.2f}. Total orders: {total_orders}. "
        f"Refund rate: {refund_rate:.2f} percent."
    )
    return [{"id": "summary-0", "type": "overall_summary", "text": text}]


def build_all_documents():
    merged = get_merged_transactions()
    raw = load_raw()
    documents = []
    documents += build_summary_document(merged)
    documents += build_category_documents(merged)
    documents += build_monthly_documents(merged)
    documents += build_brand_documents(merged)
    documents += build_campaign_documents(merged, raw["campaigns"])
    return documents


if __name__ == "__main__":
    docs = build_all_documents()
    print(f"Built {len(docs)} documents")
    out_path = DATA_DIR / "documents.json"
    with open(out_path, "w") as f:
        json.dump(docs, f, indent=2)
    print(f"Saved to {out_path}")


