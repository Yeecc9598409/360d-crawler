import os
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
from dotenv import load_dotenv

# Import existing logic
import database

# Load environment variables
load_dotenv(".env.local")

app = FastAPI(title="360D Crawler API", version="1.0.0")

# Enable CORS for React Frontend (default Vite port is 5173) and Zeabur
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

print(f"[CORS DEBUG] Loaded Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.zeabur\.app", # Fallback for any Zeabur subdomain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import scraper_css

# --- Data Models ---
class ExtractRequest(BaseModel):
    url: str
    email: Optional[str] = None
    # Removed: topic, scraper_type (Force CSS)

class ScheduleRequest(BaseModel):
    frequency: int
    unit: str = "days"
    email: str
    url: str
    is_continuous: bool = True  # Default to continuous scheduling
    # Removed: topic, scraper_type (Force CSS)

# --- Routes ---

@app.on_event("startup")
def startup_event():
    database.init_db()
    
    # Start the background scheduler ONLY if strictly not reloader
    # When using uvicorn --reload, the main process sets RUN_MAIN=true
    if os.environ.get("RUN_MAIN") == "true" or not os.environ.get("UVICORN_RELOAD"):
         import scheduler
         scheduler.start_scheduler()
    else:
        print("[Startup] Skipping scheduler start in reloader process")

@app.get("/")
def read_root():
    return {"message": "360D Crawler API (CSS Only Mode) is running"}

@app.post("/api/extract")
def extract_data(request: ExtractRequest):
    # Forced CSS Mode
    print(f"Starting CSS extraction for: {request.url}")
    data, error = scraper_css.fetch_data(request.url)

    status = "success"
    if error:
        status = "failed"
        import traceback
        traceback.print_exc() 
        database.add_history(request.url, "Auto-CSS", [], status="failed")
        raise HTTPException(status_code=500, detail=f"Extraction Failed: {error}")
    
    # Log success
    from datetime import datetime
    import json
    
    # Check for duplicate
    is_duplicate = False
    last_history = database.get_last_history_for_url(request.url)
    
    print(f"[DEBUG] last_history found: {last_history is not None}")
    
    if last_history:
        print(f"[DEBUG] last_history timestamp raw: {last_history['timestamp']}")
        try:
            last_time = datetime.strptime(last_history['timestamp'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Try alternate format if default fails
            last_time = datetime.fromisoformat(last_history['timestamp'])
        
        print(f"[DEBUG] last_time.date(): {last_time.date()}, today: {datetime.now().date()}")
        
        if last_time.date() == datetime.now().date():
             # Same day check
             # Compare data (simplified string compare of JSON dump)
             current_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
             last_json = json.dumps(json.loads(last_history['data_json']), sort_keys=True, ensure_ascii=False) # Normalize
             
             print(f"[DEBUG] current_json length: {len(current_json)}")
             print(f"[DEBUG] last_json length: {len(last_json)}")
             print(f"[DEBUG] JSONs match: {current_json == last_json}")
             
             if current_json == last_json:
                 is_duplicate = True
                 print("Duplicate extraction detected for today.")

    database.add_history(request.url, "Auto-CSS", data, status="success")
    
    # Send email notification if email is provided
    if request.email:
        import mailer
        if is_duplicate:
             subject = f"[360D] 重複確認通知 - 無更新"
             mailer.send_repeated_notification_email(request.email, subject)
             print(f"Repeated-Check Email sent to {request.email}")
        else:
             subject = f"[360D] 擷取結果 - {len(data)} 筆資料"
             mailer.send_notification_email(request.email, subject, updates=data)
             print(f"Standard Email sent to {request.email}")
    
    return {
        "status": "success",
        "count": len(data),
        "data": data
    }

@app.post("/api/schedule")
def schedule_task(request: ScheduleRequest):
    # Pass new fields to database - Defaulting Topic and ScraperType
    schedule_id = database.add_schedule(
        request.url, "Auto-CSS", request.email, request.frequency, "CSS", 
        unit=request.unit, is_continuous=request.is_continuous
    )
    print(f"Scheduling task (CSS) for {request.email}, Freq: {request.frequency} {request.unit}, Continuous: {request.is_continuous}, ID: {schedule_id}")
    return {"status": "success", "message": "Task scheduled successfully", "schedule_id": schedule_id}

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

@app.patch("/api/schedule/{schedule_id}/pause")
def toggle_schedule_pause(schedule_id: int, active: bool = False):
    """Toggle a schedule's active status."""
    database.toggle_schedule_active(schedule_id, active)
    status = "resumed" if active else "paused"
    return {"status": "success", "message": f"Schedule {status}"}

@app.get("/api/schedules")
def get_schedules():
    """Get all active schedules."""
    schedules = database.get_active_schedules()
    return schedules

@app.delete("/api/schedules/stop-all")
def stop_all_schedules():
    """Stop all active schedules."""
    count = database.deactivate_all_schedules()
    print(f"[API] Stopped {count} schedules")
    return {"status": "success", "message": f"Stopped {count} schedules", "count": count}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
