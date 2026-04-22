import requests
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-AU,en;q=0.9"
}

def get_html(url):
    try:
        time.sleep(random.uniform(2, 5))  # polite delay
        response = requests.get(url, headers=HEADERS, timeout=15)
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None
