import requests
from bs4 import BeautifulSoup
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_traditionally(url):
    print(f"Fetching {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Target: News Home Items
        # Based on inspection: .news-home__item -> .news-home__date, .news-home__heading
        news_items = soup.select(".news-home__item")
        print(f"Found {len(news_items)} news items.")
        
        for item in news_items:
            # Extract Date
            date_tag = item.select_one(".news-home__date")
            date = date_tag.get_text(strip=True) if date_tag else "N/A"
            
            # Extract Title
            title_tag = item.select_one(".news-home__heading")
            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            
            # Extract Link
            link_tag = item.select_one(".news-home__heading-link")
            link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
            if link and not link.startswith("http"):
                link = requests.compat.urljoin(url, link)
            
            results.append({
                "date": date,
                "title": title,
                "link": link,
                "summary": "Extracted via CSS Selector"
            })
            
        # Fallback/Additional: Service Cards with dates (e.g. 即測即評)
        service_cards = soup.select(".card-service")
        for card in service_cards:
            date_tag = card.select_one(".card-service__date")
            desc_tag = card.select_one(".card-service__description")
            
            if date_tag and desc_tag:
                 date = date_tag.get_text(strip=True)
                 title = desc_tag.get_text(strip=True)
                 # Clean up date if it has extra text
                 results.append({
                    "date": date,
                    "title": f"[Service/Card] {title}",
                    "link": url, # Card links vary, simplify for now
                    "summary": "Service Card Item"
                 })

        return results

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    url = "https://www.roccrane.org.tw/"
    data = scrape_traditionally(url)
    print(json.dumps(data, indent=2, ensure_ascii=False))
