"""
REMZA019 Gaming - Viewer Menu System API
Point-based rewards, activity tracking, and group chat functionality
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid
import json
import asyncio
import secrets
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from email_service import email_service

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
viewer_router = APIRouter(prefix="/api/viewer", tags=["viewer"])

# Database connection
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is required")

async def get_database():
    client = AsyncIOMotorClient(MONGO_URL)
    return client.remza019_gaming

# Pydantic Models
class ViewerRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    
class ActivityRecord(BaseModel):
    user_id: str
    activity_type: str
    points: int
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict = {}

class ChatMessage(BaseModel):
    user_id: str
    username: str
    message: str
    level: int
    timestamp: datetime = Field(default_factory=datetime.now)

class PointTransaction(BaseModel):
    user_id: str
    activity: str
    points: int
    timestamp: datetime = Field(default_factory=datetime.now)

# Point System Configuration
LEVEL_SYSTEM = {
    1: {"required": 0, "name": "Rookie Viewer", "features": ["chat"]},
    2: {"required": 100, "name": "Active Gamer", "features": ["chat", "polls"]},
    3: {"required": 250, "name": "Gaming Fan", "features": ["chat", "polls", "predictions"]},
    4: {"required": 500, "name": "Stream Supporter", "features": ["chat", "polls", "predictions", "highlights"]},
    5: {"required": 1000, "name": "VIP Viewer", "features": ["chat", "polls", "predictions", "highlights", "private_chat"]},
    6: {"required": 2000, "name": "Gaming Legend", "features": ["chat", "polls", "predictions", "highlights", "private_chat", "moderator"]}
}

ACTIVITIES = {
    "stream_view": {"points": 5, "name": "Stream View (5min)"},
    "chat_message": {"points": 2, "name": "Chat Message"},
    "like_video": {"points": 3, "name": "Like Video"},
    "share_stream": {"points": 10, "name": "Share Stream"},
    "subscribe": {"points": 25, "name": "Subscribe"},
    "daily_visit": {"points": 5, "name": "Daily Visit"},
    "vote_poll": {"points": 3, "name": "Vote in Poll"},
    "stream_prediction": {"points": 7, "name": "Stream Prediction"}
}

def calculate_level(points: int) -> int:
    """Calculate level based on points"""
    for level in sorted(LEVEL_SYSTEM.keys(), reverse=True):
        if points >= LEVEL_SYSTEM[level]["required"]:
            return level
    return 1

def get_unlocked_features(level: int) -> List[str]:
    """Get unlocked features for a level"""
    return LEVEL_SYSTEM.get(level, LEVEL_SYSTEM[1])["features"]

# API Endpoints

@viewer_router.post("/register")
async def register_viewer(registration: ViewerRegistration, response: Response):
    """Register new viewer account with session cookie"""
    from fastapi import Response
    try:
        db = await get_database()
        
        # Check if username or email already exists
        existing = await db.viewers.find_one({
            "$or": [
                {"username": registration.username},
                {"email": registration.email}
            ]
        })
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail="Username or email already registered"
            )
        
        # Generate verification code
        verification_code = secrets.token_urlsafe(32)[:8].upper()
        
        # Create new viewer account with CONSISTENT field naming
        viewer = {
            "user_id": str(uuid.uuid4()),  # PRIMARY KEY
            "id": str(uuid.uuid4()),  # LEGACY SUPPORT (for compatibility)
            "username": registration.username,
            "email": registration.email,
            "points": 0,
            "level": 1,
            "created_at": datetime.now(),
            "last_active": datetime.now(),
            "total_activities": 0,
            "unlocked_features": ["chat"],
            "email_verified": False,
            "verification_code": verification_code,
            "verification_expires": datetime.now() + timedelta(hours=24)
        }
        
        await db.viewers.insert_one(viewer)
        
        # Send verification email
        frontend_url = os.environ.get('FRONTEND_URL', 'https://remote-code-fetch.preview.019solutionsagent.com')
        try:
            await email_service.send_verification_email(
                registration.email,
                registration.username,
                verification_code,
                frontend_url
            )
            logger.info(f"📧 Verification email sent to {registration.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
        
        # Award registration bonus
        await award_points(viewer["user_id"], "registration", 10, {"welcome_bonus": True})
        
        logger.info(f"✅ New viewer registered: {registration.username} (ID: {viewer['user_id']})")
        
        # Create session and set cookie
        from session_manager import get_session_manager, set_session_cookie
        session_manager = get_session_manager()
        token = await session_manager.create_session(
            user_id=viewer["user_id"],
            username=viewer["username"],
            role="viewer",
            extra_data={"email": viewer["email"], "email_verified": False}
        )
        set_session_cookie(response, token)
        
        return {
            "success": True,
            "viewer": {
                "id": viewer["user_id"],  # Return user_id as id for frontend
                "user_id": viewer["user_id"],
                "username": viewer["username"],
                "points": 10,  # Including registration bonus
                "email": viewer["email"],
                "email_verified": viewer["email_verified"]
            },
            "message": "Registration successful! Please check your email to verify your account."
        }
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@viewer_router.post("/login")
async def login_viewer(username: str, response: Response):
    """Login viewer and create session"""
    from fastapi import Response
    from session_manager import get_session_manager, set_session_cookie
    
    try:
        db = await get_database()
        
        # Find viewer
        viewer = await db.viewers.find_one({"username": username}, {"_id": 0})
        
        if not viewer:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create session
        session_manager = get_session_manager()
        token = await session_manager.create_session(
            user_id=viewer["user_id"],
            username=viewer["username"],
            role="viewer",
            extra_data={
                "email": viewer["email"],
                "email_verified": viewer.get("email_verified", False),
                "points": viewer.get("points", 0),
                "level": viewer.get("level", 1)
            }
        )
        
        # Set cookie
        set_session_cookie(response, token)
        
        logger.info(f"✅ Viewer logged in: {username}")
        
        return {
            "success": True,
            "viewer": {
                "id": viewer["user_id"],
                "username": viewer["username"],
                "email": viewer["email"],
                "points": viewer.get("points", 0),
                "level": viewer.get("level", 1),
                "email_verified": viewer.get("email_verified", False)
            },
            "message": "Logged in successfully"
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@viewer_router.post("/logout")
async def logout_viewer(request: Request, response: Response):
    """Logout viewer and clear session"""
    from fastapi import Response, Request
    from session_manager import get_session_manager, clear_session_cookie, get_current_user_from_cookie
    
    try:
        # Get current session
        user = await get_current_user_from_cookie(request)
        
        if user:
            # Invalidate session
            session_manager = get_session_manager()
            await session_manager.invalidate_session(user["session_id"])
            logger.info(f"✅ Viewer logged out: {user['username']}")
        
        # Clear cookie
        clear_session_cookie(response)
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@viewer_router.get("/me")
async def get_current_viewer(request: Request):
    """Get current logged-in viewer"""
    from fastapi import Request
    from session_manager import get_current_user_from_cookie
    
    try:
        user = await get_current_user_from_cookie(request)
        
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get full viewer data from database
        db = await get_database()
        viewer = await db.viewers.find_one({"user_id": user["user_id"]}, {"_id": 0})
        
        if not viewer:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "viewer": viewer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current viewer error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get viewer data")

                "level": 1,
                "unlocked_features": ["chat"],
                "email_verified": False
            },
            "message": "Please check your email to verify your account",
            "session_created": True
        }
        
    except Exception as e:
        logger.error(f"Viewer registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@viewer_router.post("/verify")
async def verify_email(email: str, code: str):
    """Verify user email with verification code"""
    try:
        db = await get_database()
        
        # Find viewer by email and code
        viewer = await db.viewers.find_one({
            "email": email,
            "verification_code": code
        })
        
        if not viewer:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        # Check if code expired
        if datetime.now() > viewer.get("verification_expires", datetime.now()):
            raise HTTPException(status_code=400, detail="Verification code expired")
        
        # Verify email
        await db.viewers.update_one(
            {"email": email},
            {
                "$set": {
                    "email_verified": True,
                    "verification_code": None,
                    "verification_expires": None
                }
            }
        )
        
        logger.info(f"✅ Email verified: {email}")
        
        return {
            "success": True,
            "message": "Email verified successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

@viewer_router.get("/profile/{user_id}")
async def get_viewer_profile(user_id: str):
    """Get viewer profile with stats and progress"""
    try:
        db = await get_database()
        
        # Try multiple field names for compatibility
        viewer = await db.viewers.find_one({"user_id": user_id})
        if not viewer:
            viewer = await db.viewers.find_one({"id": user_id})
        if not viewer:
            raise HTTPException(status_code=404, detail=f"Viewer not found: {user_id}")
        
        # Update last active
        query_field = "user_id" if "user_id" in viewer else "id"
        await db.viewers.update_one(
            {query_field: user_id},
            {"$set": {"last_active": datetime.now()}}
        )
        
        # Get recent activities
        activities = await db.activities.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(10).to_list(length=10)
        
        # Calculate current level and progress
        points = viewer.get("points", 0)
        current_level = calculate_level(points)
        next_level = current_level + 1 if current_level < 6 else 6
        next_level_points = LEVEL_SYSTEM.get(next_level, {"required": points})["required"]
        
        if current_level < 6:
            current_level_req = LEVEL_SYSTEM[current_level]["required"]
            progress = ((points - current_level_req) / (next_level_points - current_level_req)) * 100
        else:
            progress = 100
        
        return {
            "id": viewer.get("user_id", viewer.get("id")),
            "username": viewer.get("username", "Unknown"),
            "email": viewer.get("email", ""),
            "points": points,
            "level": current_level,
            "level_name": LEVEL_SYSTEM[current_level]["name"],
            "unlocked_features": get_unlocked_features(current_level),
            "progress_to_next": round(progress, 1),
            "next_level_points": next_level_points,
            "total_activities": viewer.get("total_activities", 0),
            "member_since": viewer["created_at"],
            "recent_activities": activities
        }
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")

@viewer_router.post("/activity/{user_id}")
async def record_activity(user_id: str, activity_type: str, metadata: Dict = {}):
    """Record viewer activity and award points"""
    try:
        if activity_type not in ACTIVITIES:
            raise HTTPException(status_code=400, detail="Invalid activity type")
        
        points = ACTIVITIES[activity_type]["points"]
        
        # Award points and return updated profile
        result = await award_points(user_id, activity_type, points, metadata)
        
        return result
        
    except Exception as e:
        logger.error(f"Record activity error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record activity")

async def award_points(user_id: str, activity: str, points: int, metadata: Dict = {}):
    """Award points to viewer and update level"""
    try:
        db = await get_database()
        
        # Try to find viewer by user_id (NEW) or id (LEGACY)
        viewer = await db.viewers.find_one({
            "$or": [
                {"user_id": user_id},
                {"id": user_id}
            ]
        })
        if not viewer:
            raise HTTPException(status_code=404, detail="Viewer not found")
        
        # Prevent spam - check for recent similar activities
        if activity in ["chat_message", "like_video"]:
            recent = await db.activities.find_one({
                "user_id": user_id,
                "activity_type": activity,
                "timestamp": {"$gte": datetime.now() - timedelta(minutes=1)}
            })
            if recent:
                return {"success": False, "message": "Activity too recent"}
        
        # Daily activity limits
        if activity == "daily_visit":
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_visit = await db.activities.find_one({
                "user_id": user_id,
                "activity_type": "daily_visit",
                "timestamp": {"$gte": today_start}
            })
            if today_visit:
                return {"success": False, "message": "Daily visit already recorded"}
        
        # Record activity
        activity_record = {
            "user_id": user_id,
            "activity_type": activity,
            "points": points,
            "timestamp": datetime.now(),
            "metadata": metadata
        }
        
        await db.activities.insert_one(activity_record)
        
        # Update viewer points and level
        new_points = viewer["points"] + points
        new_level = calculate_level(new_points)
        unlocked_features = get_unlocked_features(new_level)
        
        # Check for level up
        level_up = new_level > viewer.get("level", 1)
        
        # Update using correct field name
        update_filter = {"user_id": viewer.get("user_id")} if "user_id" in viewer else {"id": viewer.get("id")}
        
        await db.viewers.update_one(
            update_filter,
            {
                "$set": {
                    "points": new_points,
                    "level": new_level,
                    "unlocked_features": unlocked_features,
                    "last_active": datetime.now()
                },
                "$inc": {"total_activities": 1}
            }
        )
        
        result = {
            "success": True,
            "points_awarded": points,
            "total_points": new_points,
            "level": new_level,
            "level_name": LEVEL_SYSTEM[new_level]["name"],
            "unlocked_features": unlocked_features,
            "level_up": level_up
        }
        
        if level_up:
            result["level_up_message"] = f"Congratulations! You reached {LEVEL_SYSTEM[new_level]['name']}!"
            
            # Send level up email notification
            if viewer.get("email_verified") and viewer.get("email"):
                try:
                    asyncio.create_task(
                        email_service.send_level_up_email(
                            viewer["email"],
                            viewer["username"],
                            new_level,
                            LEVEL_SYSTEM[new_level]["name"],
                            unlocked_features
                        )
                    )
                except Exception as e:
                    logger.error(f"Failed to send level up email: {e}")
        
        logger.info(f"Awarded {points} points to {viewer['username']} for {activity}")
        
        return result
        
    except Exception as e:
        logger.error(f"Award points error: {e}")
        raise HTTPException(status_code=500, detail="Failed to award points")

@viewer_router.get("/chat/messages")
async def get_chat_messages(limit: int = 50):
    """Get recent chat messages for group chat"""
    try:
        db = await get_database()
        
        messages = await db.chat_messages.find().sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # Reverse to show oldest first
        messages.reverse()
        
        return {"messages": messages}
        
    except Exception as e:
        logger.error(f"Get chat messages error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@viewer_router.post("/chat/send")
async def send_chat_message(message: ChatMessage):
    """Send message to group chat"""
    try:
        db = await get_database()
        
        # Verify user exists and can chat
        viewer = await db.viewers.find_one({"id": message.user_id})
        if not viewer:
            raise HTTPException(status_code=404, detail="Viewer not found")
        
        unlocked_features = get_unlocked_features(viewer.get("level", 1))
        if "chat" not in unlocked_features:
            raise HTTPException(status_code=403, detail="Chat not unlocked")
        
        # Create message
        chat_message = {
            "id": str(uuid.uuid4()),
            "user_id": message.user_id,
            "username": message.username,
            "message": message.message,
            "level": viewer.get("level", 1),
            "timestamp": datetime.now()
        }
        
        await db.chat_messages.insert_one(chat_message)
        
        # Award points for chatting
        await award_points(message.user_id, "chat_message", 2)
        
        # Broadcast message to all connected clients via SSE
        await broadcast_chat_message(chat_message)
        
        return {"success": True, "message": chat_message}
        
    except Exception as e:
        logger.error(f"Send chat message error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@viewer_router.get("/leaderboard")
async def get_leaderboard(limit: int = 20):
    """Get top viewers leaderboard"""
    try:
        db = await get_database()
        
        viewers = await db.viewers.find().sort("points", -1).limit(limit).to_list(length=limit)
        
        leaderboard = []
        for i, viewer in enumerate(viewers, 1):
            leaderboard.append({
                "rank": i,
                "username": viewer["username"],
                "points": viewer["points"],
                "level": viewer.get("level", 1),
                "level_name": LEVEL_SYSTEM.get(viewer.get("level", 1), LEVEL_SYSTEM[1])["name"]
            })
        
        return {"leaderboard": leaderboard}
        
    except Exception as e:
        logger.error(f"Get leaderboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@viewer_router.get("/activities")
async def get_available_activities():
    """Get list of available activities and their point values"""
    return {
        "activities": [
            {
                "type": activity_type,
                "name": data["name"],
                "points": data["points"]
            }
            for activity_type, data in ACTIVITIES.items()
        ]
    }

@viewer_router.get("/levels")
async def get_level_system():
    """Get complete level system information"""
    return {
        "levels": LEVEL_SYSTEM
    }

async def broadcast_chat_message(message: Dict):
    """Broadcast chat message to all connected clients"""
    try:
        # Import here to avoid circular imports
        from server import broadcast_to_clients
        
        event = {
            "type": "chat_message",
            "data": message
        }
        
        await broadcast_to_clients(event)
        logger.info(f"Broadcasted chat message from {message['username']}")
        
    except Exception as e:
        logger.error(f"Broadcast chat message error: {e}")

# Export router
def get_viewer_router():
    return viewer_router