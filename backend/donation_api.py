"""
REMZA019 Gaming - Donation System with Stripe Integration
Support the gaming channel with secure payment processing
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import json
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from 019solutionsintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
donation_router = APIRouter(prefix="/api/donations", tags=["donations"])


# PayPal configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'


# Database connection
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is required")

async def get_database():
    client = AsyncIOMotorClient(MONGO_URL)
    return client.remza019_gaming

# Email configuration
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'vladicaristic19@gmail.com')
SENDER_NAME = os.environ.get('SENDER_NAME', 'REMZA019 Gaming')

# Donation packages - FIXED AMOUNTS FOR SECURITY
DONATION_PACKAGES = {
    "coffee": {"amount": 5.0, "currency": "usd", "name": "☕ Buy REMZA019 a Coffee", "description": "Support with a coffee!"},
    "pizza": {"amount": 15.0, "currency": "usd", "name": "🍕 Buy REMZA019 a Pizza", "description": "Fuel the gaming sessions!"},
    "gaming_gear": {"amount": 50.0, "currency": "usd", "name": "🎮 Gaming Gear Support", "description": "Help upgrade gaming setup!"},
    "streaming_support": {"amount": 100.0, "currency": "usd", "name": "📺 Streaming Support", "description": "Support streaming equipment!"},
    "custom": {"amount": 0.0, "currency": "usd", "name": "💝 Custom Amount", "description": "Choose your support level!"}
}

# Pydantic Models
class DonationRequest(BaseModel):
    package_id: str = Field(..., description="Donation package ID")
    amount: Optional[float] = Field(None, description="Custom amount for 'custom' package only")
    donor_name: Optional[str] = Field(None, description="Donor name (optional)")
    donor_email: Optional[EmailStr] = Field(None, description="Donor email for receipt")
    message: Optional[str] = Field(None, description="Optional message from donor")
    origin_url: str = Field(..., description="Frontend origin URL")

class DonationGoal(BaseModel):
    id: str
    title: str
    description: str
    target_amount: float
    current_amount: float
    currency: str
    deadline: Optional[datetime]
    is_active: bool

# Initialize Stripe
async def get_stripe_checkout(request: Request):
    """Initialize Stripe checkout with webhook URL"""
    stripe_api_key = os.environ.get('STRIPE_API_KEY')
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/donations/webhook/stripe"
    
    return StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)

# Email Templates
DONATION_RECEIPT_TEMPLATE = """
<html>
<body style="background: #000000; color: #00ff00; font-family: monospace; padding: 20px;">
    <div style="text-align: center; border: 2px solid #00ff00; padding: 20px; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #00ff00; text-shadow: 0 0 10px #00ff00;">🎮 REMZA019 GAMING 🎮</h1>
        <h2 style="color: #10b981;">Thank You for Your Support!</h2>
        
        <div style="background: rgba(0, 255, 0, 0.1); padding: 20px; margin: 20px 0; border: 1px solid #00ff00;">
            <h3>Donation Receipt</h3>
            <p><strong>Amount:</strong> ${amount} {currency}</p>
            <p><strong>Package:</strong> {package_name}</p>
            <p><strong>Date:</strong> {date}</p>
            <p><strong>Transaction ID:</strong> {transaction_id}</p>
            {donor_message}
        </div>
        
        <div style="margin: 20px 0;">
            <p>🎯 Your support helps REMZA019 create amazing FORTNITE content!</p>
            <p>🔴 Follow the streams on YouTube: @remza019</p>
            <p>💬 Join the gaming community chat</p>
        </div>
        
        <p style="color: #888; font-size: 0.9rem;">
            This is an automated receipt. Keep this for your records.
        </p>
    </div>
</body>
</html>
"""

DONATION_NOTIFICATION_TEMPLATE = """
<html>
<body style="background: #000000; color: #00ff00; font-family: monospace; padding: 20px;">
    <div style="text-align: center; border: 2px solid #00ff00; padding: 20px; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #00ff00; text-shadow: 0 0 10px #00ff00;">💰 NEW DONATION RECEIVED!</h1>
        
        <div style="background: rgba(0, 255, 0, 0.1); padding: 15px; margin: 20px 0; border: 1px solid #00ff00;">
            <p><strong>Amount:</strong> ${amount} {currency}</p>
            <p><strong>From:</strong> {donor_name}</p>
            <p><strong>Package:</strong> {package_name}</p>
            <p><strong>Date:</strong> {date}</p>
            {donor_message}
        </div>
        
        <p>🎮 Another supporter joins the REMZA019 Gaming community!</p>
    </div>
