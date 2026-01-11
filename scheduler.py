from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import time
import os
import database
import scraper
import mailer
from typing import List

# Single scheduler instance
scheduler = BackgroundScheduler()

def check_and_run_jobs():
    """
    Checks for due schedules in DB, runs scraper, sends email.
    """
    due_jobs = database.get_due_schedules()
    print(f"[{datetime.now()}] Checking jobs... Found {len(due_jobs)} due.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Skipping jobs: API Key missing.")
        return

    for job in due_jobs:
        try:
            # 1. Scrape
            print(f"Running job for {job['url']} ({job['topic']})")
            data, error = scraper.fetch_and_extract(job['url'], job['topic'], api_key)
            
            if error:
                status = "failed"
                print(f"Job failed: {error}")
            else:
                status = "success"
                # Save to History
                database.add_history(job['url'], job['topic'], data, status="scheduled_success")
                
                # Send Email
                subject = f"360d Report: {job['topic']} - {datetime.now().strftime('%Y-%m-%d')}"
                html_body = f"""
                <h2>Scrape Result for {job['url']}</h2>
                <p><b>Topic:</b> {job['topic']}</p>
                <p><b>Items Found:</b> {len(data)}</p>
                <hr>
                <p>Check the dashboard for full details.</p>
                """
                mailer.send_notification_email(job['email'], subject, html_body)

            # 2. Update Next Run
            database.update_schedule_next_run(job['id'], job['frequency_days'])
            
        except Exception as e:
            print(f"Error processing job {job['id']}: {e}")

def start_scheduler():
    """Starts the background scheduler if not already running."""
    if not scheduler.running:
        database.init_db() # Ensure DB exists
        # Check every 1 hour (or 60 seconds for demo/debug)
        # For production/demo, let's check every 30 minutes
        scheduler.add_job(check_and_run_jobs, 'interval', minutes=60, id='master_job_check', replace_existing=True)
        scheduler.start()
