import streamlit as st
import pandas as pd
import os

from modules.scraper_utils import (
    run_all_scrapers,
    load_store_csv,
    combine_all_store_data
)

st.set_page_config(page_title="Grocery Price Comparator", layout="wide")

st.title("🛒 Grocery Price Comparison App")
st.write("Scrape local grocery prices, compare stores, and find the cheapest shopping cart.")

# --- ZIP Code Input ---
zip_code = st.text_input("Enter ZIP Code:", value="22030")

items_raw = st.text_area(
    "Enter items to search (one per line):",
    value="milk\neggs\nbread\nbanana",
    height=150
)

items = [i.strip() for i in items_raw.split("\n") if i.strip()]

# --- RUN SCRAPERS ---
if st.button("Run Scrapers for All Stores"):
    st.write("Running scrapers... please wait.")
    run_all_scrapers(zip_code, items)
    st.success("Scraping complete! CSVs saved to /datasets")

# --- View Individual Store Data ---
st.header("Store Datasets")
store_files = ["aldi_prices.csv", "safeway_prices.csv", "giant_prices.csv", "walmart_prices.csv"]

for fn in store_files:
    path = os.path.join("datasets", fn)
    if os.path.exists(path):
        st.subheader(fn.replace("_", " ").replace(".csv", "").title())
        st.dataframe(pd.read_csv(path))

# --- Combine datasets ---
if st.button("Combine All Store Data"):
    combined = combine_all_store_data()
    st.dataframe(combined)

    st.subheader("Download Combined CSV")
    st.download_button(
        "Download CSV",
        combined.to_csv(index=False),
        file_name="combined_prices.csv"
    )

# --- Shopping Cart Calculator ---
st.header("Shopping Cart Optimizer")

cart_raw = st.text_area(
    "Enter cart items (one per line):",
    value="milk\neggs\nbread"
)

if st.button("Calculate Cheapest Store for Cart"):
    cart_items = [c.strip() for c in cart_raw.split("\n") if c.strip()]
    combined_path = "datasets/combined_prices.csv"

    if not os.path.exists(combined_path):
        st.error("You need to run 'Combine All Store Data' first.")
    else:
        df = pd.read_csv(combined_path)
        results = {}

        for store in ["Aldi", "Safeway", "Giant", "Walmart"]:
            col = f"{store} Price"
            total = 0
            missing = 0
            for item in cart_items:
                row = df[df["Item_norm"].str.contains(item.lower(), na=False)]
                if not row.empty and not pd.isna(row[col].iloc[0]):
                    total += float(row[col].iloc[0])
                else:
                    missing += 1
            results[store] = {"total": total, "missing": missing}

        st.write("### Cart Price Summary")
        st.json(results)

        cheapest_store = min(results, key=lambda x: results[x]["total"])
        st.success(f"🏆 Cheapest store for your cart: **{cheapest_store}**")
