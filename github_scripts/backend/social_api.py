"""
REMZA019 Gaming - Social Features
Friends, DM, profiles, watch parties
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

social_router = APIRouter(prefix="/api/social", tags=["social"])

def get_database():
    from server import get_database as get_db
    return get_db()

class FriendRequest(BaseModel):
    from_user_id: str
    to_user_id: str
    from_username: str

class DirectMessage(BaseModel):
    from_user_id: str
    to_user_id: str
    message: str

@social_router.post("/friends/request")
async def send_friend_request(request: FriendRequest):
    """Send a friend request"""
    try:
        db = get_database()
        
        # Check if already friends or pending
        existing = await db.friendships.find_one({
            "$or": [
                {"user1_id": request.from_user_id, "user2_id": request.to_user_id},
                {"user1_id": request.to_user_id, "user2_id": request.from_user_id}
            ]
        })
        
        if existing:
            return {"success": False, "message": "Already friends or request pending"}
        
        await db.friend_requests.insert_one({
            "from_user_id": request.from_user_id,
            "to_user_id": request.to_user_id,
            "from_username": request.from_username,
            "status": "pending",
            "created_at": datetime.now()
        })
        
        return {"success": True, "message": "Friend request sent!"}
        
    except Exception as e:
        logger.error(f"Error sending friend request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@social_router.post("/friends/accept")
async def accept_friend_request(from_user_id: str, to_user_id: str):
    """Accept a friend request"""
    try:
        db = get_database()
        
        # Create friendship
        await db.friendships.insert_one({
            "user1_id": from_user_id,
            "user2_id": to_user_id,
            "created_at": datetime.now()
        })
        
        # Delete request
        await db.friend_requests.delete_one({
            "from_user_id": from_user_id,
            "to_user_id": to_user_id
        })
        
        return {"success": True, "message": "Friend request accepted!"}
        
    except Exception as e:
        logger.error(f"Error accepting friend request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@social_router.get("/friends/{user_id}")
async def get_friends(user_id: str):
    """Get user's friend list"""
    try:
        db = get_database()
        
        friendships = await db.friendships.find({
            "$or": [{"user1_id": user_id}, {"user2_id": user_id}]
        }).to_list(length=500)
        
        return {
            "friends": friendships,
            "count": len(friendships)
        }
        
    except Exception as e:
        logger.error(f"Error fetching friends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@social_router.post("/messages/send")
async def send_direct_message(message: DirectMessage):
    """Send a direct message"""
    try:
        db = get_database()
        
        await db.direct_messages.insert_one({
            "message_id": str(uuid.uuid4()),
            "from_user_id": message.from_user_id,
            "to_user_id": message.to_user_id,
            "message": message.message,
            "read": False,
            "created_at": datetime.now()
        })
        
        return {"success": True, "message": "Message sent!"}
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@social_router.get("/messages/{user_id}")
async def get_direct_messages(user_id: str, with_user_id: str):
    """Get DM conversation between two users"""
    try:
        db = get_database()
        
        messages = await db.direct_messages.find({
            "$or": [
                {"from_user_id": user_id, "to_user_id": with_user_id},
                {"from_user_id": with_user_id, "to_user_id": user_id}
            ]
        }).sort("created_at", 1).to_list(length=500)
        
        return {
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
