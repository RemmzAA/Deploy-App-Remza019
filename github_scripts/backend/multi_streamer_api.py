"""
Multi-Streamer Support API
Allows simultaneous viewing of multiple streamers with synchronized chat and switching
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/multi-streamer", tags=["multi-streamer"])

class StreamerProfile(BaseModel):
    streamer_id: str
    username: str
    platform: str  # twitch, youtube, kick
    channel_url: str
    is_live: bool
    viewer_count: int
    game: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
class MultiViewLayout(BaseModel):
    layout_id: str
    layout_type: str  # grid, pip, split, focus
    streamers: List[str]
    created_at: str

# In-memory storage (would be MongoDB in production)
active_streamers = {}
user_layouts = {}

@router.get("/streamers/available", response_model=List[StreamerProfile])
async def get_available_streamers():
    """
    Get list of available streamers for multi-view
    """
    # Demo data - would fetch from actual APIs
    demo_streamers = [
        StreamerProfile(
            streamer_id="remza019",
            username="REMZA019",
            platform="youtube",
            channel_url="http://www.youtube.com/@remza019",
            is_live=True,
            viewer_count=256,
            game="Fortnite Rocket Racing",
            thumbnail_url="https://img.youtube.com/vi/XnEtSLaI5Vo/hqdefault.jpg"
        ),
        StreamerProfile(
            streamer_id="remza019_twitch",
            username="REMZA019",
            platform="twitch",
            channel_url="https://www.twitch.tv/remza019",
            is_live=False,
            viewer_count=0,
            game="Fortnite",
            thumbnail_url="https://static-cdn.jtvnw.net/jtv_user_pictures/default-profile-picture-300x300.png"
        ),
        StreamerProfile(
            streamer_id="demo_fortnite_1",
            username="ProPlayer123",
            platform="youtube",
            channel_url="https://www.youtube.com/watch?v=GUhc9NBBxBM",
            is_live=True,
            viewer_count=1200,
            game="Fortnite Battle Royale",
            thumbnail_url="https://img.youtube.com/vi/GUhc9NBBxBM/hqdefault.jpg"
        )
    ]
    
    return demo_streamers

@router.post("/layout/create")
async def create_multi_view_layout(
    user_id: str,
    layout_type: str,
    streamer_ids: List[str]
):
    """
    Create a custom multi-view layout
    Supports: grid (4 streams), pip (picture-in-picture), split (2 streams), focus (1 main + sidebar)
    """
    if len(streamer_ids) < 1 or len(streamer_ids) > 4:
        raise HTTPException(status_code=400, detail="Must select 1-4 streamers")
    
    # Validate layout type
    valid_layouts = ["grid", "pip", "split", "focus"]
    if layout_type not in valid_layouts:
        raise HTTPException(status_code=400, detail=f"Invalid layout type. Must be one of: {valid_layouts}")
    
    # Validate streamer count for layout
    layout_limits = {
        "grid": 4,
        "pip": 2,
        "split": 2,
        "focus": 4  # 1 main + up to 3 sidebar
    }
    
    if len(streamer_ids) > layout_limits[layout_type]:
        raise HTTPException(
            status_code=400, 
            detail=f"{layout_type} layout supports max {layout_limits[layout_type]} streamers"
        )
    
    layout = MultiViewLayout(
        layout_id=str(uuid.uuid4()),
        layout_type=layout_type,
        streamers=streamer_ids,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    # Save to user layouts
    if user_id not in user_layouts:
        user_layouts[user_id] = []
    user_layouts[user_id].append(layout.dict())
    
    return {
        "success": True,
        "layout": layout,
        "message": f"{layout_type.capitalize()} layout created with {len(streamer_ids)} streamers"
    }

@router.get("/layout/user/{user_id}")
async def get_user_layouts(user_id: str):
    """
    Get all saved layouts for a user
    """
    layouts = user_layouts.get(user_id, [])
    return {
        "user_id": user_id,
        "layouts": layouts,
        "count": len(layouts)
    }

@router.delete("/layout/{layout_id}")
async def delete_layout(layout_id: str, user_id: str):
    """
    Delete a saved layout
    """
    if user_id in user_layouts:
        user_layouts[user_id] = [
            layout for layout in user_layouts[user_id] 
            if layout["layout_id"] != layout_id
        ]
        return {"success": True, "message": "Layout deleted"}
    
    raise HTTPException(status_code=404, detail="Layout not found")

@router.post("/sync-chat")
async def sync_multi_chat(streamer_ids: List[str]):
    """
    Sync chat from multiple streamers into unified feed
    Returns combined chat with color-coded sources
    """
    # Demo implementation - would integrate with actual chat APIs
    demo_messages = [
        {
            "id": str(uuid.uuid4()),
            "streamer_id": streamer_ids[0],
            "username": "Viewer123",
            "message": "This multi-view is amazing!",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "color": "#00ff00"
        },
        {
            "id": str(uuid.uuid4()),
            "streamer_id": streamer_ids[0] if len(streamer_ids) > 0 else "demo",
            "username": "GamerPro",
            "message": "Love watching multiple POVs!",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "color": "#ff00ff"
        }
    ]
    
    return {
        "messages": demo_messages,
        "streamer_count": len(streamer_ids),
        "sync_status": "active"
    }

@router.get("/stats")
async def get_multi_view_stats():
    """
    Get statistics about multi-view usage
    """
    return {
        "total_layouts": sum(len(layouts) for layouts in user_layouts.values()),
        "active_users": len(user_layouts),
        "popular_layout": "grid",
        "average_streamers_per_view": 2.5
    }
