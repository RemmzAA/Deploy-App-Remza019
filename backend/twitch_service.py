"""
REMZA019 Gaming - Twitch Integration Service
Real-time stream monitoring, VODs, and channel information
"""
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class TwitchService:
    def __init__(self):
        # WAITING FOR CLIENT_ID from user!
        self.client_id = os.environ.get('TWITCH_CLIENT_ID', 'PENDING_USER_INPUT')
        self.client_secret = os.environ.get('TWITCH_CLIENT_SECRET')
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.base_url = "https://api.twitch.tv/helix"
        self.channel_name = "remza019"
        self.user_id: Optional[str] = None
    
    async def get_access_token(self) -> str:
        """Obtain or refresh app access token using Client Credentials flow"""
        if self.access_token and self.token_expires_at and self.token_expires_at > datetime.now():
            return self.access_token
        
        if self.client_id == 'PENDING_USER_INPUT':
            logger.warning("⚠️ TWITCH_CLIENT_ID not set! Waiting for user input...")
            return None
        
        auth_url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data["access_token"]
                        expires_in = data["expires_in"]
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                        logger.info("✅ Twitch access token obtained successfully!")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to get Twitch access token: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"❌ Twitch authentication error: {e}")
            return None
    
    async def get_user_id(self, username: str = None) -> Optional[str]:
        """Get user ID from username"""
        if self.user_id:
            return self.user_id
            
        username = username or self.channel_name
        token = await self.get_access_token()
        
        if not token:
            return None
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        url = f"{self.base_url}/users?login={username}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data"):
                            self.user_id = data["data"][0]["id"]
                            logger.info(f"✅ Twitch user ID for {username}: {self.user_id}")
                            return self.user_id
                        return None
                    return None
        except Exception as e:
            logger.error(f"❌ Error getting Twitch user ID: {e}")
            return None
    
    async def check_if_live(self) -> Dict[str, Any]:
        """Check if channel is currently live"""
        if not self.user_id:
            await self.get_user_id()
        
        if not self.user_id:
            return {"is_live": False, "error": "Could not get user ID"}
        
        token = await self.get_access_token()
        if not token:
            return {"is_live": False, "error": "Authentication failed"}
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        url = f"{self.base_url}/streams?user_id={self.user_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data"):
                            stream = data["data"][0]
                            return {
                                "is_live": True,
                                "title": stream.get("title"),
                                "game_name": stream.get("game_name"),
                                "viewer_count": stream.get("viewer_count"),
                                "started_at": stream.get("started_at"),
                                "thumbnail_url": stream.get("thumbnail_url").replace("{width}", "1920").replace("{height}", "1080") if stream.get("thumbnail_url") else None,
                                "user_name": stream.get("user_name"),
                                "language": stream.get("language")
                            }
                        else:
                            return {"is_live": False}
                    return {"is_live": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"❌ Error checking Twitch live status: {e}")
            return {"is_live": False, "error": str(e)}
    
    async def get_vods(self, limit: int = 10) -> Optional[list]:
        """Fetch VODs (past broadcasts) for the channel"""
        if not self.user_id:
            await self.get_user_id()
        
        if not self.user_id:
            return None
        
        token = await self.get_access_token()
        if not token:
            return None
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        url = f"{self.base_url}/videos?user_id={self.user_id}&type=archive&first={limit}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        vods = []
                        for vod in data.get("data", []):
                            vods.append({
                                "id": vod.get("id"),
                                "title": vod.get("title"),
                                "created_at": vod.get("created_at"),
                                "duration": vod.get("duration"),
                                "view_count": vod.get("view_count"),
                                "thumbnail_url": vod.get("thumbnail_url"),
                                "url": vod.get("url")
                            })
                        logger.info(f"✅ Retrieved {len(vods)} VODs for {self.channel_name}")
                        return vods
                    return None
        except Exception as e:
            logger.error(f"❌ Error fetching Twitch VODs: {e}")
            return None
    
    async def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Fetch channel information"""
        if not self.user_id:
            await self.get_user_id()
        
        if not self.user_id:
            return None
        
        token = await self.get_access_token()
        if not token:
            return None
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        
        url = f"{self.base_url}/channels?broadcaster_id={self.user_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data"):
                            channel = data["data"][0]
                            return {
                                "broadcaster_name": channel.get("broadcaster_name"),
                                "broadcaster_language": channel.get("broadcaster_language"),
                                "game_name": channel.get("game_name"),
                                "title": channel.get("title"),
                                "delay": channel.get("delay")
                            }
                        return None
                    return None
        except Exception as e:
            logger.error(f"❌ Error fetching Twitch channel info: {e}")
            return None

# Singleton instance
twitch_service = TwitchService()
