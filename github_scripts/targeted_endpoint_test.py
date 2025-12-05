#!/usr/bin/env python3
"""
Targeted Endpoint Testing - Focus on Specific Issues
"""

import asyncio
import aiohttp
import json
from pathlib import Path

# Get backend URL from frontend .env
frontend_env_path = Path("/app/frontend/.env")
BACKEND_URL = None
if frontend_env_path.exists():
    with open(frontend_env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break

API_BASE_URL = f"{BACKEND_URL}/api"

async def test_specific_issues():
    """Test specific issues found in comprehensive test"""
    
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(timeout=timeout)
    
    try:
        print("🔍 TARGETED TESTING - SPECIFIC ISSUES")
        print("="*50)
        
        # 1. Test theme apply with correct theme ID
        print("\n1. Testing Theme Apply with correct theme IDs...")
        
        # First get admin token
        login_data = {"username": "admin", "password": "remza019admin"}
        async with session.post(f"{API_BASE_URL}/admin/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                token = result.get('token')
                print(f"✅ Admin token obtained")
                
                # Get available themes first
                async with session.get(f"{API_BASE_URL}/themes/list") as theme_response:
                    if theme_response.status == 200:
                        themes_data = await theme_response.json()
                        available_themes = [theme['id'] for theme in themes_data.get('themes', [])]
                        print(f"✅ Available themes: {available_themes}")
                        
                        # Try applying with correct theme ID
                        if available_themes:
                            theme_data = {"themeId": available_themes[0]}  # Use first available theme
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            async with session.post(f"{API_BASE_URL}/themes/apply", json=theme_data, headers=headers) as apply_response:
                                if apply_response.status == 200:
                                    print(f"✅ Theme apply works with correct ID: {available_themes[0]}")
                                else:
                                    error_text = await apply_response.text()
                                    print(f"❌ Theme apply still fails: {apply_response.status} - {error_text}")
        
        # 2. Test customization update endpoint
        print("\n2. Testing Customization Update Endpoint...")
        
        # Check what endpoints are available
        customization_endpoints = [
            "/admin/customization/update",
            "/customization/save",
            "/customization/update"
        ]
        
        for endpoint in customization_endpoints:
            async with session.get(f"{API_BASE_URL}{endpoint}") as response:
                print(f"   {endpoint}: HTTP {response.status}")
        
        # 3. Test viewer registration with different data
        print("\n3. Testing Viewer Registration...")
        
        # Try with unique data
        import time
        unique_id = str(int(time.time()))
        viewer_data = {
            "username": f"TestUser{unique_id}",
            "email": f"test{unique_id}@example.com"
        }
        
        async with session.post(f"{API_BASE_URL}/viewer/register", json=viewer_data) as response:
            if response.status == 200:
                print(f"✅ Viewer registration works with unique data")
                result = await response.json()
                print(f"   Response: {result}")
            else:
                error_text = await response.text()
                print(f"❌ Viewer registration fails: {response.status} - {error_text}")
        
        # 4. Test schedule delete with existing day
        print("\n4. Testing Schedule Delete...")
        
        # First get current schedule
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{API_BASE_URL}/admin/schedule", headers=headers) as response:
            if response.status == 200:
                schedule_data = await response.json()
                print(f"✅ Current schedule retrieved")
                
                # Find an existing day to delete
                if isinstance(schedule_data, list) and schedule_data:
                    existing_day = schedule_data[0].get('day', '').lower()
                    if existing_day:
                        async with session.delete(f"{API_BASE_URL}/admin/schedule/{existing_day}", headers=headers) as delete_response:
                            if delete_response.status == 200:
                                print(f"✅ Schedule delete works for existing day: {existing_day}")
                            else:
                                error_text = await delete_response.text()
                                print(f"❌ Schedule delete fails: {delete_response.status} - {error_text}")
        
        # 5. Test YouTube API configuration
        print("\n5. Testing YouTube API Configuration...")
        
        # Check if YOUTUBE_API_KEY is set in backend
        print("   YouTube API requires YOUTUBE_API_KEY environment variable")
        print("   This is expected to fail in testing environment")
        
        async with session.get(f"{API_BASE_URL}/youtube/latest-videos") as response:
            error_text = await response.text()
            if "YOUTUBE_API_KEY" in error_text:
                print("✅ YouTube API correctly reports missing API key (expected)")
            else:
                print(f"❌ Unexpected YouTube API error: {error_text}")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_specific_issues())