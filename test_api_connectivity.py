
import requests
import time

def test_api():
    print("Testing API connectivity to http://localhost:8000/api/extract...")
    url = "http://localhost:8000/api/extract"
    payload = {
        "url": "https://www.roccrane.org.tw/",
        "email": "test@example.com"
    }
    
    start = time.time()
    try:
        response = requests.post(url, json=payload, timeout=5)
        duration = time.time() - start
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        print(f"Duration: {duration:.2f}s")
    except Exception as e:
        print(f"API Request Failed: {e}")

if __name__ == "__main__":
    test_api()
