import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import json
import time
from typing import List, Dict, Tuple, Any
import urllib3

# Rate limiting configuration
API_CALL_DELAY = 2  # seconds to wait before each API call
MAX_RETRIES = 3     # max retry attempts on rate limit errors
RETRY_BASE_DELAY = 30  # base delay for exponential backoff (seconds)

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration for Scoping
TOPIC_PROMPTS = {
    "News/Articles": "Extract a list of articles/news from the text. For each item, capture: 'title', 'date', 'author' (if any), and a brief 'summary'.",
    "Products/Pricing": "Extract a list of products or pricing plans. For each item, capture: 'name', 'price', 'features' (list), and 'specifications'.",
    "Company Info": "Extract company contact information. Capture: 'email', 'phone', 'address', 'social_links', and 'about_us_summary'."
}

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

def clean_html(html_content: str) -> str:
    """Removes script, style, and metadata, returning clean text."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup(["script", "style", "header", "footer", "nav", "noscript", "aside", "form", "svg"]):
        element.decompose()
    
    text = soup.get_text(separator='\n')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
    return cleaned_text

def fetch_and_extract(url: str, topic: str, api_key: str, char_limit: int = 8000) -> Tuple[List[Dict[str, Any]], str]:
    """
    Fetches URL, cleans HTML, and uses Gemini to extract data based on Topic.
    Returns (Data List, Error Message).
    """
    if not api_key:
        return [], "API Key missing"

    # 1. Fetch
    try:
        # verify=False fixes the SSL Error for sites with incomplete chains
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=20, verify=False)
        response.encoding = response.apparent_encoding or 'utf-8'
        if response.status_code != 200:
            return [], f"HTTP Error {response.status_code}"
    except Exception as e:
        return [], f"Network Error: {str(e)}"

    # 2. Clean
    clean_text = clean_html(response.text)
    truncated_text = clean_text[:char_limit]

    # 3. AI Extraction
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt_instruction = TOPIC_PROMPTS.get(topic, TOPIC_PROMPTS["News/Articles"])
    
    full_prompt = f"""
    You are a strict data extraction system. 
    TASK: {prompt_instruction}
    
    SOURCE TEXT:
    {truncated_text}
    
    OUTPUT RULES:
    1. Output ONLY a valid JSON List of Objects (e.g. [{{"key": "value"}}]).
    2. If no relevant data is found for the requested topic, return empty list [].
    3. Do NOT include markdown formatting (```json ... ```). Output raw JSON string only.
    4. Ensure all text is in Traditional Chinese (繁體中文) where possible, or original language if it's a propre noun.
    """
    
    try:
        # Rate limiting: wait before making API call
        print(f"[Rate Limit] Waiting {API_CALL_DELAY}s before API call...")
        time.sleep(API_CALL_DELAY)
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                payload = model.generate_content(full_prompt)
                text_resp = payload.text
                # Cleanup potential markdown
                text_resp = text_resp.replace("```json", "").replace("```", "").strip()
                data = json.loads(text_resp)
                
                if isinstance(data, list):
                    return data, None
                elif isinstance(data, dict):
                     # Handle case where AI returns a single object instead of list
                    return [data], None
                else:
                    return [], "AI returned unexpected format"
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # Check if it's a rate limit error (429)
                if "429" in error_str or "quota" in error_str.lower():
                    wait_time = RETRY_BASE_DELAY * (2 ** attempt)  # exponential backoff
                    print(f"[Rate Limit] Hit 429 error. Attempt {attempt + 1}/{MAX_RETRIES}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Not a rate limit error, don't retry
                    break
        
        return [], f"AI Error: {str(last_error)}"
            
    except Exception as e:
        return [], f"AI Error: {str(e)}"
