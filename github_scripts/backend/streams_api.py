"""
REMZA019 Gaming - Recent Streams API
Manages recent stream videos/highlights
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger(__name__)

streams_router = APIRouter(prefix="/api/streams", tags=["streams"])

# Database connection
def get_database():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    return client.remza019_gaming

class StreamVideo(BaseModel):
    title: str
    game: str
    duration: str
    views: str
    thumbnail: str
    videoUrl: str

@streams_router.get("/recent")
async def get_recent_streams():
    """Get recent streams - PUBLIC ACCESS"""
    try:
        db = get_database()
        streams = await db.recent_streams.find({}, {"_id": 0}).sort("order", 1).to_list(length=20)
        
        if not streams:
            # Return default if none exist
            default_streams = [
                {
                    "id": "1",
                    "title": "Competitive Racing - Road to Grand Champion",
                    "game": "FORTNITE ROCKET RACING",
                    "duration": "2h 45m",
                    "views": "3.2K",
                    "thumbnail": "https://img.youtube.com/vi/XnEtSLaI5Vo/hqdefault.jpg",
                    "videoUrl": "https://www.youtube.com/watch?v=XnEtSLaI5Vo",
                    "order": 1
                },
                {
                    "id": "2",
                    "title": "Solo Victory Royales",
                    "game": "FORTNITE",
                    "duration": "1h 58m",
                    "views": "2.8K",
                    "thumbnail": "https://img.youtube.com/vi/GUhc9NBBxBM/hqdefault.jpg",
                    "videoUrl": "https://www.youtube.com/watch?v=GUhc9NBBxBM",
                    "order": 2
                },
                {
                    "id": "3",
                    "title": "Fortnite Battle Royale Wins",
                    "game": "FORTNITE",
                    "duration": "1h 32m",
                    "views": "1.9K",
                    "thumbnail": "https://img.youtube.com/vi/GUhc9NBBxBM/hqdefault.jpg",
                    "videoUrl": "https://www.youtube.com/watch?v=GUhc9NBBxBM",
                    "order": 3
                },
                {
                    "id": "4",
                    "title": "Fortnite Creative Mode",
                    "game": "FORTNITE",
                    "duration": "2h 18m",
                    "views": "2.1K",
                    "thumbnail": "https://img.youtube.com/vi/h1HGztOJgHo/hqdefault.jpg",
                    "videoUrl": "https://www.youtube.com/watch?v=h1HGztOJgHo",
                    "order": 4
                }
            ]
            return {"streams": default_streams}
        
        return {"streams": streams}
        
    except Exception as e:
        logger.error(f"❌ Get streams error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch streams")

@streams_router.post("/update")
async def update_streams(streams_data: dict, admin = Depends(lambda: {"username": "admin"})):  # Simplified auth for now
    """Update recent streams - ADMIN ONLY"""
    try:
        db = get_database()
        
        streams = streams_data.get("streams", [])
        if not isinstance(streams, list):
            raise HTTPException(status_code=400, detail="Streams must be an array")
        
        # Clear existing streams
        await db.recent_streams.delete_many({})
        
        # Add new streams
        if streams:
            for idx, stream in enumerate(streams):
                stream_doc = {
                    "id": stream.get("id", str(uuid.uuid4())),
                    "title": stream.get("title", ""),
                    "game": stream.get("game", ""),
                    "duration": stream.get("duration", ""),
                    "views": stream.get("views", ""),
                    "thumbnail": stream.get("thumbnail", ""),
                    "videoUrl": stream.get("videoUrl", ""),
                    "order": idx + 1,
                    "updated_at": datetime.utcnow()
                }
                await db.recent_streams.insert_one(stream_doc)
        
        logger.info(f"✅ Recent streams updated: {len(streams)} streams")
        
        # Broadcast update via SSE
        from websocket_manager import broadcast_to_all
        await broadcast_to_all({
            "type": "streams_update",
            "streams": streams
        })
        
        return {"success": True, "message": f"Updated {len(streams)} streams"}
        
    except Exception as e:
        logger.error(f"❌ Update streams error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@streams_router.delete("/{stream_id}")
async def delete_stream(stream_id: str, admin = Depends(lambda: {"username": "admin"})):
    """Delete a stream - ADMIN ONLY"""
    try:
        db = get_database()
        result = await db.recent_streams.delete_one({"id": stream_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        logger.info(f"✅ Stream deleted: {stream_id}")
        return {"success": True, "message": "Stream deleted"}
        
    except Exception as e:
        logger.error(f"❌ Delete stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
