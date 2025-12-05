"""
REMZA019 Gaming - Tournament & Competition System
Predictions, challenges, leaderboard seasons, and rewards
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

tournament_router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])

# Database connection
def get_database():
    from server import get_database as get_db
    return get_db()

# Pydantic Models
class Tournament(BaseModel):
    tournament_id: str
    name: str
    description: str
    game: str
    start_date: datetime
    end_date: datetime
    prize_pool: int
    entry_fee: int  # points required
    max_participants: int
    current_participants: int
    status: str  # "upcoming", "active", "completed"
    rules: List[str]

class TournamentEntry(BaseModel):
    user_id: str
    username: str
    tournament_id: str

class Prediction(BaseModel):
    prediction_id: str
    title: str
    options: List[str]
    correct_option: Optional[str] = None
    points_reward: int
    expires_at: datetime
    status: str  # "active", "closed", "resolved"

class PredictionVote(BaseModel):
    user_id: str
    username: str
    prediction_id: str
    option: str
    points_wagered: int

class Challenge(BaseModel):
    challenge_id: str
    title: str
    description: str
    challenge_type: str  # "daily", "weekly", "special"
    points_reward: int
    requirements: Dict
    expires_at: datetime
    completed_by: List[str]

class Season(BaseModel):
    season_id: str
    name: str
    start_date: datetime
    end_date: datetime
    status: str  # "active", "ended"
    top_players: List[Dict]

# TOURNAMENTS
@tournament_router.post("/create")
async def create_tournament(tournament: Tournament):
    """
    Create a new tournament (admin only)
    """
    try:
        db = get_database()
        
        tournament_id = str(uuid.uuid4())
        tournament_data = {
            "tournament_id": tournament_id,
            "name": tournament.name,
            "description": tournament.description,
            "game": tournament.game,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
            "prize_pool": tournament.prize_pool,
            "entry_fee": tournament.entry_fee,
            "max_participants": tournament.max_participants,
            "current_participants": 0,
            "status": "upcoming",
            "rules": tournament.rules,
            "participants": [],
            "created_at": datetime.now()
        }
        
        await db.tournaments.insert_one(tournament_data)
        
        logger.info(f"✅ Tournament created: {tournament.name}")
        
        return {
            "success": True,
            "tournament_id": tournament_id,
            "message": f"Tournament '{tournament.name}' created successfully!"
        }
        
    except Exception as e:
        logger.error(f"Error creating tournament: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tournament_router.get("/active")
async def get_active_tournaments():
    """
    Get all active and upcoming tournaments
    """
    try:
        db = get_database()
        
        tournaments = await db.tournaments.find({
            "status": {"$in": ["upcoming", "active"]}
        }).sort("start_date", 1).to_list(length=50)
        
        return {
            "tournaments": tournaments,
            "count": len(tournaments)
        }
        
    except Exception as e:
        logger.error(f"Error fetching tournaments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tournament_router.post("/join")
async def join_tournament(entry: TournamentEntry):
    """
    Join a tournament
    """
    try:
        db = get_database()
        
        tournament = await db.tournaments.find_one({"tournament_id": entry.tournament_id})
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        if tournament["current_participants"] >= tournament["max_participants"]:
            raise HTTPException(status_code=400, detail="Tournament is full")
        
        # Check if user already joined
        if entry.user_id in tournament.get("participants", []):
            return {
                "success": False,
                "message": "Already joined this tournament"
            }
        
        # Check user points for entry fee
        viewer = await db.viewers.find_one({"user_id": entry.user_id})
        if not viewer or viewer.get("points", 0) < tournament["entry_fee"]:
            raise HTTPException(status_code=400, detail="Insufficient points for entry fee")
        
        # Deduct entry fee
        await db.viewers.update_one(
            {"user_id": entry.user_id},
            {"$inc": {"points": -tournament["entry_fee"]}}
        )
        
        # Add participant
        await db.tournaments.update_one(
            {"tournament_id": entry.tournament_id},
            {
                "$push": {"participants": entry.user_id},
                "$inc": {"current_participants": 1}
            }
        )
        
        logger.info(f"User {entry.username} joined tournament {entry.tournament_id}")
        
        return {
            "success": True,
            "message": f"Successfully joined tournament! Entry fee: {tournament['entry_fee']} points"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining tournament: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PREDICTIONS
@tournament_router.post("/predictions/create")
async def create_prediction(prediction: Prediction):
    """
    Create a new prediction (admin only)
    """
    try:
        db = get_database()
        
        prediction_id = str(uuid.uuid4())
        prediction_data = {
            "prediction_id": prediction_id,
            "title": prediction.title,
            "options": prediction.options,
            "correct_option": None,
            "points_reward": prediction.points_reward,
            "expires_at": prediction.expires_at,
            "status": "active",
            "votes": {},
            "created_at": datetime.now()
        }
        
        await db.predictions.insert_one(prediction_data)
        
        return {
            "success": True,
            "prediction_id": prediction_id
        }
        
    except Exception as e:
        logger.error(f"Error creating prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tournament_router.post("/predictions/vote")
async def vote_prediction(vote: PredictionVote):
    """
    Place a vote/wager on a prediction
    """
    try:
        db = get_database()
        
        prediction = await db.predictions.find_one({"prediction_id": vote.prediction_id})
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        if prediction["status"] != "active":
            raise HTTPException(status_code=400, detail="Prediction is not active")
        
        # Check if user has enough points
        viewer = await db.viewers.find_one({"user_id": vote.user_id})
        if not viewer or viewer.get("points", 0) < vote.points_wagered:
            raise HTTPException(status_code=400, detail="Insufficient points")
        
        # Deduct points
        await db.viewers.update_one(
            {"user_id": vote.user_id},
            {"$inc": {"points": -vote.points_wagered}}
        )
        
        # Record vote
        await db.prediction_votes.insert_one({
            "user_id": vote.user_id,
            "username": vote.username,
            "prediction_id": vote.prediction_id,
            "option": vote.option,
            "points_wagered": vote.points_wagered,
            "created_at": datetime.now()
        })
        
        return {
            "success": True,
            "message": f"Voted for '{vote.option}' with {vote.points_wagered} points!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting on prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# CHALLENGES
@tournament_router.get("/challenges/active")
async def get_active_challenges():
    """
    Get all active challenges
    """
    try:
        db = get_database()
        
        challenges = await db.challenges.find({
            "expires_at": {"$gte": datetime.now()}
        }).sort("points_reward", -1).to_list(length=50)
        
        return {
            "challenges": challenges,
            "count": len(challenges)
        }
        
    except Exception as e:
        logger.error(f"Error fetching challenges: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tournament_router.post("/challenges/complete")
async def complete_challenge(user_id: str, challenge_id: str):
    """
    Mark challenge as completed and award points
    """
    try:
        db = get_database()
        
        challenge = await db.challenges.find_one({"challenge_id": challenge_id})
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        if user_id in challenge.get("completed_by", []):
            return {
                "success": False,
                "message": "Challenge already completed"
            }
        
        # Award points
        await db.viewers.update_one(
            {"user_id": user_id},
            {"$inc": {"points": challenge["points_reward"]}}
        )
        
        # Mark as completed
        await db.challenges.update_one(
            {"challenge_id": challenge_id},
            {"$push": {"completed_by": user_id}}
        )
        
        return {
            "success": True,
            "points_earned": challenge["points_reward"],
            "message": f"Challenge completed! Earned {challenge['points_reward']} points!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing challenge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# SEASONS
@tournament_router.get("/season/current")
async def get_current_season():
    """
    Get current season information and leaderboard
    """
    try:
        db = get_database()
        
        season = await db.seasons.find_one({
            "status": "active"
        })
        
        if not season:
            return {
                "has_season": False,
                "message": "No active season"
            }
        
        # Get top players
        top_players = await db.viewers.find().sort("points", -1).limit(50).to_list(length=50)
        
        season["top_players"] = [
            {
                "rank": i + 1,
                "username": player["username"],
                "points": player.get("points", 0),
                "level": player.get("level", 1)
            }
            for i, player in enumerate(top_players)
        ]
        
        return season
        
    except Exception as e:
        logger.error(f"Error fetching current season: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tournament_router.post("/season/reset")
async def reset_season():
    """
    End current season and start new one (admin only)
    """
    try:
        db = get_database()
        
        # End current season
        await db.seasons.update_many(
            {"status": "active"},
            {"$set": {"status": "ended", "ended_at": datetime.now()}}
        )
        
        # Create new season
        season_id = str(uuid.uuid4())
        new_season = {
            "season_id": season_id,
            "name": f"Season {datetime.now().year}",
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=90),
            "status": "active",
            "created_at": datetime.now()
        }
        
        await db.seasons.insert_one(new_season)
        
        # Optional: Reset viewer points or create season snapshot
        
        return {
            "success": True,
            "season_id": season_id,
            "message": "New season started!"
        }
        
    except Exception as e:
        logger.error(f"Error resetting season: {e}")
        raise HTTPException(status_code=500, detail=str(e))
