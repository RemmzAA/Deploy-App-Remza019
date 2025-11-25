"""
REMZA019 Gaming Admin Dashboard - API Endpoints
FastAPI endpoints for admin functionality with Real-time YouTube Sync
Real-time updates via broadcast system
"""
from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from dotenv import load_dotenv
from pathlib import Path
from audit_logger import audit_log

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

from models import *
from youtube_sync import get_sync_manager
from email_notifications import send_live_notifications_to_subscribers

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Broadcast function for real-time updates
async def broadcast_admin_update(event_type: str, data: dict):
    """Broadcast admin updates to all connected clients via WebSocket & SSE (dual mode)"""
    try:
        # Import WebSocket manager
        from websocket_manager import get_ws_manager
        
        # Prepare event data
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"🔔 BROADCASTING: {event_type}")
        logger.info(f"🔔 Data: {data}")
        
        # Broadcast via WebSocket (new system)
        try:
            ws_manager = get_ws_manager()
            
            # Determine room based on event type
            if event_type in ["live_status_update", "content_update", "channel_stats_update"]:
                await ws_manager.broadcast(event, room="public")
            else:
                await ws_manager.broadcast(event, room="admin")
            
            logger.info(f"✅ WebSocket broadcast successful: {event_type}")
        except Exception as ws_error:
            logger.warning(f"⚠️ WebSocket broadcast failed: {ws_error}")
        
        # Also broadcast via SSE (legacy fallback)
        try:
            from server import broadcast_to_clients
            await broadcast_to_clients(event)
            logger.info(f"✅ SSE broadcast successful: {event_type}")
        except Exception as sse_error:
            logger.warning(f"⚠️ SSE broadcast failed: {sse_error}")
        
    except Exception as e:
        logger.error(f"❌ Broadcast error: {e}")
        # Don't fail the main operation if broadcast fails

# Admin API Router
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'remza019_admin_secret_key_gaming')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 8

# Security scheme
security = HTTPBearer()

