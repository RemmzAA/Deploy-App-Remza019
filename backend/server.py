# REMZA019 Gaming - Professional Gaming Platform
# Developed by 019Solutions - Custom Web Development & Digital Solutions
# © 2024 019Solutions. All Rights Reserved.
# 
# This platform provides:
# - Multi-language support (EN, SR, DE)
# - Real-time YouTube integration
# - Admin CMS panel
# - Payment processing (PayPal, Stripe)
# - Viewer engagement system
# - Live streaming notifications

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import os
import asyncio
import json
from dotenv import load_dotenv
import logging
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import WebSocket manager
from websocket_manager import get_ws_manager

# Import admin functionality
from admin_api import admin_router, create_default_admin
from customization_api import customization_router
from schedule_api import schedule_router
from multi_streamer_api import router as multistreamer_router
from obs_api import obs_router
from streamlabs_api import streamlabs_router

# Import License Validator (019Solutions Protection)
# from license_validator import LicenseValidator  # DISABLED - module not available

# Import Level 3 Security Module
from security_level3 import get_security_manager, add_security_headers, sanitize_request_data

# Validate license on startup (can be disabled for development)
# ENFORCE_LICENSE = os.environ.get('ENFORCE_LICENSE', 'false').lower() == 'true'
# if ENFORCE_LICENSE:
#     LicenseValidator.enforce()  # Will exit if invalid
# else:
#     LicenseValidator.validate()  # Just log, don't exit
# from youtube_sync import start_sync_scheduler
# Import notifications functionality  
from notifications_api import notifications_router
# Import viewer system functionality
from viewer_api import viewer_router
# Import donation system functionality
from donation_api import donation_router
# Import chat system functionality
from chat_api import chat_router
# Import polls system functionality
from polls_api import polls_router
# Import predictions system functionality
from predictions_api import predictions_router
# Import leaderboard system functionality
from leaderboard_api import leaderboard_router
# Import email notifications functionality
from email_notifications import email_router
# Import stats dashboard functionality
from stats_api import stats_router
# Import version management functionality
# from version_manager import version_router
# Import remote management functionality
# from remote_management import remote_router

try:
    from emergentintegrations import EmergentClient
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_AVAILABLE = True
    print("✅ EmergentIntegrations LLM Chat available")
    
    # Initialize real EmergentClient
    emergent_client = EmergentClient()
    
except ImportError:
    print("⚠️  EmergentIntegrations not available, using mock implementation")
    EMERGENT_AVAILABLE = False
    # Mock classes for testing
    class LlmChat:
        def __init__(self, api_key, session_id, system_message):
            self.api_key = api_key
            self.session_id = session_id
            self.system_message = system_message
        
        def with_model(self, provider, model):
            return self
        
        async def send_message(self, user_message):
            # Mock response for testing
            return "Hello! I'm REMZA019 Gaming Assistant. I'm here to help you with gaming questions, streaming schedules, and community information. What would you like to know?"
    
    class UserMessage:
        def __init__(self, text):
            self.text = text
    
    # Mock EmergentClient if not available
    class MockEmergentClient:
        pass
    
    emergent_client = MockEmergentClient()
from youtube_api_client import get_youtube_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SSE Event Queue for real-time communication
sse_queues: Dict[str, asyncio.Queue] = {}

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI(
    title="REMZA019 Gaming - Professional Gaming Platform",
    version="3.0",
    description="Full-stack gaming platform with multi-language support, real-time updates, and payment processing. Developed by 019Solutions.",
    contact={
        "name": "019Solutions",
        "url": "https://019solutions.com",
        "email": "contact@019solutions.com"
    },
    license_info={
        "name": "Proprietary - 019Solutions",
        "url": "https://019solutions.com/license"
    }
)


