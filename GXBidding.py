# from deep_translator import GoogleTranslator
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import time
# from urllib.parse import urljoin

# headers = {
#     "User-Agent": "Mozilla/5.0"
# }

# def translate_text(text):
#     try:
#         return GoogleTranslator(source='zh-CN', target='en').translate(text)
#     except Exception as e:
#         print(f"Translation error for '{text}': {e}")
#         return text

# def scrape_and_save(base_url, total_pages=143, output_file="final_data.xlsx"):
#     data_list = []
    
#     for page_no in range(total_pages):
#         page_url = f'/AnnouncementList?code=B-001-01&pagesize=20&pageindex={page_no}'
#         website = urljoin(base_url, page_url)

#         retries = 3  # Retry up to 3 times if a timeout occurs
#         while retries > 0:
#             try:
#                 response = requests.get(website, headers=headers, timeout=10)
                
#                 if response.status_code != 200:
#                     print(f"Failed to fetch page {page_no+1}: Status {response.status_code}")
#                     break  # If the page is inaccessible, skip it
                
#                 soup = BeautifulSoup(response.text, 'lxml')
#                 links_and_titles = soup.find_all('a', class_='list-group-item-action')

#                 for idx, link in enumerate(links_and_titles, start=(page_no * 20) + 1):
#                     title_span = link.find('span', class_='text-truncate')
#                     if title_span:
#                         original_title = title_span.get_text(strip=True)

#                         # Add delay to avoid rate-limiting
#                         time.sleep(1)

#                         translated_title = translate_text(original_title)
#                         full_link = urljoin(base_url, link['href'])

#                         data_list.append({
#                             'Page Number': page_no + 1,
#                             'Index on Page': idx,
#                             'Page URL': website,
#                             'Original Title': original_title,
#                             'Translated Title': translated_title,
#                             'Link': full_link
#                         })

#                 print(f"Page {page_no+1} scraped successfully. Total entries so far: {len(data_list)}")
#                 time.sleep(2)
#                 break  # Break retry loop if successful

#             except requests.exceptions.Timeout:
#                 print(f"Timeout occurred while fetching page {page_no+1}. Retrying ({retries-1} attempts left)...")
#                 retries -= 1
#                 time.sleep(5)

#             except requests.exceptions.RequestException as e:
#                 print(f"An error occurred on page {page_no+1}: {e}")
#                 break  # Move to the next page if an error occurs

#     df = pd.DataFrame(data_list)

#     # Print total data count
#     print(f"\nTotal Data Entries Collected: {df.shape[0]}")

#     # Save to Excel
#     df.to_excel(output_file, index=False)
#     print(f"Data saved to {output_file}")

#     return df  # Optional, for further use

# # Run the scraper
# base_url = "http://www.gxbidding.com"
# scrape_and_save(base_url, total_pages=143)

# Alternate Of For Loop 

import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from googletrans import Translator
translator=Translator()
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
# }
def safe_request(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying {attempt+1}/{retries}...")
            time.sleep(delay)
    return None  
def find_total_pages(url):
    page = 1
    while True:
        website = f"{url}&pageindex={page}"
        response = safe_request(website)   
        if not response:
            print('Failed to fetch the page. Stopping.')
            break 
        soup = BeautifulSoup(response.text, 'html.parser')
        np = soup.find('li', class_='page-item disabled')
        if np:
            return page
        
        page += 1
        time.sleep(2)  
    
    return page

def scrape_data(base_url, total_pages):
    data_list = [] 
    for page_no in range(0, total_pages + 1): 
        page_url = f"{base_url}/AnnouncementList?code=B-001-01&pagesize=20&pageindex={page_no}"
        response = safe_request(page_url)

        if not response:
            print(f"Skipping page {page_no+1} due to request failure.")
            continue
        
        soup = BeautifulSoup(response.text, 'lxml')
        links = soup.find_all('a', class_='list-group-item-action')
        
        for link in links:
            title_span = link.find('span', class_='text-truncate')
            if title_span:
                title = title_span.get_text(strip=True)
                title_link = urljoin(base_url, link.get('href'))
                translated_title = translator.translate(title, src='zh-cn', dest='en').text
                data_list.append({
                    "Page No": page_no+1,
                    "Page Link": page_url,
                    "Title": translated_title,
                    "Title Link": title_link
                })
        
        print(f"Page {page_no+1} scraped successfully.")
        time.sleep(2)  
    
    return data_list
base_url = "http://www.gxbidding.com"
announcement_url = f"{base_url}/AnnouncementList?code=B-001-01&pagesize=20"

total_pages_count = find_total_pages(announcement_url)
print(f"Total Pages Found: {total_pages_count}")

data_list = scrape_data(base_url, total_pages_count)
print(f"\nTotal Data Entries Collected: {len(data_list)}")
df = pd.DataFrame(data_list)
df.to_excel('Bidding_Data.xlsx', index=False)
# df