# Database connection
def get_database():
    """Get database connection"""
    try:
        mongodb_url = os.environ.get('MONGO_URL')
        if not mongodb_url:
            raise ValueError("MONGO_URL environment variable is required")
        client = AsyncIOMotorClient(mongodb_url)
        # Use database name from environment or extract from URL
        db_name = os.environ.get('DB_NAME', 'remza019_gaming')
        return client[db_name]
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Authentication Functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(admin_id: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        'admin_id': admin_id,
        'exp': expire,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated admin"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get('admin_id')
        
        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        db = get_database()
        admin = await db.admin_users.find_one({'id': admin_id, 'is_active': True})
        
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
            
        return admin
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Rate limiting storage (in-memory, for production use Redis)
from collections import defaultdict
from datetime import datetime, timedelta

login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP has exceeded login attempts"""
    now = datetime.now()
    # Clean old attempts
    login_attempts[ip_address] = [
        attempt_time for attempt_time in login_attempts[ip_address]
        if now - attempt_time < LOCKOUT_DURATION
    ]
    return len(login_attempts[ip_address]) < MAX_LOGIN_ATTEMPTS

# Authentication Endpoints
@admin_router.post("/auth/login", response_model=LoginResponse)
async def admin_login(login_data: LoginRequest, request: Request):
    """Admin login endpoint with rate limiting"""
    try:
        db = get_database()
        ip_address = request.client.host if request.client else "unknown"
        
        # Rate limiting check
        if not check_rate_limit(ip_address):
            logger.warning(f"🚫 Rate limit exceeded for IP: {ip_address}")
            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Please try again in 15 minutes."
            )
        
        # Find admin user
        admin = await db.admin_users.find_one({'username': login_data.username, 'is_active': True})
        
        if not admin or not verify_password(login_data.password, admin['password_hash']):
            # Record failed attempt for rate limiting
            login_attempts[ip_address].append(datetime.now())
            
            # Audit log failed attempt
            audit_log.log_auth_attempt(login_data.username, False, ip_address, "Invalid credentials")
            return LoginResponse(success=False, message="Invalid credentials")
        
        # Create access token
        token = create_access_token(admin['id'])
        
        # Update last login
        await db.admin_users.update_one(
            {'id': admin['id']}, 
            {'$set': {'last_login': datetime.now()}}
        )
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="login",
            details={"ip": ip_address, "success": True}
        ).dict())
        
        # Audit log successful login
        audit_log.log_auth_attempt(admin['username'], True, ip_address)
        logger.info(f"✅ Admin login successful: {admin['username']}")
        
        return LoginResponse(
            success=True,
            token=token,
            message="Login successful",
            admin_id=admin['id']
        )
        
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return LoginResponse(success=False, message="Login failed")

@admin_router.post("/auth/logout")
async def admin_logout(admin = Depends(get_current_admin)):
    """Admin logout endpoint"""
    try:
        db = get_database()
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="logout",
            details={"timestamp": datetime.now().isoformat()}
        ).dict())
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

# Dashboard Endpoints
@admin_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(admin = Depends(get_current_admin)):
    """Get dashboard statistics"""
    try:
        db = get_database()
        
        # Get channel stats
        channel_stats = await db.channel_stats.find_one({}, sort=[('updated_at', -1)])
        if not channel_stats:
            # Create default stats
            default_stats = ChannelStats(
                subscriber_count="178",
                video_count="15",
                total_views="3247",
                current_viewers="0",
                is_live=False
            )
            await db.channel_stats.insert_one(default_stats.dict())
            channel_stats = default_stats.dict()
        
        # Count documents
        recent_streams_count = await db.recent_streams.count_documents({})
        scheduled_streams_count = await db.stream_schedule.count_documents({})
        total_videos = await db.video_content.count_documents({'is_active': True})
        
        return DashboardStats(
            channel_stats=ChannelStats(**channel_stats),
            recent_streams_count=recent_streams_count,
            scheduled_streams_count=scheduled_streams_count,
            total_videos=total_videos,
            last_updated=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard stats")

# Live Stream Management
@admin_router.post("/live/toggle")
async def toggle_live_status(update_data: UpdateLiveStatusRequest, admin = Depends(get_current_admin)):
    """Toggle live stream status - MANUAL ADMIN OVERRIDE"""
    try:
        db = get_database()
        
        # Update channel stats with admin override flag
        await db.channel_stats.update_one(
            {}, 
            {
                '$set': {
                    'is_live': update_data.is_live,
                    'current_viewers': update_data.current_viewers or "0",
                    'live_game': update_data.live_game,
                    'admin_override': True,  # MARK AS ADMIN OVERRIDE
                    'updated_at': datetime.now()
                }
            },
            upsert=True
        )
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="toggle_live_status",
            details={
                "is_live": update_data.is_live,
                "viewers": update_data.current_viewers,
                "game": update_data.live_game,
                "override": True
            }
        ).dict())
        
        status = "LIVE" if update_data.is_live else "OFFLINE"
        logger.info(f"✅ Live status MANUALLY set to {status} by admin {admin['username']} (override active)")
        
        # Send email notifications if going LIVE
        if update_data.is_live:
            try:
                logger.info("📧 Sending LIVE notification emails to subscribers...")
                result = await send_live_notifications_to_subscribers(
                    streamer_name="REMZA019 Gaming",
                    game_name=update_data.live_game or "FORTNITE",
                    youtube_url="https://www.youtube.com/@REMZA019"
                )
                logger.info(f"✅ LIVE notification result: {result}")
            except Exception as email_error:
                logger.error(f"❌ Failed to send email notifications: {email_error}")
                # Continue even if email fails
        
        # Broadcast update to all clients
        await broadcast_admin_update("live_status_update", {
            "is_live": update_data.is_live,
            "current_viewers": update_data.current_viewers or "0",
            "live_game": update_data.live_game,
            "manual_override": True
        })
        
        return {
            "success": True, 
            "message": f"Stream status MANUALLY set to {status} (YouTube sync will respect this)",
            "is_live": update_data.is_live,
            "admin_override": True
        }
        
    except Exception as e:
        logger.error(f"❌ Live toggle error: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle live status")

@admin_router.post("/live/update-viewers")
async def update_viewer_count(viewers: str, admin = Depends(get_current_admin)):
    """Update current viewer count"""
    try:
        db = get_database()
        
        await db.channel_stats.update_one(
            {}, 
            {
                '$set': {
                    'current_viewers': viewers,
                    'updated_at': datetime.now()
                }
            }
        )
        
        return {"success": True, "message": f"Viewer count updated to {viewers}"}
        
    except Exception as e:
        logger.error(f"❌ Update viewers error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update viewer count")

@admin_router.post("/live/reset-override")
async def reset_admin_override(admin = Depends(get_current_admin)):
    """Reset admin override - allow YouTube sync to auto-update"""
    try:
        db = get_database()
        
        await db.channel_stats.update_one(
            {},
            {
                '$set': {
                    'admin_override': False,
                    'updated_at': datetime.now()
                }
            }
        )
        
        # Also reset featured video override
        await db.featured_video.update_one(
            {},
            {
                '$set': {
                    'admin_override': False,
                    'updated_at': datetime.now()
                }
            }
        )
        
        logger.info(f"✅ Admin override RESET by {admin['username']} - YouTube sync will now auto-update")
        
        # Broadcast update
        await broadcast_admin_update("override_reset", {
            "message": "YouTube sync auto-update re-enabled",
            "reset_by": admin.get('username')
        })
        
        return {
            "success": True,
            "message": "Admin override reset - YouTube sync will now auto-update live status and videos"
        }
        
    except Exception as e:
        logger.error(f"❌ Reset override error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset override")

# Channel Stats Management
@admin_router.post("/stats/update")
async def update_channel_stats(update_data: UpdateChannelStatsRequest, admin = Depends(get_current_admin)):
    """Update channel statistics"""
    try:
        db = get_database()
        
        update_fields = {'updated_at': datetime.now()}
        if update_data.subscriber_count:
            update_fields['subscriber_count'] = update_data.subscriber_count
        if update_data.video_count:
            update_fields['video_count'] = update_data.video_count
        if update_data.total_views:
            update_fields['total_views'] = update_data.total_views
        
        await db.channel_stats.update_one(
            {}, 
            {'$set': update_fields},
            upsert=True
        )
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="update_channel_stats",
            details=update_fields
        ).dict())
        
        logger.info(f"✅ Channel stats updated by admin {admin['username']}")
        
        return {"success": True, "message": "Channel stats updated successfully"}
        
    except Exception as e:
        logger.error(f"❌ Update stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update channel stats")

# Stream Schedule Management
@admin_router.get("/schedule", response_model=List[StreamSchedule])
async def get_stream_schedule(admin = Depends(get_current_admin)):
    """Get stream schedule"""
    try:
        db = get_database()
        
        schedule = await db.stream_schedule.find({'is_active': True}).to_list(length=None)
        
        # If no schedule exists, create default schedule
        if not schedule:
            default_schedule = [
                {'day': 'MON', 'time': '19:00', 'game': 'FORTNITE', 'is_active': True},
                {'day': 'TUE', 'time': '20:00', 'game': 'COD MULTIPLAYER', 'is_active': True},
                {'day': 'WED', 'time': '19:30', 'game': 'FORTNITE ROCKET RACING', 'is_active': True},
                {'day': 'THU', 'time': '20:00', 'game': 'FORTNITE', 'is_active': True},
                {'day': 'FRI', 'time': '19:00', 'game': 'COD WARZONE', 'is_active': True},
                {'day': 'SAT', 'time': '15:00', 'game': 'FORTNITE TOURNAMENT', 'is_active': True},
                {'day': 'SUN', 'time': '18:00', 'game': 'FORTNITE', 'is_active': True}
            ]
            
            for sched in default_schedule:
                schedule_obj = StreamSchedule(**sched)
                await db.stream_schedule.insert_one(schedule_obj.dict())
            
            # Reload schedule
            schedule = await db.stream_schedule.find({'is_active': True}).to_list(length=None)
        
        return [StreamSchedule(**item) for item in schedule]
        
    except Exception as e:
        logger.error(f"❌ Get schedule error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch schedule")

@admin_router.post("/schedule/update")
async def update_schedule_day(schedule_data: UpdateScheduleRequest, admin = Depends(get_current_admin)):
    """Update schedule for specific day"""
    try:
        db = get_database()
        
        # Update or insert schedule for the day
        await db.stream_schedule.update_one(
            {'day': schedule_data.day},
            {
                '$set': {
                    'day': schedule_data.day,
                    'time': schedule_data.time,
                    'game': schedule_data.game,
                    'is_active': True,
                    'updated_at': datetime.now()
                }
            },
            upsert=True
        )
        
        # Get updated full schedule
        schedule_cursor = db.stream_schedule.find({'is_active': True})
        schedule_list = await schedule_cursor.to_list(length=100)
        for item in schedule_list:
            if '_id' in item:
                del item['_id']
        
        # Broadcast schedule update
        await broadcast_admin_update("schedule_update", {
            "schedule": schedule_list,
            "updated_day": schedule_data.day
        })
        
        # Log activity
        await log_admin_activity(admin['id'], "update_schedule", schedule_data.dict())
        
        logger.info(f"✅ Schedule updated for {schedule_data.day} by admin {admin['username']}")
        
        return {"success": True, "message": f"Schedule updated for {schedule_data.day}", "schedule": schedule_list}
        
    except Exception as e:
        logger.error(f"❌ Update schedule error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update schedule")

@admin_router.delete("/schedule/{day}")
async def delete_schedule_day(day: str, admin = Depends(get_current_admin)):
    """Delete schedule for specific day"""
    try:
        db = get_database()
        
        result = await db.stream_schedule.update_one(
            {'day': day.upper()},
            {'$set': {'is_active': False, 'updated_at': datetime.now()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        # Get updated schedule
        schedule_cursor = db.stream_schedule.find({'is_active': True})
        schedule_list = await schedule_cursor.to_list(length=100)
        for item in schedule_list:
            if '_id' in item:
                del item['_id']
        
        # Broadcast schedule update
        await broadcast_admin_update("schedule_update", {
            "schedule": schedule_list,
            "deleted_day": day
        })
        
        # Log activity
        await log_admin_activity(admin['id'], "delete_schedule", {"day": day})
        
        return {"success": True, "message": f"Schedule deleted for {day}", "schedule": schedule_list}
        
    except Exception as e:
        logger.error(f"❌ Delete schedule error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete schedule")

@admin_router.get("/content/about")
async def get_about_content():
    """Get About section content - PUBLIC ACCESS for frontend"""
    try:
        db = get_database()
        
        about = await db.about_content.find_one({}, sort=[('updated_at', -1)])
        
        if not about:
            # Create default about content
            default_content = AboutContent(content=[
                "🎮 Casual gamer focused on FORTNITE gameplay and content creation",
                "🏎️ FORTNITE ROCKET RACING competitor - the ONLY game I compete in tournaments", 
                "🎯 Real FORTNITE gameplay sessions, no fake content or exaggerated claims",
                "📺 Honest FORTNITE gaming content with authentic viewers and followers",
                "🇷🇸 Based in Serbia, streaming FORTNITE in CET timezone",
                "❌ NOT an esports representative - just a passionate FORTNITE gamer"
            ])
            
            await db.about_content.insert_one(default_content.dict())
            return {"content": default_content.content}
        
        return {"content": about.get('content', [])}
        
    except Exception as e:
        logger.error(f"❌ Get about content error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch about content")

# Content Management - Enhanced
@admin_router.post("/content/about/update")
async def update_about_content(content_data: UpdateAboutRequest, admin = Depends(get_current_admin)):
    """Update About section content - FIXED VERSION"""
    try:
        db = get_database()
        
        # Ensure content is always a list
        content_list = content_data.content if isinstance(content_data.content, list) else [content_data.content]
        
        # Create AboutContent with timestamp
        about_content = AboutContent(
            content=content_list,
            updated_at=datetime.now()
        )
        
        # Update with complete replacement (not merge)
        result = await db.about_content.update_one(
            {},
            {'$set': {
                'content': about_content.content,
                'updated_at': about_content.updated_at
            }},
            upsert=True
        )
        
        logger.info(f"✅ About content updated: {len(content_list)} items, modified: {result.modified_count}, upserted: {result.upserted_id}")
        
        # Log activity
        await log_admin_activity(admin['id'], "update_about_content", {"content_length": len(content_list)})
        
        # REAL-TIME BROADCAST - About content updated
        await broadcast_admin_update("about_content_update", {  # FIXED: Match frontend listener
            "content_type": "about",
            "content": content_list,
            "updated_by": admin.get('username', admin.get('id')),
            "action": "About section updated",
            "timestamp": about_content.updated_at.isoformat()
        })
        
        return {
            "success": True,
            "message": "About content updated successfully",
            "content": content_list,
            "updated_at": about_content.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Update about error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to update about content: {str(e)}")

@admin_router.get("/content/featured-video")
async def get_featured_video_config(admin = Depends(get_current_admin)):
    """Get featured video configuration"""
    try:
        db = get_database()
        
        featured = await db.featured_video.find_one({}, sort=[('updated_at', -1)])
        
        if not featured:
            # Create default featured video
            default_featured = FeaturedVideo(
                video_id='GUhc9NBBxBM',
                title='REMZA019 - UNLUCKY (Channel Presentation)',
                description='REMZA019 channel presentation video! Subscribe and like for more gaming content from Serbia.',
                thumbnail_url='https://img.youtube.com/vi/GUhc9NBBxBM/maxresdefault.jpg'
            )
            
            await db.featured_video.insert_one(default_featured.dict())
            return default_featured.dict()
        
        # Convert ObjectId to string for JSON serialization
        if '_id' in featured:
            del featured['_id']
            
        return featured
        
    except Exception as e:
        logger.error(f"❌ Get featured video error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch featured video")

@admin_router.post("/content/featured-video/update")
async def update_featured_video(video_data: UpdateFeaturedVideoRequest, admin = Depends(get_current_admin)):
    """Update featured video - MANUAL ADMIN OVERRIDE"""
    try:
        db = get_database()
        
        # Generate thumbnail URL
        thumbnail_url = f'https://img.youtube.com/vi/{video_data.video_id}/maxresdefault.jpg'
        
        featured_video = FeaturedVideo(
            video_id=video_data.video_id,
            title=video_data.title,
            description=video_data.description,
            thumbnail_url=thumbnail_url
        )
        
        # Add admin override flag
        featured_dict = featured_video.dict()
        featured_dict['admin_override'] = True
        featured_dict['set_by_admin'] = admin['username']
        
        await db.featured_video.update_one(
            {},
            {'$set': featured_dict},
            upsert=True
        )
        
        # Log activity
        await log_admin_activity(admin['id'], "update_featured_video", video_data.dict())
        
        logger.info(f"✅ Featured video MANUALLY set by admin {admin['username']}: {video_data.video_id}")
        
        # Broadcast update to all clients
        await broadcast_admin_update("featured_video_update", {
            "video_id": video_data.video_id,
            "title": video_data.title,
            "manual_override": True
        })
        
        return {
            "success": True, 
            "message": "Featured video updated successfully (manual override active)",
            "admin_override": True
        }
        
    except Exception as e:
        logger.error(f"❌ Update featured video error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update featured video")

# Recent Streams Management - Enhanced
@admin_router.get("/streams", response_model=List[RecentStream])
async def get_recent_streams(admin = Depends(get_current_admin)):
    """Get recent streams"""
    try:
        db = get_database()
        streams = await db.recent_streams.find({}).sort([('created_at', -1)]).to_list(length=None)
        return [RecentStream(**stream) for stream in streams]
        
    except Exception as e:
        logger.error(f"❌ Get streams error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch streams")

@admin_router.post("/streams/add")
async def add_recent_stream(stream_data: AddStreamRequest, admin = Depends(get_current_admin)):
    """Add new recent stream"""
    try:
        db = get_database()
        
        # Generate thumbnail if not provided
        thumbnail_url = stream_data.thumbnail
        if not thumbnail_url and 'youtube.com/watch?v=' in stream_data.video_url:
            video_id = stream_data.video_url.split('v=')[1].split('&')[0]
            thumbnail_url = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        
        new_stream = RecentStream(
            title=stream_data.title,
            game=stream_data.game,
            duration=stream_data.duration,
            views=stream_data.views,
            video_url=stream_data.video_url,
            thumbnail=thumbnail_url or ''
        )
        
        await db.recent_streams.insert_one(new_stream.dict())
        
        # Log activity
        await log_admin_activity(admin['id'], "add_stream", stream_data.dict())
        
        logger.info(f"✅ Stream added: {stream_data.title} by admin {admin['username']}")
        
        return {"success": True, "message": "Stream added successfully"}
        
    except Exception as e:
        logger.error(f"❌ Add stream error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add stream")

@admin_router.delete("/streams/{stream_id}")
async def delete_stream(stream_id: str, admin = Depends(get_current_admin)):
    """Delete a stream"""
    try:
        db = get_database()
        
        result = await db.recent_streams.delete_one({'id': stream_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        # Log activity
        await log_admin_activity(admin['id'], "delete_stream", {"stream_id": stream_id})
        
        return {"success": True, "message": "Stream deleted successfully"}
        
    except Exception as e:
        logger.error(f"❌ Delete stream error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete stream")
@admin_router.get("/streams", response_model=List[RecentStream])
async def get_recent_streams(admin = Depends(get_current_admin)):
    """Get recent streams"""
    try:
        db = get_database()
        streams = await db.recent_streams.find({}).sort([('created_at', -1)]).to_list(length=None)
        return [RecentStream(**stream) for stream in streams]
        
    except Exception as e:
        logger.error(f"❌ Get streams error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch streams")

@admin_router.post("/streams/add")
async def add_recent_stream(stream_data: AddStreamRequest, admin = Depends(get_current_admin)):
    """Add new recent stream"""
    try:
        db = get_database()
        
        # Generate thumbnail if not provided
        thumbnail_url = stream_data.thumbnail
        if not thumbnail_url and 'youtube.com/watch?v=' in stream_data.video_url:
            video_id = stream_data.video_url.split('v=')[1].split('&')[0]
            thumbnail_url = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        
        new_stream = RecentStream(
            title=stream_data.title,
            game=stream_data.game,
            duration=stream_data.duration,
            views=stream_data.views,
            video_url=stream_data.video_url,
            thumbnail=thumbnail_url or ''
        )
        
        await db.recent_streams.insert_one(new_stream.dict())
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="add_stream",
            details=stream_data.dict()
        ).dict())
        
        logger.info(f"✅ Stream added: {stream_data.title} by admin {admin['username']}")
        
        return {"success": True, "message": "Stream added successfully"}
        
    except Exception as e:
        logger.error(f"❌ Add stream error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add stream")

@admin_router.delete("/streams/{stream_id}")
async def delete_stream(stream_id: str, admin = Depends(get_current_admin)):
    """Delete a stream"""
    try:
        db = get_database()
        
        result = await db.recent_streams.delete_one({'id': stream_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="delete_stream",
            details={"stream_id": stream_id}
        ).dict())
        
        return {"success": True, "message": "Stream deleted successfully"}
        
    except Exception as e:
        logger.error(f"❌ Delete stream error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete stream")

# Admin Activity Log
@admin_router.get("/activity", response_model=List[AdminActivity])
async def get_admin_activity(limit: int = 50, admin = Depends(get_current_admin)):
    """Get recent admin activity"""
    try:
        db = get_database()
        
        activities = await db.admin_activity.find({}).sort([('timestamp', -1)]).limit(limit).to_list(length=None)
        return [AdminActivity(**activity) for activity in activities]
        
    except Exception as e:
        logger.error(f"❌ Get activity error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch activity log")

# YouTube Real-time Sync Endpoints
@admin_router.post("/youtube/sync")
async def manual_youtube_sync(background_tasks: BackgroundTasks, admin = Depends(get_current_admin)):
    """Manually trigger YouTube sync"""
    try:
        sync_manager = get_sync_manager()
        await sync_manager.initialize_db()
        
        # Trigger sync in background
        result = await sync_manager.sync_channel_data()
        
        if result['success']:
            # Log activity
            await log_admin_activity(admin['id'], "manual_youtube_sync", {
                "sync_time": result['sync_time'],
                "channel_data": result['channel_data']
            })
            
            return {
                "success": True,
                "message": "YouTube sync completed successfully",
                "data": result
            }
        else:
            return {
                "success": False,
                "message": f"YouTube sync failed: {result.get('error')}",
                "data": result
            }
            
    except Exception as e:
        logger.error(f"❌ Manual sync error: {e}")
        raise HTTPException(status_code=500, detail="Manual sync failed")

@admin_router.get("/youtube/sync-status")
async def get_sync_status(admin = Depends(get_current_admin)):
    """Get YouTube sync status"""
    try:
        db = get_database()
        
        # Get latest channel stats
        channel_stats = await db.channel_stats.find_one({}, {"_id": 0}, sort=[('last_updated', -1)])
        
        # Get recent videos count
        recent_videos = await db.recent_videos.count_documents({})
        
        # Get last sync time
        last_sync = None
        if channel_stats and 'last_updated' in channel_stats:
            last_sync = channel_stats['last_updated']
        
        return {
            "sync_active": True,
            "last_sync": last_sync,
            "channel_stats": channel_stats,
            "recent_videos_count": recent_videos,
            "next_sync": "Every 5 minutes"
        }
        
    except Exception as e:
        logger.error(f"❌ Sync status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

@admin_router.post("/youtube/force-update")
async def force_youtube_update(update_data: dict, admin = Depends(get_current_admin)):
    """Force update YouTube data manually"""
    try:
        db = get_database()
        
        # Update channel stats if provided
        if 'channel_stats' in update_data:
            stats_data = update_data['channel_stats']
            stats_data['updated_at'] = datetime.now()
            stats_data['manual_override'] = True
            
            await db.channel_stats.update_one(
                {},
                {'$set': stats_data},
                upsert=True
            )
        
        # Update videos if provided
        if 'videos' in update_data:
            for video in update_data['videos']:
                video['updated_at'] = datetime.now()
                video['manual_override'] = True
                
                await db.recent_videos.update_one(
                    {'video_id': video.get('video_id', video.get('id'))},
                    {'$set': video},
                    upsert=True
                )
        
        # Log activity
        await log_admin_activity(admin['id'], "force_youtube_update", update_data)
        
        return {"success": True, "message": "YouTube data updated manually"}
        
    except Exception as e:
        logger.error(f"❌ Force update error: {e}")
        raise HTTPException(status_code=500, detail="Force update failed")

# Enhanced Dashboard with Real-time Data
@admin_router.get("/dashboard/real-time-stats")
async def get_real_time_stats(admin = Depends(get_current_admin)):
    """Get real-time dashboard stats with YouTube sync"""
    try:
        db = get_database()
        
        # Trigger fresh sync if data is old
        channel_stats = await db.channel_stats.find_one({}, {"_id": 0}, sort=[('last_updated', -1)])
        
        sync_needed = True
        if channel_stats and 'last_updated' in channel_stats:
            time_diff = datetime.now() - channel_stats['last_updated']
            if time_diff.total_seconds() < 300:  # Less than 5 minutes old
                sync_needed = False
        
        if sync_needed:
            # Trigger background sync
            try:
                sync_manager = await get_sync_manager()
                await sync_manager.initialize()  # Initialize DB and YouTube client
                sync_result = await sync_manager.sync_channel_stats()
                
                if sync_result:
                    channel_stats = sync_result
            except Exception as e:
                logger.warning(f"⚠️ YouTube sync failed, using fallback: {e}")
        
        # Get counts
        recent_streams_count = await db.recent_streams.count_documents({})
        scheduled_streams_count = await db.stream_schedule.count_documents({})
        recent_videos_count = await db.recent_videos.count_documents({})
        
        return {
            "channel_stats": channel_stats or {
                "subscriber_count": "178",
                "video_count": "15",
                "view_count": "3247",
                "is_live": False,
                "current_viewers": "0"
            },
            "recent_streams_count": recent_streams_count,
            "scheduled_streams_count": scheduled_streams_count,
            "recent_videos_count": recent_videos_count,
            "last_updated": datetime.now(),
            "sync_status": "active"
        }
        
    except Exception as e:
        logger.error(f"❌ Real-time stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch real-time stats")

# Helper function for activity logging
async def log_admin_activity(admin_id: str, action: str, details: dict):
    """Log admin activity"""
    try:
        db = get_database()
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin_id,
            action=action,
            details=details
        ).dict())
    except Exception as e:
        logger.error(f"❌ Activity logging error: {e}")
@admin_router.get("/settings", response_model=SiteSettings)
async def get_site_settings(admin = Depends(get_current_admin)):
    """Get site settings"""
    try:
        db = get_database()
        
        settings = await db.site_settings.find_one({})
        if not settings:
            default_settings = SiteSettings()
            await db.site_settings.insert_one(default_settings.dict())
            return default_settings
        
        return SiteSettings(**settings)
        
    except Exception as e:
        logger.error(f"❌ Get settings error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch site settings")

@admin_router.post("/settings/update")
async def update_site_settings(settings_data: SiteSettings, admin = Depends(get_current_admin)):
    """Update site settings"""
    try:
        db = get_database()
        
        await db.site_settings.update_one(
            {},
            {'$set': settings_data.dict()},
            upsert=True
        )
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="update_site_settings",
            details=settings_data.dict()
        ).dict())
        
        return {"success": True, "message": "Site settings updated successfully"}
        
    except Exception as e:
        logger.error(f"❌ Update settings error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update site settings")

# ============================================================================
# ABOUT TAGS MANAGEMENT ENDPOINTS
# ============================================================================

@admin_router.get("/content/tags")
async def get_about_tags():
    """Get About section tags - PUBLIC ACCESS"""
    try:
        db = get_database()
        tags_doc = await db.about_tags.find_one({}, {"_id": 0})
        
        if not tags_doc:
            # Return default tags if none exist
            default_tags = [
                {"icon": "🏆", "text": "Competitive Player"},
                {"icon": "🏎️", "text": "Rocket Racing Specialist"},
                {"icon": "📺", "text": "Content Creator"},
                {"icon": "🇷🇸", "text": "Serbia (CET)"},
                {"icon": "💯", "text": "Authentic Gameplay"}
            ]
            return {"tags": default_tags}
        
        return {"tags": tags_doc.get("tags", [])}
        
    except Exception as e:
        logger.error(f"❌ Get tags error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tags")

@admin_router.post("/content/tags/update")
async def update_about_tags(
    tags_data: dict,
    admin = Depends(get_current_admin)
):
    """Update About section tags - ADMIN ONLY"""
    try:
        db = get_database()
        
        # Validate tags structure
        tags = tags_data.get("tags", [])
        if not isinstance(tags, list):
            raise HTTPException(status_code=400, detail="Tags must be an array")
        
        # Ensure each tag has icon and text
        for tag in tags:
            if not isinstance(tag, dict) or "icon" not in tag or "text" not in tag:
                raise HTTPException(status_code=400, detail="Each tag must have 'icon' and 'text' fields")
        
        # Update or insert tags
        await db.about_tags.update_one(
            {},
            {"$set": {
                "tags": tags,
                "updated_at": datetime.now(),
                "updated_by": admin['username']
            }},
            upsert=True
        )
        
        logger.info(f"✅ About tags updated: {len(tags)} tags")
        
        # Broadcast update
        await broadcast_admin_update("tags_update", {"tags": tags})
        
        # Log activity
        await db.admin_activity.insert_one(AdminActivity(
            admin_id=admin['id'],
            action="update_about_tags",
            details={"tags_count": len(tags)}
        ).dict())
        
        return {"success": True, "message": "Tags updated successfully", "tags": tags}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update tags error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update tags")

async def create_default_admin():
    """Create default admin user if none exists"""
    try:
        db = get_database()
        
        existing_admin = await db.admin_users.find_one({'username': 'admin'})
        if not existing_admin:
            default_admin = AdminUser(
                username='admin',
                password_hash=hash_password('remza019admin')  # Default password
            )
            await db.admin_users.insert_one(default_admin.dict())
            logger.info("✅ Default admin user created - Username: admin, Password: remza019admin")
            
    except Exception as e:
        logger.error(f"❌ Error creating default admin: {e}")

@admin_router.get("/events")
async def get_admin_events():
    """
    Get recent admin events/activity
    Returns empty for now - can be expanded later for audit logs
    """
    return {
        "events": [],
        "message": "No recent events"
    }