import pandas as pd
from pathlib import Path
# Points to the data/ folder, regardless of where this script is run from
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
def load_raw():
 """Load all five raw CSVs into a dict of DataFrames."""
 # Read each CSV into a pandas table (DataFrame)
 customers = pd.read_csv(DATA_DIR / "customers.csv")
 products = pd.read_csv(DATA_DIR / "products.csv")
 # parse_dates converts the timestamp column from text into a real date/time
 transactions = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["timestamp"])
 events = pd.read_csv(DATA_DIR / "events.csv")
 campaigns = pd.read_csv(DATA_DIR / "campaigns.csv")
 # Return everything as a dictionary so you can grab any table by name
 return {
 "customers": customers,
 "products": products,
 "transactions": transactions,
 "events": events,
 "campaigns": campaigns,
 }
def get_merged_transactions():
 """Merge transactions with product info on product_id."""
 data = load_raw()
 # "merge" is like a VLOOKUP/SQL JOIN: attach product info (category,
 # brand, price) onto each transaction row, matching on product_id
 merged = data["transactions"].merge(
 data["products"], on="product_id", how="left"
 )
 return merged
def get_merged_with_customers():
 """Merge transactions+products with customer info too."""
 merged = get_merged_transactions()
 data = load_raw()
 # Same idea again, this time attaching customer info too
 merged = merged.merge(data["customers"], on="customer_id", how="left")
 return merged
# This block only runs when you execute this file directly
# (python -m src.load_data) -- it won't run when other files import it
if __name__ == "__main__":
 merged = get_merged_transactions()
 print(f"Merged shape: {merged.shape}") # (rows, columns) -- sanity check
 print(merged.head()) # show first 5 rows