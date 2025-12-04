# Support System API - REMZA019 Gaming
# Member Support & Ticket System

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['remza019_gaming']
support_tickets_collection = db['support_tickets']

router = APIRouter(prefix="/api/support", tags=["support"])

# Pydantic Models
class CreateTicketRequest(BaseModel):
    subject: str
    message: str
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, URGENT
    category: str = "GENERAL"  # GENERAL, LICENSE, TECHNICAL, BILLING

class ReplyTicketRequest(BaseModel):
    ticket_id: str
    message: str
    is_admin: bool = False

class UpdateTicketStatus(BaseModel):
    ticket_id: str
    status: str  # OPEN, IN_PROGRESS, WAITING, RESOLVED, CLOSED

# Helper Functions
def generate_ticket_id() -> str:
    """Generate unique ticket ID"""
    import secrets
    import string
    return 'TICK-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

# API Endpoints

@router.post("/create-ticket")
async def create_support_ticket(data: CreateTicketRequest, member_email: Optional[str] = None):
    """
    Create a new support ticket
    """
    try:
        ticket_id = generate_ticket_id()
        now = datetime.now(timezone.utc).isoformat()
        
        ticket_doc = {
            "ticket_id": ticket_id,
            "member_email": member_email,
            "subject": data.subject,
            "category": data.category,
            "priority": data.priority,
            "status": "OPEN",
            "messages": [
                {
                    "message": data.message,
                    "is_admin": False,
                    "timestamp": now
                }
            ],
            "created_at": now,
            "updated_at": now,
            "resolved_at": None
        }
        
        await support_tickets_collection.insert_one(ticket_doc)
        
        return {
            "success": True,
            "message": "Support ticket created successfully",
            "ticket_id": ticket_id
        }
    
    except Exception as e:
        logger.error(f"Create ticket error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reply")
async def reply_to_ticket(data: ReplyTicketRequest):
    """
    Reply to a support ticket
    """
    try:
        ticket = await support_tickets_collection.find_one({"ticket_id": data.ticket_id})
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        now = datetime.now(timezone.utc).isoformat()
        
        new_message = {
            "message": data.message,
            "is_admin": data.is_admin,
            "timestamp": now
        }
        
        # Update ticket
        await support_tickets_collection.update_one(
            {"ticket_id": data.ticket_id},
            {
                "$push": {"messages": new_message},
                "$set": {
                    "updated_at": now,
                    "status": "IN_PROGRESS" if ticket['status'] == 'OPEN' else ticket['status']
                }
            }
        )
        
        return {
            "success": True,
            "message": "Reply added successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reply error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticket/{ticket_id}")
async def get_ticket(ticket_id: str):
    """
    Get ticket details
    """
    try:
        ticket = await support_tickets_collection.find_one({"ticket_id": ticket_id}, {"_id": 0})
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "success": True,
            "ticket": ticket
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get ticket error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets")
async def list_tickets(member_email: Optional[str] = None, status: Optional[str] = None):
    """
    List support tickets (filtered by member email or status)
    """
    try:
        query = {}
        
        if member_email:
            query['member_email'] = member_email
        
        if status:
            query['status'] = status
        
        tickets = await support_tickets_collection.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).to_list(length=100)
        
        return {
            "success": True,
            "tickets": tickets,
            "total": len(tickets)
        }
    
    except Exception as e:
        logger.error(f"List tickets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-status")
async def update_ticket_status(data: UpdateTicketStatus):
    """
    Update ticket status (admin only)
    """
    try:
        ticket = await support_tickets_collection.find_one({"ticket_id": data.ticket_id})
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        update_data = {
            "status": data.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if data.status in ["RESOLVED", "CLOSED"]:
            update_data['resolved_at'] = datetime.now(timezone.utc).isoformat()
        
        await support_tickets_collection.update_one(
            {"ticket_id": data.ticket_id},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": f"Ticket status updated to {data.status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_support_stats():
    """
    Get support statistics (admin only)
    """
    try:
        total = await support_tickets_collection.count_documents({})
        open_tickets = await support_tickets_collection.count_documents({"status": "OPEN"})
        in_progress = await support_tickets_collection.count_documents({"status": "IN_PROGRESS"})
        resolved = await support_tickets_collection.count_documents({"status": "RESOLVED"})
        closed = await support_tickets_collection.count_documents({"status": "CLOSED"})
        
        return {
            "success": True,
            "stats": {
                "total": total,
                "open": open_tickets,
                "in_progress": in_progress,
                "resolved": resolved,
                "closed": closed
            }
        }
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
