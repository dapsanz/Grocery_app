import requests
import pandas as pd
from datetime import date

def scrape_walmart(zip_code, items):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    results = []

    for item in items:
        url = f"https://www.walmart.com/search/api/query?query={item}"

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            r = resp.json()   # may throw JSONDecodeError
        except Exception:
            continue  # skip bad response

        products = r.get("items", [])
        if not products:
            continue

        for prod in products:
            name = prod.get("title")
            offer = prod.get("primaryOffer", {}) or {}
            price = offer.get("offerPrice") or offer.get("price")

            if price is None:
                continue

            results.append({
                "Store": "Walmart",
                "Item": name,
                "Price": float(price),
                "Zip": zip_code,
                "Date": date.today()
            })

    return pd.DataFrame(results)
