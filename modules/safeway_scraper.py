import time
import pandas as pd
from datetime import date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape_safeway(zip_code, items, headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    # Correct WebDriver initialization
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    results = []

    for item in items:
        url = f"https://www.safeway.com/shop/search-results.html?q={item}"
        driver.get(url)
        time.sleep(4)

        cards = driver.find_elements(By.CSS_SELECTOR, ".product-card")

        for c in cards:
            try:
                name = c.find_element(By.CSS_SELECTOR, ".product-title").text
                price = (
                    c.find_element(By.CSS_SELECTOR, ".product-price")
                    .text.replace("$", "")
                )

                results.append({
                    "Store": "Safeway",
                    "Item": name,
                    "Price": float(price),
                    "Zip": zip_code,
                    "Date": date.today()
                })

            except Exception:
                pass

    driver.quit()
    return pd.DataFrame(results)
