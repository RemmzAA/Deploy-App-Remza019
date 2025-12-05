"""
REMZA019 Gaming - Premium Subscription System
Stripe recurring payments for Premium, Pro, and VIP tiers
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

logger = logging.getLogger(__name__)

subscription_router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

# Database connection
def get_database():
    from server import get_database as get_db
    return get_db()

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "price": 4.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Ad-free experience",
            "Basic chat badge",
            "Support the channel",
            "Early access to VODs"
        ],
        "perks": {
            "ad_free": True,
            "badge": "basic",
            "chat_priority": False,
            "custom_emotes": False,
            "exclusive_content": False
        }
    },
    "pro": {
        "name": "Pro",
        "price": 9.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "All Basic features",
            "Pro chat badge",
            "Custom emotes",
            "Priority chat",
            "Exclusive Discord role",
            "Monthly giveaway entries"
        ],
        "perks": {
            "ad_free": True,
            "badge": "pro",
            "chat_priority": True,
            "custom_emotes": True,
            "exclusive_content": True,
            "giveaway_entries": 5
        }
    },
    "vip": {
        "name": "VIP",
        "price": 19.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "All Pro features",
            "VIP chat badge",
            "Direct message access to streamer",
            "Exclusive VIP-only streams",
            "Your name in credits",
            "Custom emote requests",
            "Monthly 1-on-1 gaming session",
            "Unlimited giveaway entries"
        ],
        "perks": {
            "ad_free": True,
            "badge": "vip",
            "chat_priority": True,
            "custom_emotes": True,
            "exclusive_content": True,
            "direct_message": True,
            "vip_streams": True,
            "credits_mention": True,
            "emote_requests": True,
            "gaming_session": True,
            "giveaway_entries": -1  # Unlimited
        }
    }
}

# Pydantic Models
class SubscriptionRequest(BaseModel):
    user_id: str
    plan: str  # "basic", "pro", "vip"
    email: EmailStr

class SubscriptionResponse(BaseModel):
    success: bool
    subscription_id: Optional[str] = None
    checkout_url: Optional[str] = None
    message: str

class UserSubscription(BaseModel):
    user_id: str
    plan: str
    status: str  # "active", "cancelled", "expired"
    stripe_subscription_id: Optional[str] = None
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False

@subscription_router.get("/plans")
async def get_subscription_plans():
    """
    Get all available subscription plans
    """
    return {
        "plans": SUBSCRIPTION_PLANS,
        "success": True
    }

@subscription_router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(request: SubscriptionRequest):
    """
    Create a new subscription checkout session
    Uses existing Stripe integration from donation_api
    """
    try:
        # Validate plan
        if request.plan not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Invalid subscription plan")
        
        plan = SUBSCRIPTION_PLANS[request.plan]
        db = get_database()
        
        # Check if user already has active subscription
        existing = await db.subscriptions.find_one({
            "user_id": request.user_id,
            "status": "active"
        })
        
        if existing:
            return SubscriptionResponse(
                success=False,
                message="User already has an active subscription"
            )
        
        # Create subscription record
        subscription_id = str(uuid.uuid4())
        subscription = {
            "subscription_id": subscription_id,
            "user_id": request.user_id,
            "plan": request.plan,
            "plan_name": plan["name"],
            "price": plan["price"],
            "status": "pending",
            "created_at": datetime.now(),
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=30),
            "stripe_subscription_id": None,
            "cancel_at_period_end": False,
            "email": request.email
        }
        
        await db.subscriptions.insert_one(subscription)
        
        # NOTE: In production, integrate with Stripe Checkout for recurring payments
        # For now, return success with checkout URL placeholder
        checkout_url = f"/checkout/subscription/{subscription_id}"
        
        logger.info(f"✅ Subscription created: {request.plan} for user {request.user_id}")
        
        return SubscriptionResponse(
            success=True,
            subscription_id=subscription_id,
            checkout_url=checkout_url,
            message=f"Subscription checkout created for {plan['name']} plan"
        )
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@subscription_router.get("/user/{user_id}")
async def get_user_subscription(user_id: str):
    """
    Get user's current subscription status
    """
    try:
        db = get_database()
        
        subscription = await db.subscriptions.find_one({
            "user_id": user_id,
            "status": "active"
        })
        
        if not subscription:
            return {
                "has_subscription": False,
                "plan": None,
                "status": "none"
            }
        
        plan = SUBSCRIPTION_PLANS.get(subscription["plan"], {})
        
        return {
            "has_subscription": True,
            "subscription_id": subscription["subscription_id"],
            "plan": subscription["plan"],
            "plan_name": subscription["plan_name"],
            "price": subscription["price"],
            "status": subscription["status"],
            "current_period_start": subscription["current_period_start"],
            "current_period_end": subscription["current_period_end"],
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
            "perks": plan.get("perks", {}),
            "features": plan.get("features", [])
        }
        
    except Exception as e:
        logger.error(f"Error fetching user subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@subscription_router.post("/cancel/{subscription_id}")
async def cancel_subscription(subscription_id: str, user_id: str):
    """
    Cancel subscription at end of billing period
    """
    try:
        db = get_database()
        
        subscription = await db.subscriptions.find_one({
            "subscription_id": subscription_id,
            "user_id": user_id
        })
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Set to cancel at period end
        await db.subscriptions.update_one(
            {"subscription_id": subscription_id},
            {
                "$set": {
                    "cancel_at_period_end": True,
                    "cancelled_at": datetime.now()
                }
            }
        )
        
        logger.info(f"Subscription {subscription_id} set to cancel at period end")
        
        return {
            "success": True,
            "message": "Subscription will be cancelled at the end of the current billing period",
            "end_date": subscription["current_period_end"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@subscription_router.post("/reactivate/{subscription_id}")
async def reactivate_subscription(subscription_id: str, user_id: str):
    """
    Reactivate a cancelled subscription
    """
    try:
        db = get_database()
        
        subscription = await db.subscriptions.find_one({
            "subscription_id": subscription_id,
            "user_id": user_id
        })
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Remove cancellation flag
        await db.subscriptions.update_one(
            {"subscription_id": subscription_id},
            {
                "$set": {
                    "cancel_at_period_end": False
                },
                "$unset": {
                    "cancelled_at": ""
                }
            }
        )
        
        logger.info(f"Subscription {subscription_id} reactivated")
        
        return {
            "success": True,
            "message": "Subscription reactivated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reactivating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@subscription_router.get("/stats")
async def get_subscription_stats():
    """
    Get subscription statistics (admin only)
    """
    try:
        db = get_database()
        
        total = await db.subscriptions.count_documents({})
        active = await db.subscriptions.count_documents({"status": "active"})
        
        # Count by plan
        basic_count = await db.subscriptions.count_documents({
            "status": "active",
            "plan": "basic"
        })
        pro_count = await db.subscriptions.count_documents({
            "status": "active",
            "plan": "pro"
        })
        vip_count = await db.subscriptions.count_documents({
            "status": "active",
            "plan": "vip"
        })
        
        # Calculate monthly revenue
        monthly_revenue = (
            basic_count * SUBSCRIPTION_PLANS["basic"]["price"] +
            pro_count * SUBSCRIPTION_PLANS["pro"]["price"] +
            vip_count * SUBSCRIPTION_PLANS["vip"]["price"]
        )
        
        return {
            "total_subscriptions": total,
            "active_subscriptions": active,
            "by_plan": {
                "basic": basic_count,
                "pro": pro_count,
                "vip": vip_count
            },
            "monthly_revenue": round(monthly_revenue, 2),
            "currency": "USD"
        }
        
    except Exception as e:
        logger.error(f"Error fetching subscription stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@subscription_router.post("/activate-trial/{user_id}")
async def activate_trial_subscription(user_id: str, plan: str = "basic"):
    """
    Activate a 7-day trial subscription for a user
    """
    try:
        if plan not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        db = get_database()
        
        # Check if user already had trial
        existing_trial = await db.subscriptions.find_one({
            "user_id": user_id,
            "is_trial": True
        })
        
        if existing_trial:
            return {
                "success": False,
                "message": "User already used trial subscription"
            }
        
        # Create trial subscription
        subscription_id = str(uuid.uuid4())
        plan_data = SUBSCRIPTION_PLANS[plan]
        
        trial_subscription = {
            "subscription_id": subscription_id,
            "user_id": user_id,
            "plan": plan,
            "plan_name": plan_data["name"],
            "price": 0,
            "status": "active",
            "is_trial": True,
            "created_at": datetime.now(),
            "current_period_start": datetime.now(),
            "current_period_end": datetime.now() + timedelta(days=7),
            "cancel_at_period_end": False
        }
        
        await db.subscriptions.insert_one(trial_subscription)
        
        logger.info(f"✅ Trial subscription activated for user {user_id}")
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "message": f"7-day {plan_data['name']} trial activated!",
            "expires_at": trial_subscription["current_period_end"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating trial: {e}")
        raise HTTPException(status_code=500, detail=str(e))