</body>
</html>
"""

async def send_donation_receipt(donor_email: str, donation_data: Dict):
    """Send donation receipt email to donor"""
    try:
        if not GMAIL_APP_PASSWORD:
            logger.warning("Gmail app password not configured, skipping receipt email")
            return
        
        # Format donor message
        donor_message = ""
        if donation_data.get('message'):
            donor_message = f"<p><strong>Your Message:</strong> \"{donation_data['message']}\"</p>"
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎮 REMZA019 Gaming - Donation Receipt (${donation_data['amount']})"
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = donor_email
        
        # HTML content
        html_content = DONATION_RECEIPT_TEMPLATE.format(
            amount=donation_data['amount'],
            currency=donation_data['currency'].upper(),
            package_name=donation_data['package_name'],
            date=donation_data['date'],
            transaction_id=donation_data['transaction_id'],
            donor_message=donor_message
        )
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Donation receipt sent to {donor_email}")
        
    except Exception as e:
        logger.error(f"❌ Error sending donation receipt: {e}")

async def notify_admin_donation(donation_data: Dict):
    """Notify admin about new donation"""
    try:
        if not GMAIL_APP_PASSWORD:
            logger.warning("Gmail app password not configured, skipping admin notification")
            return
        
        # Format donor message
        donor_message = ""
        if donation_data.get('message'):
            donor_message = f"<p><strong>Donor Message:</strong> \"{donation_data['message']}\"</p>"
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎮 NEW DONATION: ${donation_data['amount']} from {donation_data.get('donor_name', 'Anonymous')}"
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = SENDER_EMAIL
        
        # HTML content
        html_content = DONATION_NOTIFICATION_TEMPLATE.format(
            amount=donation_data['amount'],
            currency=donation_data['currency'].upper(),
            donor_name=donation_data.get('donor_name', 'Anonymous Supporter'),
            package_name=donation_data['package_name'],
            date=donation_data['date'],
            donor_message=donor_message
        )
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Donation notification sent to admin")
        
    except Exception as e:
        logger.error(f"❌ Error sending donation notification: {e}")

# API Endpoints

@donation_router.get("/packages")
async def get_donation_packages():
    """Get available donation packages"""
    return {
        "packages": DONATION_PACKAGES,
        "currency": "USD",
        "description": "Support REMZA019 Gaming with secure donations"
    }

@donation_router.post("/checkout")
async def create_donation_checkout(
    request: Request,
    donation: DonationRequest,
    background_tasks: BackgroundTasks
):
    """Create Stripe checkout session for donation"""
    try:
        # Validate package
        if donation.package_id not in DONATION_PACKAGES:
            raise HTTPException(status_code=400, detail="Invalid donation package")
        
        package = DONATION_PACKAGES[donation.package_id]
        
        # Determine amount
        if donation.package_id == "custom":
            if not donation.amount or donation.amount < 1.0:
                raise HTTPException(status_code=400, detail="Custom amount must be at least $1.00")
            amount = float(donation.amount)
        else:
            amount = package["amount"]
        
        # Initialize Stripe
        stripe_checkout = await get_stripe_checkout(request)
        
        # Create success and cancel URLs
        success_url = f"{donation.origin_url}/donation-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{donation.origin_url}/donation-cancelled"
        
        # Prepare metadata
        metadata = {
            "package_id": donation.package_id,
            "package_name": package["name"],
            "donor_name": donation.donor_name or "Anonymous",
            "donor_email": donation.donor_email or "",
            "message": donation.message or "",
            "source": "remza019_gaming_website"
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency=package["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store transaction in database
        db = await get_database()
        transaction = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "amount": amount,
            "currency": package["currency"],
            "package_id": donation.package_id,
            "package_name": package["name"],
            "donor_name": donation.donor_name,
            "donor_email": donation.donor_email,
            "message": donation.message,
            "payment_status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "metadata": metadata
        }
        
        await db.payment_transactions.insert_one(transaction)
        
        logger.info(f"Created donation checkout for ${amount} - Session: {session.session_id}")
        
        return {
            "success": True,
            "checkout_url": session.url,
            "session_id": session.session_id,
            "amount": amount,
            "currency": package["currency"]
        }
        
    except Exception as e:
        logger.error(f"Donation checkout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create donation checkout")

@donation_router.get("/status/{session_id}")
async def get_donation_status(
    session_id: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Check donation payment status"""
    try:
        db = await get_database()
        
        # Get transaction from database
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Check if already processed
        if transaction["payment_status"] == "completed":
            return {
                "status": "complete",
                "payment_status": "paid",
                "amount": transaction["amount"],
                "currency": transaction["currency"],
                "package_name": transaction["package_name"]
            }
        
        # Check with Stripe
        stripe_checkout = await get_stripe_checkout(request)
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction status
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "payment_status": checkout_status.payment_status,
                    "stripe_status": checkout_status.status,
                    "updated_at": datetime.now()
                }
            }
        )
        
        # If payment completed, process donation
        if checkout_status.payment_status == "paid" and transaction["payment_status"] != "completed":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "completed"}}
            )
            
            # Process successful donation
            background_tasks.add_task(process_successful_donation, transaction)
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount": checkout_status.amount_total / 100,  # Convert from cents
            "currency": checkout_status.currency,
            "package_name": transaction["package_name"]
        }
        
    except Exception as e:
        logger.error(f"Get donation status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get donation status")

