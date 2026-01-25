import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv(".env.local")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env.local")
    exit(1)

genai.configure(api_key=api_key)

print("--- Listing Available Models ---")
try:
    models = genai.list_models()
    found_any = False
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            found_any = True
            print(f"Name: {m.name}")
            print(f"Display Name: {m.display_name}")
            print(f"Version: {m.version}")
            print("-" * 20)
    
    if not found_any:
        print("No models found with 'generateContent' capability.")

except Exception as e:
    print(f"Error listing models: {e}")

print("\n--- Testing 'gemini-1.5-flash' availability ---")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you online?")
    print("Success! Response:", response.text)
except Exception as e:
    print(f"Failed to use gemini-1.5-flash: {e}")

print("\n--- Testing 'gemini-pro' availability ---")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, are you online?")
    print("Success! Response:", response.text)
except Exception as e:
    print(f"Failed to use gemini-pro: {e}")
