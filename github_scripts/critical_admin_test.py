#!/usr/bin/env python3
"""
CRITICAL ADMIN PANEL TESTING - 10/10 Quality Check
Testing the KEY FEATURE (admin panel) of REMZA019 Gaming platform
Focus on the 2 critical bugs that were reportedly fixed:
1. About section update not working
2. Viewer menu issues
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

# Get backend URL from frontend .env
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
print(f"🎯 Testing Admin Panel at: {API_BASE_URL}")

class CriticalAdminTester:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_failures': [],
            'admin_token': None
        }
        self.session = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up critical admin testing environment...")
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name, passed, details="", is_critical=False):
        """Log test result with critical failure tracking"""
        self.results['total_tests'] += 1
        if passed:
            self.results['passed_tests'] += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   ℹ️  {details}")
        else:
            self.results['failed_tests'] += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   🔍 {details}")
            if is_critical:
                self.results['critical_failures'].append(f"{test_name}: {details}")

    async def admin_login(self):
        """Login as admin to get authentication token"""
        print("\n🔐 ADMIN LOGIN - CRITICAL AUTHENTICATION TEST")
        
        login_data = {
            "username": "admin",
            "password": "remza019admin"
        }
        
        try:
            url = f"{API_BASE_URL}/admin/auth/login"
            async with self.session.post(url, json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('token'):
                        self.results['admin_token'] = data['token']
                        self.log_test_result("Admin login successful", True, f"Token received: {data['token'][:20]}...")
                        return True
                    else:
                        self.log_test_result("Admin login response validation", False, f"Invalid response: {data}", is_critical=True)
                        return False
                else:
                    response_text = await response.text()
                    self.log_test_result("Admin login", False, f"HTTP {response.status}: {response_text}", is_critical=True)
                    return False
        except Exception as e:
            self.log_test_result("Admin login", False, f"Exception: {str(e)}", is_critical=True)
            return False

    async def test_about_section_update(self):
        """TEST 1: Admin About Section Update (MOST IMPORTANT!)"""
        print("\n🎯 TEST 1: ADMIN ABOUT SECTION UPDATE - MOST CRITICAL TEST")
        
        if not self.results['admin_token']:
            self.log_test_result("About update test", False, "No admin token available", is_critical=True)
            return
        
        # First, get current about content
        headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
        
        try:
            # GET current about content
            url = f"{API_BASE_URL}/admin/content/about"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    current_data = await response.json()
                    self.log_test_result("Get About content", True, f"Current content retrieved")
                else:
                    response_text = await response.text()
                    self.log_test_result("Get About content", False, f"HTTP {response.status}: {response_text}", is_critical=True)
                    return
        except Exception as e:
            self.log_test_result("Get About content", False, f"Exception: {str(e)}", is_critical=True)
            return
        
        # Update About content with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_content = [
            f"Test Line 1 - Updated at {timestamp}",
            "Test Line 2 - This is new content",
            "Test Line 3 - Must appear on main page"
        ]
        
        update_data = {"content": new_content}
        
        try:
            # POST update about content
            url = f"{API_BASE_URL}/admin/content/about/update"
            async with self.session.post(url, json=update_data, headers=headers) as response:
                if response.status == 200:
                    update_result = await response.json()
                    if update_result.get('success'):
                        self.log_test_result("About content update", True, f"Content updated successfully")
                        
                        # Verify update by getting content again
                        await asyncio.sleep(1)  # Wait for update to propagate
                        
                        url = f"{API_BASE_URL}/admin/content/about"
                        async with self.session.get(url, headers=headers) as response:
                            if response.status == 200:
                                updated_data = await response.json()
                                if updated_data.get('content') == new_content:
                                    self.log_test_result("About content persistence", True, "NEW content verified in database", is_critical=False)
                                else:
                                    self.log_test_result("About content persistence", False, f"Content mismatch. Expected: {new_content}, Got: {updated_data.get('content')}", is_critical=True)
                            else:
                                response_text = await response.text()
                                self.log_test_result("About content verification", False, f"HTTP {response.status}: {response_text}", is_critical=True)
                    else:
                        self.log_test_result("About content update", False, f"Update failed: {update_result}", is_critical=True)
                else:
                    response_text = await response.text()
                    self.log_test_result("About content update", False, f"HTTP {response.status}: {response_text}", is_critical=True)
        except Exception as e:
            self.log_test_result("About content update", False, f"Exception: {str(e)}", is_critical=True)

    async def test_live_status_toggle(self):
        """TEST 2: Live Status Toggle"""
        print("\n🔴 TEST 2: LIVE STATUS TOGGLE")
        
        if not self.results['admin_token']:
            self.log_test_result("Live status toggle test", False, "No admin token available", is_critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
        
        try:
            toggle_data = {
                "is_live": True,
                "current_viewers": "10",
                "live_game": "FORTNITE TEST"
            }
            url = f"{API_BASE_URL}/admin/live/toggle"
            async with self.session.post(url, json=toggle_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        self.log_test_result("Live status toggle", True, f"Status: {data.get('is_live')}")
                        
                        # Check if WebSocket/SSE broadcast was sent
                        if 'broadcast_sent' in data:
                            self.log_test_result("Live status broadcast", True, "Real-time update sent")
                        else:
                            self.log_test_result("Live status broadcast", False, "No broadcast confirmation")
                    else:
                        self.log_test_result("Live status toggle", False, f"Toggle failed: {data}")
                else:
                    response_text = await response.text()
                    self.log_test_result("Live status toggle", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test_result("Live status toggle", False, f"Exception: {str(e)}")

    async def test_schedule_management(self):
        """TEST 3: Schedule Management"""
        print("\n📅 TEST 3: SCHEDULE MANAGEMENT")
        
        if not self.results['admin_token']:
            self.log_test_result("Schedule management test", False, "No admin token available", is_critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
        
        # Test GET schedule
        try:
            url = f"{API_BASE_URL}/admin/schedule"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    schedule_data = await response.json()
                    self.log_test_result("Get schedule", True, f"Retrieved {len(schedule_data)} schedule entries")
                else:
                    response_text = await response.text()
                    self.log_test_result("Get schedule", False, f"HTTP {response.status}: {response_text}")
                    return
        except Exception as e:
            self.log_test_result("Get schedule", False, f"Exception: {str(e)}")
            return
        
        # Test ADD schedule entry
        new_schedule = {
            "day": "TEST_DAY",
            "time": "20:00",
            "game": "FORTNITE TEST",
            "description": "Test schedule entry"
        }
        
        try:
            url = f"{API_BASE_URL}/admin/schedule/update"
            async with self.session.post(url, json=new_schedule, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        self.log_test_result("Add schedule entry", True, "Schedule entry added")
                        
                        # Test DELETE schedule entry
                        url = f"{API_BASE_URL}/admin/schedule/TEST_DAY"
                        async with self.session.delete(url, headers=headers) as response:
                            if response.status == 200:
                                delete_data = await response.json()
                                if delete_data.get('success'):
                                    self.log_test_result("Delete schedule entry", True, "Schedule entry deleted")
                                else:
                                    self.log_test_result("Delete schedule entry", False, f"Delete failed: {delete_data}")
                            else:
                                response_text = await response.text()
                                self.log_test_result("Delete schedule entry", False, f"HTTP {response.status}: {response_text}")
                    else:
                        self.log_test_result("Add schedule entry", False, f"Add failed: {data}")
                else:
                    response_text = await response.text()
                    self.log_test_result("Add schedule entry", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test_result("Schedule management", False, f"Exception: {str(e)}")

    async def test_channel_stats_update(self):
        """TEST 4: Channel Stats Update"""
        print("\n📊 TEST 4: CHANNEL STATS UPDATE")
        
        if not self.results['admin_token']:
            self.log_test_result("Channel stats update test", False, "No admin token available", is_critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
        
        stats_data = {
            "subscriber_count": "250",
            "video_count": "25",
            "view_count": "7500"
        }
        
        try:
            url = f"{API_BASE_URL}/admin/stats/update"
            async with self.session.post(url, json=stats_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        self.log_test_result("Channel stats update", True, f"Stats updated: {stats_data}")
                    else:
                        self.log_test_result("Channel stats update", False, f"Update failed: {data}")
                else:
                    response_text = await response.text()
                    self.log_test_result("Channel stats update", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test_result("Channel stats update", False, f"Exception: {str(e)}")

    async def test_dashboard_data(self):
        """TEST 5: Dashboard Data"""
        print("\n📈 TEST 5: DASHBOARD DATA")
        
        if not self.results['admin_token']:
            self.log_test_result("Dashboard data test", False, "No admin token available", is_critical=True)
            return
        
        headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
        
        try:
            url = f"{API_BASE_URL}/admin/dashboard/stats"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    
                    # Validate dashboard data structure
                    required_fields = ['channel_stats', 'recent_streams_count', 'scheduled_streams_count']
                    missing_fields = [field for field in required_fields if field not in dashboard_data]
                    
                    if not missing_fields:
                        self.log_test_result("Dashboard data structure", True, "All required fields present")
                        
                        # Validate channel stats
                        channel_stats = dashboard_data.get('channel_stats', {})
                        if 'subscriber_count' in channel_stats and 'video_count' in channel_stats:
                            self.log_test_result("Dashboard stats data", True, f"Subscriber count: {channel_stats.get('subscriber_count')}, Videos: {channel_stats.get('video_count')}")
                        else:
                            self.log_test_result("Dashboard stats data", False, "Missing subscriber or video count")
                    else:
                        self.log_test_result("Dashboard data structure", False, f"Missing fields: {missing_fields}")
                else:
                    response_text = await response.text()
                    self.log_test_result("Dashboard data", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test_result("Dashboard data", False, f"Exception: {str(e)}")

    async def test_viewer_system(self):
        """TEST 6: Viewer System (if time permits)"""
        print("\n👥 TEST 6: VIEWER SYSTEM")
        
        # Test viewer registration
        viewer_data = {
            "username": f"test_viewer",
            "email": f"test_{int(datetime.now().timestamp())}@remza019.com"
        }
        
        try:
            url = f"{API_BASE_URL}/viewer/register"
            async with self.session.post(url, json=viewer_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('viewer'):
                        viewer_id = data['viewer'].get('id')
                        self.log_test_result("Viewer registration", True, f"Viewer ID: {viewer_id}")
                        
                        # Test viewer profile retrieval
                        if viewer_id:
                            url = f"{API_BASE_URL}/viewer/profile/{viewer_id}"
                            async with self.session.get(url) as response:
                                if response.status == 200:
                                    profile_data = await response.json()
                                    self.log_test_result("Viewer profile retrieval", True, f"Profile retrieved for {viewer_id}")
                                else:
                                    self.log_test_result("Viewer profile retrieval", False, f"HTTP {response.status}")
                    else:
                        self.log_test_result("Viewer registration", False, f"Registration failed: {data}")
                else:
                    response_text = await response.text()
                    self.log_test_result("Viewer registration", False, f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test_result("Viewer system", False, f"Exception: {str(e)}")

    async def test_sse_event_fix(self):
        """Test SSE Event Type Fix (content_update → about_content_update)"""
        print("\n🔄 TESTING SSE EVENT TYPE FIX")
        
        # This test would require monitoring SSE events during about content update
        # For now, we'll test that the SSE endpoint is accessible
        try:
            test_client_id = "test_admin_client"
            url = f"{API_BASE_URL}/sse/{test_client_id}"
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'text/event-stream' in content_type:
                            self.log_test_result("SSE endpoint accessible", True, "Event stream ready for about_content_update events")
                        else:
                            self.log_test_result("SSE endpoint content type", False, f"Wrong content type: {content_type}")
                    else:
                        self.log_test_result("SSE endpoint accessible", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("SSE endpoint test", False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all critical admin panel tests"""
        print("🚀 STARTING CRITICAL ADMIN PANEL TESTING")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Login first
            login_success = await self.admin_login()
            
            if login_success:
                # Run all critical tests
                await self.test_about_section_update()  # MOST IMPORTANT
                await self.test_live_status_toggle()
                await self.test_schedule_management()
                await self.test_channel_stats_update()
                await self.test_dashboard_data()
                await self.test_viewer_system()
                await self.test_sse_event_fix()
            else:
                print("❌ CRITICAL FAILURE: Cannot proceed without admin authentication")
                
        finally:
            await self.cleanup()
        
        # Print final results
        print("\n" + "=" * 60)
        print("🎯 CRITICAL ADMIN PANEL TEST RESULTS")
        print("=" * 60)
        
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 TOTAL TESTS: {total}")
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.results['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.results['critical_failures'])}):")
            for failure in self.results['critical_failures']:
                print(f"   ❌ {failure}")
        
        # Determine overall result
        if success_rate >= 90 and not self.results['critical_failures']:
            print(f"\n🏆 RESULT: ADMIN PANEL IS COMPETITIVE WITH BIGGER FIRMS!")
            print("✅ 10/10 Quality achieved - Ready for production")
        elif success_rate >= 80:
            print(f"\n⚠️  RESULT: ADMIN PANEL NEEDS MINOR FIXES")
            print("🔧 8-9/10 Quality - Close to competitive level")
        else:
            print(f"\n❌ RESULT: ADMIN PANEL HAS MAJOR ISSUES")
            print("🚨 Below 8/10 Quality - Not competitive with bigger firms")
        
        return success_rate >= 90 and not self.results['critical_failures']

async def main():
    """Main test execution"""
    tester = CriticalAdminTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 ADMIN PANEL TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n💥 ADMIN PANEL TESTING FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())