"""
REMZA019 Gaming - Email Notifications System
Automated email notifications for stream events
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from typing import List
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger("email_notifications")

email_router = APIRouter(prefix="/email", tags=["email"])

class EmailTemplate:
    @staticmethod
    def live_notification(streamer_name: str, youtube_url: str):
        """Email template for LIVE notifications"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
                    color: #10b981;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #1a1a1a;
                    border: 2px solid #10b981;
                    border-radius: 10px;
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: #10b981;
                    text-shadow: 0 0 10px #10b981;
                }}
                .live-badge {{
                    background: #dc2626;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 20px;
                    display: inline-block;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background: #10b981;
                    color: black;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                    transition: all 0.3s;
                }}
                .button:hover {{
                    background: #059669;
                    transform: scale(1.05);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">🎮 {streamer_name} GAMING</div>
                
                <div style="text-align: center;">
                    <div class="live-badge">🔴 LIVE NOW!</div>
                </div>
                
                <h2 style="color: #10b981; text-align: center;">Stream je počeo!</h2>
                
                <p style="font-size: 16px; text-align: center;">
                    {streamer_name} je upravo otišao LIVE!<br>
                    Pridružite se stream-u sada i ne propustite akciju! 🎯
                </p>
                
                <div style="text-align: center;">
                    <a href="{youtube_url}" class="button">
                        📺 GLEDAJ STREAM
                    </a>
                </div>
                
                <p style="text-align: center; margin-top: 30px; font-size: 14px;">
                    🏆 Zarađujte poene gledanjem streama!<br>
                    💬 Ćaskajte sa ostalim gledaocima!<br>
                    🎯 Učestvujte u pollovima i predikcijama!
                </p>
                
                <div class="footer">
                    <p>Primili ste ovu email notifikaciju jer ste se pretplatili na {streamer_name} Gaming obaveštenja.</p>
                    <p style="color: #10b981;">REMZA019 Gaming</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

async def send_email_notification(
    to_emails: List[str],
    subject: str,
    html_content: str
):
    """Send email notification via SMTP"""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", smtp_user)
        
        if not smtp_user or not smtp_password:
            logger.warning("⚠️ SMTP credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ", ".join(to_emails)
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent to {len(to_emails)} recipients")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email send error: {e}")
        return False

def get_database():
    from server import get_database as get_db
    return get_db()

async def send_live_notifications_to_subscribers(streamer_name: str, game_name: str, youtube_url: str):
    """Helper function to send LIVE notifications - NO AUTH REQUIRED (internal use)"""
    try:
        db = get_database()
        
        # Get all subscribers
        subscribers = await db.subscribers.find(
            {"subscribed": True},
            {"_id": 0, "email": 1}
        ).to_list(length=10000)
        
        if not subscribers:
            logger.info("No subscribers to notify")
            return {"success": True, "message": "No subscribers", "count": 0}
        
        emails = [sub["email"] for sub in subscribers if sub.get("email")]
        
        if not emails:
            logger.info("No valid emails found")
            return {"success": True, "message": "No valid emails", "count": 0}
        
        # Create email content
        subject = f"🔴 {streamer_name} is LIVE NOW! Playing {game_name}"
        html_content = EmailTemplate.live_notification(streamer_name, youtube_url)
        
        # Send emails (NO background tasks, direct send)
        import asyncio
        for email in emails[:50]:  # Limit to 50 for safety
            try:
                await asyncio.create_task(send_email_notification([email], subject, html_content))
            except Exception as e:
                logger.error(f"Failed to send to {email}: {e}")
        
        logger.info(f"✅ Sent {min(len(emails), 50)} LIVE notifications")
        
        return {
            "success": True,
            "message": f"Sent notifications to {min(len(emails), 50)} subscribers",
            "count": min(len(emails), 50)
        }
        
    except Exception as e:
        logger.error(f"❌ Send live notifications error: {e}")
        return {"success": False, "message": str(e)}

@email_router.post("/notify-live")
async def notify_subscribers_live_endpoint(
    background_tasks: BackgroundTasks,
    authorization: str = None
):
    """Send LIVE notifications to all subscribers - PUBLIC ENDPOINT (used internally)"""
    # Note: This is called internally from admin_api, authentication checked there
    try:
        db = get_database()
        
        # Get all subscribers
        subscribers = await db.subscribers.find(
            {"subscribed": True},
            {"_id": 0, "email": 1}
        ).to_list(length=10000)
        
        if not subscribers:
            return {"success": True, "message": "No subscribers to notify", "count": 0}
        
        emails = [sub["email"] for sub in subscribers if sub.get("email")]
        
        if not emails:
            return {"success": True, "message": "No valid emails found", "count": 0}
        
        # Create email content
        streamer_name = "REMZA019"
        youtube_url = "https://www.youtube.com/@REMZA019"
        subject = f"🔴 {streamer_name} is LIVE NOW!"
        html_content = EmailTemplate.live_notification(streamer_name, youtube_url)
        
        # Send emails in background (batches of 50)
        batch_size = 50
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            background_tasks.add_task(
                send_email_notification,
                batch,
                subject,
                html_content
            )
        
        logger.info(f"✅ Queued {len(emails)} LIVE notifications")
        
        return {
            "success": True,
            "message": f"Sending notifications to {len(emails)} subscribers",
            "count": len(emails)
        }
        
    except Exception as e:
        logger.error(f"❌ Notify live error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notifications")

@email_router.post("/test")
async def send_test_email(
    email: EmailStr,
    background_tasks: BackgroundTasks
):
    """Send test email - PUBLIC (for testing)"""
    try:
        subject = "🎮 Test Email from REMZA019 Gaming"
        html_content = EmailTemplate.live_notification("REMZA019", "https://www.youtube.com/@REMZA019")
        
        background_tasks.add_task(
            send_email_notification,
            [email],
            subject,
            html_content
        )
        
        return {"success": True, "message": f"Test email queued for {email}"}
        
    except Exception as e:
        logger.error(f"❌ Test email error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test email")

@email_router.get("/subscribers/count")
async def get_subscribers_count():
    """Get count of email subscribers - PUBLIC"""
    try:
        db = get_database()
        count = await db.subscribers.count_documents({"subscribed": True})
        return {"count": count}
    except Exception as e:
        logger.error(f"❌ Get subscribers count error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscribers count")
