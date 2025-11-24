import os
import pandas as pd
from datetime import date
from rapidfuzz import process, fuzz

from modules.aldi_scraper import scrape_aldi
from modules.safeway_scraper import scrape_safeway
from modules.giant_scraper import scrape_giant
from modules.walmart_scraper import scrape_walmart

DATA_DIR = "datasets"

os.makedirs(DATA_DIR, exist_ok=True)

# --------------------------------------------
# Save helpers
# --------------------------------------------

def save_csv(df, name):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    df.to_csv(path, index=False)
    return path

def load_store_csv(name):
    path = os.path.join(DATA_DIR, f"{name}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

# --------------------------------------------
# Run all scrapers
# --------------------------------------------

def run_all_scrapers(zip_code, items):
    save_csv(scrape_aldi(zip_code, items), "aldi_prices")
    save_csv(scrape_safeway(zip_code, items), "safeway_prices")
    save_csv(scrape_giant(zip_code, items), "giant_prices")
    save_csv(scrape_walmart(zip_code, items), "walmart_prices")

# --------------------------------------------
# Combine datasets with fuzzy match
# --------------------------------------------

def combine_all_store_data(threshold=80):
    stores = {
        "Aldi": load_store_csv("aldi_prices"),
        "Safeway": load_store_csv("safeway_prices"),
        "Giant": load_store_csv("giant_prices"),
        "Walmart": load_store_csv("walmart_prices"),
    }

    # Normalize items
    for s in stores:
        df = stores[s]
        if not df.empty:
            df["Item_norm"] = df["Item"].str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True)

    # Base store (Aldi as reference)
    base = stores["Aldi"].copy()
    result = pd.DataFrame()
    result["Item"] = base["Item"]
    result["Item_norm"] = base["Item_norm"]

    # For each other store, fuzzy match
    for store_name, df in stores.items():
        prices = []
        for item in result["Item_norm"]:
            if df.empty:
                prices.append(None)
                continue

            choices = df["Item_norm"].tolist()
            match = process.extractOne(item, choices, scorer=fuzz.token_sort_ratio)

            if match and match[1] >= threshold:
                matched_item = match[0]
                price = df[df["Item_norm"] == matched_item]["Price"].iloc[0]
                prices.append(price)
            else:
                prices.append(None)

        result[f"{store_name} Price"] = prices

    # Determine cheapest
    cheapest_store = []
    cheapest_price = []

    for idx, row in result.iterrows():
        prices = {
            store: row[f"{store} Price"]
            for store in stores
            if not pd.isna(row[f"{store} Price"])
        }

        if prices:
            best = min(prices, key=prices.get)
            cheapest_store.append(best)
            cheapest_price.append(prices[best])
        else:
            cheapest_store.append(None)
            cheapest_price.append(None)

    result["Cheapest Store"] = cheapest_store
    result["Cheapest Price"] = cheapest_price

    save_csv(result, "combined_prices")

    return result
