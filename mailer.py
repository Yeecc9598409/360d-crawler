import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

import random
from datetime import datetime # Added this import



def send_notification_email(to_email: str, subject: str, content_html: str = "", updates: list = None):
    """
    Sends notification email via n8n Webhook (preferred) or SMTP.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")

    # --- Generate HTML Body (Shared for both methods) ---

    
    if updates and len(updates) > 0:
        # Template A: Update Found
        body = f"""
        <html>
        <body>
            <h2>今日更新了 ({today_str})</h2>
            <p>親愛的用戶您好：</p>
            <p>系統檢測到目標網站有新的內容更新。</p>
            <hr>
            <h3>即時更新詳情：</h3>
            <ul>
                {"".join([f"<li><a href='{item.get('link', '#')}'>{item.get('title', 'No Title')}</a> <span style='color:#888'>({item.get('date', '')})</span></li>" for item in updates])}
            </ul>
        </body>
        </html>
        """
    else:
        # Template B: No Update
        body = f"""
        <html>
        <body>
            <h2>今日沒有更新 ({today_str})</h2>
            <p>親愛的用戶您好：</p>
            <p>今日目標網站目前沒有檢測到顯著的變動。</p>
            <hr>
            <p>系統將持續為您監控...</p>
        </body>
        </html>
        """
    
    # 1. Try n8n Webhook
    webhook_url = os.getenv("MAILER_WEBHOOK_URL")
    if webhook_url:
        try:
            import requests
            print(f"[Mailer] Sending via n8n Webhook: {webhook_url}")
            # Send PRE-GENERATED HTML
            payload = {
                "to_email": to_email,
                "subject": subject,
                "html_body": body # Key changed to be explicit
            }
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code == 200:
                print("[Mailer] n8n Webhook success.")
                return True
            else:
                print(f"[Mailer] n8n Webhook failed: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"[Mailer] n8n Webhook error: {e}")

    # 2. Try SMTP 
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password:
        if not webhook_url:
            print("[Mailer] No Webhook or SMTP Credentials found. Simulating email.")
            print(f"--- Email to {to_email} ---\nSubject: {subject}\n-----------------------")
        return True 

    msg = MIMEMultipart()
    msg['From'] = f"360d Notification <{smtp_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html')) # Use the pre-generated body

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"[Mailer] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[Mailer] Failed to send email: {e}")
        return False

def send_repeated_notification_email(to_email: str, subject: str):
    """
    Sends a 'Repeated Check - No Update' email.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")

    
    # Template C: No New Updates (Repeated Check)
    body = f"""
    <html>
    <body>
        <h2>重複確認通知 ({today_str})</h2>
        <p>親愛的用戶您好：</p>
        <p>您剛剛再次執行了爬取，但系統比對後發現，網站內容與您上次執行時完全相同。</p>
        <p>這代表目前沒有新的更新。</p>
        <hr>
        <p>祝您有美好的一天！</p>
    </body>
    </html>
    """

    # 1. Try n8n Webhook
    webhook_url = os.getenv("MAILER_WEBHOOK_URL")
    if webhook_url:
        try:
            import requests
            print(f"[Mailer] Sending 'Repeated' email via Webhook: {webhook_url}")
            payload = {
                "to_email": to_email,
                "subject": subject,
                "html_body": body
            }
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code == 200:
                print("[Mailer] Webhook success.")
                return True
        except Exception as e:
            print(f"[Mailer] Webhook error: {e}")

    # 2. Try SMTP
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password:
        return True

    msg = MIMEMultipart()
    msg['From'] = f"360d Notification <{smtp_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"[Mailer] Repeated-Check Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[Mailer] Failed to send email: {e}")
        return False
