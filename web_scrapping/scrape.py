from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

# ----------------------------
# Browser Setup
# ----------------------------
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

print("Opening Unsplash...")

driver.get(
    "https://unsplash.com/s/photos/product?orientation=square"
)

# Let the challenge complete
time.sleep(8)

# ----------------------------
# Scrape All Pages
# ----------------------------
all_products = []

TOTAL_PAGES = 43

for page in range(1, TOTAL_PAGES + 1):

    print(f"Fetching page {page}/{TOTAL_PAGES}")

    data = driver.execute_async_script(f"""
    const done = arguments[0];

    fetch(
        '/napi/search/photos?query=product&orientation=squarish&page={page}&per_page=20'
    )
    .then(r => r.json())
    .then(data => done(data))
    .catch(err => done({{error: err.toString()}}));
    """)

    if "results" not in data:
        print(f"Failed page {page}")
        continue

    for item in data["results"]:

        # Skip premium content
        if item.get("plus") or item.get("premium"):
            continue

        name = (
            item.get("alt_description")
            or item.get("description")
            or "Untitled Product"
        )

        product = {
            "external_id": item["id"],
            "name": name,
            "description": item.get("description") or name,
            "slug": item.get("slug"),
            "image_url": item["urls"]["regular"],
            "thumbnail_url": item["urls"]["small"],
            "width": item["width"],
            "height": item["height"],
            "color": item["color"],
            "category": "uncategorized"
        }

        all_products.append(product)

driver.quit()

# ----------------------------
# Save JSON
# ----------------------------
with open(
    "products.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        all_products,
        f,
        indent=4,
        ensure_ascii=False
    )

print(f"\nSaved {len(all_products)} products")
print("File: products.json")