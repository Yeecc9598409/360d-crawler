import requests
from bs4 import BeautifulSoup

url = "https://www.roccrane.org.tw/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, verify=False, timeout=10)
    response.encoding = response.apparent_encoding or 'utf-8'
    
    with open("site_dump.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print("Downloaded site_dump.html")
    
    # Preliminary peek
    soup = BeautifulSoup(response.text, 'html.parser')
    print("\n--- Potential News/Article Sections ---")
    # Looking for common tags for news
    for tag in soup.find_all(['h2', 'h3', 'h4'], limit=10):
        print(f"<{tag.name} class='{tag.get('class')}'>{tag.get_text(strip=True)}</{tag.name}>")

except Exception as e:
    print(f"Error: {e}")