async def process_successful_donation(transaction: Dict):
    """Process successful donation - send emails and update goals"""
    try:
        # Prepare donation data for emails
        donation_data = {
            "amount": transaction["amount"],
            "currency": transaction["currency"],
            "package_name": transaction["package_name"],
            "donor_name": transaction.get("donor_name", "Anonymous Supporter"),
            "message": transaction.get("message", ""),
            "date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "transaction_id": transaction["session_id"][:16]
        }
        
        # Send receipt to donor if email provided
        if transaction.get("donor_email"):
            await send_donation_receipt(transaction["donor_email"], donation_data)
        
        # Notify admin about donation
        await notify_admin_donation(donation_data)
        
        # Update donation goals
        db = await get_database()
        
        # Add to total donations
        await db.donation_stats.update_one(
            {"type": "total"},
            {
                "$inc": {
                    "total_amount": transaction["amount"],
                    "total_donations": 1
                },
                "$set": {"updated_at": datetime.now()}
            },
            upsert=True
        )
        
        # Record individual donation
        donation_record = {
            "id": str(uuid.uuid4()),
            "session_id": transaction["session_id"],
            "amount": transaction["amount"],
            "currency": transaction["currency"],
            "package_name": transaction["package_name"],
            "donor_name": transaction.get("donor_name", "Anonymous"),
            "message": transaction.get("message", ""),
            "created_at": datetime.now(),
            "is_public": True  # Can be displayed on website
        }
        
        await db.donations.insert_one(donation_record)
        
        logger.info(f"✅ Processed successful donation: ${transaction['amount']} from {transaction.get('donor_name', 'Anonymous')}")
        
    except Exception as e:
        logger.error(f"❌ Error processing successful donation: {e}")

@donation_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        stripe_checkout = await get_stripe_checkout(request)
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Stripe webhook received: {webhook_response.event_type}")
        
        # Handle specific webhook events
        if webhook_response.event_type == "checkout.session.completed":
            db = await get_database()
            
            # Update transaction
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": webhook_response.payment_status,
                        "webhook_processed": True,
                        "updated_at": datetime.now()
                    }
                }
            )
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

@donation_router.get("/recent")
async def get_recent_donations(limit: int = 10):
    """Get recent public donations for display"""
    try:
        db = await get_database()
        
        donations = await db.donations.find(
            {"is_public": True}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Format for frontend
        formatted_donations = []
        for donation in donations:
            formatted_donations.append({
                "donor_name": donation.get("donor_name", "Anonymous"),
                "amount": donation["amount"],
                "currency": donation["currency"],
                "package_name": donation["package_name"],
                "message": donation.get("message", ""),
                "date": donation["created_at"].strftime("%B %d, %Y"),
                "relative_date": donation["created_at"]
            })
        
        return {"donations": formatted_donations}
        
    except Exception as e:
        logger.error(f"Get recent donations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent donations")

@donation_router.get("/stats")
async def get_donation_stats():
    """Get donation statistics"""
    try:
        db = await get_database()
        
        stats = await db.donation_stats.find_one({"type": "total"})
        
        if not stats:
            return {
                "total_amount": 0.0,
                "total_donations": 0,
                "currency": "USD"
            }
        
        return {
            "total_amount": stats.get("total_amount", 0.0),
            "total_donations": stats.get("total_donations", 0),
            "currency": "USD",
            "last_updated": stats.get("updated_at")
        }
        
    except Exception as e:
        logger.error(f"Get donation stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get donation stats")

# Export router
def get_donation_router():
    return donation_router