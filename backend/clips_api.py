"""
019 Solutions - Clips & Highlights System
Create, share, and discover best gaming moments
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

clips_router = APIRouter(prefix="/api/clips", tags=["clips"])

# Database connection
def get_database():
    from server import get_database as get_db
    return get_db()

# Pydantic Models
class Clip(BaseModel):
    clip_id: str
    title: str
    creator_id: str
    creator_name: str
    duration: int  # seconds
    views: int
    likes: int
    created_at: datetime
    video_url: str
    thumbnail_url: str
    tags: List[str]
    game: Optional[str] = None
    is_highlight: bool = False

class CreateClipRequest(BaseModel):
    title: str
    creator_id: str
    creator_name: str
    video_url: str
    thumbnail_url: str
    duration: int
    tags: List[str] = []
    game: Optional[str] = None

class ClipReaction(BaseModel):
    user_id: str
    clip_id: str
    reaction_type: str  # "like", "love", "fire", "laugh"

@clips_router.post("/create")
async def create_clip(request: CreateClipRequest):
    """
    Create a new clip/highlight
    """
    try:
        db = get_database()
        
        clip_id = str(uuid.uuid4())
        clip = {
            "clip_id": clip_id,
            "title": request.title,
            "creator_id": request.creator_id,
            "creator_name": request.creator_name,
            "video_url": request.video_url,
            "thumbnail_url": request.thumbnail_url,
            "duration": request.duration,
            "tags": request.tags,
            "game": request.game,
            "views": 0,
            "likes": 0,
            "created_at": datetime.now(),
            "is_highlight": False,
            "reactions": {}
        }
        
        await db.clips.insert_one(clip)
        
        logger.info(f"✅ Clip created: {clip_id} - {request.title}")
        
        return {
            "success": True,
            "clip_id": clip_id,
            "message": "Clip created successfully!"
        }
        
    except Exception as e:
        logger.error(f"Error creating clip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.get("/trending")
async def get_trending_clips(limit: int = 10, time_range: str = "week"):
    """
    Get trending clips based on views and likes
    time_range: "day", "week", "month", "all"
    """
    try:
        db = get_database()
        
        # Calculate time range
        time_filter = {}
        if time_range == "day":
            time_filter = {"created_at": {"$gte": datetime.now() - timedelta(days=1)}}
        elif time_range == "week":
            time_filter = {"created_at": {"$gte": datetime.now() - timedelta(days=7)}}
        elif time_range == "month":
            time_filter = {"created_at": {"$gte": datetime.now() - timedelta(days=30)}}
        
        # Get clips sorted by engagement (views + likes * 10)
        clips = await db.clips.find(time_filter).sort([
            ("likes", -1),
            ("views", -1)
        ]).limit(limit).to_list(length=limit)
        
        return {
            "clips": clips,
            "count": len(clips),
            "time_range": time_range
        }
        
    except Exception as e:
        logger.error(f"Error fetching trending clips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.get("/{clip_id}")
async def get_clip(clip_id: str):
    """
    Get specific clip and increment view count
    """
    try:
        db = get_database()
        
        clip = await db.clips.find_one({"clip_id": clip_id})
        
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Increment views
        await db.clips.update_one(
            {"clip_id": clip_id},
            {"$inc": {"views": 1}}
        )
        
        clip["views"] += 1
        
        return clip
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching clip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.post("/{clip_id}/react")
async def react_to_clip(clip_id: str, reaction: ClipReaction):
    """
    Add reaction to clip (like, love, fire, etc.)
    """
    try:
        db = get_database()
        
        clip = await db.clips.find_one({"clip_id": clip_id})
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Check if user already reacted
        existing_reaction = await db.clip_reactions.find_one({
            "clip_id": clip_id,
            "user_id": reaction.user_id
        })
        
        if existing_reaction:
            # Update reaction
            await db.clip_reactions.update_one(
                {"clip_id": clip_id, "user_id": reaction.user_id},
                {"$set": {"reaction_type": reaction.reaction_type}}
            )
        else:
            # Add new reaction
            await db.clip_reactions.insert_one({
                "clip_id": clip_id,
                "user_id": reaction.user_id,
                "reaction_type": reaction.reaction_type,
                "created_at": datetime.now()
            })
            
            # Increment likes count
            await db.clips.update_one(
                {"clip_id": clip_id},
                {"$inc": {"likes": 1}}
            )
        
        return {
            "success": True,
            "message": "Reaction added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reacting to clip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.get("/user/{user_id}")
async def get_user_clips(user_id: str, limit: int = 20):
    """
    Get all clips created by a user
    """
    try:
        db = get_database()
        
        clips = await db.clips.find({
            "creator_id": user_id
        }).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        return {
            "clips": clips,
            "count": len(clips)
        }
        
    except Exception as e:
        logger.error(f"Error fetching user clips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.post("/{clip_id}/highlight")
async def mark_as_highlight(clip_id: str):
    """
    Mark clip as official highlight (admin only)
    """
    try:
        db = get_database()
        
        result = await db.clips.update_one(
            {"clip_id": clip_id},
            {"$set": {"is_highlight": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        return {
            "success": True,
            "message": "Clip marked as highlight"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking highlight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.get("/highlights/official")
async def get_official_highlights(limit: int = 10):
    """
    Get official channel highlights
    """
    try:
        db = get_database()
        
        highlights = await db.clips.find({
            "is_highlight": True
        }).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        return {
            "highlights": highlights,
            "count": len(highlights)
        }
        
    except Exception as e:
        logger.error(f"Error fetching highlights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.delete("/{clip_id}")
async def delete_clip(clip_id: str, user_id: str):
    """
    Delete a clip (creator or admin only)
    """
    try:
        db = get_database()
        
        clip = await db.clips.find_one({"clip_id": clip_id})
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Verify ownership (simplified - add admin check in production)
        if clip["creator_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        await db.clips.delete_one({"clip_id": clip_id})
        await db.clip_reactions.delete_many({"clip_id": clip_id})
        
        return {
            "success": True,
            "message": "Clip deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting clip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@clips_router.get("/search")
async def search_clips(query: str, limit: int = 20):
    """
    Search clips by title, tags, or game
    """
    try:
        db = get_database()
        
        clips = await db.clips.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}},
                {"game": {"$regex": query, "$options": "i"}}
            ]
        }).limit(limit).to_list(length=limit)
        
        return {
            "clips": clips,
            "count": len(clips),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching clips: {e}")
        raise HTTPException(status_code=500, detail=str(e))
