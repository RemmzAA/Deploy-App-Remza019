"""
REMZA019 Gaming - Predictions System
Stream predictions for viewer engagement
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import uuid

from admin_api import get_current_admin
from websocket_manager import get_ws_manager

logger = logging.getLogger("predictions")

predictions_router = APIRouter(prefix="/predictions", tags=["predictions"])

# Pydantic models
class Prediction(BaseModel):
    id: str
    question: str
    option_a: str
    option_b: str
    votes_a: int = 0
    votes_b: int = 0
    active: bool
    created_at: str
    created_by: str
    total_votes: int = 0
    result: Optional[str] = None  # 'a', 'b', or None
    ended_at: Optional[str] = None

class CreatePredictionRequest(BaseModel):
    question: str
    option_a: str
    option_b: str

class PredictRequest(BaseModel):
    prediction_id: str
    choice: str  # 'a' or 'b'
    user_id: str
    username: str

class ResolvePredictionRequest(BaseModel):
    result: str  # 'a' or 'b'

# In-memory storage
active_predictions: Dict[str, Prediction] = {}
prediction_votes: Dict[str, Dict[str, str]] = {}  # {prediction_id: {user_id: choice}}

@predictions_router.post("/create")
async def create_prediction(
    request: CreatePredictionRequest,
    admin = Depends(get_current_admin)
):
    """Create a new prediction - ADMIN ONLY"""
    try:
        prediction = Prediction(
            id=str(uuid.uuid4()),
            question=request.question,
            option_a=request.option_a,
            option_b=request.option_b,
            active=True,
            created_at=datetime.now().isoformat(),
            created_by=admin['username'],
            votes_a=0,
            votes_b=0,
            total_votes=0
        )
        
        active_predictions[prediction.id] = prediction
        prediction_votes[prediction.id] = {}
        
        logger.info(f"✅ Prediction created: {prediction.question}")
        
        # Broadcast new prediction
        ws_manager = get_ws_manager()
        await ws_manager.broadcast({
            "type": "new_prediction",
            "prediction": prediction.dict()
        })
        
        return {"success": True, "prediction": prediction.dict()}
        
    except Exception as e:
        logger.error(f"❌ Create prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create prediction")

@predictions_router.get("/active")
async def get_active_predictions():
    """Get all active predictions - PUBLIC"""
    try:
        active = [pred.dict() for pred in active_predictions.values() if pred.active]
        return {"predictions": active}
    except Exception as e:
        logger.error(f"❌ Get active predictions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active predictions")

@predictions_router.post("/predict")
async def make_prediction(request: PredictRequest):
    """Make a prediction - PUBLIC"""
    try:
        prediction = active_predictions.get(request.prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        if not prediction.active:
            raise HTTPException(status_code=400, detail="Prediction is not active")
        
        if request.choice not in ['a', 'b']:
            raise HTTPException(status_code=400, detail="Invalid choice. Must be 'a' or 'b'")
        
        # Check if user already predicted
        if request.user_id in prediction_votes[request.prediction_id]:
            raise HTTPException(status_code=400, detail="You have already made a prediction")
        
        # Record prediction
        if request.choice == 'a':
            prediction.votes_a += 1
        else:
            prediction.votes_b += 1
        
        prediction.total_votes += 1
        prediction_votes[request.prediction_id][request.user_id] = request.choice
        
        logger.info(f"✅ Prediction made: {request.username} chose {request.choice}")
        
        # Broadcast updated prediction (hide vote counts until resolved)
        ws_manager = get_ws_manager()
        await ws_manager.broadcast({
            "type": "prediction_update",
            "prediction": {
                "id": prediction.id,
                "question": prediction.question,
                "option_a": prediction.option_a,
                "option_b": prediction.option_b,
                "total_votes": prediction.total_votes,
                "active": prediction.active
            }
        })
        
        return {"success": True, "message": f"Prediction recorded: {request.choice}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record prediction")

@predictions_router.post("/resolve/{prediction_id}")
async def resolve_prediction(
    prediction_id: str,
    request: ResolvePredictionRequest,
    admin = Depends(get_current_admin)
):
    """Resolve a prediction with the actual result - ADMIN ONLY"""
    try:
        prediction = active_predictions.get(prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        if request.result not in ['a', 'b']:
            raise HTTPException(status_code=400, detail="Invalid result. Must be 'a' or 'b'")
        
        prediction.active = False
        prediction.result = request.result
        prediction.ended_at = datetime.now().isoformat()
        
        # Calculate accuracy
        correct_votes = prediction.votes_a if request.result == 'a' else prediction.votes_b
        accuracy = (correct_votes / prediction.total_votes * 100) if prediction.total_votes > 0 else 0
        
        logger.info(f"✅ Prediction resolved: {prediction.question} - Result: {request.result}")
        logger.info(f"   Accuracy: {accuracy:.1f}% ({correct_votes}/{prediction.total_votes})")
        
        # Broadcast resolution with full results
        ws_manager = get_ws_manager()
        await ws_manager.broadcast({
            "type": "prediction_resolved",
            "prediction": prediction.dict(),
            "accuracy": round(accuracy, 1),
            "correct_votes": correct_votes
        })
        
        return {
            "success": True,
            "prediction": prediction.dict(),
            "accuracy": round(accuracy, 1),
            "correct_votes": correct_votes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resolve prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve prediction")

@predictions_router.get("/results/{prediction_id}")
async def get_prediction_results(prediction_id: str):
    """Get prediction results - PUBLIC (only shows results if resolved)"""
    try:
        prediction = active_predictions.get(prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Only show vote breakdown if prediction is resolved
        if prediction.result:
            percentage_a = (prediction.votes_a / prediction.total_votes * 100) if prediction.total_votes > 0 else 0
            percentage_b = (prediction.votes_b / prediction.total_votes * 100) if prediction.total_votes > 0 else 0
            
            return {
                "prediction_id": prediction.id,
                "question": prediction.question,
                "option_a": prediction.option_a,
                "option_b": prediction.option_b,
                "votes_a": prediction.votes_a,
                "votes_b": prediction.votes_b,
                "percentage_a": round(percentage_a, 1),
                "percentage_b": round(percentage_b, 1),
                "total_votes": prediction.total_votes,
                "result": prediction.result,
                "ended_at": prediction.ended_at
            }
        else:
            return {
                "prediction_id": prediction.id,
                "question": prediction.question,
                "option_a": prediction.option_a,
                "option_b": prediction.option_b,
                "total_votes": prediction.total_votes,
                "active": prediction.active,
                "message": "Results will be revealed when prediction is resolved"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get prediction results error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prediction results")

@predictions_router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    admin = Depends(get_current_admin)
):
    """Delete a prediction - ADMIN ONLY"""
    try:
        if prediction_id in active_predictions:
            del active_predictions[prediction_id]
            if prediction_id in prediction_votes:
                del prediction_votes[prediction_id]
            
            logger.info(f"✅ Prediction deleted: {prediction_id}")
            
            # Broadcast deletion
            ws_manager = get_ws_manager()
            await ws_manager.broadcast({
                "type": "prediction_deleted",
                "prediction_id": prediction_id
            })
            
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Prediction not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prediction")
