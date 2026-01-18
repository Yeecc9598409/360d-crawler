import requests
from bs4 import BeautifulSoup
import urllib3
from typing import List, Dict, Tuple, Any

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data(url: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Fetches data using traditional CSS selectors (BeautifulSoup).
    Optimized for roccrane.org.tw.
    Returns (Data List, Error Message).
    """
    print(f"[CSS Scraper] Fetching {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code != 200:
            return [], f"HTTP Error {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # 1. Target: News Home Items
        # Structure: .news-home__item -> .news-home__date, .news-home__heading
        news_items = soup.select(".news-home__item")
        
        for item in news_items:
            date_tag = item.select_one(".news-home__date")
            date = date_tag.get_text(strip=True) if date_tag else "N/A"
            
            title_tag = item.select_one(".news-home__heading")
            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            
            link_tag = item.select_one(".news-home__heading-link")
            link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
            if link and not link.startswith("http"):
                link = requests.compat.urljoin(url, link)
            
            results.append({
                "date": date,
                "title": title,
                "summary": title, # Use title as summary for CSS mode
                "link": link,
                "source": "CSS_Scraper"
            })
            
        # 2. Target: Service/Course Cards (e.g. 即測即評)
        # Structure: .card-service -> .card-service__date, .card-service__description
        service_cards = soup.select(".card-service")
        for card in service_cards:
            date_tag = card.select_one(".card-service__date")
            desc_tag = card.select_one(".card-service__description")
            
            if date_tag and desc_tag:
                 date = date_tag.get_text(strip=True)
                 title = desc_tag.get_text(strip=True)
                 link_tag = card.select_one("a.card-service__learnmore")
                 link = link_tag['href'] if link_tag and link_tag.has_attr('href') else url
                 if link and not link.startswith("http"):
                    link = requests.compat.urljoin(url, link)

                 results.append({
                    "date": date,
                    "title": f"[Service] {title}",
                    "summary": title,
                    "link": link,
                    "source": "CSS_Scraper"
                 })

        if not results:
             return [], "No items found with current CSS selectors."

        print(f"[CSS Scraper] Successfully extracted {len(results)} items.")
        return results, None

    except Exception as e:
        return [], f"Scraping Error: {str(e)}"
