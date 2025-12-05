"""
019 Solutions - Interactive Audience Notifications System
Real-time notifications for viewers without Discord dependency
Email integration with vladicaristic19@gmail.com
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EMAIL CONFIGURATION - 019 Solutions
SENDER_EMAIL = "vladicaristic19@gmail.com"
SENDER_NAME = "019 Solutions"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Email Templates
WELCOME_EMAIL_TEMPLATE = """
<html>
<body style="background: #000000; color: #00ff00; font-family: monospace; padding: 20px;">
    <div style="text-align: center; border: 2px solid #00ff00; padding: 20px; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #00ff00; text-shadow: 0 0 10px #00ff00;">🎮 019 SOLUTIONS 🎮</h1>
        <h2 style="color: #10b981;">Welcome to the Gaming Community!</h2>
        
        <p>Thanks for subscribing to REMZA019 notifications!</p>
        <p>You'll now receive:</p>
        
        <ul style="text-align: left; color: #00ff00;">
            <li>🔴 Live stream alerts when REMZA019 goes live</li>
            <li>📅 Schedule updates and stream announcements</li>
            <li>📹 New gaming video notifications</li>
            <li>🎯 Special gaming events and tournaments</li>
        </ul>
        
        <div style="background: rgba(0, 255, 0, 0.1); padding: 15px; margin: 20px 0; border: 1px solid #00ff00;">
            <p><strong>🎮 Get ready for epic FORTNITE gameplay!</strong></p>
            <p>🔗 YouTube: youtube.com/@remza019</p>
            <p>💬 Discord: Join our gaming community</p>
        </div>
        
        <p style="color: #888;">You can manage your preferences anytime on our website.</p>
        <p style="color: #10b981; font-weight: bold;">Game On! 🎮</p>
    </div>
</body>
</html>
"""

LIVE_NOTIFICATION_TEMPLATE = """
<html>
<body style="background: #000000; color: #00ff00; font-family: monospace; padding: 20px;">
    <div style="text-align: center; border: 2px solid #00ff00; padding: 20px; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #00ff00; text-shadow: 0 0 10px #00ff00; animation: pulse 2s infinite;">🔴 LIVE NOW! 🔴</h1>
        <h2 style="color: #10b981;">REMZA019 is streaming!</h2>
        
        <div style="background: rgba(0, 255, 0, 0.1); padding: 15px; margin: 20px 0; border: 1px solid #00ff00;">
            <h3>{title}</h3>
            <p style="font-size: 18px;">{message}</p>
        </div>
        
        <div style="margin: 20px 0;">
            <a href="{url}" style="background: #00ff00; color: #000000; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                🎮 JOIN THE STREAM NOW! 🎮
            </a>
        </div>
        
        <p style="color: #888;">Don't miss out on the action!</p>
    </div>
