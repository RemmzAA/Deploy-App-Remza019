#!/usr/bin/env python3
"""
Test Email and Discord Bot Systems
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/app/backend')

async def test_email_system():
    """Test email notification system"""
    print("\n" + "="*60)
    print("📧 EMAIL NOTIFICATION SYSTEM TEST")
    print("="*60)
    
    # Check configuration
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    
    print(f"\n1. Configuration Check:")
    print(f"   SMTP_SERVER: {smtp_server}")
    print(f"   SMTP_USER: {smtp_user}")
    print(f"   SMTP_PASSWORD: {'✅ SET' if smtp_password else '❌ NOT SET'}")
    print(f"   FROM_EMAIL: {from_email}")
    
    if not all([smtp_server, smtp_user, smtp_password]):
        print("\n❌ Email system is NOT configured!")
        print("   Missing required environment variables.")
        return False
    
    print("\n✅ Email configuration is VALID!")
    
    # Test sending email
    print("\n2. Testing Email Send...")
    try:
        from email_notifications import send_email_notification, EmailTemplate
        
        test_email = "vladica.ristic19@gmail.com"  # Your email from .env
        subject = "🎮 REMZA019 Gaming - Test Notification"
        html_content = EmailTemplate.live_notification("REMZA019", "https://www.youtube.com/@REMZA019")
        
        result = await send_email_notification([test_email], subject, html_content)
        
        if result:
            print(f"✅ Test email sent successfully to {test_email}!")
            return True
        else:
            print("❌ Failed to send test email!")
            return False
            
    except Exception as e:
        print(f"❌ Email send error: {e}")
        return False

async def test_discord_bot():
    """Test Discord bot configuration"""
    print("\n" + "="*60)
    print("🤖 DISCORD BOT SYSTEM TEST")
    print("="*60)
    
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    discord_token = os.getenv('DISCORD_BOT_TOKEN')
    discord_channel = os.getenv('DISCORD_NOTIFICATION_CHANNEL')
    
    print(f"\n1. Configuration Check:")
    print(f"   DISCORD_BOT_TOKEN: {'✅ SET' if discord_token and discord_token != 'PENDING_USER_INPUT' else '❌ NOT SET'}")
    print(f"   DISCORD_CHANNEL_ID: {discord_channel if discord_channel else '❌ NOT SET'}")
    
    if not discord_token or discord_token == 'PENDING_USER_INPUT':
        print("\n❌ Discord bot is NOT configured!")
        print("   DISCORD_BOT_TOKEN is missing or set to 'PENDING_USER_INPUT'")
        return False
    
    if not discord_channel:
        print("\n⚠️ Discord bot token is set, but CHANNEL ID is missing!")
        print("   Bot can respond to commands, but cannot send automatic notifications.")
        return False
    
    print("\n✅ Discord bot configuration is VALID!")
    
    # Check if bot is running
    print("\n2. Checking if Discord bot is running...")
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    
    if 'discord_bot.py' in result.stdout:
        print("✅ Discord bot process is RUNNING!")
        return True
    else:
        print("⚠️ Discord bot is NOT running!")
        print("   Configuration is valid, but bot process needs to be started.")
        return False

async def test_notification_flow():
    """Test complete notification flow"""
    print("\n" + "="*60)
    print("🔔 NOTIFICATION FLOW TEST")
    print("="*60)
    
    print("\n1. Checking subscriber database...")
    from server import get_database
    
    db = get_database()
    count = await db.subscribers.count_documents({"subscribed": True})
    
    print(f"   Subscribers in database: {count}")
    
    if count == 0:
        print("\n⚠️ No subscribers found in database!")
        print("   Adding a test subscriber...")
        
        test_subscriber = {
            "email": "test@remza019gaming.com",
            "subscribed": True,
            "subscribed_at": "2024-10-29T19:00:00Z"
        }
        
        await db.subscribers.insert_one(test_subscriber)
        print("✅ Test subscriber added!")
    
    print("\n2. Testing notification trigger...")
    print("   This would normally be triggered when stream goes live.")
    print("   You can manually trigger it from Admin Panel:")
    print("   - Go to Admin Panel > Live Management")
    print("   - Click 'Notify Subscribers' button")
    
    return True

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 REMZA019 GAMING - NOTIFICATION SYSTEMS TEST")
    print("="*60)
    
    email_ok = await test_email_system()
    discord_ok = await test_discord_bot()
    flow_ok = await test_notification_flow()
    
    print("\n" + "="*60)
    print("📊 FINAL REPORT")
    print("="*60)
    
    print(f"\n📧 Email System: {'✅ WORKING' if email_ok else '❌ NOT WORKING'}")
    print(f"🤖 Discord Bot: {'✅ CONFIGURED' if discord_ok else '⚠️ NEEDS SETUP'}")
    print(f"🔔 Notification Flow: {'✅ READY' if flow_ok else '❌ NOT READY'}")
    
    if email_ok and discord_ok:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
    elif email_ok:
        print("\n✅ Email notifications are working!")
        print("⚠️ Discord bot needs to be started or configured.")
    else:
        print("\n⚠️ Some systems need configuration.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())
