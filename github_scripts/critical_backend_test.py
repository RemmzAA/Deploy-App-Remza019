#!/usr/bin/env python3
"""
Critical Backend Testing Suite for REMZA019 Gaming Multi-Language Complete
Focus on 4 critical areas as requested in review:
1. About Content API (Critical - user reported issue)
2. Channel Stats API (Critical - statistics update)  
3. Live Status API (Important)
4. Admin Authentication
"""

import asyncio
import aiohttp
import json
import os
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
    exit(1)

API_BASE_URL = f"{BACKEND_URL}/api"
print(f"🎯 Testing Backend URL: {API_BASE_URL}")

class CriticalBackendTester:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_issues': [],
            'admin_token': None
        }
        self.session = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up critical test environment...")
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name, passed, details="", is_critical=False):
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
            if is_critical:
                self.results['critical_issues'].append(f"{test_name}: {details}")

    async def test_api_endpoint(self, endpoint, method="GET", data=None, headers=None, expected_status=200):
        """Test individual API endpoint"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if headers is None:
                headers = {"Content-Type": "application/json"}
            
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data
                        except:
                            response_text = await response.text()
                            return True, response_text
                    else:
                        response_text = await response.text()
                        return False, f"HTTP {status}: {response_text}"
            elif method == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data
                        except:
                            response_text = await response.text()
                            return True, response_text
                    else:
                        response_text = await response.text()
                        return False, f"HTTP {status}: {response_text}"
        except Exception as e:
            return False, str(e)

    async def test_admin_authentication(self):
        """Test Admin Authentication - CRITICAL AREA 4"""
        print("\n🔐 CRITICAL TEST 4: Admin Authentication")
        
        # Test admin login with provided credentials - CORRECT ENDPOINT
        login_data = {
            "username": "admin",
            "password": "remza019admin"
        }
        
        success, result = await self.test_api_endpoint("/admin/auth/login", method="POST", data=login_data)
        self.log_test_result("Admin login with credentials (admin/remza019admin)", success, 
                           "" if success else str(result), is_critical=True)
        
        if success and isinstance(result, dict):
            # Check for token or success indicator
            if result.get('success') or result.get('token') or result.get('access_token'):
                self.log_test_result("Admin login response validation", True)
                # Store token if available
                if result.get('token'):
                    self.results['admin_token'] = result['token']
                elif result.get('access_token'):
                    self.results['admin_token'] = result['access_token']
                return True
            else:
                self.log_test_result("Admin login response validation", False, 
                                   f"No success/token in response: {result}", is_critical=True)
                return False
        else:
            self.log_test_result("Admin login response format", False, 
                               "Invalid response format", is_critical=True)
            return False

    async def test_about_content_api(self):
        """Test About Content API - CRITICAL AREA 1 (User reported issue)"""
        print("\n📝 CRITICAL TEST 1: About Content API (User Reported Issue)")
        
        # Test GET /api/admin/content/about (public endpoint)
        success, result = await self.test_api_endpoint("/admin/content/about")
        self.log_test_result("GET /api/admin/content/about - returns content array", success, 
                           "" if success else str(result), is_critical=True)
        
        if success:
            # Validate response structure
            if isinstance(result, (list, dict)):
                self.log_test_result("About content response structure valid", True)
                
                # Check if it's an array or has content
                if isinstance(result, list) or (isinstance(result, dict) and result.get('content')):
                    self.log_test_result("About content contains data", True)
                else:
                    self.log_test_result("About content contains data", False, 
                                       "No content found in response", is_critical=True)
            else:
                self.log_test_result("About content response structure valid", False, 
                                   f"Expected array/object, got {type(result)}", is_critical=True)
        
        # Test POST /api/admin/content/about/update (requires auth)
        update_data = {
            "content": ["Updated about content for testing - REMZA019 Gaming", "Test content line 2"]
        }
        
        # Use auth headers if token available
        headers = {"Content-Type": "application/json"}
        if self.results.get('admin_token'):
            headers["Authorization"] = f"Bearer {self.results['admin_token']}"
        
        success, result = await self.test_api_endpoint("/admin/content/about/update", 
                                                     method="POST", data=update_data, headers=headers)
        self.log_test_result("POST /api/admin/content/about/update - updates work", success, 
                           "" if success else str(result), is_critical=True)
        
        if success and isinstance(result, dict):
            if result.get('success') or result.get('message'):
                self.log_test_result("About content update response validation", True)
            else:
                self.log_test_result("About content update response validation", False, 
                                   f"No success indicator: {result}", is_critical=True)

    async def test_channel_stats_api(self):
        """Test Channel Stats API - CRITICAL AREA 2"""
        print("\n📊 CRITICAL TEST 2: Channel Stats API (Statistics Update)")
        
        # Use auth headers if token available
        headers = {"Content-Type": "application/json"}
        if self.results.get('admin_token'):
            headers["Authorization"] = f"Bearer {self.results['admin_token']}"
        
        # Test GET /api/admin/dashboard/stats - CORRECT ENDPOINT
        success, result = await self.test_api_endpoint("/admin/dashboard/stats", headers=headers)
        self.log_test_result("GET /api/admin/dashboard/stats - stats return correctly", success, 
                           "" if success else str(result), is_critical=True)
        
        if success and isinstance(result, dict):
            # Check for expected dashboard stats
            expected_fields = ['subscriber_count', 'video_count', 'view_count', 'total_views', 'channel_stats']
            found_fields = []
            for field in expected_fields:
                if field in result or any(field in str(v) for v in result.values() if isinstance(v, dict)):
                    found_fields.append(field)
            
            if found_fields:
                self.log_test_result("Dashboard stats structure validation", True, 
                                   f"Found fields: {found_fields}")
            else:
                self.log_test_result("Dashboard stats structure validation", False, 
                                   f"Missing expected stats fields: {expected_fields}", is_critical=True)
        
        # Test POST /api/admin/stats/update - CORRECT ENDPOINT
        stats_update_data = {
            "subscriber_count": "150",
            "video_count": "25", 
            "total_views": "5000"
        }
        
        success, result = await self.test_api_endpoint("/admin/stats/update", 
                                                     method="POST", data=stats_update_data, headers=headers)
        self.log_test_result("POST /api/admin/stats/update - stats update works", success, 
                           "" if success else str(result), is_critical=True)

    async def test_live_status_api(self):
        """Test Live Status API - CRITICAL AREA 3"""
        print("\n🔴 CRITICAL TEST 3: Live Status API")
        
        # Test GET /api/notifications/live-status (public endpoint)
        success, result = await self.test_api_endpoint("/notifications/live-status")
        self.log_test_result("GET /api/notifications/live-status - live status returns", success, 
                           "" if success else str(result), is_critical=True)
        
        if success and isinstance(result, dict):
            # Check for live status fields
            expected_fields = ['is_live', 'status', 'live', 'streaming']
            found_fields = []
            for field in expected_fields:
                if field in result:
                    found_fields.append(field)
            
            if found_fields:
                self.log_test_result("Live status response structure", True, 
                                   f"Found status fields: {found_fields}")
            else:
                self.log_test_result("Live status response structure", False, 
                                   f"No status fields found in: {result}", is_critical=True)
        
        # Test POST /api/admin/live/toggle (requires auth)
        toggle_data = {
            "is_live": True,
            "live_game": "FORTNITE",
            "current_viewers": "0"
        }
        
        # Use auth headers if token available
        headers = {"Content-Type": "application/json"}
        if self.results.get('admin_token'):
            headers["Authorization"] = f"Bearer {self.results['admin_token']}"
        
        success, result = await self.test_api_endpoint("/admin/live/toggle", 
                                                     method="POST", data=toggle_data, headers=headers)
        self.log_test_result("POST /api/admin/live/toggle - admin can toggle live status", success, 
                           "" if success else str(result), is_critical=True)

    async def test_additional_critical_endpoints(self):
        """Test additional endpoints that might be critical"""
        print("\n🔍 Additional Critical Endpoint Tests")
        
        # Test basic server health
        success, result = await self.test_api_endpoint("/")
        self.log_test_result("API root endpoint health check", success, 
                           "" if success else str(result))
        
        # Test admin endpoints that might be related
        admin_endpoints = [
            "/admin/dashboard/real-time-stats",
            "/admin/youtube/sync-status",
            "/admin/schedule",
            "/admin/streams"
        ]
        
        # Use auth headers if token available
        headers = {"Content-Type": "application/json"}
        if self.results.get('admin_token'):
            headers["Authorization"] = f"Bearer {self.results['admin_token']}"
        
        for endpoint in admin_endpoints:
            success, result = await self.test_api_endpoint(endpoint, headers=headers)
            endpoint_name = endpoint.replace("/admin/", "").replace("/", " ")
            self.log_test_result(f"Admin {endpoint_name} endpoint", success, 
                               "" if success else str(result))

    async def run_all_tests(self):
        """Run all critical tests"""
        print("🎯 REMZA019 Gaming Multi-Language Complete - Critical Backend Verification")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run tests in order of criticality
            await self.test_admin_authentication()
            await self.test_about_content_api()
            await self.test_channel_stats_api()
            await self.test_live_status_api()
            await self.test_additional_critical_endpoints()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 CRITICAL BACKEND VERIFICATION SUMMARY")
        print("=" * 80)
        
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.results['critical_issues'])}):")
            for issue in self.results['critical_issues']:
                print(f"   • {issue}")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND")
        
        print("\n" + "=" * 80)
        
        return success_rate >= 75.0  # 75% success rate threshold

async def main():
    """Main test execution"""
    tester = CriticalBackendTester()
    success = await tester.run_all_tests()
    
    if success:
        print("🎉 CRITICAL BACKEND VERIFICATION PASSED")
        return 0
    else:
        print("💥 CRITICAL BACKEND VERIFICATION FAILED")
        return 1

if __name__ == "__main__":
    import sys
    result = asyncio.run(main())
    sys.exit(result)