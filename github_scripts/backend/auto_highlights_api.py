"""
AI Auto-Highlights API
Automatically generates highlight clips from stream data using AI analysis
"""

import os
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
import uuid

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/auto-highlights", tags=["auto-highlights"])

# Initialize LLM Chat with Emergent Universal Key
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")

class HighlightRequest(BaseModel):
    stream_id: str
    duration_minutes: int
    chat_messages: List[Dict]
    game_events: Optional[List[Dict]] = []
    
class HighlightResponse(BaseModel):
    highlight_id: str
    timestamp: str
    title: str
    description: str
    start_time: float
    end_time: float
    confidence_score: float
    reason: str

@router.post("/analyze", response_model=List[HighlightResponse])
async def analyze_stream_for_highlights(request: HighlightRequest):
    """
    Analyze stream data to automatically identify highlight moments using AI
    """
    try:
        # Initialize AI chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"highlight-{request.stream_id}",
            system_message="""You are an expert gaming stream analyst. Your job is to identify the most exciting moments from a stream based on chat reactions, viewer engagement, and game events. 
            
            Analyze the provided data and identify 3-5 key highlight moments. For each highlight, provide:
            1. Exact timestamp (in seconds from stream start)
            2. Title (short, catchy)
            3. Description (what made this moment special)
            4. Confidence score (0-1, how sure you are this is highlight-worthy)
            5. Reason (why viewers would want to watch this)
            
            Focus on moments with:
            - Sudden spikes in chat activity
            - Excitement words (pog, wow, amazing, insane, wtf, etc.)
            - Game events (kills, wins, achievements)
            - Peak viewer reactions
            
            Respond ONLY with valid JSON array format."""
        ).with_model("openai", "gpt-4o-mini")
        
        # Prepare analysis prompt
        analysis_data = {
            "stream_duration_minutes": request.duration_minutes,
            "total_chat_messages": len(request.chat_messages),
            "chat_sample": request.chat_messages[:100] if len(request.chat_messages) > 100 else request.chat_messages,
            "game_events": request.game_events
        }
        
        prompt = f"""Analyze this Fortnite stream data and identify highlight moments:

Stream Duration: {request.duration_minutes} minutes
Total Chat Messages: {len(request.chat_messages)}

Chat Messages (chronological sample):
{chr(10).join([f"[{msg.get('timestamp', 0)}s] {msg.get('user', 'Unknown')}: {msg.get('text', '')}" for msg in request.chat_messages[:50]])}

Game Events:
{chr(10).join([f"[{event.get('timestamp', 0)}s] {event.get('type', 'Unknown')}: {event.get('description', '')}" for event in request.game_events])}

Return JSON array of 3-5 highlights in this EXACT format:
[
  {{
    "timestamp": 125.5,
    "title": "Insane Victory Royale",
    "description": "Epic final kill with sniper headshot",
    "confidence_score": 0.95,
    "reason": "Chat went crazy with 50+ messages in 10 seconds",
    "duration": 30
  }}
]"""

        # Send message to AI
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        import json
        highlights_data = json.loads(response.strip())
        
        # Convert to response format
        highlights = []
        for h in highlights_data:
            highlight = HighlightResponse(
                highlight_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                title=h.get("title", "Highlight"),
                description=h.get("description", ""),
                start_time=float(h.get("timestamp", 0)),
                end_time=float(h.get("timestamp", 0)) + float(h.get("duration", 30)),
                confidence_score=float(h.get("confidence_score", 0.7)),
                reason=h.get("reason", "Viewer engagement spike")
            )
            highlights.append(highlight)
        
        return highlights
        
    except Exception as e:
        print(f"❌ Error analyzing highlights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze highlights: {str(e)}")

@router.get("/recent/{stream_id}")
async def get_recent_highlights(stream_id: str):
    """
    Get recently generated highlights for a stream
    """
    # This would fetch from database in production
    return {
        "stream_id": stream_id,
        "highlights": [],
        "message": "Highlight history not yet implemented"
    }

@router.post("/generate-clip")
async def generate_clip_from_highlight(
    stream_id: str,
    start_time: float,
    end_time: float,
    title: str
):
    """
    Generate a video clip from the highlight timestamps
    This would integrate with video processing in production
    """
    return {
        "success": True,
        "clip_id": str(uuid.uuid4()),
        "stream_id": stream_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "status": "queued",
        "message": "Clip generation queued (not yet implemented)"
    }
