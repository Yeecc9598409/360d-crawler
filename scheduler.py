from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import time
import os
import database
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

    import scraper_css
    import json
    
    for job in due_jobs:
        try:
            # 1. Scrape (Forced CSS)
            print(f"Running job for {job['url']} (Auto-CSS)")
            data, error = scraper_css.fetch_data(job['url'])
            
            if error:
                status = "failed"
                print(f"Job failed: {error}")
            else:
                status = "success"
                
                # 2. Check for duplicate content
                is_duplicate = False
                last_history = database.get_last_history_for_url(job['url'])
                
                if last_history:
                    try:
                        current_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
                        last_json = json.dumps(json.loads(last_history['data_json']), sort_keys=True, ensure_ascii=False)
                        
                        if current_json == last_json:
                            is_duplicate = True
                            print(f"[Scheduler] Duplicate content detected for {job['url']}")
                    except Exception as e:
                        print(f"[Scheduler] Error comparing history: {e}")
                
                # Save to History
                database.add_history(job['url'], "Auto-CSS", data, status="scheduled_success")
                
                # 3. Send Email based on duplicate check
                if is_duplicate:
                    # No change - send "no update" email
                    subject = "360d 通知: 今日無更新 (內容未變更)"
                    mailer.send_notification_email(job['email'], subject, updates=[])
                elif len(data) > 0:
                    subject = f"360d 通知: 今日有更新 ({len(data)} 則)"
                    mailer.send_notification_email(job['email'], subject, updates=data)
                else:
                    subject = "360d 通知: 今日無更新"
                    mailer.send_notification_email(job['email'], subject, updates=[])

            # 4. Handle one-time vs continuous scheduling
            is_continuous = job.get('is_continuous', 1)  # Default to continuous
            if is_continuous:
                # Update Next Run for continuous scheduling
                job_unit = job.get('unit', 'days')
                database.update_schedule_next_run(job['id'], job['frequency_days'], unit=job_unit)
            else:
                # One-time scheduling - deactivate after running
                database.toggle_schedule_active(job['id'], False)
                print(f"[Scheduler] One-time job {job['id']} completed and deactivated.")
            
        except Exception as e:
            print(f"Error processing job {job['id']}: {e}")

def start_scheduler():
    """Starts the background scheduler if not already running."""
    if not scheduler.running:
        database.init_db() # Ensure DB exists
        # Check every 3 seconds for near-instant response
        scheduler.add_job(check_and_run_jobs, 'interval', seconds=3, id='master_job_check', replace_existing=True)
        scheduler.start()
        print("[Scheduler] Started - checking every 3 seconds")
