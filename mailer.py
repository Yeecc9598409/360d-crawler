import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_notification_email(to_email: str, subject: str, content_html: str):
    """
    Sends an email using SMTP credentials from environment variables.
    """
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password:
        print("SMTP Credentials not found. Skipping email.")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"360d Notification <{smtp_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(content_html, 'html'))

    try:
        # Defaults to Gmail SMTP (port 587)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
