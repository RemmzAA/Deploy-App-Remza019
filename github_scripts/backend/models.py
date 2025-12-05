"""
REMZA019 Gaming Admin Dashboard - Database Models
MongoDB collections for admin content management
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import uuid4

# Admin Authentication Models
class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    password_hash: str  # Will be bcrypt hashed
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True

class AdminSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    admin_id: str
    token: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime
    is_active: bool = True

# Stream Management Models
class StreamSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    day: str  # MON, TUE, WED, etc.
    time: str  # "19:00"
    game: str  # "FORTNITE"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class RecentStream(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    game: str
    duration: str  # "2h 45m"
    views: str  # "3.2K"
    thumbnail: str  # YouTube thumbnail URL
    video_url: str  # YouTube video URL
    is_featured: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Channel Stats Models
class ChannelStats(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    subscriber_count: str  # "178"
    video_count: str  # "15" 
    total_views: str  # "3247"
    current_viewers: str = "0"  # Live viewer count
    is_live: bool = False
    live_game: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

# Content Management Models
class AboutContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: List[str]  # Array of paragraph texts
    updated_at: datetime = Field(default_factory=datetime.now)

class FeaturedVideo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    video_id: str  # YouTube video ID
    title: str
    description: str
    thumbnail_url: str
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)

class VideoContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    video_id: str  # YouTube video ID
    title: str
    description: str
    thumbnail_url: str
    watch_url: str
    view_count: str
    duration: str
    is_featured: bool = False
    display_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Site Settings Models
class SiteSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    site_title: str = "REMZA019 GAMING"
    site_description: str = "Professional Gaming Content Creator"
    social_links: Dict[str, str] = {
        "youtube": "http://www.youtube.com/@remza019",
        "discord": "#",
        "twitch": "#"
    }
    updated_at: datetime = Field(default_factory=datetime.now)

# Admin Activity Log
class AdminActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    admin_id: str
    action: str  # "update_live_status", "add_stream", etc.
    details: Dict[str, Any]  # JSON details of the change
    timestamp: datetime = Field(default_factory=datetime.now)

# API Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str
    admin_id: Optional[str] = None

class DashboardStats(BaseModel):
    channel_stats: ChannelStats
    recent_streams_count: int
    scheduled_streams_count: int
    total_videos: int
    last_updated: datetime

# Update Request Models
class UpdateLiveStatusRequest(BaseModel):
    is_live: bool
    current_viewers: Optional[str] = "0"
    live_game: Optional[str] = None

class UpdateChannelStatsRequest(BaseModel):
    subscriber_count: Optional[str] = None
    video_count: Optional[str] = None
    total_views: Optional[str] = None

class AddStreamRequest(BaseModel):
    title: str
    game: str
    duration: str
    views: str
    video_url: str
    thumbnail: Optional[str] = None

class UpdateScheduleRequest(BaseModel):
    day: str
    time: str
    game: str

class UpdateAboutRequest(BaseModel):
    content: Union[str, List[str]]
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Convert string to list if needed - TX Admin style flexibility"""
        if isinstance(v, str):
            # Split by newlines and filter empty lines
            lines = [line.strip() for line in v.split('\n') if line.strip()]
            return lines if lines else [v]
        return v

class UpdateFeaturedVideoRequest(BaseModel):
    video_id: str
    title: str
    description: str

class AddVideoContentRequest(BaseModel):
    video_id: str
    title: str
    description: str
    watch_url: str
    view_count: str
    duration: str


# About Tags Model
class AboutTag(BaseModel):
    icon: str  # Emoji icon like "🏆", "🏎️"
    text: str  # Tag text like "Competitive Player"

class AboutTagsUpdate(BaseModel):
    tags: List[AboutTag]

    is_featured: bool = False