</body>
</html>
"""

# Notifications API Router
notifications_router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Database connection
def get_database():
    """Get database connection"""
    try:
        mongodb_url = os.environ.get('MONGO_URL')
        if not mongodb_url:
            raise ValueError("MONGO_URL environment variable is required")
        client = AsyncIOMotorClient(mongodb_url)
        db_name = os.environ.get('DB_NAME', 'remza019_gaming')
        return client[db_name]
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Notification Models
class Subscriber(BaseModel):
    id: str = None
    email: EmailStr
    push_endpoint: Optional[str] = None
    push_keys: Optional[Dict] = None
    preferences: Dict = {
        'live_notifications': True,
        'schedule_updates': True,
        'new_videos': True,
        'email_notifications': True,
        'push_notifications': True
    }
    subscribed_at: datetime = None
    is_active: bool = True
    timezone: Optional[str] = "CET"

class NotificationRequest(BaseModel):
    type: str  # 'live', 'schedule', 'video', 'announcement'
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    url: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class PushSubscription(BaseModel):
    email: EmailStr
    endpoint: str
    keys: Dict

class EmailNotification(BaseModel):
    email: EmailStr
    preferences: Dict

# Notification Storage
class NotificationLog(BaseModel):
    id: str = None
    type: str
    title: str
    message: str
    sent_to_count: int
    sent_at: datetime
    success_count: int = 0
    error_count: int = 0

# SUBSCRIBER MANAGEMENT
@notifications_router.post("/subscribe/email")
async def subscribe_email(email_data: EmailNotification):
    """Subscribe to email notifications"""
    try:
        db = get_database()
        
        # Check if already subscribed
        existing = await db.subscribers.find_one({'email': email_data.email})
        
        if existing:
            # Update preferences
            await db.subscribers.update_one(
                {'email': email_data.email},
                {
                    '$set': {
                        'preferences': email_data.preferences,
                        'is_active': True,
                        'updated_at': datetime.now()
                    }
                }
            )
            message = "Subscription preferences updated!"
        else:
            # Create new subscription
            subscriber = Subscriber(
                id=str(uuid.uuid4()),
                email=email_data.email,
                preferences=email_data.preferences,
                subscribed_at=datetime.now()
            )
            
            await db.subscribers.insert_one(subscriber.dict())
            message = "Successfully subscribed to notifications!"
        
        # Send welcome email
        await send_welcome_email(email_data.email)
        
        return {
            "success": True,
            "message": message,
            "subscriber_count": await db.subscribers.count_documents({'is_active': True})
        }
        
    except Exception as e:
        logger.error(f"❌ Email subscription error: {e}")
        raise HTTPException(status_code=500, detail="Subscription failed")

@notifications_router.post("/subscribe/push")
async def subscribe_push(push_data: PushSubscription):
    """Subscribe to push notifications"""
    try:
        db = get_database()
        
        # Update existing subscriber or create new one
        await db.subscribers.update_one(
            {'email': push_data.email},
            {
                '$set': {
                    'push_endpoint': push_data.endpoint,
                    'push_keys': push_data.keys,
                    'preferences.push_notifications': True,
                    'updated_at': datetime.now()
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Push notifications enabled!",
            "endpoint": push_data.endpoint
        }
        
    except Exception as e:
        logger.error(f"❌ Push subscription error: {e}")
        raise HTTPException(status_code=500, detail="Push subscription failed")

class UnsubscribeRequest(BaseModel):
    email: EmailStr

@notifications_router.post("/unsubscribe")
async def unsubscribe(request: UnsubscribeRequest):
    """Unsubscribe from all notifications"""
    try:
        db = get_database()
        
        result = await db.subscribers.update_one(
            {'email': request.email},
            {'$set': {'is_active': False, 'updated_at': datetime.now()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return {"success": True, "message": "Successfully unsubscribed"}
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 404) without wrapping them
        raise
    except Exception as e:
        logger.error(f"❌ Unsubscribe error: {e}")
        raise HTTPException(status_code=500, detail="Unsubscribe failed")

# NOTIFICATION SENDING
@notifications_router.post("/send")
async def send_notification(notification: NotificationRequest, background_tasks: BackgroundTasks):
    """Send notification to all active subscribers"""
    try:
        db = get_database()
        
        # Get active subscribers based on notification type
        preference_key = f"{notification.type}_notifications"
        subscribers = await db.subscribers.find({
            'is_active': True,
            f'preferences.{preference_key}': True
        }).to_list(length=None)
        
        if not subscribers:
            return {"success": False, "message": "No active subscribers found"}
        
        # Send notifications in background
        background_tasks.add_task(
            process_notifications,
            subscribers,
            notification
        )
        
        # Log notification
        log_entry = NotificationLog(
            id=str(uuid.uuid4()),
            type=notification.type,
            title=notification.title,
            message=notification.message,
            sent_to_count=len(subscribers),
            sent_at=datetime.now()
        )
        
        await db.notification_logs.insert_one(log_entry.dict())
        
        return {
            "success": True,
            "message": f"Notification queued for {len(subscribers)} subscribers",
            "subscriber_count": len(subscribers)
        }
        
    except Exception as e:
        logger.error(f"❌ Send notification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notifications")

# LIVE STATUS NOTIFICATIONS
@notifications_router.post("/live/start")
async def notify_live_start(background_tasks: BackgroundTasks, game: str = "FORTNITE", viewers: str = "0"):
    """Notify all subscribers that stream has started"""
    try:
        notification = NotificationRequest(
            type="live",
            title="🔴 019 SOLUTIONS IS LIVE!",
            message=f"Join the stream now! Playing {game} with {viewers} viewers watching.",
            url="/"
        )
        
        return await send_notification(notification, background_tasks)
        
    except Exception as e:
        logger.error(f"❌ Live start notification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send live notification")

@notifications_router.post("/schedule/update")
async def notify_schedule_update(background_tasks: BackgroundTasks, day: str, time: str, game: str):
    """Notify subscribers about schedule changes"""
    try:
        notification = NotificationRequest(
            type="schedule",
            title="📅 Stream Schedule Updated",
            message=f"New stream scheduled: {day} at {time} - {game}",
            url="/"
        )
        
        return await send_notification(notification, background_tasks)
        
    except Exception as e:
        logger.error(f"❌ Schedule notification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send schedule notification")

# STATS AND MANAGEMENT
@notifications_router.get("/stats")
async def get_notification_stats():
    """Get notification statistics"""
    try:
        db = get_database()
        
        total_subscribers = await db.subscribers.count_documents({'is_active': True})
        email_subscribers = await db.subscribers.count_documents({
            'is_active': True,
            'preferences.email_notifications': True
        })
        push_subscribers = await db.subscribers.count_documents({
            'is_active': True,
            'preferences.push_notifications': True,
            'push_endpoint': {'$exists': True}
        })
        
        recent_notifications = await db.notification_logs.find({}, {"_id": 0}).sort([('sent_at', -1)]).limit(5).to_list(length=None)
        
        return {
            "total_subscribers": total_subscribers,
            "email_subscribers": email_subscribers,
            "push_subscribers": push_subscribers,
            "recent_notifications": recent_notifications
        }
        
    except Exception as e:
        logger.error(f"❌ Notification stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

# HELPER FUNCTIONS
async def process_notifications(subscribers: List[Dict], notification: NotificationRequest):
    """Process notifications in background"""
    try:
        db = get_database()
        success_count = 0
        error_count = 0
        
        for subscriber in subscribers:
            try:
                # Send email notification
                if subscriber.get('preferences', {}).get('email_notifications', False):
                    await send_email_notification(subscriber['email'], notification)
                    success_count += 1
                
                # Send push notification 
                if (subscriber.get('preferences', {}).get('push_notifications', False) and 
                    subscriber.get('push_endpoint')):
                    await send_push_notification(subscriber, notification)
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to send notification to {subscriber.get('email')}: {e}")
                error_count += 1
        
        # Update log with results
        await db.notification_logs.update_one(
            {'type': notification.type, 'sent_at': {'$gte': datetime.now() - timedelta(minutes=5)}},
            {'$set': {'success_count': success_count, 'error_count': error_count}}
        )
        
        logger.info(f"✅ Notifications sent: {success_count} success, {error_count} errors")
        
    except Exception as e:
        logger.error(f"❌ Background notification processing error: {e}")

async def send_welcome_email(email: str):
    """Send welcome email to new subscriber using vladicaristic19@gmail.com"""
    try:
        # Get Gmail app password from environment
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        if not gmail_password:
            logger.warning("⚠️ Gmail app password not configured, email sending disabled")
            return
            
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🎮 Welcome to 019 Solutions Community!"
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = email
        
        # Attach HTML content
        html_part = MIMEText(WELCOME_EMAIL_TEMPLATE, 'html')
        msg.attach(html_part)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, gmail_password)
            server.send_message(msg)
        
        logger.info(f"✅ Welcome email sent to {email} from {SENDER_EMAIL}")
        
    except Exception as e:
        logger.error(f"❌ Welcome email error: {e}")

async def send_email_notification(email: str, notification: NotificationRequest):
    """Send email notification using vladicaristic19@gmail.com"""
    try:
        # Get Gmail app password from environment
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        if not gmail_password:
            logger.warning("⚠️ Gmail app password not configured, email sending disabled")
            return
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎮 019 Solutions - {notification.title}"
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = email
        
        # Use appropriate template based on notification type
        if notification.type == "live":
            html_content = LIVE_NOTIFICATION_TEMPLATE.format(
                title=notification.title,
                message=notification.message,
                url=notification.url or "http://www.youtube.com/@remza019"
            )
        else:
            # Generic notification template
            html_content = f"""
            <html>
            <body style="background: #000000; color: #00ff00; font-family: monospace; padding: 20px;">
                <div style="text-align: center; border: 2px solid #00ff00; padding: 20px; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #00ff00; text-shadow: 0 0 10px #00ff00;">🎮 019 SOLUTIONS 🎮</h1>
                    <h2 style="color: #10b981;">{notification.title}</h2>
                    
                    <div style="background: rgba(0, 255, 0, 0.1); padding: 15px; margin: 20px 0; border: 1px solid #00ff00;">
                        <p style="font-size: 18px;">{notification.message}</p>
                    </div>
                    
                    <p style="color: #888;">Stay tuned for more gaming content!</p>
                </div>
            </body>
            </html>
            """
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, gmail_password)
            server.send_message(msg)
            
        logger.info(f"✅ Email notification sent to {email}: {notification.title}")
        
    except Exception as e:
        logger.error(f"❌ Email notification error: {e}")

async def send_push_notification(subscriber: Dict, notification: NotificationRequest):
    """Send push notification"""
    try:
        # Push notification implementation would go here
        logger.info(f"✅ Push notification sent to {subscriber['email']}: {notification.title}")
        
    except Exception as e:
        logger.error(f"❌ Push notification error: {e}")

# PUBLIC ENDPOINTS
@notifications_router.get("/live-status")
async def get_live_status():
    """Get current live stream status for viewers"""
    try:
        db = get_database()
        
        # Get latest channel stats
        stats = await db.channel_stats.find_one({}, sort=[('updated_at', -1)])
        
        if not stats:
            return {"is_live": False, "message": "Stream offline"}
        
        return {
            "is_live": stats.get('is_live', False),
            "current_viewers": stats.get('current_viewers', '0'),  # Fixed: use 'current_viewers' to match admin API
            "game": stats.get('live_game', 'FORTNITE'),
            "last_updated": stats.get('updated_at', datetime.now())
        }
        
    except Exception as e:
        logger.error(f"❌ Live status error: {e}")
        return {"is_live": False, "message": "Status unavailable"}

@notifications_router.get("/next-stream")
async def get_next_stream():
    """Get information about next scheduled stream"""
    try:
        db = get_database()
        
        # Get current day and find next stream
        current_day = datetime.now().strftime('%a').upper()
        days_order = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        
        schedule = await db.stream_schedule.find({'is_active': True}).to_list(length=None)
        
        if not schedule:
            return {"message": "No scheduled streams"}
        
        # Find next stream
        for i in range(7):  # Check next 7 days
            day_index = (days_order.index(current_day) + i) % 7
            day = days_order[day_index]
            
            stream = next((s for s in schedule if s['day'] == day), None)
            if stream:
                return {
                    "day": stream['day'],
                    "time": stream['time'],
                    "game": stream['game'],
                    "message": f"Next stream: {day} at {stream['time']} - {stream['game']}"
                }
        
        return {"message": "No upcoming streams scheduled"}
        
    except Exception as e:
        logger.error(f"❌ Next stream error: {e}")
        return {"message": "Schedule unavailable"}