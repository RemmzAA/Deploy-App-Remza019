"""
REMZA019 Gaming - Theme Manager API
Pre-configured themes and full site customization
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from admin_api import get_current_admin

logger = logging.getLogger("theme_api")

theme_router = APIRouter(prefix="/themes", tags=["themes"])

# PRE-CONFIGURED THEMES
PREDEFINED_THEMES = {
    "matrix_green": {
        "name": "Matrix Green (Default)",
        "description": "Classic Matrix hacker theme with green rain",
        "colors": {
            "primary": "#00ff00",
            "secondary": "#0d0208",
            "background": "#000000",
            "text": "#00ff00",
            "accent": "#39ff14",
            "cardBg": "rgba(0, 255, 0, 0.05)",
            "border": "rgba(0, 255, 0, 0.3)"
        },
        "fonts": {
            "primary": "'Orbitron', monospace",
            "secondary": "'Courier New', monospace"
        },
        "effects": {
            "matrixRain": True,
            "glowEffect": True,
            "scanLines": True
        }
    },
    "cyber_purple": {
        "name": "Cyber Purple",
        "description": "Cyberpunk purple neon theme",
        "colors": {
            "primary": "#8b00ff",
            "secondary": "#1a0033",
            "background": "#0a0015",
            "text": "#e0b0ff",
            "accent": "#ff00ff",
            "cardBg": "rgba(139, 0, 255, 0.1)",
            "border": "rgba(139, 0, 255, 0.4)"
        },
        "fonts": {
            "primary": "'Orbitron', sans-serif",
            "secondary": "'Rajdhani', sans-serif"
        },
        "effects": {
            "matrixRain": False,
            "glowEffect": True,
            "scanLines": True
        }
    },
    "neon_blue": {
        "name": "Neon Blue",
        "description": "Electric blue gaming theme",
        "colors": {
            "primary": "#00d9ff",
            "secondary": "#001a33",
            "background": "#000510",
            "text": "#a0e7ff",
            "accent": "#0099cc",
            "cardBg": "rgba(0, 217, 255, 0.08)",
            "border": "rgba(0, 217, 255, 0.35)"
        },
        "fonts": {
            "primary": "'Rajdhani', sans-serif",
            "secondary": "'Exo 2', sans-serif"
        },
        "effects": {
            "matrixRain": False,
            "glowEffect": True,
            "scanLines": False
        }
    },
    "toxic_green": {
        "name": "Toxic Green",
        "description": "Radioactive green gaming theme",
        "colors": {
            "primary": "#39ff14",
            "secondary": "#0a1f0a",
            "background": "#000000",
            "text": "#b4ff9f",
            "accent": "#7fff00",
            "cardBg": "rgba(57, 255, 20, 0.1)",
            "border": "rgba(57, 255, 20, 0.4)"
        },
        "fonts": {
            "primary": "'Audiowide', cursive",
            "secondary": "'Russo One', sans-serif"
        },
        "effects": {
            "matrixRain": True,
            "glowEffect": True,
            "scanLines": True
        }
    },
    "blood_red": {
        "name": "Blood Red",
        "description": "Aggressive red gaming theme",
        "colors": {
            "primary": "#ff0000",
            "secondary": "#1a0000",
            "background": "#0d0000",
            "text": "#ffcccc",
            "accent": "#ff4444",
            "cardBg": "rgba(255, 0, 0, 0.08)",
            "border": "rgba(255, 0, 0, 0.35)"
        },
        "fonts": {
            "primary": "'Teko', sans-serif",
            "secondary": "'Quantico', sans-serif"
        },
        "effects": {
            "matrixRain": False,
            "glowEffect": True,
            "scanLines": True
        }
    },
    "midnight_dark": {
        "name": "Midnight Dark",
        "description": "Elegant dark theme with gold accents",
        "colors": {
            "primary": "#ffd700",
            "secondary": "#0f0f1e",
            "background": "#000000",
            "text": "#e0e0e0",
            "accent": "#ffed4e",
            "cardBg": "rgba(255, 215, 0, 0.05)",
            "border": "rgba(255, 215, 0, 0.25)"
        },
        "fonts": {
            "primary": "'Montserrat', sans-serif",
            "secondary": "'Roboto', sans-serif"
        },
        "effects": {
            "matrixRain": False,
            "glowEffect": False,
            "scanLines": False
        }
    }
}

class ThemeData(BaseModel):
    themeId: Optional[str] = None
    theme_name: Optional[str] = None  # Alternative field name
    customColors: Optional[Dict[str, str]] = {}
    customFonts: Optional[Dict[str, str]] = {}
    customEffects: Optional[Dict[str, bool]] = {}
    colors: Optional[Dict[str, str]] = {}  # Alternative field name
    fonts: Optional[Dict[str, str]] = {}  # Alternative field name
    
    class Config:
        extra = "allow"  # Allow extra fields

def get_database():
    """Get database instance"""
    from server import get_database as get_db
    return get_db()

@theme_router.get("/list")
async def get_available_themes():
    """Get list of all available pre-configured themes"""
    themes_list = []
    for theme_id, theme_data in PREDEFINED_THEMES.items():
        themes_list.append({
            "id": theme_id,
            "name": theme_data["name"],
            "description": theme_data["description"],
            "preview": theme_data["colors"]
        })
    
    return {
        "success": True,
        "themes": themes_list,
        "count": len(themes_list)
    }

@theme_router.get("/current")
async def get_current_theme():
    """Get currently active theme"""
    try:
        db = get_database()
        
        # Get from database
        theme_config = await db.theme_config.find_one(
            {"type": "active_theme"},
            {"_id": 0}
        )
        
        if not theme_config:
            # Return default theme
            default_theme = PREDEFINED_THEMES["matrix_green"].copy()
            default_theme["id"] = "matrix_green"
            logger.info("📝 Returning default theme: matrix_green")
            return {"success": True, "theme": default_theme}
        
        theme_id = theme_config.get("themeId", "matrix_green")
        theme_data = PREDEFINED_THEMES.get(theme_id, PREDEFINED_THEMES["matrix_green"]).copy()
        
        # Apply custom overrides if any
        if "customColors" in theme_config and theme_config["customColors"]:
            theme_data["colors"].update(theme_config["customColors"])
        if "customFonts" in theme_config and theme_config["customFonts"]:
            theme_data["fonts"].update(theme_config["customFonts"])
        if "customEffects" in theme_config and theme_config["customEffects"]:
            theme_data["effects"].update(theme_config["customEffects"])
        
        theme_data["id"] = theme_id
        
        logger.info(f"✅ Current theme retrieved: {theme_id}")
        return {"success": True, "theme": theme_data}
        
    except Exception as e:
        logger.error(f"❌ Get current theme error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@theme_router.post("/apply")
async def apply_theme(
    data: ThemeData,
    admin = Depends(get_current_admin)
):
    """Apply a theme (ADMIN ONLY - theme changes visible to all)"""
    try:
        db = get_database()
        
        # Get theme ID from either field
        theme_id = data.themeId or data.theme_name
        if not theme_id:
            raise HTTPException(status_code=400, detail="Theme ID or theme_name is required")
        
        # Validate theme exists
        if theme_id not in PREDEFINED_THEMES:
            raise HTTPException(status_code=400, detail=f"Invalid theme ID: {theme_id}")
        
        # Prepare theme config
        theme_config = {
            "type": "active_theme",
            "themeId": theme_id,
            "customColors": data.customColors or data.colors or {},
            "customFonts": data.customFonts or data.fonts or {},
            "customEffects": data.customEffects or {},
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": admin["username"]
        }
        
        # Save to database
        await db.theme_config.update_one(
            {"type": "active_theme"},
            {"$set": theme_config},
            upsert=True
        )
        
        logger.info(f"✅ Theme applied: {theme_id} by {admin['username']}")
        
        # Broadcast to all clients
        from admin_api import broadcast_admin_update
        await broadcast_admin_update("theme_changed", {
            "themeId": theme_id,
            "theme": PREDEFINED_THEMES[theme_id]
        })
        
        return {
            "success": True,
            "message": f"Theme '{PREDEFINED_THEMES[theme_id]['name']}' applied successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Apply theme error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@theme_router.post("/customize")
async def customize_theme(
    data: ThemeData,
    admin = Depends(get_current_admin)
):
    """Customize current theme with custom colors/fonts/effects (ADMIN ONLY)"""
    try:
        db = get_database()
        
        # Get current theme
        current = await db.theme_config.find_one({"type": "active_theme"})
        theme_id = current.get("themeId", "matrix_green") if current else "matrix_green"
        
        # Update with customizations
        update_data = {
            "type": "active_theme",
            "themeId": theme_id,
            "customColors": data.customColors or {},
            "customFonts": data.customFonts or {},
            "customEffects": data.customEffects or {},
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": admin["username"]
        }
        
        await db.theme_config.update_one(
            {"type": "active_theme"},
            {"$set": update_data},
            upsert=True
        )
        
        logger.info(f"✅ Theme customized by {admin['username']}")
        
        # Broadcast
        from admin_api import broadcast_admin_update
        await broadcast_admin_update("theme_changed", update_data)
        
        return {"success": True, "message": "Theme customizations applied"}
        
    except Exception as e:
        logger.error(f"❌ Customize theme error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@theme_router.post("/reset")
async def reset_theme(admin = Depends(get_current_admin)):
    """Reset theme to default Matrix Green"""
    try:
        db = get_database()
        
        await db.theme_config.delete_one({"type": "active_theme"})
        
        logger.info(f"✅ Theme reset to default by {admin['username']}")
        
        # Broadcast
        from admin_api import broadcast_admin_update
        await broadcast_admin_update("theme_changed", {
            "themeId": "matrix_green",
            "theme": PREDEFINED_THEMES["matrix_green"]
        })
        
        return {"success": True, "message": "Theme reset to Matrix Green"}
        
    except Exception as e:
        logger.error(f"❌ Reset theme error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
