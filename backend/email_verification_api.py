"""
REMZA019 Gaming - Email Verification System
Secure email verification before users can access full features
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import uuid
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

email_verification_router = APIRouter(prefix="/api/auth", tags=["email-verification"])

# Database connection
def get_database():
    mongodb_url = os.environ.get('MONGO_URL')
    if not mongodb_url:
        raise ValueError("MONGO_URL environment variable is required")
    client = AsyncIOMotorClient(mongodb_url)
    return client.remza019_gaming

# Models
class EmailVerificationRequest(BaseModel):
    email: EmailStr
    username: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str

# Email Templates
VERIFICATION_EMAIL_TEMPLATE = """
<html>
<head>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
            color: #00ff00;
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #00ff00;
            text-shadow: 0 0 15px #00ff00;
            font-size: 32px;
            margin: 0;
        }}
        .welcome-message {{
            background: rgba(0, 255, 0, 0.1);
            padding: 20px;
            border-left: 4px solid #00ff00;
            margin: 20px 0;
        }}
        .token-box {{
            background: #000000;
            border: 2px solid #00ff00;
            padding: 20px;
            margin: 25px 0;
            text-align: center;
            border-radius: 8px;
        }}
        .token {{
            font-size: 28px;
            font-weight: bold;
            color: #00ff00;
            letter-spacing: 3px;
            text-shadow: 0 0 10px #00ff00;
        }}
        .verify-button {{
            display: inline-block;
            background: #00ff00;
            color: #000000;
            padding: 15px 40px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            font-size: 18px;
            margin: 20px 0;
            transition: all 0.3s;
        }}
        .verify-button:hover {{
            background: #10b981;
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }}
        .features {{
            background: rgba(0, 255, 0, 0.05);
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .features ul {{
            text-align: left;
            padding-left: 25px;
        }}
        .features li {{
            margin: 10px 0;
            color: #00ff00;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #00ff00;
            color: #666;
            font-size: 12px;
        }}
        .expiry-warning {{
            color: #ff0000;
            font-weight: bold;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 REMZA019 GAMING 🎮</h1>
        </div>
        
        <div class="welcome-message">
            <h2 style="color: #10b981; margin-top: 0;">Welcome, {username}!</h2>
            <p style="font-size: 16px;">Thanks for joining the REMZA019 Gaming community!</p>
        </div>
        
        <p style="font-size: 14px; line-height: 1.6;">
            To activate your account and unlock all gaming features, please verify your email address by entering this verification code:
        </p>
        
        <div class="token-box">
            <p style="margin: 0; color: #888; font-size: 14px;">Your Verification Code:</p>
            <div class="token">{token}</div>
        </div>
        
        <div style="text-align: center;">
            <a href="{verification_url}" class="verify-button">
                ✅ VERIFY EMAIL NOW
            </a>
        </div>
        
        <div class="expiry-warning">
            ⚠️ This code expires in 24 hours!
        </div>
        
        <div class="features">
            <p style="font-weight: bold; color: #10b981; margin-top: 0;">🎯 What you'll unlock:</p>
            <ul>
                <li>🔴 <strong>LIVE stream notifications</strong> - Never miss a stream!</li>
                <li>💬 <strong>Group chat access</strong> - Chat with other gamers</li>
                <li>📊 <strong>Points & rewards system</strong> - Earn rewards for watching</li>
                <li>🗳️ <strong>Polls & predictions</strong> - Participate in community votes</li>
                <li>🏆 <strong>Leaderboard ranking</strong> - Compete for top spots</li>
                <li>🎮 <strong>Exclusive content</strong> - Early access to videos</li>
            </ul>
        </div>
        
        <p style="color: #888; font-size: 13px; margin-top: 30px;">
            If you didn't sign up for REMZA019 Gaming, please ignore this email.
        </p>
        
        <div class="footer">
            <p>© 2024 REMZA019 Gaming - Serbia's Premier Gaming Channel</p>
            <p style="color: #10b981;">🎮 Game On! 🎮</p>
        </div>
    </div>
</body>
</html>
"""

VERIFICATION_SUCCESS_EMAIL = """
<html>
<head>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
            color: #00ff00;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
        }}
        h1 {{
            color: #00ff00;
            text-shadow: 0 0 15px #00ff00;
        }}
        .success-icon {{
            font-size: 80px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Email Verified!</h1>
        <h2 style="color: #10b981;">Welcome to REMZA019 Gaming, {username}!</h2>
        <p style="font-size: 16px;">Your account is now fully activated!</p>
        <p>You now have access to all gaming features and can start earning points right away!</p>
        <p style="margin-top: 30px; color: #10b981; font-size: 18px; font-weight: bold;">🎮 Let's Game! 🎮</p>
    </div>
</body>
</html>
"""

def generate_verification_token() -> str:
    """Generate secure 6-digit verification token"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

async def send_verification_email(email: str, username: str, token: str):
    """Send verification email"""
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
        msg['Subject'] = f"🎮 Verify Your REMZA019 Gaming Account - Code: {token}"
        msg['From'] = f"REMZA019 Gaming <{from_email}>"
        msg['To'] = email
        
        # Verification URL (redirect to frontend)
        verification_url = f"https://gamecms-1.preview.019solutionsagent.com/?verify={token}&email={email}"
        
        # Attach HTML content
        html_content = VERIFICATION_EMAIL_TEMPLATE.format(
            username=username,
            token=token,
            verification_url=verification_url
        )
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"✅ Verification email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email send error: {e}")
        return False

async def send_success_email(email: str, username: str):
    """Send success confirmation email"""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", smtp_user)
        
        if not smtp_user or not smtp_password:
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🎉 Welcome to REMZA019 Gaming - Account Activated!"
        msg['From'] = f"REMZA019 Gaming <{from_email}>"
        msg['To'] = email
        
        html_content = VERIFICATION_SUCCESS_EMAIL.format(username=username)
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"✅ Success email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Success email error: {e}")
        return False

# API Endpoints

@email_verification_router.post("/send-verification")
async def send_verification(request: EmailVerificationRequest, background_tasks: BackgroundTasks):
    """Send verification email to user"""
    try:
        db = get_database()
        
        # Check if email already verified
        viewer = await db.viewers.find_one({"email": request.email})
        if viewer and viewer.get("email_verified"):
            return {
                "success": False,
                "message": "Email already verified"
            }
        
        # Generate verification token
        token = generate_verification_token()
        expires_at = datetime.now() + timedelta(hours=24)
        
        # Store verification token
        verification_data = {
            "email": request.email,
            "username": request.username,
            "token": token,
            "expires_at": expires_at,
            "created_at": datetime.now(),
            "verified": False
        }
        
        await db.email_verifications.update_one(
            {"email": request.email},
            {"$set": verification_data},
            upsert=True
        )
        
        # Send email in background
        background_tasks.add_task(send_verification_email, request.email, request.username, token)
        
        logger.info(f"📧 Verification email queued for {request.email}")
        
        return {
            "success": True,
            "message": "Verification email sent! Check your inbox.",
            "expires_in": "24 hours"
        }
        
    except Exception as e:
        logger.error(f"❌ Send verification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

@email_verification_router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest, background_tasks: BackgroundTasks):
    """Verify email with token"""
    try:
        db = get_database()
        
        # Find verification record
        verification = await db.email_verifications.find_one({
            "email": request.email,
            "token": request.token
        })
        
        if not verification:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        # Check if expired
        if datetime.now() > verification["expires_at"]:
            raise HTTPException(status_code=400, detail="Verification code expired")
        
        # Check if already verified
        if verification.get("verified"):
            return {
                "success": True,
                "message": "Email already verified",
                "already_verified": True
            }
        
        # Mark as verified
        await db.email_verifications.update_one(
            {"email": request.email},
            {"$set": {"verified": True, "verified_at": datetime.now()}}
        )
        
        # Update viewer account
        await db.viewers.update_one(
            {"email": request.email},
            {"$set": {"email_verified": True, "verified_at": datetime.now()}}
        )
        
        # Subscribe to notifications by default
        await db.subscribers.update_one(
            {"email": request.email},
            {
                "$set": {
                    "id": str(uuid.uuid4()),
                    "email": request.email,
                    "preferences": {
                        "live_notifications": True,
                        "schedule_updates": True,
                        "new_videos": True,
                        "email_notifications": True
                    },
                    "subscribed_at": datetime.now(),
                    "is_active": True,
                    "subscribed": True
                }
            },
            upsert=True
        )
        
        # Send success email
        background_tasks.add_task(send_success_email, request.email, verification["username"])
        
        logger.info(f"✅ Email verified: {request.email}")
        
        return {
            "success": True,
            "message": "Email verified successfully!",
            "email": request.email,
            "verified_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Verify email error: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

@email_verification_router.post("/resend-verification")
async def resend_verification(email: EmailStr, background_tasks: BackgroundTasks):
    """Resend verification email"""
    try:
        db = get_database()
        
        # Find existing verification
        verification = await db.email_verifications.find_one({"email": email})
        
        if not verification:
            raise HTTPException(status_code=404, detail="No verification request found")
        
        if verification.get("verified"):
            return {
                "success": False,
                "message": "Email already verified"
            }
        
        # Generate new token
        token = generate_verification_token()
        expires_at = datetime.now() + timedelta(hours=24)
        
        await db.email_verifications.update_one(
            {"email": email},
            {
                "$set": {
                    "token": token,
                    "expires_at": expires_at,
                    "resent_at": datetime.now()
                }
            }
        )
        
        # Send email
        background_tasks.add_task(send_verification_email, email, verification["username"], token)
        
        logger.info(f"📧 Verification email resent to {email}")
        
        return {
            "success": True,
            "message": "Verification email resent! Check your inbox."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resend verification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend verification")

@email_verification_router.get("/check-verification/{email}")
async def check_verification_status(email: str):
    """Check if email is verified"""
    try:
        db = get_database()
        
        viewer = await db.viewers.find_one({"email": email})
        
        if not viewer:
            return {
                "email": email,
                "verified": False,
                "exists": False
            }
        
        return {
            "email": email,
            "verified": viewer.get("email_verified", False),
            "exists": True,
            "username": viewer.get("username")
        }
        
    except Exception as e:
        logger.error(f"❌ Check verification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check verification status")
