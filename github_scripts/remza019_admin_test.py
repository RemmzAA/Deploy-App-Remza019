#!/usr/bin/env python3
"""
REMZA019 Gaming Admin Panel - Comprehensive Testing Suite
Tests all admin endpoints with focus on Featured Video & Content Management
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_env_path = Path("/app/backend/.env")
frontend_env_path = Path("/app/frontend/.env")

if backend_env_path.exists():
    load_dotenv(backend_env_path)

# Get URLs from environment
BACKEND_URL = None
if frontend_env_path.exists():
    with open(frontend_env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break

if not BACKEND_URL:
    print("❌ ERROR: Could not find REACT_APP_BACKEND_URL in frontend/.env")
    sys.exit(1)

API_BASE_URL = f"{BACKEND_URL}/api"

class REMZA019AdminTester:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_failures': [],
            'admin_endpoints': {},
            'error_logs': []
        }
        self.session = None
        self.admin_token = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up REMZA019 Admin Panel test environment...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name, passed, details="", critical=False):
        """Log test result"""
        self.results['total_tests'] += 1
        if passed:
            self.results['passed_tests'] += 1
            print(f"✅ {test_name}")
        else:
            self.results['failed_tests'] += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   Details: {details}")
                self.results['error_logs'].append(f"{test_name}: {details}")
            if critical:
                self.results['critical_failures'].append(test_name)

    async def admin_login(self):
        """Login as admin to get authentication token"""
        print("\n🔐 Admin Authentication...")
        
        login_data = {
            "username": "admin",
            "password": "remza019admin"
        }
        
        try:
            url = f"{API_BASE_URL}/admin/auth/login"
            async with self.session.post(url, json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("token"):
                        self.admin_token = result["token"]
                        self.log_test_result("Admin login successful", True)
                        return True
                    else:
                        self.log_test_result("Admin login - token missing", False, "No token in response", critical=True)
                        return False
                else:
                    self.log_test_result("Admin login failed", False, f"HTTP {response.status}", critical=True)
                    return False
        except Exception as e:
            self.log_test_result("Admin login error", False, str(e), critical=True)
            return False

    async def test_featured_video_management(self):
        """Test Featured Video Management - PRIORITY HIGH"""
        print("\n🎬 Testing Featured Video Management - PRIORITY HIGH...")
        
        if not self.admin_token:
            self.log_test_result("Featured Video Management", False, "No admin token", critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Update Featured Video
        featured_video_data = {
            "video_id": "TEST123",
            "title": "Test Video",
            "description": "Test desc"
        }
        
        try:
            url = f"{API_BASE_URL}/admin/content/featured-video/update"
            async with self.session.post(url, json=featured_video_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("POST /api/admin/content/featured-video/update", True)
                    
                    # Verify response structure
                    if result.get("success"):
                        self.log_test_result("Featured video update response validation", True)
                    else:
                        self.log_test_result("Featured video update response validation", False, "Missing success field")
                else:
                    self.log_test_result("POST /api/admin/content/featured-video/update", False, f"HTTP {response.status}", critical=True)
        except Exception as e:
            self.log_test_result("POST /api/admin/content/featured-video/update", False, str(e), critical=True)
        
        # Test 2: Get Featured Video Data to Confirm
        try:
            url = f"{API_BASE_URL}/admin/content/featured-video"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET featured video data", True)
                    
                    # Verify stored data
                    if isinstance(result, dict):
                        if result.get("video_id") == "TEST123":
                            self.log_test_result("Featured video data persistence", True, "Video ID matches")
                        else:
                            self.log_test_result("Featured video data persistence", False, f"Expected TEST123, got {result.get('video_id')}")
                    else:
                        self.log_test_result("Featured video data structure", False, "Response is not a dict")
                else:
                    self.log_test_result("GET featured video data", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET featured video data", False, str(e))

    async def test_about_content_management(self):
        """Test About Content Management"""
        print("\n📝 Testing About Content Management...")
        
        # Test 1: GET About Content (should work without auth)
        try:
            url = f"{API_BASE_URL}/admin/content/about"
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET /api/admin/content/about", True)
                    
                    # Verify response structure
                    if isinstance(result, dict) and "content" in result:
                        self.log_test_result("About content response structure", True)
                    else:
                        self.log_test_result("About content response structure", False, "Missing content field")
                else:
                    self.log_test_result("GET /api/admin/content/about", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET /api/admin/content/about", False, str(e))
        
        # Test 2: POST About Content Update (requires auth)
        if not self.admin_token:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        about_data = {
            "content": ["Test line 1", "Test line 2"]
        }
        
        try:
            url = f"{API_BASE_URL}/admin/content/about/update"
            async with self.session.post(url, json=about_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("POST /api/admin/content/about/update", True)
                    
                    # Verify immediate update by getting content again
                    get_url = f"{API_BASE_URL}/admin/content/about"
                    async with self.session.get(get_url) as get_response:
                        if get_response.status == 200:
                            get_result = await get_response.json()
                            stored_content = get_result.get("content", [])
                            if "Test line 1" in stored_content and "Test line 2" in stored_content:
                                self.log_test_result("About content updates immediately", True)
                            else:
                                self.log_test_result("About content updates immediately", False, f"Content not updated: {stored_content}")
                        else:
                            self.log_test_result("About content verification", False, "Could not verify update")
                else:
                    self.log_test_result("POST /api/admin/content/about/update", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("POST /api/admin/content/about/update", False, str(e))

    async def test_about_tags_management(self):
        """Test About Tags Management"""
        print("\n🏷️ Testing About Tags Management...")
        
        # Test 1: GET About Tags (public)
        try:
            url = f"{API_BASE_URL}/admin/content/tags"
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET /api/admin/content/tags", True)
                    
                    # Verify response structure
                    if isinstance(result, dict) and "tags" in result:
                        self.log_test_result("Tags response structure", True)
                        tags = result["tags"]
                        if isinstance(tags, list):
                            self.log_test_result("Tags is array", True)
                        else:
                            self.log_test_result("Tags is array", False, f"Tags is {type(tags)}")
                    else:
                        self.log_test_result("Tags response structure", False, "Missing tags field")
                else:
                    self.log_test_result("GET /api/admin/content/tags", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET /api/admin/content/tags", False, str(e))
        
        # Test 2: POST Tags Update (requires auth)
        if not self.admin_token:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        tags_data = {
            "tags": [{"icon": "🎮", "text": "Test Tag"}]
        }
        
        try:
            url = f"{API_BASE_URL}/admin/content/tags/update"
            async with self.session.post(url, json=tags_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("POST /api/admin/content/tags/update", True)
                    
                    # Verify tags stored
                    get_url = f"{API_BASE_URL}/admin/content/tags"
                    async with self.session.get(get_url) as get_response:
                        if get_response.status == 200:
                            get_result = await get_response.json()
                            stored_tags = get_result.get("tags", [])
                            if any(tag.get("text") == "Test Tag" for tag in stored_tags):
                                self.log_test_result("Tags stored successfully", True)
                            else:
                                self.log_test_result("Tags stored successfully", False, f"Test tag not found in: {stored_tags}")
                        else:
                            self.log_test_result("Tags verification", False, "Could not verify tags")
                else:
                    self.log_test_result("POST /api/admin/content/tags/update", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("POST /api/admin/content/tags/update", False, str(e))

    async def test_schedule_management(self):
        """Test Schedule Management"""
        print("\n📅 Testing Schedule Management...")
        
        if not self.admin_token:
            self.log_test_result("Schedule Management", False, "No admin token", critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: GET Schedule (requires auth)
        try:
            url = f"{API_BASE_URL}/admin/schedule"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET /api/admin/schedule", True)
                    
                    # Verify response structure
                    if isinstance(result, list):
                        self.log_test_result("Schedule response structure", True)
                    else:
                        self.log_test_result("Schedule response structure", False, f"Expected list, got {type(result)}")
                else:
                    self.log_test_result("GET /api/admin/schedule", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET /api/admin/schedule", False, str(e))
        
        # Test 2: POST Schedule Update
        schedule_data = {
            "day": "MON",
            "time": "20:00",
            "game": "TEST"
        }
        
        try:
            url = f"{API_BASE_URL}/admin/schedule/update"
            async with self.session.post(url, json=schedule_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("POST /api/admin/schedule/update", True)
                    
                    # Verify schedule operations by getting schedule again
                    get_url = f"{API_BASE_URL}/admin/schedule"
                    async with self.session.get(get_url, headers=headers) as get_response:
                        if get_response.status == 200:
                            get_result = await get_response.json()
                            # Check if MON entry exists in the list
                            mon_found = any(item.get("day") == "MON" and item.get("game") == "TEST" for item in get_result)
                            if mon_found:
                                self.log_test_result("Schedule update verification", True)
                            else:
                                self.log_test_result("Schedule update verification", False, f"MON not updated in: {get_result}")
                        else:
                            self.log_test_result("Schedule update verification", False, "Could not verify update")
                else:
                    self.log_test_result("POST /api/admin/schedule/update", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("POST /api/admin/schedule/update", False, str(e))
        
        # Test 3: DELETE Schedule Entry
        try:
            url = f"{API_BASE_URL}/admin/schedule/MON"
            async with self.session.delete(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("DELETE /api/admin/schedule/MON", True)
                    
                    # Verify deletion by checking schedule again
                    get_url = f"{API_BASE_URL}/admin/schedule"
                    async with self.session.get(get_url, headers=headers) as get_response:
                        if get_response.status == 200:
                            get_result = await get_response.json()
                            # Check if MON entry is removed or inactive
                            mon_active = any(item.get("day") == "MON" and item.get("is_active", True) for item in get_result)
                            if not mon_active:
                                self.log_test_result("Schedule deletion verification", True)
                            else:
                                self.log_test_result("Schedule deletion verification", False, f"MON still active in: {get_result}")
                        else:
                            self.log_test_result("Schedule deletion verification", False, "Could not verify deletion")
                else:
                    self.log_test_result("DELETE /api/admin/schedule/MON", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("DELETE /api/admin/schedule/MON", False, str(e))

    async def test_live_status_control(self):
        """Test Live Status Control"""
        print("\n🔴 Testing Live Status Control...")
        
        if not self.admin_token:
            self.log_test_result("Live Status Control", False, "No admin token", critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: GET Live Status via dashboard stats
        try:
            url = f"{API_BASE_URL}/admin/dashboard/stats"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET live status via dashboard stats", True)
                    
                    # Verify response structure
                    if isinstance(result, dict) and "channel_stats" in result:
                        self.log_test_result("Live status response structure", True)
                    else:
                        self.log_test_result("Live status response structure", False, f"Expected dict with channel_stats, got {type(result)}")
                else:
                    self.log_test_result("GET live status via dashboard stats", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET live status via dashboard stats", False, str(e))
        
        # Test 2: POST Live Toggle (requires proper data structure)
        live_toggle_data = {
            "is_live": True,
            "current_viewers": "5",
            "live_game": "TEST GAME"
        }
        
        try:
            url = f"{API_BASE_URL}/admin/live/toggle"
            async with self.session.post(url, json=live_toggle_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("POST /api/admin/live/toggle", True)
                    
                    # Verify live status toggle works
                    if isinstance(result, dict) and "is_live" in result:
                        self.log_test_result("Live status toggle response", True)
                    else:
                        self.log_test_result("Live status toggle response", False, "Missing is_live field")
                else:
                    self.log_test_result("POST /api/admin/live/toggle", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("POST /api/admin/live/toggle", False, str(e))

    async def test_dashboard_stats(self):
        """Test Dashboard Stats"""
        print("\n📊 Testing Dashboard Stats...")
        
        if not self.admin_token:
            self.log_test_result("Dashboard Stats", False, "No admin token", critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test: GET Dashboard Real-time Stats (requires auth)
        try:
            url = f"{API_BASE_URL}/admin/dashboard/real-time-stats"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET /api/admin/dashboard/real-time-stats", True)
                    
                    # Verify all stats returned
                    if isinstance(result, dict):
                        expected_fields = ["channel_stats", "last_updated"]
                        missing_fields = [field for field in expected_fields if field not in result]
                        if not missing_fields:
                            self.log_test_result("Dashboard stats - all fields present", True)
                        else:
                            self.log_test_result("Dashboard stats - all fields present", False, f"Missing: {missing_fields}")
                    else:
                        self.log_test_result("Dashboard stats response structure", False, f"Expected dict, got {type(result)}")
                else:
                    self.log_test_result("GET /api/admin/dashboard/real-time-stats", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET /api/admin/dashboard/real-time-stats", False, str(e))

    async def test_chat_system(self):
        """Test Chat System (NEW)"""
        print("\n💬 Testing Chat System (NEW)...")
        
        # Chat endpoints are mounted directly without /api prefix
        CHAT_BASE_URL = f"{BACKEND_URL}/chat"
        
        # Test 1: GET Chat Messages
        try:
            url = f"{CHAT_BASE_URL}/messages"
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET /chat/messages", True)
                    
                    # Verify response structure (should have messages field)
                    if isinstance(result, dict) and "messages" in result:
                        self.log_test_result("Chat messages response structure", True)
                    else:
                        self.log_test_result("Chat messages response structure", False, f"Expected dict with messages, got {type(result)}")
                else:
                    self.log_test_result("GET /chat/messages", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET /chat/messages", False, str(e))
        
        # Test 2: POST Chat Send (correct data structure)
        chat_data = {
            "user": "TestUser",
            "user_id": "test_user_123",
            "level": 1,
            "text": "Test message from admin panel testing"
        }
        
        try:
            url = f"{CHAT_BASE_URL}/send"
            async with self.session.post(url, json=chat_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("POST /chat/send", True)
                    
                    # Verify response
                    if isinstance(result, dict) and result.get("success"):
                        self.log_test_result("Chat send response validation", True)
                    else:
                        self.log_test_result("Chat send response validation", False, "Missing success field")
                else:
                    self.log_test_result("POST /chat/send", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("POST /chat/send", False, str(e))
        
        # Test 3: GET Chat Online Count
        try:
            url = f"{CHAT_BASE_URL}/online-count"
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test_result("GET /chat/online-count", True)
                    
                    # Verify response structure
                    if isinstance(result, dict) and "count" in result:
                        self.log_test_result("Chat online count response structure", True)
                    else:
                        self.log_test_result("Chat online count response structure", False, "Missing count field")
                else:
                    self.log_test_result("GET /chat/online-count", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("GET /chat/online-count", False, str(e))

    async def run_all_tests(self):
        """Run all admin panel tests"""
        print("🎮 REMZA019 Gaming Admin Panel - Comprehensive Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Admin authentication is required for most tests
            if await self.admin_login():
                # Run all test suites
                await self.test_featured_video_management()
                await self.test_about_content_management()
                await self.test_about_tags_management()
                await self.test_schedule_management()
                await self.test_live_status_control()
                await self.test_dashboard_stats()
                await self.test_chat_system()
            else:
                print("❌ CRITICAL: Admin authentication failed - cannot proceed with admin tests")
        
        finally:
            await self.cleanup()
        
        # Print final results
        self.print_results()

    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 REMZA019 GAMING ADMIN PANEL TEST RESULTS")
        print("=" * 60)
        
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if self.results['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.results['critical_failures'])}):")
            for failure in self.results['critical_failures']:
                print(f"   ❌ {failure}")
        
        if success_rate >= 90:
            print(f"\n✅ EXCELLENT: Admin panel is {success_rate:.1f}% functional!")
        elif success_rate >= 75:
            print(f"\n⚠️  GOOD: Admin panel is {success_rate:.1f}% functional with minor issues")
        else:
            print(f"\n❌ NEEDS ATTENTION: Admin panel is only {success_rate:.1f}% functional")
        
        # Featured Video specific status
        featured_video_tests = [log for log in self.results['error_logs'] if 'featured-video' in log.lower()]
        if not featured_video_tests:
            print("\n🎬 FEATURED VIDEO: 100% FUNCTIONAL ✅")
        else:
            print(f"\n🎬 FEATURED VIDEO: ISSUES DETECTED ❌")
            for issue in featured_video_tests:
                print(f"   - {issue}")

async def main():
    """Main test execution"""
    tester = REMZA019AdminTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())