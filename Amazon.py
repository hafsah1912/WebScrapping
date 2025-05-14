import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import warnings

warnings.filterwarnings("ignore")
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36" 
}

def find_total_pages(url):
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}") 
    if response.status_code != 200:
        print("Failed to fetch the page.")
        return 0
    soup = BeautifulSoup(response.text, 'html.parser')
    last_page = soup.find('span', class_='s-pagination-item s-pagination-disabled')
    return int(last_page.get_text()) if last_page and last_page.get_text().isdigit() else 1

def scrape_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url} | Status Code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', {'data-component-type': 's-search-result'})

    page_data = []
 
    page_data.append({
            'Title': title,
            'Image URL': image_url,
            'Rating': rating,
            'Reviews': reviews,
            'Current Price': current_price,
            'M.R.P': mrp,
            'Discount': discount,
            'Delivery Date': delivery
        })

    return page_data

base_url = "https://www.amazon.in/s?i=electronics&rh=n%3A1389401031&s=popularity-rank&fs=true"

total_pages = find_total_pages(base_url)
print(f"Total pages found: {total_pages}")

all_products = []
for page in range(1, total_pages + 1):
    print(f"Scraping page {page} of {total_pages}...")
    page_url = f"{base_url}&page={page}"
    all_products.extend(scrape_page(page_url))
    time.sleep(2) 
df = pd.DataFrame(all_products)
df
