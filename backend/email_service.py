"""
019 Solutions - Email Notification Service
Automated email system for user engagement and notifications
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
from typing import Optional, Dict
import asyncio

logger = logging.getLogger(__name__)

# Email configuration
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@remza019gaming.com')
FROM_NAME = os.environ.get('FROM_NAME', '019 Solutions')

class EmailService:
    def __init__(self):
        self.enabled = bool(SMTP_USER and SMTP_PASSWORD)
        if not self.enabled:
            logger.warning("⚠️ Email service disabled - SMTP credentials not configured")
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email with retry logic"""
        if not self.enabled:
            logger.info(f"📧 [MOCK] Email to {to_email}: {subject}")
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
            message['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASSWORD,
                start_tls=True
            )
            
            logger.info(f"✅ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email send failed to {to_email}: {e}")
            return False
    
    async def send_verification_email(self, to_email: str, username: str, verification_code: str, base_url: str) -> bool:
        """Send email verification"""
        subject = "🎮 Verify Your 019 Solutions Account"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #000; color: #00ff00; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #0a0a0a; border: 2px solid #00ff00; border-radius: 10px; padding: 30px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 32px; font-weight: bold; color: #00ff00; text-shadow: 0 0 10px #00ff00; }}
                .content {{ line-height: 1.6; }}
                .button {{ display: inline-block; padding: 15px 30px; background: #00ff00; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
                .code {{ font-size: 24px; font-weight: bold; color: #00ff00; background: #000; padding: 15px; border-radius: 5px; text-align: center; letter-spacing: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #00ff00; font-size: 12px; color: #888; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎮 019 SOLUTIONS</div>
                </div>
                <div class="content">
                    <h2>Welcome, {username}! 🎉</h2>
                    <p>Thanks for joining 019 Solutions! To complete your registration, please verify your email address.</p>
                    
                    <p>Click the button below to verify your account:</p>
                    <center>
                        <a href="{base_url}/verify?code={verification_code}&email={to_email}" class="button">
                            ✅ Verify My Account
                        </a>
                    </center>
                    
                    <p>Or use this verification code:</p>
                    <div class="code">{verification_code}</div>
                    
                    <p><strong>This code expires in 24 hours.</strong></p>
                    
                    <p>After verification, you'll unlock:</p>
                    <ul>
                        <li>✅ Full access to chat</li>
                        <li>✅ Earn points and level up</li>
                        <li>✅ Participate in polls & predictions</li>
                        <li>✅ Compete on leaderboards</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>If you didn't create this account, you can safely ignore this email.</p>
                    <p>© 2025 019 Solutions. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to 019 Solutions, {username}!
        
        Verification Code: {verification_code}
        
        Click here to verify: {base_url}/verify?code={verification_code}&email={to_email}
        
        This code expires in 24 hours.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_level_up_email(self, to_email: str, username: str, new_level: int, level_name: str, unlocked_features: list) -> bool:
        """Send level up notification"""
        subject = f"🎉 Level Up! You're now Level {new_level}"
        
        features_html = "".join([f"<li>✅ {f}</li>" for f in unlocked_features])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #000; color: #00ff00; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #0a0a0a; border: 2px solid #00ff00; border-radius: 10px; padding: 30px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .celebration {{ font-size: 64px; margin: 20px 0; }}
                .level-badge {{ background: #00ff00; color: #000; padding: 10px 30px; border-radius: 25px; font-size: 24px; font-weight: bold; display: inline-block; }}
                .content {{ line-height: 1.6; }}
                .features {{ background: #000; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="celebration">🎉🎮🏆</div>
                    <h1>LEVEL UP!</h1>
                    <div class="level-badge">Level {new_level}</div>
                </div>
                <div class="content">
                    <p>Congratulations, <strong>{username}</strong>!</p>
                    <p>You've reached <strong>{level_name}</strong> and unlocked new features:</p>
                    <div class="features">
                        <ul>{features_html}</ul>
                    </div>
                    <p>Keep earning points to unlock even more features!</p>
                    <center>
                        <a href="{os.environ.get('FRONTEND_URL', 'https://remote-code-fetch.preview.019solutionsagent.com')}" style="display: inline-block; padding: 15px 30px; background: #00ff00; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0;">
                            🎮 View My Profile
                        </a>
                    </center>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_stream_live_notification(self, to_email: str, username: str, stream_title: str, stream_url: str) -> bool:
        """Send stream going live notification"""
        subject = "🔴 LIVE NOW! REMZA019 is streaming"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #000; color: #ff0000; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #0a0a0a; border: 3px solid #ff0000; border-radius: 10px; padding: 30px; }}
                .live-badge {{ background: #ff0000; color: #fff; padding: 10px 20px; border-radius: 5px; font-weight: bold; display: inline-block; animation: pulse 1s infinite; }}
                @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
                .button {{ display: inline-block; padding: 15px 30px; background: #ff0000; color: #fff; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <center>
                    <div class="live-badge">🔴 LIVE NOW</div>
                    <h1>{stream_title}</h1>
                    <p>Hey {username}, REMZA019 just went live!</p>
                    <a href="{stream_url}" class="button">🎮 Watch Now</a>
                </center>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_leaderboard_notification(self, to_email: str, username: str, old_rank: int, new_rank: int, total_points: int) -> bool:
        """Send leaderboard rank change notification"""
        subject = f"🏆 Leaderboard Update - You're now #{new_rank}!"
        
        rank_change = "up" if new_rank < old_rank else "down"
        emoji = "🚀" if rank_change == "up" else "📉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #000; color: #ffff00; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #0a0a0a; border: 2px solid #ffff00; border-radius: 10px; padding: 30px; }}
                .rank {{ font-size: 48px; font-weight: bold; color: #ffff00; }}
            </style>
        </head>
        <body>
            <div class="container">
                <center>
                    <h1>{emoji} Leaderboard Update</h1>
                    <p>Hey {username}!</p>
                    <p>Your rank changed: <strong>#{old_rank}</strong> → <strong>#{new_rank}</strong></p>
                    <div class="rank">#{new_rank}</div>
                    <p>Total Points: <strong>{total_points}</strong></p>
                    <a href="{os.environ.get('FRONTEND_URL', 'https://remote-code-fetch.preview.019solutionsagent.com')}" style="display: inline-block; padding: 15px 30px; background: #ffff00; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0;">
                        🏆 View Leaderboard
                    </a>
                </center>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_daily_reminder(self, to_email: str, username: str, points: int, streak: int) -> bool:
        """Send daily visit reminder"""
        subject = "🎮 Don't lose your streak! Visit 019 Solutions today"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #000; color: #00ff00; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #0a0a0a; border: 2px solid #00ff00; border-radius: 10px; padding: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <center>
                    <h1>🔥 {streak} Day Streak!</h1>
                    <p>Hey {username}!</p>
                    <p>You have <strong>{points} points</strong> and a <strong>{streak} day streak</strong>!</p>
                    <p>Don't break it! Visit today to earn your +5 daily bonus.</p>
                    <a href="{os.environ.get('FRONTEND_URL', 'https://remote-code-fetch.preview.019solutionsagent.com')}" style="display: inline-block; padding: 15px 30px; background: #00ff00; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0;">
                        🎮 Visit Now (+5 Points)
                    </a>
                </center>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)

# Global email service instance
email_service = EmailService()
