"""
019 Solutions - OBS WebSocket API Integration
Remote OBS Studio Control (Stream, Scenes, Sources, Audio)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

obs_router = APIRouter(prefix="/api/obs", tags=["obs"])

# OBS WebSocket Configuration
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Will use from environment

# MOCK MODE - For development without OBS running
MOCK_MODE = True

# Mock data for testing
MOCK_SCENES = [
    {"name": "Gaming Scene", "uuid": "scene-1", "is_active": True},
    {"name": "Intro Scene", "uuid": "scene-2", "is_active": False},
    {"name": "BRB Scene", "uuid": "scene-3", "is_active": False},
    {"name": "Outro Scene", "uuid": "scene-4", "is_active": False}
]

MOCK_SOURCES = {
    "Gaming Scene": [
        {"id": 1, "name": "Game Capture", "type": "game_capture", "visible": True},
        {"id": 2, "name": "Webcam", "type": "video_capture", "visible": True},
        {"id": 3, "name": "Alert Overlay", "type": "browser_source", "visible": False},
        {"id": 4, "name": "Chat Overlay", "type": "browser_source", "visible": True}
    ],
    "Intro Scene": [
        {"id": 5, "name": "Intro Video", "type": "media_source", "visible": True},
        {"id": 6, "name": "Starting Soon Text", "type": "text_source", "visible": True}
    ]
}

MOCK_AUDIO_SOURCES = [
    {"name": "Desktop Audio", "muted": False, "volume": 0.75},
    {"name": "Microphone", "muted": False, "volume": 0.85},
    {"name": "Music", "muted": True, "volume": 0.50}
]

# Mock streaming state
MOCK_STREAM_STATE = {
    "streaming": False,
    "recording": False,
    "stream_time": "00:00:00",
    "bytes_sent": 0,
    "frames_sent": 0,
    "fps": 60.0
}

# Models
class SceneInfo(BaseModel):
    name: str
    uuid: str
    is_active: bool

class SourceInfo(BaseModel):
    id: int
    name: str
    type: str
    visible: bool

class AudioSourceInfo(BaseModel):
    name: str
    muted: bool
    volume: float

class StreamStatus(BaseModel):
    streaming: bool
    recording: bool
    stream_time: str
    bytes_sent: int
    frames_sent: int
    fps: float

# CONNECTION & STATUS ENDPOINTS

@obs_router.get("/status")
async def get_obs_status():
    """Get OBS connection and stream status"""
    try:
        if MOCK_MODE:
            return {
                "success": True,
                "connected": True,
                "obs_version": "29.0.0 (MOCK)",
                "websocket_version": "5.0.0 (MOCK)",
                "streaming": MOCK_STREAM_STATE["streaming"],
                "recording": MOCK_STREAM_STATE["recording"],
                "current_scene": MOCK_SCENES[0]["name"],
                "mode": "mock"
            }
        
        # Real OBS connection would go here
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Get OBS status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get OBS status")

@obs_router.get("/stream/status")
async def get_stream_status():
    """Get detailed streaming status"""
    try:
        if MOCK_MODE:
            return {
                "success": True,
                "status": MOCK_STREAM_STATE,
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Get stream status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stream status")

# STREAMING CONTROL

@obs_router.post("/stream/start")
async def start_streaming(admin = Depends(lambda: {"username": "admin"})):
    """Start streaming"""
    try:
        if MOCK_MODE:
            MOCK_STREAM_STATE["streaming"] = True
            logger.info(f"✅ Stream started by {admin['username']} (MOCK)")
            return {
                "success": True,
                "message": "Streaming started",
                "mode": "mock"
            }
        
        # Real implementation:
        # obs_client.start_stream()
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Start stream error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start stream")

@obs_router.post("/stream/stop")
async def stop_streaming(admin = Depends(lambda: {"username": "admin"})):
    """Stop streaming"""
    try:
        if MOCK_MODE:
            MOCK_STREAM_STATE["streaming"] = False
            logger.info(f"✅ Stream stopped by {admin['username']} (MOCK)")
            return {
                "success": True,
                "message": "Streaming stopped",
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Stop stream error: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop stream")

# RECORDING CONTROL

@obs_router.post("/recording/start")
async def start_recording(admin = Depends(lambda: {"username": "admin"})):
    """Start recording"""
    try:
        if MOCK_MODE:
            MOCK_STREAM_STATE["recording"] = True
            logger.info(f"✅ Recording started by {admin['username']} (MOCK)")
            return {
                "success": True,
                "message": "Recording started",
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Start recording error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start recording")

@obs_router.post("/recording/stop")
async def stop_recording(admin = Depends(lambda: {"username": "admin"})):
    """Stop recording"""
    try:
        if MOCK_MODE:
            MOCK_STREAM_STATE["recording"] = False
            logger.info(f"✅ Recording stopped by {admin['username']} (MOCK)")
            return {
                "success": True,
                "message": "Recording stopped",
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Stop recording error: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop recording")

# SCENE MANAGEMENT

@obs_router.get("/scenes")
async def list_scenes():
    """Get all scenes"""
    try:
        if MOCK_MODE:
            return {
                "success": True,
                "scenes": MOCK_SCENES,
                "current_scene": next((s["name"] for s in MOCK_SCENES if s["is_active"]), None),
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ List scenes error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list scenes")

@obs_router.post("/scenes/{scene_name}/activate")
async def switch_scene(scene_name: str, admin = Depends(lambda: {"username": "admin"})):
    """Switch to a specific scene"""
    try:
        if MOCK_MODE:
            # Update mock data
            for scene in MOCK_SCENES:
                scene["is_active"] = (scene["name"] == scene_name)
            
            logger.info(f"✅ Switched to scene '{scene_name}' by {admin['username']} (MOCK)")
            return {
                "success": True,
                "message": f"Switched to scene: {scene_name}",
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Switch scene error: {e}")
        raise HTTPException(status_code=500, detail="Failed to switch scene")

# SOURCE MANAGEMENT

@obs_router.get("/scenes/{scene_name}/sources")
async def get_scene_sources(scene_name: str):
    """Get all sources in a scene"""
    try:
        if MOCK_MODE:
            sources = MOCK_SOURCES.get(scene_name, [])
            return {
                "success": True,
                "scene_name": scene_name,
                "sources": sources,
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ Get sources error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sources")

@obs_router.post("/scenes/{scene_name}/sources/{source_id}/visibility")
async def toggle_source_visibility(
    scene_name: str, 
    source_id: int, 
    visible: bool,
    admin = Depends(lambda: {"username": "admin"})
):
    """Show or hide a source in a scene"""
    try:
        if MOCK_MODE:
            # Update mock data
            if scene_name in MOCK_SOURCES:
                for source in MOCK_SOURCES[scene_name]:
                    if source["id"] == source_id:
                        source["visible"] = visible
                        status = "shown" if visible else "hidden"
                        logger.info(f"✅ Source '{source['name']}' {status} by {admin['username']} (MOCK)")
                        return {
                            "success": True,
                            "message": f"Source {status}",
                            "mode": "mock"
                        }
            
            raise HTTPException(status_code=404, detail="Source not found")
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Toggle source error: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle source")

# AUDIO CONTROL

@obs_router.get("/audio/sources")
async def list_audio_sources():
    """Get all audio sources"""
    try:
        if MOCK_MODE:
            return {
                "success": True,
                "audio_sources": MOCK_AUDIO_SOURCES,
                "mode": "mock"
            }
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except Exception as e:
        logger.error(f"❌ List audio sources error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list audio sources")

@obs_router.post("/audio/{source_name}/mute")
async def toggle_audio_mute(
    source_name: str,
    muted: bool,
    admin = Depends(lambda: {"username": "admin"})
):
    """Mute or unmute an audio source"""
    try:
        if MOCK_MODE:
            for source in MOCK_AUDIO_SOURCES:
                if source["name"] == source_name:
                    source["muted"] = muted
                    status = "muted" if muted else "unmuted"
                    logger.info(f"✅ Audio '{source_name}' {status} by {admin['username']} (MOCK)")
                    return {
                        "success": True,
                        "message": f"Audio {status}",
                        "mode": "mock"
                    }
            
            raise HTTPException(status_code=404, detail="Audio source not found")
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Toggle audio mute error: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle audio mute")

@obs_router.post("/audio/{source_name}/volume")
async def set_audio_volume(
    source_name: str,
    volume: float,
    admin = Depends(lambda: {"username": "admin"})
):
    """Set audio source volume (0.0 - 1.0)"""
    try:
        if volume < 0 or volume > 1:
            raise HTTPException(status_code=400, detail="Volume must be between 0.0 and 1.0")
        
        if MOCK_MODE:
            for source in MOCK_AUDIO_SOURCES:
                if source["name"] == source_name:
                    source["volume"] = volume
                    logger.info(f"✅ Audio '{source_name}' volume set to {volume:.2f} by {admin['username']} (MOCK)")
                    return {
                        "success": True,
                        "message": f"Volume set to {volume:.2f}",
                        "mode": "mock"
                    }
            
            raise HTTPException(status_code=404, detail="Audio source not found")
        
        raise HTTPException(status_code=501, detail="Real OBS not implemented yet")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Set audio volume error: {e}")
        raise HTTPException(status_code=500, detail="Failed to set audio volume")
