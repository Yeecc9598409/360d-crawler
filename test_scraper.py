import scraper
import os
import json
from dotenv import load_dotenv

load_dotenv(".env.local")
api_key = os.getenv("GEMINI_API_KEY")

url = "https://www.roccrane.org.tw/"
print("URL:", url)
print("Key length:", len(api_key) if api_key else 0)

data, error = scraper.fetch_and_extract(url, "News/Articles", api_key)

print("---RESULT---")
if error:
    print("FAILED:", error)
else:
    print("SUCCESS:", len(data), "items")
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to result.json")
print("---END---")
