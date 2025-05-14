import requests
from bs4 import BeautifulSoup
import time
from googletrans import Translator
def fetch_page(session, url, form_data=None):
    response = session.post(url, data=form_data) if form_data else session.get(url)
    return BeautifulSoup(response.text, "html.parser")
def extract_form_data(soup):
    return {
        "__VIEWSTATE": soup.select_one("input[name='__VIEWSTATE']")["value"] if soup.select_one("input[name='__VIEWSTATE']") else "",
        "__VIEWSTATEGENERATOR": soup.select_one("input[name='__VIEWSTATEGENERATOR']")["value"] if soup.select_one("input[name='__VIEWSTATEGENERATOR']") else "",
        "__EVENTVALIDATION": soup.select_one("input[name='__EVENTVALIDATION']")["value"] if soup.select_one("input[name='__EVENTVALIDATION']") else "",
    }
def find_previous_page(soup):
    prev_button = soup.select_one("a.glyphicon-chevron-left:not(.aspNetDisabled)")
    return prev_button["href"].split("'")[1] if prev_button and "href" in prev_button.attrs else None
def extract_titles_and_descriptions(soup):
    news_group = soup.find('div', class_='news-group')
    if news_group:
        titles = [title.get_text(strip=True) for title in news_group.find_all('h3')]
        descriptions = [description.get_text(strip=True) for description in news_group.find_all('p')]
        return list(zip(titles, descriptions))
    return []
def translate_text(titles, descriptions):
    translator = Translator()
    translated_titles = []
    translated_descriptions = []
    for title in titles:
        try:
            translated = translator.translate(title, src='auto', dest='en')
            translated_titles.append(translated.text if translated and translated.text else title)
        except Exception:
            translated_titles.append(title)
    for description in descriptions:
        try:
            translated = translator.translate(description, src='auto', dest='en')
            translated_descriptions.append(translated.text if translated and translated.text else description)
        except Exception:
            translated_descriptions.append(description)
    return translated_titles, translated_descriptions
def scrape_pages():
    url = "https://www.ssif.gov.jo/NewsGroup.aspx?group_key=announce"
    session = requests.Session()
    soup = fetch_page(session, url)
    total_pages = 1
    total_items = 0
    all_data = []
    while True:
        data = extract_titles_and_descriptions(soup)
        if not data:
            break
        titles, descriptions = zip(*data) if data else ([], [])
        translated_titles, translated_descriptions = translate_text(titles, descriptions)
        for title, description in zip(translated_titles, translated_descriptions):
            all_data.append({"title": title, "description": description})
            total_items += 1
        print(f"Page {total_pages}: {len(translated_titles)} titles extracted")
        form_data = extract_form_data(soup)
        prev_page_target = find_previous_page(soup)
        if not prev_page_target:
            break
        form_data["__EVENTTARGET"], form_data["__EVENTARGUMENT"] = prev_page_target, ""
        time.sleep(1)
        soup = fetch_page(session, url, form_data)
        total_pages += 1
    return {
        "status": "success",
        "message": "Scraping completed",
        "total_pages": total_pages - 1,
        "total_items": total_items,
        "data": all_data
    }
if __name__ == "__main__":
    result = scrape_pages()
    print(result)