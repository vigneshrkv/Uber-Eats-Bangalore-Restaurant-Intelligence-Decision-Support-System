import pandas as pd
import sqlite3
import json
import os

DB_FILE      = "food_data.db"
CSV_FILE     = "CLEANED1.csv"
ORDERS_FILE  = "orders.json"

# ── Check files exist ────────────────────────────────────────────────────────
for f in [CSV_FILE, ORDERS_FILE]:
    if not os.path.exists(f):
        print(f"ERROR: {f} not found. Place it in the same folder as this script.")
        exit(1)

conn = sqlite3.connect(DB_FILE)

# ── Load restaurants ─────────────────────────────────────────────────────────
print("Loading CLEANED1.csv ...")
df = pd.read_csv(CSV_FILE)

# Rename columns with brackets so SQL works cleanly
df.rename(columns={
    "listed_in(type)": "listed_type",
    "listed_in(city)": "listed_city",
}, inplace=True)

df.to_sql("restaurants", conn, if_exists="replace", index=False)
print(f"  restaurants table: {len(df):,} rows loaded")

# ── Load orders ──────────────────────────────────────────────────────────────
print("Loading orders.json ...")
with open(ORDERS_FILE) as f:
    orders = json.load(f)

odf = pd.DataFrame(orders)

# Convert Yes/No → 1/0 so SQL CASE WHEN discount_used=1 works
odf["discount_used"] = odf["discount_used"].map({"Yes": 1, "No": 0})

odf.to_sql("orders", conn, if_exists="replace", index=False)
print(f"  orders table: {len(odf):,} rows loaded")

conn.commit()
conn.close()
print(f"\nDone. Database saved as: {DB_FILE}")
print("Now run:  streamlit run app.py")