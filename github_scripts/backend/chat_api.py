"""
REMZA019 Gaming - Real-Time Chat System
Handles member chat messages and broadcasting
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger("chat")

chat_router = APIRouter(prefix="/chat", tags=["chat"])

# WebSocket connection manager for chat
class ChatConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"💬 Chat client connected. Active: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"💬 Chat client disconnected. Active: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

chat_manager = ChatConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    id: str
    user: str
    user_id: str
    level: int
    text: str
    timestamp: str

class SendMessageRequest(BaseModel):
    user: str
    user_id: str
    level: int
    text: str

# Store recent messages in memory (for new joiners)
recent_messages: List[dict] = []
MAX_RECENT_MESSAGES = 50

@chat_router.get("/messages")
async def get_recent_messages():
    """Get recent chat messages"""
    return {"messages": recent_messages}

@chat_router.post("/send")
async def send_message(request: SendMessageRequest):
    """Send a chat message and broadcast to all connected clients"""
    try:
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "user": request.user,
            "user_id": request.user_id,
            "level": request.level,
            "text": request.text,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in recent messages
        recent_messages.append(message)
        
        # Keep only last MAX_RECENT_MESSAGES
        if len(recent_messages) > MAX_RECENT_MESSAGES:
            recent_messages.pop(0)
        
        # Broadcast to all connected clients
        await chat_manager.broadcast({
            "type": "new_message",
            "message": message
        })
        
        logger.info(f"💬 Message sent by {request.user}: {request.text[:50]}")
        
        return {"success": True, "message": message}
        
    except Exception as e:
        logger.error(f"❌ Send message error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@chat_router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await chat_manager.connect(websocket)
    
    try:
        # Send recent messages on connect
        await websocket.send_json({
            "type": "history",
            "messages": recent_messages
        })
        
        # Keep connection alive
        while True:
            # Wait for messages from client (keep-alive pings)
            data = await websocket.receive_text()
            
            # Echo back to confirm connection
            if data == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ Chat WebSocket error: {e}")
        chat_manager.disconnect(websocket)

@chat_router.get("/online-count")
async def get_online_count():
    """Get count of online users in chat"""
    return {
        "count": len(chat_manager.active_connections),
        "online": len(chat_manager.active_connections) > 0
    }