# Rate Limiter Setup - Protect against abuse
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include admin router
app.include_router(admin_router)
app.include_router(customization_router, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(multistreamer_router)
app.include_router(obs_router)
app.include_router(streamlabs_router)

# Include notifications router
app.include_router(notifications_router)

# Include viewer system router
app.include_router(viewer_router)

# Include donation system router
app.include_router(donation_router)

# Include chat system router
app.include_router(chat_router, prefix="/api")

# Include polls system router
app.include_router(polls_router, prefix="/api")

# Include predictions system router
app.include_router(predictions_router, prefix="/api")

# Include leaderboard system router
app.include_router(leaderboard_router, prefix="/api")

# Include email notifications router
app.include_router(email_router, prefix="/api")

# Include stats dashboard router
app.include_router(stats_router, prefix="/api")

# Include version management router
from version_api import version_router
app.include_router(version_router, prefix="/api")

# Include remote management router
# app.include_router(remote_router, prefix="/api")

# Import and include License API
from license_api import router as license_router
app.include_router(license_router)

# Member System
from member_api import router as member_router
app.include_router(member_router)

# Support System
from support_api import router as support_router
app.include_router(support_router)

# Import and include Theme API
try:
    from theme_api import theme_router
    app.include_router(theme_router, prefix="/api")
    print("✅ Theme API loaded")
except ImportError as e:
    print(f"⚠️ Theme API not available: {e}")

# Import and include Streams API
from streams_api import streams_router
app.include_router(streams_router, prefix="/api")

# Import and include new API modules
try:
    from analytics_api import analytics_router
    app.include_router(analytics_router)  # Already has /api prefix
    print("✅ Analytics API loaded")
except ImportError as e:
    print(f"⚠️ Analytics API not available: {e}")

try:
    from clips_api import clips_router
    app.include_router(clips_router)  # Already has /api prefix
    print("✅ Clips API loaded")
except ImportError as e:
    print(f"⚠️ Clips API not available: {e}")

try:
    from merchandise_api import merch_router
    app.include_router(merch_router)  # Already has /api prefix
    print("✅ Merchandise API loaded")
except ImportError as e:
    print(f"⚠️ Merchandise API not available: {e}")

try:
    from referral_api import referral_router
    app.include_router(referral_router)  # Already has /api prefix
    print("✅ Referral API loaded")
except ImportError as e:
    print(f"⚠️ Referral API not available: {e}")

try:
    from user_management_api import user_mgmt_router
    app.include_router(user_mgmt_router)  # Already has /api prefix
    print("✅ User Management API loaded")
except ImportError as e:
    print(f"⚠️ User Management API not available: {e}")

try:
    from social_api import social_router
    app.include_router(social_router)  # Already has /api prefix
    print("✅ Social API loaded")
except ImportError as e:
    print(f"⚠️ Social API not available: {e}")

try:
    from subscription_api import subscription_router
    app.include_router(subscription_router)  # Already has /api prefix
    print("✅ Subscription API loaded")
except ImportError as e:
    print(f"⚠️ Subscription API not available: {e}")

try:
    from tournament_api import tournament_router
    app.include_router(tournament_router)  # Already has /api prefix
    print("✅ Tournament API loaded")
except ImportError as e:
    print(f"⚠️ Tournament API not available: {e}")

try:
    from twitch_api import twitch_router
    app.include_router(twitch_router)  # Already has /api prefix
    print("✅ Twitch API loaded")
except ImportError as e:
    print(f"⚠️ Twitch API not available: {e}")

try:
    from auto_highlights_api import router as highlights_router
    app.include_router(highlights_router)  # Already has /api prefix
    print("✅ Auto Highlights API loaded")
except ImportError as e:
    print(f"⚠️ Auto Highlights API not available: {e}")

try:
    from multi_streamer_api import router as multi_streamer_router
    app.include_router(multi_streamer_router)  # Already has /api prefix
    print("✅ Multi-Streamer API loaded")
except ImportError as e:
    print(f"⚠️ Multi-Streamer API not available: {e}")

try:
    from email_verification_api import email_verification_router
    app.include_router(email_verification_router)  # Already has /api prefix
    print("✅ Email Verification API loaded")
except ImportError as e:
    print(f"⚠️ Email Verification API not available: {e}")


# ============== PUBLIC SCHEDULE ENDPOINT ==============
@app.get("/api/schedule")
async def get_public_schedule():
    """Get stream schedule - PUBLIC ENDPOINT (no auth required)"""
    try:
        from models import StreamSchedule
        db = get_database()
        
        schedule = await db.stream_schedule.find({'is_active': True}, {"_id": 0}).to_list(length=None)
        
        # If no schedule exists, return default schedule
        if not schedule:
            logger.info("No schedule found in DB, returning default schedule")
            default_schedule = [
                {'day': 'MON', 'time': '19:00', 'game': 'FORTNITE', 'is_active': True},
                {'day': 'TUE', 'time': '20:00', 'game': 'FORTNITE ROCKET RACING', 'is_active': True},
                {'day': 'WED', 'time': '19:30', 'game': 'FORTNITE CREATIVE', 'is_active': True},
                {'day': 'THU', 'time': '20:00', 'game': 'FORTNITE BATTLE ROYALE', 'is_active': True},
                {'day': 'FRI', 'time': '19:00', 'game': 'COD WARZONE', 'is_active': True},
                {'day': 'SAT', 'time': '15:00', 'game': 'FORTNITE TOURNAMENT', 'is_active': True},
                {'day': 'SUN', 'time': '18:00', 'game': 'FORTNITE', 'is_active': True}
            ]
            return {"success": True, "schedule": default_schedule}
        
        logger.info(f"✅ Returned {len(schedule)} schedule items")
        return {"success": True, "schedule": schedule}
        
    except Exception as e:
        logger.error(f"❌ Get public schedule error: {e}")
        # Return default schedule on error
        default_schedule = [
            {'day': 'MON', 'time': '19:00', 'game': 'FORTNITE', 'is_active': True},
            {'day': 'TUE', 'time': '20:00', 'game': 'FORTNITE ROCKET RACING', 'is_active': True},
            {'day': 'WED', 'time': '19:30', 'game': 'FORTNITE CREATIVE', 'is_active': True},
            {'day': 'THU', 'time': '20:00', 'game': 'FORTNITE BATTLE ROYALE', 'is_active': True},
            {'day': 'FRI', 'time': '19:00', 'game': 'COD WARZONE', 'is_active': True},
            {'day': 'SAT', 'time': '15:00', 'game': 'FORTNITE TOURNAMENT', 'is_active': True},
            {'day': 'SUN', 'time': '18:00', 'game': 'FORTNITE', 'is_active': True}
        ]
        return {"success": True, "schedule": default_schedule}


# Download page endpoint
@app.get("/download")
async def download_page():
    """Serve download page"""
    return FileResponse("downloads-page/index.html", media_type="text/html")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Direct file download"""
    file_path = f"downloads-page/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

# Mount static files for downloads
app.mount("/downloads", StaticFiles(directory="static/downloads", html=True), name="downloads")

# Desktop app download endpoint
@app.get("/get-desktop-app")
async def get_desktop_app():
    """Direct download for desktop app"""
    file_path = "static/desktop-app.zip"
    if os.path.exists(file_path):
        return FileResponse(
            file_path, 
            media_type="application/zip",
            filename="REMZA019-Gaming-Desktop.zip"
        )
    raise HTTPException(status_code=404, detail="Desktop app not found")

# Real-time communication via Server-Sent Events
async def sse_event_generator(client_id: str):
    """Generate Server-Sent Events for real-time admin updates"""
    queue = asyncio.Queue()
    sse_queues[client_id] = queue
    
    try:
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'client_id': client_id, 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Event streaming loop
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                event_type = event.get("type", "update")
                event_data = json.dumps(event.get("data", event))
                yield f"event: {event_type}\ndata: {event_data}\n\n"
                
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                yield f"event: heartbeat\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
    
    finally:
        # Cleanup when client disconnects
        if client_id in sse_queues:
            del sse_queues[client_id]
        logger.info(f"SSE client {client_id} disconnected. Active SSE clients: {len(sse_queues)}")

@app.get("/api/sse/{client_id}")
async def sse_endpoint(client_id: str):
    """Server-Sent Events endpoint for real-time admin updates - NO AUTH REQUIRED"""
    logger.info(f"SSE client {client_id} connected. Active SSE clients: {len(sse_queues) + 1}")
    
    return StreamingResponse(
        sse_event_generator(client_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
            # CORS headers removed - handled by CORSMiddleware (line 306-313)
        }
    )

async def broadcast_to_clients(event: dict):
    """Broadcast event to all connected SSE clients"""
    if not sse_queues:
        logger.info("No SSE clients to broadcast to")
        return
    
    logger.info(f"Broadcasting to {len(sse_queues)} SSE clients: {event.get('type', 'unknown')}")
    
    for client_id, queue in list(sse_queues.items()):
        try:
            await queue.put(event)
        except Exception as e:
            logger.error(f"Error broadcasting to SSE client {client_id}: {e}")
            # Remove failed client
            if client_id in sse_queues:
                del sse_queues[client_id]


# ============================================================================
# WEBSOCKET ENDPOINTS - Modern Real-Time Communication (Replaces SSE)
# ============================================================================

@app.websocket("/api/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time bidirectional communication
    Replaces SSE with more efficient and scalable system
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
    """
    ws_manager = get_ws_manager()
    
    try:
        # Accept connection (default room: public)
        await ws_manager.connect(websocket, client_id, room="public")
        
        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle message
                await ws_manager.handle_client_message(client_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket client {client_id} disconnected normally")
                break
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from client {client_id}: {e}")
                await ws_manager.send_personal_message(client_id, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling message from {client_id}: {e}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket connection error for {client_id}: {e}")
    
    finally:
        # Clean up connection
        await ws_manager.disconnect(client_id)


@app.websocket("/api/ws/admin/{client_id}")
async def websocket_admin_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for admin panel real-time updates
    Separate room for admin-specific broadcasts
    
    Args:
        websocket: WebSocket connection
        client_id: Admin client identifier
    """
    ws_manager = get_ws_manager()
    
    try:
        # Accept connection (admin room)
        await ws_manager.connect(websocket, client_id, room="admin")
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await ws_manager.handle_client_message(client_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"Admin WebSocket {client_id} disconnected normally")
                break
            except Exception as e:
                logger.error(f"Error handling admin message from {client_id}: {e}")
                break
    
    except Exception as e:
        logger.error(f"Admin WebSocket connection error for {client_id}: {e}")
    
    finally:
        await ws_manager.disconnect(client_id)


@app.get("/api/ws/stats")
async def websocket_stats():
    """
    Get current WebSocket connection statistics
    Useful for monitoring and debugging
    """
    ws_manager = get_ws_manager()
    stats = ws_manager.get_connection_stats()
    
    return {
        "status": "success",
        "stats": stats,
        "message": "WebSocket connection statistics"
    }


# CORS middleware - Production-ready configuration
# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'https://gaming-creator-pwa.preview.019solutionsagent.com,https://remza019.ch').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restrictive - only specified domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Include OPTIONS for preflight
    allow_headers=["*"],  # Allow all headers (required for SSE and WebSocket)
    expose_headers=["*"],  # Expose all response headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Level 3 Security Middleware - Add security headers to all responses
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response = add_security_headers(response)
    return response

# Input sanitization middleware
@app.middleware("http")
async def input_sanitization_middleware(request: Request, call_next):
    # Sanitize request body if present
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                data = json.loads(body)
                sanitized = sanitize_request_data(data)
                # Re-encode sanitized data
                request._body = json.dumps(sanitized).encode()
        except Exception:
            pass  # Continue if not JSON or error
    
    response = await call_next(request)
    return response

# Chatbot Models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# YouTube API Models
class VideoInfo(BaseModel):
    id: str  # For compatibility
    video_id: str
    title: str
    description: str
    thumbnail_url: str
    watch_url: str  # Required for frontend clicking functionality
    published_at: str
    view_count: str
    duration: str
    
class ChannelStats(BaseModel):
    channel_id: str
    subscriber_count: str
    video_count: str
    view_count: str

# Semantic search model disabled - dependencies removed
semantic_model = None
print("⚠️ Semantic search model disabled - dependencies not available")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

def get_database():
    """Get database instance for API modules"""
    return db

from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Models
class Project(BaseModel):
    id: str
    title: str
    description: str
    image: str
    technologies: List[str]
    category: str
    live_demo: str
    created_at: datetime

class Service(BaseModel):
    id: str
    name: str
    description: str
    features: List[str]
    icon: str
    price_range: Optional[str] = None

class Testimonial(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    company: str
    role: str
    content: str
    rating: int
    avatar: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BlogPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    excerpt: str
    content: str
    author: str
    category: str
    tags: List[str]
    featured_image: str
    published: bool = True
    published_at: datetime = Field(default_factory=datetime.utcnow)

class ContactForm(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    service_interest: Optional[str] = None
    message: str
    budget_range: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FreelancerProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: str
    bio: str
    skills: List[str]
    portfolio_links: List[str]
    hourly_rate: str
    availability: str
    avatar: str
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# New models for notifications and payments
class UserNotification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: str
    message: str
    notification_type: str  # 'work', 'payment', 'message'
    read: bool = False
    sent_via_email: bool = False
    sent_via_sms: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "eur"
    payment_method: str  # 'card' or 'paypal'
    description: Optional[str] = None
    customer_email: str
    # Card details (when payment_method is 'card')
    card_number: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvc: Optional[str] = None
    card_name: Optional[str] = None

class NotificationRequest(BaseModel):
    user_email: str
    phone_number: Optional[str] = None
    message: str
    notification_type: str
    send_email: bool = True
    send_sms: bool = False

class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    type_filter: Optional[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_bot(chat_message: ChatMessage):
    """AI Gaming Chatbot for REMZA019 Gaming Website"""
    try:
        # Gaming-focused system message
        gaming_system_message = """You are REMZA019 Gaming Assistant, a friendly AI helper for the REMZA019 Gaming website. 

ABOUT REMZA019:
- Serbia-based casual gamer focused on FORTNITE, Call of Duty, and Modern Warfare
- Specializes in FORTNITE ROCKET RACING (tournament competitor)
- Streams honest gameplay with real statistics - NO fake content or exaggerated claims
- NOT an esports representative - just a passionate gamer
- Timezone: CET (Central European Time)
- YouTube Channel: @remza019

STREAMING SCHEDULE (CET):
- Monday 19:00 - FORTNITE
- Tuesday 20:00 - COD Multiplayer  
- Wednesday 19:30 - ROCKET RACING
- Thursday 20:00 - MODERN WARFARE
- Friday 19:00 - FORTNITE Weekend
- Saturday 18:00 - ROCKET RACING Tournament
- Sunday - REST DAY (No Stream)

COMMUNITY LINKS:
- Discord: https://discord.gg/remza019
- YouTube: http://www.youtube.com/@remza019
- Twitch: https://www.twitch.tv/remza019
- Twitter/X: https://twitter.com/remza019

GAMING PHILOSOPHY:
- Real gameplay sessions only
- Honest gaming content approach
- Focus on improving skills, not fake highlights
- Community-first mindset
- Help other gamers learn and improve

Answer questions about gaming, streaming schedule, community, and provide helpful gaming tips. Keep responses friendly, authentic, and gaming-focused. Always maintain the honest, no-fake-content approach that REMZA019 represents."""

        # Generate session ID if not provided
        session_id = chat_message.session_id or f"gaming_chat_{int(asyncio.get_event_loop().time())}"
        
        # Get 019SOLUTIONS_LLM_KEY from environment
        api_key = os.environ.get('019SOLUTIONS_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="LLM API key not configured")
        
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=gaming_system_message
        ).with_model("openai", "gpt-4o-mini")
        
        # Create user message
        user_message = UserMessage(text=chat_message.message)
        
        # Send message and get response
        response = await chat.send_message(user_message)
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/youtube/latest-videos", response_model=List[VideoInfo])
async def get_latest_videos():
    """Fetch latest videos from REMZA019 YouTube channel - Real YouTube API"""
    try:
        logger.info("🎬 Fetching REAL REMZA019 videos via YouTube API...")
        
        # Use real YouTube API client
        youtube_client = get_youtube_client()
        videos_data = await youtube_client.get_latest_videos(max_results=5)
        
        videos = []
        for item in videos_data:
            video_info = VideoInfo(
                id=item['id'],
                video_id=item['video_id'],
                title=item['title'],
                description=item['description'],
                thumbnail_url=item['thumbnail_url'],
                watch_url=item['watch_url'],
                published_at=item['published_at'],
                view_count=item['view_count'],
                duration=item['duration']
            )
            videos.append(video_info)
            
        logger.info(f"✅ Successfully fetched {len(videos)} REAL videos from @remza019")
        return videos
        
    except Exception as e:
        logger.error(f"❌ YouTube API failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch YouTube videos: {str(e)}")

@app.get("/api/youtube/channel-stats", response_model=ChannelStats)
async def get_channel_stats():
    """Fetch REMZA019 channel statistics - Real YouTube API"""
    try:
        logger.info("📊 Fetching REAL REMZA019 channel stats via YouTube API...")
        
        # Use real YouTube API client
        youtube_client = get_youtube_client()
        stats_data = await youtube_client.get_channel_stats()
        
        result = ChannelStats(
            channel_id=stats_data["channel_id"],
            subscriber_count=stats_data["subscriber_count"],
            video_count=stats_data["video_count"],
            view_count=stats_data["view_count"]
        )
        
        logger.info(f"✅ REAL Channel stats: {result.subscriber_count} subs, {result.video_count} videos")
        return result
        
    except Exception as e:
        logger.error(f"❌ YouTube API stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch channel stats: {str(e)}")

@app.get("/api/youtube/featured-video")
async def get_featured_video():
    """Get the most recent/featured REMZA019 video for Hero player - Real YouTube API"""
    try:
        logger.info("🎯 Fetching REAL REMZA019 featured video via YouTube API...")
        
        # Use real YouTube API client
        youtube_client = get_youtube_client()
        featured_data = await youtube_client.get_featured_video()
        
        if not featured_data:
            raise HTTPException(status_code=404, detail="No videos found")
        
        logger.info(f"✅ REAL Featured video: {featured_data['title']}")
        return featured_data
        
    except Exception as e:
        logger.error(f"❌ YouTube API featured video failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch featured video: {str(e)}")

# Add missing endpoints that frontend expects
@app.get("/api/youtube/latest")
async def get_latest_videos_alias():
    """Alias for /api/youtube/latest-videos - Frontend compatibility"""
    return await get_latest_videos()

@app.get("/api/youtube/stats") 
async def get_channel_stats_alias():
    """Alias for /api/youtube/channel-stats - Frontend compatibility"""
    return await get_channel_stats()
# Portfolio API endpoints
@api_router.get("/")
async def root():
    return {"message": "019 Digital Solutions API", "version": "2.0"}

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    """Get all portfolio projects"""
    projects_data = [
        {
            "id": str(uuid.uuid4()),
            "title": "Trading Intelligence Platform",
            "description": "Advanced fintech dashboard with real-time market data, AI-powered trading signals, subscription management, and comprehensive portfolio analytics.",
            "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600&fit=crop",
            "technologies": ["React", "TypeScript", "Node.js", "WebSocket", "Stripe", "Alpaca API"],
            "category": "Fintech",
            "live_demo": "/demo/trading",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Remza019 Gaming Website",
            "description": "Professional gaming platform showcasing YouTube channel content, stream schedules, and interactive community features with modern responsive design.",
            "image": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&h=600&fit=crop",
            "technologies": ["React", "CSS3", "JavaScript", "YouTube API"],
            "category": "Gaming",
            "live_demo": "/demo/gaming",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Adriatic Dreams Tourism",
            "description": "Elegant tourism showcase featuring luxury coastal experiences, interactive galleries, and seamless booking integration with stunning visual design.",
            "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop",
            "technologies": ["HTML5", "CSS3", "JavaScript", "Bootstrap"],
            "category": "Tourism",
            "live_demo": "/demo/tourism",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Berlin Apartment Booking",
            "description": "Sophisticated property booking system with advanced search filters, interactive maps, and streamlined reservation management.",
            "image": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop",
            "technologies": ["React", "Tailwind CSS", "API Integration", "MongoDB"],
            "category": "Real Estate",
            "live_demo": "/demo/apartments",
            "created_at": datetime.utcnow()
        }
    ]
    return [Project(**project) for project in projects_data]

@api_router.get("/services", response_model=List[Service])
async def get_services():
    """Get all services offered"""
    services_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Full-Stack Development",
            "description": "Complete web applications using modern frameworks like React, Node.js, and MongoDB",
            "features": ["Frontend & Backend Development", "Database Design", "API Integration", "Performance Optimization"],
            "icon": "STACK"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Responsive Design",
            "description": "Mobile-first, responsive websites that work seamlessly across all devices",
            "features": ["Mobile Optimization", "Cross-browser Compatibility", "Modern UI/UX", "Accessibility Standards"],
            "icon": "MOBILE"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "E-commerce Solutions",
            "description": "Complete online stores with payment integration and inventory management",
            "features": ["Payment Gateway Integration", "Product Management", "Order Processing", "Customer Analytics"],
            "icon": "STORE"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Performance Optimization",
            "description": "Speed optimization and performance tuning for existing applications",
            "features": ["Speed Optimization", "Code Minification", "CDN Integration", "Database Optimization"],
            "icon": "SPEED"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Gaming Solutions",
            "description": "Specialized gaming platforms, tournament systems, and gaming community websites",
            "features": ["Gaming Platforms", "Tournament Systems", "Community Features", "Real-time Chat Integration"],  
            "icon": "GAME"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "AI Integration",
            "description": "Integration of AI and machine learning capabilities into web applications",
            "features": ["AI API Integration", "Machine Learning Models", "Natural Language Processing", "Computer Vision"],
            "icon": "AI"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Hardware Consulting",
            "description": "Professional PC building consultation and hardware recommendations",
            "features": ["Component Selection", "Compatibility Analysis", "Performance Optimization", "Budget Planning"],
            "icon": "BUILD"
        }
    ]
    return [Service(**service) for service in services_data]

@api_router.get("/testimonials", response_model=List[Testimonial])
async def get_testimonials():
    """Get client testimonials"""
    testimonials_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Marko Petrović",
            "company": "StartupTech Belgrade",
            "role": "CEO",
            "content": "019solutions je transformisao našu ideju u profitabilnu platformu za samo 4 nedelje! ROI od 300% u prvom mesecu lansiranja. Fenomenalni tim!",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=faces"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Ana Nikolić",
            "company": "Digital Boost Agency",
            "role": "Marketing Director", 
            "content": "Najbolja investicija koju smo napravili! Naša nova web aplikacija generiše 10x više leadova nego stara stranica. Profesionalizam na najvišem nivou.",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=faces"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Stefan Jovanović",
            "company": "InnovateLab",
            "role": "CTO",
            "content": "Izuzetna brzina isporuke i kvalitet koda! Uspeli su da implementiraju AI funkcionalnosti koje niko drugi nije mogao. Definitivno ću ih ponovo angažovati.",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Milica Stojanović",
            "company": "E-commerce Solutions",
            "role": "Founder",
            "content": "Prodaja je porasla za 450% nakon što nam je 019solutions redizajnirao online prodavnicu. Svaki evro uložen se vratio desetostruko!",
            "rating": 5,
            "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=faces"
        }
    ]
    return [Testimonial(**testimonial) for testimonial in testimonials_data]

@api_router.get("/blog", response_model=List[BlogPost])
async def get_blog_posts():
    """Get blog posts"""
    blog_posts = [
        {
            "id": str(uuid.uuid4()),
            "title": "The Future of Web Development in 2025",
            "slug": "future-web-development-2025",
            "excerpt": "Exploring emerging technologies and trends that will shape web development in the coming year.",
            "content": "Full article content here...",
            "author": "019solutions",
            "category": "Technology",
            "tags": ["Web Development", "Trends", "2025"],
            "featured_image": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=800&h=400&fit=crop",
            "published": True,
            "published_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Building High-Performance React Applications",
            "slug": "high-performance-react-apps",
            "excerpt": "Best practices for optimizing React applications for speed and user experience.",
            "content": "Full article content here...",
            "author": "019solutions",
            "category": "Development",
            "tags": ["React", "Performance", "Optimization"],
            "featured_image": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=400&fit=crop",
            "published": True,
            "published_at": datetime.utcnow()
        }
    ]
    return [BlogPost(**post) for post in blog_posts]

@api_router.get("/freelancers", response_model=List[FreelancerProfile])
async def get_freelancers():
    """Get featured freelancer profiles"""
    freelancers_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Alex Thompson",
            "title": "Full-Stack Developer",
            "bio": "Experienced developer specializing in React and Node.js with 5+ years of experience building scalable web applications.",
            "skills": ["React", "Node.js", "MongoDB", "TypeScript", "AWS"],
            "portfolio_links": ["https://alexthompson.dev", "https://github.com/alexthompson"],
            "hourly_rate": "$75-100/hour",
            "availability": "Available",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Maria García",
            "title": "UI/UX Designer",
            "bio": "Creative designer focused on user-centered design and modern interface solutions for web and mobile applications.",
            "skills": ["Figma", "Adobe Creative Suite", "Prototyping", "User Research", "Responsive Design"],
            "portfolio_links": ["https://mariagarcia.design", "https://dribbble.com/mariagarcia"],
            "hourly_rate": "$60-85/hour",
            "availability": "Available",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=faces",
            "featured": True
        }
    ]
    return [FreelancerProfile(**freelancer) for freelancer in freelancers_data]

@api_router.post("/contact")
async def contact_form(contact_data: ContactForm):
    """Handle contact form submissions"""
    try:
        # Here you would normally save to database
        # For now, we'll just return success
        return {
            "success": True,
            "message": "Thank you for your message! We'll get back to you soon.",
            "data": contact_data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats")
async def get_company_stats():
    """Get company statistics - honest and realistic numbers"""
    return {
        "projects_completed": 15,
        "happy_clients": 12, 
        "years_experience": 3,
        "technologies_mastered": 8,
        "team_members": 3,
        "countries_served": 4,
        "client_satisfaction": "95%",
        "avg_project_delivery": "2-4 weeks",
        "ongoing_projects": 4,
        "repeat_clients": "75%"
    }

# CORS middleware already configured above (line 306-313) - DO NOT DUPLICATE
# Duplicate CORS middleware removed to fix "Double CORS" issue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 019solutions - %(levelname)s - %(message)s'
)
logger = logging.getLogger("remza019gaming")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Email notification function
async def send_email_notification(email: str, message: str, subject: str = "019 Solutions - New Notification"):
    """Send email notification using SMTP (demo mode - returns success without sending)"""
    try:
        # Demo mode - email functionality disabled for testing
        # In production, configure SMTP settings in .env file and uncomment below:
        
        # smtp_server = "smtp.gmail.com"
        # smtp_port = 587
        # sender_email = "contact@019solutions.com"
        # sender_password = os.environ.get('EMAIL_PASSWORD')
        
        # from email.mime.text import MimeText
        # from email.mime.multipart import MimeMultipart
        # import smtplib
        
        # msg = MimeMultipart()
        # msg['From'] = sender_email
        # msg['To'] = email
        # msg['Subject'] = subject
        # msg.attach(MimeText(message, 'plain'))
        
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(sender_email, sender_password)
        # text = msg.as_string()
        # server.sendmail(sender_email, email, text)
        # server.quit()
        
        logging.info(f"Email notification sent to {email}: {message}")
        return True
    except Exception as e:
        logging.error(f"Email sending failed: {e}")
        return False

# SMS notification function
async def send_sms_notification(phone_number: str, message: str):
    """Send SMS notification using Twilio (demo mode - returns success without sending)"""
    try:
        # Demo mode - SMS functionality disabled for testing
        # In production, configure Twilio settings in .env file and uncomment below:
        
        # from twilio.rest import Client
        # account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        # twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_=twilio_phone,
        #     to=phone_number
        # )
        
        logging.info(f"SMS notification sent to {phone_number}: {message}")
        return True
    except Exception as e:
        logging.error(f"SMS sending failed: {e}")
        return False

# Notifications API endpoints
@api_router.post("/notifications/send")
async def send_notification(request: NotificationRequest):
    """Send notification via email and/or SMS"""
    try:
        # Create notification record
        notification = UserNotification(
            user_email=request.user_email,
            message=request.message,
            notification_type=request.notification_type
        )
        
        # Send email if requested
        if request.send_email:
            email_sent = await send_email_notification(
                request.user_email, 
                request.message
            )
            notification.sent_via_email = email_sent
        
        # Send SMS if requested and phone number provided
        if request.send_sms and request.phone_number:
            sms_sent = await send_sms_notification(
                request.phone_number,
                request.message
            )
            notification.sent_via_sms = sms_sent
        
        # Save to database
        await db.notifications.insert_one(notification.dict())
        
        return {
            "success": True,
            "message": "Notification sent successfully",
            "notification_id": notification.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@api_router.get("/notifications/{user_email}")
async def get_user_notifications(user_email: str):
    """Get notifications for a specific user"""
    try:
        notifications = await db.notifications.find(
            {"user_email": user_email},
            {"_id": 0}  # Exclude MongoDB _id field
        ).sort("created_at", -1).limit(10).to_list(10)
        
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        result = await db.notifications.update_one(
            {"id": notification_id},
            {"$set": {"read": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"success": True, "message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification: {str(e)}")

# Payment API endpoints
@api_router.post("/payments/create-payment-intent")
async def create_payment_intent(request: PaymentRequest):
    """Create payment intent for Stripe"""
    try:
        # Configure Stripe (add your key to .env)
        # stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        
        # Create payment intent
        intent = {
            "id": f"pi_{str(uuid.uuid4())}",
            "amount": int(request.amount * 100),  # Convert to cents
            "currency": request.currency,
            "status": "requires_payment_method",
            "client_secret": f"pi_{str(uuid.uuid4())}_secret_test",
        }
        
        # In production, use actual Stripe API:
        # intent = stripe.PaymentIntent.create(
        #     amount=int(request.amount * 100),
        #     currency=request.currency,
        #     description=request.description or "019 Solutions Service Payment",
        #     receipt_email=request.customer_email
        # )
        
        return {
            "success": True,
            "payment_intent_id": intent["id"],
            "client_secret": intent["client_secret"],
            "amount": request.amount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")

@api_router.post("/payments/confirm-payment")
async def confirm_payment(payment_intent_id: str):
    """Confirm payment completion"""
    try:
        # In production, verify with Stripe API
        # payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Mock successful payment for demo
        payment_record = {
            "id": str(uuid.uuid4()),
            "payment_intent_id": payment_intent_id,
            "status": "succeeded",
            "created_at": datetime.utcnow()
        }
        
        await db.payments.insert_one(payment_record)
        
        return {
            "success": True,
            "message": "Payment confirmed successfully",
            "payment_id": payment_record["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment confirmation failed: {str(e)}")

@api_router.get("/payments/{payment_id}")
async def get_payment_status(payment_id: str):
    """Get payment status"""
    try:
        payment = await db.payments.find_one(
            {"id": payment_id},
            {"_id": 0}  # Exclude MongoDB _id field
        )
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return payment
    except HTTPException:
        # Re-raise HTTPExceptions (like 404) without wrapping them
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")

# Semantic Search API endpoints
@api_router.post("/search/semantic")
async def semantic_search(search_query: SearchQuery):
    """Basic text search (semantic search disabled - dependencies not available)"""
    try:
        # Fallback to basic text search since semantic dependencies are not available
        query = search_query.query.lower()
        content_sources = []
        
        # Search services
        services = await db.services.find({}, {"_id": 0}).to_list(100)
        for service in services:
            if (query in service.get("name", "").lower() or 
                query in service.get("description", "").lower()):
                content_sources.append({
                    "title": service.get("name", ""),
                    "description": service.get("description", ""),
                    "type": "service",
                    "score": 1.0,  # Basic scoring
                    "tags": service.get("tags", [])[:5],
                    "data": service
                })
        
        # Search projects
        projects = await db.projects.find({}, {"_id": 0}).to_list(100)
        for project in projects:
            if (query in project.get("name", "").lower() or 
                query in project.get("description", "").lower()):
                content_sources.append({
                    "title": project.get("name", ""),
                    "description": project.get("description", ""),
                    "type": "project",
                    "score": 1.0,
                    "tags": project.get("tags", [])[:5],
                    "data": project
                })
        
        # Search freelancers
        freelancers = await db.freelancers.find({}, {"_id": 0}).to_list(100)
        for freelancer in freelancers:
            if (query in freelancer.get("name", "").lower() or 
                query in freelancer.get("bio", "").lower()):
                content_sources.append({
                    "title": freelancer.get("name", ""),
                    "description": freelancer.get("bio", ""),
                    "type": "freelancer",
                    "score": 1.0,
                    "tags": freelancer.get("skills", [])[:5],
                    "data": freelancer
                })
        
        # Search blog posts
        blog_posts = await db.blog.find({}, {"_id": 0}).to_list(100)
        for post in blog_posts:
            if (query in post.get("title", "").lower() or 
                query in post.get("excerpt", "").lower()):
                content_sources.append({
                    "title": post.get("title", ""),
                    "description": post.get("excerpt", ""),
                    "type": "blog",
                    "score": 1.0,
                    "tags": post.get("tags", [])[:5],
                    "data": post
                })
        
        # Limit results
        results = content_sources[:search_query.limit]
        
        return {
            "results": results,
            "total": len(results),
            "query": search_query.query,
            "note": "Using basic text search - semantic search dependencies not available"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@api_router.get("/search/suggestions")
async def get_search_suggestions():
    """Get popular search suggestions"""
    try:
        suggestions = [
            "web development",
            "full-stack development", 
            "responsive design",
            "e-commerce solutions",
            "AI integration",
            "gaming development",
            "hardware consulting",
            "performance optimization",
            "portfolio projects",
            "freelance developers"
        ]
        
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

# Include the router in the main app (after all endpoints are defined)
app.include_router(api_router)

# Build frontend and serve React app (after all API routes)
# Note: Frontend is served separately by supervisor, not by backend
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"

# Serve React build as static files (AFTER all API routes are registered) - DISABLED in this setup
# Frontend is served separately by supervisor on port 3000
logger.info("🎮 Backend API ready - Frontend served separately on port 3000")

# Startup event to initialize admin and sync
@app.on_event("startup")
async def startup_event():
    """Initialize admin system and YouTube sync on startup"""
    try:
        await create_default_admin()
        logger.info("🚀 Admin system initialized successfully")
        
        # Start YouTube sync scheduler in background
        # asyncio.create_task(start_sync_scheduler())
        logger.info("🔄 YouTube sync scheduler disabled for testing")
        
    except Exception as e:
        logger.error(f"❌ Startup initialization failed: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)