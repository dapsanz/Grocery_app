import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date

def scrape_aldi(zip_code, items):
    url = f"https://www.aldi.us/en/weekly-specials/our-weekly-ads/?zip={zip_code}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    data = []

    cards = soup.select(".product-tile, .product")

    for c in cards:
        name = c.get_text(strip=True)
        if any(i.lower() in name.lower() for i in items):
            price_el = c.select_one(".price, .product-price")
            if price_el:
                price = price_el.get_text(strip=True).replace("$", "")
                data.append({
                    "Store": "Aldi",
                    "Item": name,
                    "Price": float(price),
                    "Zip": zip_code,
                    "Date": date.today()
                })

    return pd.DataFrame(data)
