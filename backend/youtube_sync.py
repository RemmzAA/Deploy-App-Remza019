"""
REMZA019 Gaming - YouTube Synchronization System
Using Official YouTube Data API v3 (No Web Scraping!)
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from youtube_api_client import get_youtube_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeSyncManager:
    def __init__(self):
        self.channel_handle = "@remza019"
        self.db = None
        self.youtube_client = None
        self.last_sync = None
        
    async def initialize(self):
        """Initialize database and YouTube API client"""
        try:
            # Initialize database
            mongodb_url = os.environ.get('MONGO_URL')
            if not mongodb_url:
                raise ValueError("MONGO_URL environment variable is required")
            client = AsyncIOMotorClient(mongodb_url)
            db_name = os.environ.get('DB_NAME', 'remza019_gaming')
            self.db = client[db_name]
            logger.info("✅ Database initialized")
            
            # Initialize YouTube API client
            try:
                self.youtube_client = get_youtube_client()
                logger.info("✅ YouTube API client initialized")
            except Exception as e:
                logger.warning(f"⚠️ YouTube API client initialization failed: {e}")
                logger.info("📋 Using fallback data mode")
                self.youtube_client = None
                
        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            raise

    async def sync_channel_stats(self) -> Dict:
        """
        Sync channel statistics using YouTube Data API v3
        Replaces web scraping with official API calls
        """
        try:
            if not self.youtube_client:
                logger.info("📋 YouTube API not available, using fallback stats")
                return await self._get_fallback_stats()
            
            logger.info("📊 Syncing channel stats via YouTube Data API v3...")
            
            # Get channel stats from official API
            stats = await self.youtube_client.get_channel_stats()
            
            if stats:
                # Store in database
                await self._store_channel_stats(stats)
                self.last_sync = datetime.now()
                
                logger.info(f"✅ Channel stats synced: {stats['subscriber_count']} subscribers")
                return stats
            else:
                logger.warning("⚠️ No stats returned from API, using fallback")
                return await self._get_fallback_stats()
                
        except Exception as e:
            logger.error(f"❌ Error syncing channel stats: {e}")
            return await self._get_fallback_stats()

    async def sync_latest_videos(self, max_results: int = 5) -> List[Dict]:
        """
        Sync latest videos using YouTube Data API v3
        Replaces web scraping with official API calls
        """
        try:
            if not self.youtube_client:
                logger.info("📋 YouTube API not available, using fallback videos")
                return await self._get_fallback_videos()
            
            logger.info("🎬 Syncing latest videos via YouTube Data API v3...")
            
            # Get videos from official API
            videos = await self.youtube_client.get_latest_videos(max_results=max_results)
            
            if videos:
                # Store in database
                await self._store_videos(videos)
                logger.info(f"✅ Synced {len(videos)} videos")
                return videos
            else:
                logger.warning("⚠️ No videos returned from API, using fallback")
                return await self._get_fallback_videos()
                
        except Exception as e:
            logger.error(f"❌ Error syncing videos: {e}")
            return await self._get_fallback_videos()

    async def check_live_status(self) -> Dict:
        """
        Check if channel is currently live
        Uses YouTube Data API v3 search for live broadcasts
        """
        try:
            if not self.youtube_client:
                return {"is_live": False, "live_video_id": None}
            
            # Get channel ID first
            channel_id = await self.youtube_client.get_channel_by_handle()
            if not channel_id:
                return {"is_live": False, "live_video_id": None}
            
            # Search for live broadcasts
            search_response = self.youtube_client.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                eventType='live',
                type='video',
                maxResults=1
            ).execute()
            
            if search_response.get('items'):
                live_video = search_response['items'][0]
                return {
                    "is_live": True,
                    "live_video_id": live_video['id']['videoId'],
                    "live_title": live_video['snippet']['title'],
                    "live_thumbnail": live_video['snippet']['thumbnails']['high']['url']
                }
            else:
                return {"is_live": False, "live_video_id": None}
                
        except Exception as e:
            logger.error(f"❌ Error checking live status: {e}")
            return {"is_live": False, "live_video_id": None}

    async def _store_channel_stats(self, stats: Dict):
        """Store channel statistics in database"""
        try:
            if not self.db:
                return
            
            stats_data = {
                "channel_id": stats.get('channel_id'),
                "subscriber_count": stats.get('subscriber_count', '0'),
                "video_count": stats.get('video_count', '0'),
                "view_count": stats.get('view_count', '0'),
                "updated_at": datetime.now(),
                "source": "youtube_api_v3"
            }
            
            await self.db.channel_stats.update_one(
                {},
                {'$set': stats_data},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing channel stats: {e}")

    async def _store_videos(self, videos: List[Dict]):
        """Store videos in database"""
        try:
            if not self.db:
                return
            
            for video in videos:
                video_data = {
                    "video_id": video['id'],
                    "title": video['title'],
                    "description": video['description'],
                    "thumbnail_url": video['thumbnail_url'],
                    "watch_url": video['watch_url'],
                    "published_at": video['published_at'],
                    "view_count": video.get('view_count', '0'),
                    "duration": video.get('duration', 'N/A'),
                    "updated_at": datetime.now(),
                    "source": "youtube_api_v3"
                }
                
                await self.db.videos.update_one(
                    {"video_id": video['id']},
                    {'$set': video_data},
                    upsert=True
                )
                
        except Exception as e:
            logger.error(f"❌ Error storing videos: {e}")

    async def _get_fallback_stats(self) -> Dict:
        """Fallback stats when API is unavailable"""
        try:
            if self.db:
                # Try to get last known stats from database
                stats = await self.db.channel_stats.find_one({}, sort=[('updated_at', -1)])
                if stats:
                    return {
                        'channel_id': stats.get('channel_id'),
                        'subscriber_count': stats.get('subscriber_count', '178'),
                        'video_count': stats.get('video_count', '15'),
                        'view_count': stats.get('view_count', '3247')
                    }
        except:
            pass
        
        # Default fallback
        return {
            'channel_id': 'UC_remza019_fallback',
            'subscriber_count': '178',
            'video_count': '15',
            'view_count': '3247'
        }

    async def _get_fallback_videos(self) -> List[Dict]:
        """Fallback videos when API is unavailable"""
        try:
            if self.db:
                # Try to get last known videos from database
                videos = await self.db.videos.find({}, sort=[('published_at', -1)]).limit(5).to_list(length=5)
                if videos:
                    return [{
                        'id': v.get('video_id'),
                        'video_id': v.get('video_id'),
                        'title': v.get('title'),
                        'description': v.get('description'),
                        'thumbnail_url': v.get('thumbnail_url'),
                        'watch_url': v.get('watch_url'),
                        'published_at': v.get('published_at'),
                        'view_count': v.get('view_count', '0'),
                        'duration': v.get('duration', 'N/A')
                    } for v in videos]
        except:
            pass
        
        # Default fallback
        return [
            {
                'id': 'Ab8TeivYRk4',
                'video_id': 'Ab8TeivYRk4',
                'title': 'REMZA019 Gaming - FORTNITE Parkour Gameplay',
                'description': 'Experience epic FORTNITE gameplay! High-quality 4K 60fps parkour action.',
                'thumbnail_url': 'https://img.youtube.com/vi/Ab8TeivYRk4/hqdefault.jpg',
                'watch_url': 'https://www.youtube.com/watch?v=Ab8TeivYRk4',
                'published_at': '2024-10-01T15:00:00Z',
                'view_count': '4.2K',
                'duration': 'PT10M15S'
            }
        ]

    async def run_periodic_sync(self, interval_minutes: int = 5):
        """
        Run periodic synchronization
        Syncs channel stats and videos every interval_minutes
        """
        logger.info(f"🔄 Starting periodic sync (every {interval_minutes} minutes)")
        
        while True:
            try:
                logger.info("🔄 Running periodic sync...")
                
                # Sync channel stats
                await self.sync_channel_stats()
                
                # Sync latest videos
                await self.sync_latest_videos()
                
                # Check live status
                live_status = await self.check_live_status()
                if live_status['is_live']:
                    logger.info(f"🔴 Channel is LIVE: {live_status.get('live_title', 'Unknown')}")
                
                logger.info(f"✅ Periodic sync complete. Next sync in {interval_minutes} minutes")
                
            except Exception as e:
                logger.error(f"❌ Error in periodic sync: {e}")
            
            # Wait for next sync
            await asyncio.sleep(interval_minutes * 60)


# Global sync manager instance
sync_manager = None

async def get_sync_manager() -> YouTubeSyncManager:
    """Get or create sync manager instance"""
    global sync_manager
    if sync_manager is None:
        sync_manager = YouTubeSyncManager()
        await sync_manager.initialize()
    return sync_manager

# Background task for periodic sync
async def start_youtube_sync_background():
    """Start YouTube sync as background task"""
    try:
        manager = await get_sync_manager()
        await manager.run_periodic_sync(interval_minutes=5)
    except Exception as e:
        logger.error(f"❌ Background sync error: {e}")
