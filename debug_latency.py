
import time
import scraper_css
import requests

def test_speed(url):
    print(f"Testing fetch for: {url}")
    start = time.time()
    try:
        data, error = scraper_css.fetch_data(url)
        duration = time.time() - start
        print(f"Duration: {duration:.2f} seconds")
        if error:
            print(f"Error: {error}")
        else:
            print(f"Success! Got {len(data)} items.")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test valid URL
    test_speed("https://www.roccrane.org.tw/news")
