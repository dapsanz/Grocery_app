import time
import pandas as pd
from datetime import date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape_giant(zip_code, items, headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    # FIXED WebDriver initialization
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    results = []

    for item in items:
        url = f"https://giantfood.com/shopping/search/?searchTerm={item}"
        driver.get(url)
        time.sleep(4)

        cards = driver.find_elements(By.CSS_SELECTOR, ".product__details")

        for c in cards:
            try:
                name = c.find_element(By.CSS_SELECTOR, ".product__name").text
                price = (
                    c.find_element(By.CSS_SELECTOR, ".product__price")
                    .text.replace("$", "")
                )

                results.append({
                    "Store": "Giant",
                    "Item": name,
                    "Price": float(price),
                    "Zip": zip_code,
                    "Date": date.today()
                })
            except:
                pass

    driver.quit()
    return pd.DataFrame(results)
