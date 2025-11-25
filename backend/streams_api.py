"""
REMZA019 Gaming - Streams API
Mock recent streams endpoint (now using YouTube API directly)
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import logging

logger = logging.getLogger("streams_api")

streams_router = APIRouter(prefix="/streams", tags=["streams"])

class StreamItem(BaseModel):
    id: str
    title: str
    game: str
    thumbnail: str
    duration: str
    views: str

@streams_router.get("/recent")
async def get_recent_streams():
    """
    Get recent streams
    NOTE: This is now handled by YouTube API integration (/api/youtube/latest-videos)
    This endpoint exists to prevent 404 errors
    """
    return {
        "message": "Use /api/youtube/latest-videos for real YouTube streams",
        "streams": []
    }
