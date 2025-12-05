"""
REMZA019 Gaming - Polls System
Real-time polling system for viewer engagement
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import uuid

from admin_api import get_current_admin
from websocket_manager import get_ws_manager

logger = logging.getLogger("polls")

polls_router = APIRouter(prefix="/polls", tags=["polls"])

# Pydantic models
class PollOption(BaseModel):
    id: str
    text: str
    votes: int = 0

class Poll(BaseModel):
    id: str
    question: str
    options: List[PollOption]
    active: bool
    created_at: str
    created_by: str
    total_votes: int = 0
    ended_at: Optional[str] = None

class CreatePollRequest(BaseModel):
    question: str
    options: List[str]  # List of option texts

class VoteRequest(BaseModel):
    poll_id: str
    option_id: str
    user_id: str
    username: str

# In-memory storage (can be moved to MongoDB later)
active_polls: Dict[str, Poll] = {}
poll_votes: Dict[str, Dict[str, str]] = {}  # {poll_id: {user_id: option_id}}

def get_database():
    from server import get_database as get_db
    return get_db()

@polls_router.post("/create")
async def create_poll(
    request: CreatePollRequest,
    admin = Depends(get_current_admin)
):
    """Create a new poll - ADMIN ONLY"""
    try:
        # Create poll options
        options = [
            PollOption(
                id=str(uuid.uuid4()),
                text=option_text,
                votes=0
            ) for option_text in request.options
        ]
        
        # Create poll
        poll = Poll(
            id=str(uuid.uuid4()),
            question=request.question,
            options=options,
            active=True,
            created_at=datetime.now().isoformat(),
            created_by=admin['username'],
            total_votes=0
        )
        
        active_polls[poll.id] = poll
        poll_votes[poll.id] = {}
        
        logger.info(f"✅ Poll created: {poll.question} by {admin['username']}")
        
        # Broadcast new poll to all clients
        ws_manager = get_ws_manager()
        await ws_manager.broadcast({
            "type": "new_poll",
            "poll": poll.dict()
        })
        
        return {"success": True, "poll": poll.dict()}
        
    except Exception as e:
        logger.error(f"❌ Create poll error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create poll")

@polls_router.get("/active")
async def get_active_polls():
    """Get all active polls - PUBLIC"""
    try:
        active = [poll.dict() for poll in active_polls.values() if poll.active]
        return {"polls": active}
    except Exception as e:
        logger.error(f"❌ Get active polls error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active polls")

@polls_router.post("/vote")
async def vote_in_poll(request: VoteRequest):
    """Vote in a poll - PUBLIC"""
    try:
        poll = active_polls.get(request.poll_id)
        
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        if not poll.active:
            raise HTTPException(status_code=400, detail="Poll is not active")
        
        # Check if user already voted
        if request.user_id in poll_votes[request.poll_id]:
            raise HTTPException(status_code=400, detail="You have already voted in this poll")
        
        # Find option and increment vote
        option_found = False
        for option in poll.options:
            if option.id == request.option_id:
                option.votes += 1
                option_found = True
                break
        
        if not option_found:
            raise HTTPException(status_code=404, detail="Option not found")
        
        # Record vote
        poll_votes[request.poll_id][request.user_id] = request.option_id
        poll.total_votes += 1
        
        logger.info(f"✅ Vote recorded: {request.username} voted in poll {poll.question}")
        
        # Broadcast updated poll results
        ws_manager = get_ws_manager()
        await ws_manager.broadcast({
            "type": "poll_update",
            "poll": poll.dict()
        })
        
        return {"success": True, "poll": poll.dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Vote error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record vote")

@polls_router.post("/end/{poll_id}")
async def end_poll(
    poll_id: str,
    admin = Depends(get_current_admin)
):
    """End a poll - ADMIN ONLY"""
    try:
        poll = active_polls.get(poll_id)
        
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        poll.active = False
        poll.ended_at = datetime.now().isoformat()
        
        logger.info(f"✅ Poll ended: {poll.question} by {admin['username']}")
        
        # Broadcast poll ended
        ws_manager = get_ws_manager()
        await ws_manager.broadcast({
            "type": "poll_ended",
            "poll": poll.dict()
        })
        
        return {"success": True, "poll": poll.dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ End poll error: {e}")
        raise HTTPException(status_code=500, detail="Failed to end poll")

@polls_router.get("/results/{poll_id}")
async def get_poll_results(poll_id: str):
    """Get poll results - PUBLIC"""
    try:
        poll = active_polls.get(poll_id)
        
        if not poll:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        # Calculate percentages
        results = []
        for option in poll.options:
            percentage = (option.votes / poll.total_votes * 100) if poll.total_votes > 0 else 0
            results.append({
                "id": option.id,
                "text": option.text,
                "votes": option.votes,
                "percentage": round(percentage, 1)
            })
        
        return {
            "poll_id": poll.id,
            "question": poll.question,
            "total_votes": poll.total_votes,
            "active": poll.active,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get poll results error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get poll results")

@polls_router.delete("/{poll_id}")
async def delete_poll(
    poll_id: str,
    admin = Depends(get_current_admin)
):
    """Delete a poll - ADMIN ONLY"""
    try:
        if poll_id in active_polls:
            del active_polls[poll_id]
            if poll_id in poll_votes:
                del poll_votes[poll_id]
            
            logger.info(f"✅ Poll deleted: {poll_id} by {admin['username']}")
            
            # Broadcast poll deletion
            ws_manager = get_ws_manager()
            await ws_manager.broadcast({
                "type": "poll_deleted",
                "poll_id": poll_id
            })
            
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Poll not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete poll error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete poll")
