"""
REMZA019 Gaming - Stream Schedule API
Dynamic stream scheduling system with admin management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import logging

from admin_api import get_current_admin

logger = logging.getLogger("schedule_api")

schedule_router = APIRouter(prefix="/schedule", tags=["schedule"])

class StreamSchedule(BaseModel):
    day: str  # Monday, Tuesday, etc.
    time: str  # "20:00"
    game: str
    description: Optional[str] = ""
    duration: Optional[str] = "2-3 hours"
    active: Optional[bool] = True

class StreamScheduleResponse(BaseModel):
    id: str
    day: str
    time: str
    game: str
    description: str
    duration: str
    active: bool
    created_at: datetime
    updated_at: datetime

def get_database():
    """Get database instance"""
    from server import get_database as get_db
    return get_db()

async def broadcast_schedule_update():
    """Broadcast schedule update to all connected clients via SSE"""
    try:
        from admin_api import broadcast_admin_update
        schedules = await get_all_schedules()
        await broadcast_admin_update("schedule_update", {
            "schedules": schedules
        })
        logger.info("✅ Schedule update broadcasted to all clients")
    except Exception as e:
        logger.error(f"Failed to broadcast schedule update: {e}")

async def get_all_schedules():
    """Helper to get all active schedules"""
    db = get_database()
    schedules = await db.schedules.find(
        {"active": True},
        {"_id": 0}
    ).sort("day_order", 1).to_list(100)
    return schedules

@schedule_router.get("/list")
async def list_schedules():
    """Get all active stream schedules (PUBLIC)"""
    try:
        schedules = await get_all_schedules()
        return {
            "success": True,
            "schedules": schedules
        }
    except Exception as e:
        logger.error(f"❌ List schedules error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@schedule_router.post("/add")
async def add_schedule(
    schedule: StreamSchedule,
    admin = Depends(get_current_admin)
):
    """Add new stream schedule (ADMIN ONLY)"""
    try:
        db = get_database()
        
        # Day order mapping
        day_order_map = {
            "Monday": 1, "Tuesday": 2, "Wednesday": 3,
            "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7
        }
        
        schedule_data = {
            "id": str(uuid.uuid4()),
            "day": schedule.day,
            "day_order": day_order_map.get(schedule.day, 8),
            "time": schedule.time,
            "game": schedule.game,
            "description": schedule.description or "",
            "duration": schedule.duration or "2-3 hours",
            "active": schedule.active if schedule.active is not None else True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": admin.get("username", "admin")
        }
        
        result = await db.schedules.insert_one(schedule_data)
        
        logger.info(f"✅ Schedule added: {schedule.day} {schedule.time} - {schedule.game}")
        
        # Broadcast update
        await broadcast_schedule_update()
        
        # Return without _id
        schedule_data.pop('_id', None)
        
        return {
            "success": True,
            "message": "Schedule added successfully!",
            "schedule": schedule_data
        }
        
    except Exception as e:
        logger.error(f"❌ Add schedule error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@schedule_router.put("/update/{schedule_id}")
async def update_schedule(
    schedule_id: str,
    schedule: StreamSchedule,
    admin = Depends(get_current_admin)
):
    """Update existing schedule (ADMIN ONLY)"""
    try:
        db = get_database()
        
        # Day order mapping
        day_order_map = {
            "Monday": 1, "Tuesday": 2, "Wednesday": 3,
            "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7
        }
        
        update_data = {
            "day": schedule.day,
            "day_order": day_order_map.get(schedule.day, 8),
            "time": schedule.time,
            "game": schedule.game,
            "description": schedule.description or "",
            "duration": schedule.duration or "2-3 hours",
            "active": schedule.active if schedule.active is not None else True,
            "updated_at": datetime.now(),
            "updated_by": admin.get("username", "admin")
        }
        
        result = await db.schedules.update_one(
            {"id": schedule_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        logger.info(f"✅ Schedule updated: {schedule_id}")
        
        # Broadcast update
        await broadcast_schedule_update()
        
        return {
            "success": True,
            "message": "Schedule updated successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update schedule error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@schedule_router.delete("/delete/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    admin = Depends(get_current_admin)
):
    """Delete schedule (ADMIN ONLY)"""
    try:
        db = get_database()
        
        result = await db.schedules.delete_one({"id": schedule_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        logger.info(f"✅ Schedule deleted: {schedule_id}")
        
        # Broadcast update
        await broadcast_schedule_update()
        
        return {
            "success": True,
            "message": "Schedule deleted successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete schedule error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@schedule_router.post("/seed-defaults")
async def seed_default_schedules(admin = Depends(get_current_admin)):
    """Seed default stream schedules (ADMIN ONLY - ONE TIME USE)"""
    try:
        db = get_database()
        
        # Check if schedules already exist
        existing_count = await db.schedules.count_documents({})
        if existing_count > 0:
            return {
                "success": False,
                "message": f"Schedules already exist ({existing_count} schedules). Use delete endpoint first."
            }
        
        default_schedules = [
            {
                "id": str(uuid.uuid4()),
                "day": "Monday",
                "day_order": 1,
                "time": "20:00",
                "game": "CS2",
                "description": "Competitive gameplay",
                "duration": "2-3 hours",
                "active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": admin.get("username", "admin")
            },
            {
                "id": str(uuid.uuid4()),
                "day": "Wednesday",
                "day_order": 3,
                "time": "19:00",
                "game": "Valorant",
                "description": "Ranked grind",
                "duration": "3-4 hours",
                "active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": admin.get("username", "admin")
            },
            {
                "id": str(uuid.uuid4()),
                "day": "Friday",
                "day_order": 5,
                "time": "21:00",
                "game": "Variety Stream",
                "description": "Fun games with community",
                "duration": "4-5 hours",
                "active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": admin.get("username", "admin")
            }
        ]
        
        result = await db.schedules.insert_many(default_schedules)
        
        logger.info(f"✅ Seeded {len(default_schedules)} default schedules")
        
        # Broadcast update
        await broadcast_schedule_update()
        
        # Return without _id
        for schedule in default_schedules:
            schedule.pop('_id', None)
        
        return {
            "success": True,
            "message": f"Seeded {len(default_schedules)} default schedules successfully!",
            "schedules": default_schedules
        }
        
    except Exception as e:
        logger.error(f"❌ Seed schedules error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
