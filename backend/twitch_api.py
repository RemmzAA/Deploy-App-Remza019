"""
REMZA019 Gaming - Twitch API Endpoints
Real-time stream monitoring, VODs, and Twitch player integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from twitch_service import twitch_service

logger = logging.getLogger(__name__)

twitch_router = APIRouter(prefix="/api/twitch", tags=["twitch"])

# Response Models
class StreamStatus(BaseModel):
    is_live: bool
    title: Optional[str] = None
    game_name: Optional[str] = None
    viewer_count: Optional[int] = None
    started_at: Optional[str] = None
    thumbnail_url: Optional[str] = None
    user_name: Optional[str] = None
    language: Optional[str] = None
    error: Optional[str] = None

class VOD(BaseModel):
    id: str
    title: str
    created_at: str
    duration: str
    view_count: int
    thumbnail_url: str
    url: str

class ChannelInfo(BaseModel):
    broadcaster_name: Optional[str]
    broadcaster_language: Optional[str]
    game_name: Optional[str]
    title: Optional[str]
    delay: Optional[int]

@twitch_router.get("/status", response_model=StreamStatus)
async def get_stream_status():
    """
    Check if remza019 is currently live on Twitch
    Returns stream information if live, or is_live: false if offline
    """
    try:
        status = await twitch_service.check_if_live()
        logger.info(f"Stream status check: {status.get('is_live', False)}")
        return StreamStatus(**status)
    except Exception as e:
        logger.error(f"Error checking stream status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check stream status: {str(e)}")

@twitch_router.get("/vods", response_model=List[VOD])
async def get_vods(limit: int = 10):
    """
    Get past broadcasts (VODs) from remza019 Twitch channel
    Args:
        limit: Number of VODs to return (default: 10, max: 20)
    """
    try:
        if limit > 20:
            limit = 20
        
        vods = await twitch_service.get_vods(limit=limit)
        
        if vods is None:
            raise HTTPException(status_code=404, detail="No VODs found or failed to fetch")
        
        logger.info(f"Retrieved {len(vods)} VODs")
        return [VOD(**vod) for vod in vods]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VODs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch VODs: {str(e)}")

@twitch_router.get("/channel", response_model=ChannelInfo)
async def get_channel_info():
    """
    Get channel information for remza019
    Returns broadcaster details, current game, title, etc.
    """
    try:
        info = await twitch_service.get_channel_info()
        
        if info is None:
            raise HTTPException(status_code=404, detail="Channel information not found")
        
        logger.info(f"Channel info retrieved: {info.get('broadcaster_name')}")
        return ChannelInfo(**info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching channel info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch channel info: {str(e)}")

@twitch_router.get("/embed-url")
async def get_embed_url():
    """
    Get Twitch embed URL for the channel
    Frontend can use this to embed the Twitch player
    """
    try:
        channel_name = "remza019"
        parent_domain = "verify-gaming-1.preview.019solutionsagent.com"
        
        embed_url = f"https://player.twitch.tv/?channel={channel_name}&parent={parent_domain}"
        chat_url = f"https://www.twitch.tv/embed/{channel_name}/chat?parent={parent_domain}"
        
        return {
            "channel_name": channel_name,
            "embed_url": embed_url,
            "chat_url": chat_url,
            "twitch_url": f"https://www.twitch.tv/{channel_name}"
        }
    except Exception as e:
        logger.error(f"Error generating embed URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate embed URL: {str(e)}")

@twitch_router.post("/refresh-status")
async def refresh_stream_status():
    """
    Force refresh of stream status (useful for manual checks)
    Returns updated stream information
    """
    try:
        # Clear cached user_id to force re-fetch
        twitch_service.user_id = None
        await twitch_service.get_user_id()
        
        status = await twitch_service.check_if_live()
        logger.info(f"Stream status refreshed: {status.get('is_live', False)}")
        
        return {
            "success": True,
            "status": status,
            "refreshed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error refreshing stream status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh status: {str(e)}")

# Health check endpoint
@twitch_router.get("/health")
async def twitch_health_check():
    """
    Check if Twitch API integration is working
    """
    try:
        # Try to get user ID
        user_id = await twitch_service.get_user_id()
        
        if not user_id:
            return {
                "status": "warning",
                "message": "Twitch API credentials may be invalid",
                "user_id": None
            }
        
        return {
            "status": "healthy",
            "message": "Twitch API integration working",
            "channel": "remza019",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Twitch health check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
