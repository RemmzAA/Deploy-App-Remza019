#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE BACKEND TEST - ALL CRITICAL ENDPOINTS
Testing with correct endpoint paths and parameters
"""

import asyncio
import aiohttp
import json
import time
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

async def run_final_test():
    """Run final comprehensive test with correct endpoints"""
    
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(timeout=timeout)
    
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'critical_endpoints': {},
        'issues': []
    }
    
    def log_test(name, success, details=""):
        results['total_tests'] += 1
        if success:
            results['passed_tests'] += 1
            print(f"✅ {name}")
        else:
            results['failed_tests'] += 1
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
                results['issues'].append(f"{name}: {details}")
    
    try:
        print("🎯 FINAL COMPREHENSIVE BACKEND TEST - ALL CRITICAL ENDPOINTS")
        print("="*70)
        
        # 1. ADMIN AUTHENTICATION
        print("\n🔐 1. ADMIN AUTHENTICATION")
        admin_token = None
        login_data = {"username": "admin", "password": "remza019admin"}
        async with session.post(f"{API_BASE_URL}/admin/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                admin_token = result.get('token')
                log_test("Admin Authentication", True, f"Token: {admin_token[:20]}...")
                results['critical_endpoints']['admin_auth'] = True
            else:
                log_test("Admin Authentication", False, f"HTTP {response.status}")
                results['critical_endpoints']['admin_auth'] = False
        
        # 2. VERSION API (NEWLY FIXED)
        print("\n🔄 2. VERSION API ENDPOINTS (NEWLY FIXED)")
        version_endpoints = [
            ("/version/current", "Version Current"),
            ("/version/check-update", "Version Check Update"),
            ("/version/info", "Version Info")
        ]
        
        version_success = 0
        for endpoint, name in version_endpoints:
            async with session.get(f"{API_BASE_URL}{endpoint}") as response:
                if response.status == 200:
                    result = await response.json()
                    log_test(name, True)
                    version_success += 1
                else:
                    log_test(name, False, f"HTTP {response.status}")
        
        results['critical_endpoints']['version_api'] = version_success == 3
        
        # 3. THEME API
        print("\n🎨 3. THEME API ENDPOINTS")
        
        # Get themes list
        async with session.get(f"{API_BASE_URL}/themes/list") as response:
            if response.status == 200:
                themes_data = await response.json()
                theme_count = len(themes_data.get('themes', []))
                log_test("Theme List (6 themes)", theme_count == 6, f"Found {theme_count} themes")
                available_themes = [theme['id'] for theme in themes_data.get('themes', [])]
            else:
                log_test("Theme List", False, f"HTTP {response.status}")
                available_themes = []
        
        # Get current theme
        async with session.get(f"{API_BASE_URL}/themes/current") as response:
            if response.status == 200:
                log_test("Theme Current", True)
            else:
                log_test("Theme Current", False, f"HTTP {response.status}")
        
        # Apply theme (with admin auth)
        if admin_token and available_themes:
            theme_data = {"themeId": available_themes[0]}
            headers = {"Authorization": f"Bearer {admin_token}"}
            async with session.post(f"{API_BASE_URL}/themes/apply", json=theme_data, headers=headers) as response:
                if response.status == 200:
                    log_test("Theme Apply (Admin Auth)", True)
                    results['critical_endpoints']['theme_api'] = True
                else:
                    error_text = await response.text()
                    log_test("Theme Apply (Admin Auth)", False, f"HTTP {response.status}")
                    results['critical_endpoints']['theme_api'] = False
        else:
            log_test("Theme Apply (Admin Auth)", False, "No admin token or themes available")
            results['critical_endpoints']['theme_api'] = False
        
        # 4. ADMIN SCHEDULE API
        print("\n📅 4. ADMIN SCHEDULE API")
        
        if admin_token:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Get schedule
            async with session.get(f"{API_BASE_URL}/admin/schedule", headers=headers) as response:
                if response.status == 200:
                    schedule_data = await response.json()
                    log_test("Admin Schedule Get", True)
                    
                    # Update schedule
                    update_data = {
                        "day": "monday",
                        "time": "19:00",
                        "game": "FORTNITE Test",
                        "description": "Test update"
                    }
                    async with session.post(f"{API_BASE_URL}/admin/schedule/update", json=update_data, headers=headers) as update_response:
                        if update_response.status == 200:
                            log_test("Admin Schedule Update", True)
                            
                            # Delete schedule (use existing day)
                            if isinstance(schedule_data, list) and schedule_data:
                                existing_day = schedule_data[0].get('day', '').lower()
                                if existing_day:
                                    async with session.delete(f"{API_BASE_URL}/admin/schedule/{existing_day}", headers=headers) as delete_response:
                                        if delete_response.status == 200:
                                            log_test("Admin Schedule Delete", True)
                                            results['critical_endpoints']['admin_schedule'] = True
                                        else:
                                            log_test("Admin Schedule Delete", False, f"HTTP {delete_response.status}")
                                            results['critical_endpoints']['admin_schedule'] = False
                                else:
                                    log_test("Admin Schedule Delete", False, "No existing day found")
                                    results['critical_endpoints']['admin_schedule'] = False
                            else:
                                log_test("Admin Schedule Delete", False, "Invalid schedule data")
                                results['critical_endpoints']['admin_schedule'] = False
                        else:
                            log_test("Admin Schedule Update", False, f"HTTP {update_response.status}")
                            results['critical_endpoints']['admin_schedule'] = False
                else:
                    log_test("Admin Schedule Get", False, f"HTTP {response.status}")
                    results['critical_endpoints']['admin_schedule'] = False
        else:
            log_test("Admin Schedule API", False, "No admin token")
            results['critical_endpoints']['admin_schedule'] = False
        
        # 5. CUSTOMIZATION API
        print("\n🎨 5. CUSTOMIZATION API")
        
        # Get current customization
        async with session.get(f"{API_BASE_URL}/customization/current") as response:
            if response.status == 200:
                log_test("Customization Get Current", True)
                
                # Save customization (with admin auth) - using correct endpoint
                if admin_token:
                    customization_data = {
                        "userName": "REMZA019 Gaming Test",
                        "matrixColor": "#00ff00",
                        "textColor": "#ffffff",
                        "logoUrl": "/test-logo.png"
                    }
                    headers = {"Authorization": f"Bearer {admin_token}"}
                    async with session.post(f"{API_BASE_URL}/customization/save", json=customization_data, headers=headers) as save_response:
                        if save_response.status == 200:
                            log_test("Customization Save (Admin Auth)", True)
                            results['critical_endpoints']['customization_api'] = True
                        else:
                            error_text = await save_response.text()
                            log_test("Customization Save (Admin Auth)", False, f"HTTP {save_response.status}")
                            results['critical_endpoints']['customization_api'] = False
                else:
                    log_test("Customization Save", False, "No admin token")
                    results['critical_endpoints']['customization_api'] = False
            else:
                log_test("Customization Get Current", False, f"HTTP {response.status}")
                results['critical_endpoints']['customization_api'] = False
        
        # 6. VIEWER API
        print("\n👥 6. VIEWER API")
        
        # Register viewer with unique data
        unique_id = str(int(time.time()))
        viewer_data = {
            "username": f"TestGamer{unique_id}",
            "email": f"testgamer{unique_id}@remza019.com"
        }
        
        async with session.post(f"{API_BASE_URL}/viewer/register", json=viewer_data) as response:
            if response.status == 200:
                result = await response.json()
                viewer_id = result.get('viewer', {}).get('id')
                log_test("Viewer Registration", True)
                
                if viewer_id:
                    # Get viewer profile
                    async with session.get(f"{API_BASE_URL}/viewer/profile/{viewer_id}") as profile_response:
                        if profile_response.status == 200:
                            log_test("Viewer Get Profile", True)
                            
                            # Award points
                            points_data = {
                                "points": 50,
                                "activity": "stream_view",
                                "description": "Test point award"
                            }
                            async with session.post(f"{API_BASE_URL}/viewer/activity/{viewer_id}?activity_type=stream_view") as points_response:
                                if points_response.status == 200:
                                    log_test("Viewer Award Points", True)
                                    results['critical_endpoints']['viewer_api'] = True
                                else:
                                    log_test("Viewer Award Points", False, f"HTTP {points_response.status}")
                                    results['critical_endpoints']['viewer_api'] = False
                        else:
                            log_test("Viewer Get Profile", False, f"HTTP {profile_response.status}")
                            results['critical_endpoints']['viewer_api'] = False
                else:
                    log_test("Viewer Get Profile", False, "No viewer ID returned")
                    results['critical_endpoints']['viewer_api'] = False
            else:
                error_text = await response.text()
                log_test("Viewer Registration", False, f"HTTP {response.status}")
                results['critical_endpoints']['viewer_api'] = False
        
        # 7. ADDITIONAL CRITICAL ENDPOINTS
        print("\n🔍 7. ADDITIONAL CRITICAL ENDPOINTS")
        
        # API Health
        async with session.get(f"{API_BASE_URL}/") as response:
            if response.status == 200:
                log_test("API Health Check", True)
            else:
                log_test("API Health Check", False, f"HTTP {response.status}")
        
        # YouTube API (expected to fail without API key)
        async with session.get(f"{API_BASE_URL}/youtube/latest-videos") as response:
            error_text = await response.text()
            if "YOUTUBE_API_KEY" in error_text:
                log_test("YouTube API (Expected Failure)", True, "Correctly reports missing API key")
            else:
                log_test("YouTube API", False, "Unexpected error")
        
        # FINAL REPORT
        print("\n" + "="*70)
        print("🎯 FINAL COMPREHENSIVE TEST REPORT")
        print("="*70)
        
        success_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Passed: {results['passed_tests']}")
        print(f"   Failed: {results['failed_tests']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 CRITICAL ENDPOINTS STATUS:")
        critical_success = sum(1 for success in results['critical_endpoints'].values() if success)
        critical_total = len(results['critical_endpoints'])
        
        for endpoint, success in results['critical_endpoints'].items():
            status = "✅" if success else "❌"
            print(f"   {status} {endpoint.replace('_', ' ').title()}")
        
        critical_rate = (critical_success / critical_total * 100) if critical_total > 0 else 0
        print(f"\n🎯 CRITICAL SUCCESS RATE: {critical_rate:.1f}% ({critical_success}/{critical_total})")
        
        if results['issues']:
            print(f"\n🚨 ISSUES FOUND:")
            for issue in results['issues']:
                print(f"   • {issue}")
        
        # Assessment
        if critical_rate >= 90:
            print(f"\n🎉 ASSESSMENT: EXCELLENT - All critical endpoints working!")
        elif critical_rate >= 75:
            print(f"\n✅ ASSESSMENT: GOOD - Most critical endpoints working")
        elif critical_rate >= 50:
            print(f"\n⚠️  ASSESSMENT: NEEDS ATTENTION - Several critical issues")
        else:
            print(f"\n❌ ASSESSMENT: CRITICAL PROBLEMS - Major backend failures")
        
        return results
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(run_final_test())