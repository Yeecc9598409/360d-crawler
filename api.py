import os
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
from dotenv import load_dotenv

# Import existing logic
import scraper
import database

# Load environment variables
load_dotenv(".env.local")

app = FastAPI(title="360D Crawler API", version="1.0.0")

# Enable CORS for React Frontend (default Vite port is 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class ExtractRequest(BaseModel):
    url: str
    topic: str = "News/Articles"
    email: Optional[str] = None

class ScheduleRequest(BaseModel):
    frequency: int
    email: str
    url: str
    topic: str = "News/Articles"

# --- Routes ---

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def read_root():
    return {"message": "360D Crawler API is running"}

@app.post("/api/extract")
def extract_data(request: ExtractRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Server Configuration Error: API Key missing")

    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")

    print(f"Starting extraction for: {request.url} Topic: {request.topic}")
    
    # Call the existing scraper logic
    data, error = scraper.fetch_and_extract(request.url, request.topic, api_key)
    
    status = "success"
    if error:
        status = "failed"
        import traceback
        traceback.print_exc() # Print full error to console
        # Log failure but return error to user
        database.add_history(request.url, request.topic, [], status="failed")
        raise HTTPException(status_code=500, detail=f"Extraction Failed: {error}")
    
    # Log success
    database.add_history(request.url, request.topic, data, status="success")
    
    return {
        "status": "success",
        "count": len(data),
        "data": data
    }

@app.post("/api/schedule")
def schedule_task(request: ScheduleRequest):
    # Pass new fields to database
    database.add_schedule(request.url, request.topic, request.email, request.frequency)
    print(f"Scheduling task for {request.email}, Frequency: {request.frequency}, URL: {request.url}")
    return {"status": "success", "message": "Task scheduled successfully (Mock)"}

@app.get("/api/history")
def get_history(limit: int = 10):
    history = database.get_history(limit=limit)
    # Parse the stringified 'summary' back to JSON if needed, 
    # but database.get_history returns raw dicts. 
    # The 'summary' field in db is a string representation of the list.
    # We might need to clean it up for the frontend.
    cleaned_history = []
    for item in history:
        try:
            # Safe eval or json load if feasible. 
            # In app.py it used eval(), which is risky but existing.
            # We'll stick to basic return for now.
            count = 0
            if isinstance(item['summary'], str):
                 # Quick hack to get count without risky eval if possible, 
                 # or just return raw string.
                 pass
        except:
            pass
        cleaned_history.append(item)
        
    return cleaned_history

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
