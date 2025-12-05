"""
REMZA019 Gaming - Referral & Affiliate Program
Viral growth system with rewards for inviting friends
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import secrets
import logging

logger = logging.getLogger(__name__)

referral_router = APIRouter(prefix="/api/referrals", tags=["referrals"])

# Database connection
def get_database():
    from server import get_database as get_db
    return get_db()

# Referral Rewards
REFERRAL_REWARDS = {
    "referrer": {
        "signup": 50,  # Points for referrer when someone signs up
        "first_activity": 100,  # Bonus when referred user completes first activity
        "subscription": 500  # Bonus when referred user subscribes
    },
    "referred": {
        "signup": 50  # Welcome bonus for using referral code
    },
    "milestones": {
        10: {"points": 1000, "badge": "Recruiter Bronze"},
        25: {"points": 2500, "badge": "Recruiter Silver"},
        50: {"points": 5000, "badge": "Recruiter Gold"},
        100: {"points": 15000, "badge": "Recruiter Diamond"}
    }
}

# Pydantic Models
class ReferralCode(BaseModel):
    code: str
    user_id: str
    username: str
    created_at: datetime
    uses: int
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: bool

class UseReferralRequest(BaseModel):
    referred_user_id: str
    referred_username: str
    referral_code: str

@referral_router.post("/generate")
async def generate_referral_code(user_id: str, username: str):
    """
    Generate a unique referral code for a user
    """
    try:
        db = get_database()
        
        # Check if user already has a code
        existing = await db.referrals.find_one({"user_id": user_id})
        
        if existing:
            return {
                "success": True,
                "referral_code": existing["code"],
                "message": "Using existing referral code",
                "referral_link": f"/join?ref={existing['code']}"
            }
        
        # Generate unique code
        code = f"{username.upper()[:4]}{secrets.token_hex(4).upper()}"
        
        referral_data = {
            "code": code,
            "user_id": user_id,
            "username": username,
            "created_at": datetime.now(),
            "uses": 0,
            "total_points_earned": 0,
            "referred_users": [],
            "is_active": True
        }
        
        await db.referrals.insert_one(referral_data)
        
        logger.info(f"✅ Referral code generated: {code} for user {username}")
        
        return {
            "success": True,
            "referral_code": code,
            "referral_link": f"/join?ref={code}",
            "message": "Referral code generated successfully!"
        }
        
    except Exception as e:
        logger.error(f"Error generating referral code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@referral_router.post("/use")
async def use_referral_code(request: UseReferralRequest):
    """
    Apply a referral code when new user signs up
    """
    try:
        db = get_database()
        
        # Find referral code
        referral = await db.referrals.find_one({"code": request.referral_code})
        
        if not referral:
            raise HTTPException(status_code=404, detail="Invalid referral code")
        
        if not referral["is_active"]:
            raise HTTPException(status_code=400, detail="Referral code is inactive")
        
        # Check if user already used a referral code
        existing_use = await db.referral_uses.find_one({
            "referred_user_id": request.referred_user_id
        })
        
        if existing_use:
            return {
                "success": False,
                "message": "User already used a referral code"
            }
        
        # Reward referrer
        referrer_reward = REFERRAL_REWARDS["referrer"]["signup"]
        await db.viewers.update_one(
            {"user_id": referral["user_id"]},
            {"$inc": {"points": referrer_reward}}
        )
        
        # Reward referred user
        referred_reward = REFERRAL_REWARDS["referred"]["signup"]
        await db.viewers.update_one(
            {"user_id": request.referred_user_id},
            {"$inc": {"points": referred_reward}}
        )
        
        # Record referral use
        await db.referral_uses.insert_one({
            "referral_code": request.referral_code,
            "referrer_id": referral["user_id"],
            "referrer_username": referral["username"],
            "referred_user_id": request.referred_user_id,
            "referred_username": request.referred_username,
            "created_at": datetime.now(),
            "rewards_given": {
                "referrer": referrer_reward,
                "referred": referred_reward
            }
        })
        
        # Update referral stats
        new_uses = referral["uses"] + 1
        await db.referrals.update_one(
            {"code": request.referral_code},
            {
                "$inc": {
                    "uses": 1,
                    "total_points_earned": referrer_reward
                },
                "$push": {"referred_users": request.referred_user_id}
            }
        )
        
        # Check for milestone rewards
        milestone_reward = REFERRAL_REWARDS["milestones"].get(new_uses)
        if milestone_reward:
            await db.viewers.update_one(
                {"user_id": referral["user_id"]},
                {
                    "$inc": {"points": milestone_reward["points"]},
                    "$push": {"badges": milestone_reward["badge"]}
                }
            )
            
            logger.info(f"🎉 Milestone reached! {referral['username']} reached {new_uses} referrals!")
        
        logger.info(f"✅ Referral code used: {request.referral_code} by {request.referred_username}")
        
        return {
            "success": True,
            "referrer_reward": referrer_reward,
            "referred_reward": referred_reward,
            "milestone_reached": milestone_reward is not None,
            "milestone_reward": milestone_reward,
            "message": f"Referral code applied! You earned {referred_reward} bonus points!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error using referral code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@referral_router.get("/stats/{user_id}")
async def get_referral_stats(user_id: str):
    """
    Get referral statistics for a user
    """
    try:
        db = get_database()
        
        referral = await db.referrals.find_one({"user_id": user_id})
        
        if not referral:
            return {
                "has_referral_code": False,
                "message": "No referral code generated yet"
            }
        
        # Get detailed stats
        referral_uses = await db.referral_uses.find({
            "referrer_id": user_id
        }).to_list(length=1000)
        
        # Calculate next milestone
        current_uses = referral["uses"]
        next_milestone = None
        for milestone_count in sorted(REFERRAL_REWARDS["milestones"].keys()):
            if milestone_count > current_uses:
                next_milestone = {
                    "count": milestone_count,
                    "reward": REFERRAL_REWARDS["milestones"][milestone_count],
                    "remaining": milestone_count - current_uses
                }
                break
        
        return {
            "has_referral_code": True,
            "referral_code": referral["code"],
            "referral_link": f"/join?ref={referral['code']}",
            "total_referrals": referral["uses"],
            "total_points_earned": referral.get("total_points_earned", 0),
            "referred_users": referral.get("referred_users", []),
            "recent_referrals": referral_uses[-10:],  # Last 10
            "next_milestone": next_milestone,
            "milestones_achieved": [
                m for m in REFERRAL_REWARDS["milestones"].keys()
                if m <= current_uses
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching referral stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@referral_router.get("/leaderboard")
async def get_referral_leaderboard(limit: int = 20):
    """
    Get top referrers leaderboard
    """
    try:
        db = get_database()
        
        top_referrers = await db.referrals.find({
            "is_active": True
        }).sort("uses", -1).limit(limit).to_list(length=limit)
        
        leaderboard = [
            {
                "rank": i + 1,
                "username": ref["username"],
                "referrals": ref["uses"],
                "total_points_earned": ref.get("total_points_earned", 0)
            }
            for i, ref in enumerate(top_referrers)
        ]
        
        return {
            "leaderboard": leaderboard,
            "count": len(leaderboard)
        }
        
    except Exception as e:
        logger.error(f"Error fetching referral leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@referral_router.post("/deactivate")
async def deactivate_referral_code(user_id: str):
    """
    Deactivate user's referral code
    """
    try:
        db = get_database()
        
        result = await db.referrals.update_one(
            {"user_id": user_id},
            {"$set": {"is_active": False}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Referral code not found")
        
        return {
            "success": True,
            "message": "Referral code deactivated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating referral code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@referral_router.post("/activity-bonus")
async def reward_referral_activity(referred_user_id: str, activity_type: str):
    """
    Reward referrer when referred user completes activities
    activity_type: "first_activity", "subscription", etc.
    """
    try:
        db = get_database()
        
        # Find who referred this user
        referral_use = await db.referral_uses.find_one({
            "referred_user_id": referred_user_id
        })
        
        if not referral_use:
            return {
                "success": False,
                "message": "User was not referred"
            }
        
        # Check if bonus already given
        bonus_key = f"bonus_{activity_type}"
        if referral_use.get(bonus_key):
            return {
                "success": False,
                "message": "Bonus already claimed"
            }
        
        # Award bonus to referrer
        bonus = REFERRAL_REWARDS["referrer"].get(activity_type, 0)
        if bonus > 0:
            await db.viewers.update_one(
                {"user_id": referral_use["referrer_id"]},
                {"$inc": {"points": bonus}}
            )
            
            # Mark bonus as given
            await db.referral_uses.update_one(
                {"referred_user_id": referred_user_id},
                {"$set": {bonus_key: True, f"{bonus_key}_at": datetime.now()}}
            )
            
            logger.info(f"✅ Referral bonus: {bonus} points to {referral_use['referrer_username']} for {activity_type}")
        
        return {
            "success": True,
            "bonus": bonus,
            "message": f"Referrer earned {bonus} bonus points!"
        }
        
    except Exception as e:
        logger.error(f"Error rewarding referral activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))
