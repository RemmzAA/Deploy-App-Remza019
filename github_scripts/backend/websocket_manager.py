"""
REMZA019 Gaming - WebSocket Real-Time System
REMZA019 Gaming - Remote Management & Monitoring System
Replaces SSE with scalable WebSocket connections
"""
import asyncio
from typing import Dict, Set, List
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates
    Handles multiple clients, broadcasting, and connection lifecycle
    """
    
    def __init__(self):
        # Active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Connection rooms for targeted broadcasts
        self.rooms: Dict[str, Set[str]] = {
            "admin": set(),      # Admin panel connections
            "public": set(),     # Public page connections
            "viewers": set()     # Viewer menu connections
        }
        self._lock = asyncio.Lock()
        
    async def connect(self, websocket: WebSocket, client_id: str, room: str = "public"):
        """
        Accept new WebSocket connection
        
        Args:
            websocket: WebSocket connection object
            client_id: Unique client identifier
            room: Connection room (admin, public, viewers)
        """
        await websocket.accept()
        
        async with self._lock:
            # Store connection
            self.active_connections[client_id] = websocket
            
            # Add to room
            if room in self.rooms:
                self.rooms[room].add(client_id)
            
        logger.info(f"✅ WebSocket connected: {client_id} (room: {room})")
        logger.info(f"📊 Active connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message(client_id, {
            "type": "connection_established",
            "client_id": client_id,
            "room": room,
            "timestamp": datetime.now().isoformat()
        })
    
    async def disconnect(self, client_id: str):
        """
        Remove WebSocket connection
        
        Args:
            client_id: Client identifier to disconnect
        """
        async with self._lock:
            # Remove from active connections
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            
            # Remove from all rooms
            for room_clients in self.rooms.values():
                room_clients.discard(client_id)
        
        logger.info(f"❌ WebSocket disconnected: {client_id}")
        logger.info(f"📊 Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, client_id: str, message: dict):
        """
        Send message to specific client
        
        Args:
            client_id: Target client identifier
            message: Message data (dict)
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"❌ Error sending to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast(self, message: dict, room: str = None):
        """
        Broadcast message to all clients or specific room
        
        Args:
            message: Message data (dict)
            room: Optional room name to broadcast to
        """
        # Add timestamp to all broadcasts
        message["timestamp"] = datetime.now().isoformat()
        
        # Determine target clients
        if room and room in self.rooms:
            target_clients = self.rooms[room]
        else:
            target_clients = set(self.active_connections.keys())
        
        # Send to all target clients
        disconnected_clients = []
        for client_id in target_clients:
            if client_id in self.active_connections:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"❌ Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
        
        logger.info(f"📡 Broadcast sent to {len(target_clients)} clients (room: {room or 'all'})")
    
    async def broadcast_live_status(self, is_live: bool, viewer_count: int = 0, game: str = ""):
        """
        Broadcast live status update to all public connections
        
        Args:
            is_live: Whether stream is live
            viewer_count: Current viewer count
            game: Game being played
        """
        message = {
            "type": "live_status_update",
            "data": {
                "is_live": is_live,
                "viewer_count": viewer_count,
                "game": game,
                "status_text": "LIVE NOW" if is_live else "OFFLINE"
            }
        }
        await self.broadcast(message, room="public")
    
    async def broadcast_channel_stats(self, subscriber_count: str, video_count: str, view_count: str):
        """
        Broadcast channel statistics update
        
        Args:
            subscriber_count: Subscriber count
            video_count: Video count
            view_count: View count
        """
        message = {
            "type": "channel_stats_update",
            "data": {
                "subscriber_count": subscriber_count,
                "video_count": video_count,
                "view_count": view_count
            }
        }
        await self.broadcast(message, room="admin")
    
    async def broadcast_content_update(self, content_type: str, content_data: dict):
        """
        Broadcast content update (About, Featured Video, Schedule)
        
        Args:
            content_type: Type of content (about, featured_video, schedule)
            content_data: Updated content data
        """
        message = {
            "type": "content_update",
            "content_type": content_type,
            "data": content_data
        }
        await self.broadcast(message, room="public")
    
    async def broadcast_notification(self, notification_type: str, title: str, body: str):
        """
        Broadcast notification to all viewers
        
        Args:
            notification_type: Type of notification (info, success, warning, error)
            title: Notification title
            body: Notification body
        """
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "body": body
        }
        await self.broadcast(message, room="viewers")
    
    def get_connection_stats(self) -> dict:
        """
        Get current connection statistics
        
        Returns:
            dict: Connection stats by room
        """
        return {
            "total_connections": len(self.active_connections),
            "admin_connections": len(self.rooms["admin"]),
            "public_connections": len(self.rooms["public"]),
            "viewer_connections": len(self.rooms["viewers"])
        }
    
    async def handle_client_message(self, client_id: str, message: dict):
        """
        Handle incoming message from client
        
        Args:
            client_id: Client sending the message
            message: Message data
        """
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to ping with pong
            await self.send_personal_message(client_id, {
                "type": "pong",
                "client_id": client_id
            })
        
        elif message_type == "join_room":
            # Add client to specific room
            room = message.get("room")
            if room in self.rooms:
                async with self._lock:
                    self.rooms[room].add(client_id)
                logger.info(f"✅ {client_id} joined room: {room}")
        
        elif message_type == "leave_room":
            # Remove client from specific room
            room = message.get("room")
            if room in self.rooms:
                async with self._lock:
                    self.rooms[room].discard(client_id)
                logger.info(f"❌ {client_id} left room: {room}")
        
        else:
            logger.warning(f"⚠️ Unknown message type from {client_id}: {message_type}")


# Global WebSocket manager instance
ws_manager = WebSocketManager()

def get_ws_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance"""
    return ws_manager
