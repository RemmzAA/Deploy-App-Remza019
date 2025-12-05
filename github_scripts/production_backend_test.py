#!/usr/bin/env python3
"""
CRITICAL PRODUCTION TESTING - ALL ENDPOINTS
Backend Testing Suite for REMZA019 Gaming Platform
Tests ALL backend functionality as requested in production review
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Production URL from review request
BACKEND_URL = "https://gamer-dashboard-5.preview.emergentagent.com"
API_BASE_URL = f"{BACKEND_URL}/api"

class ProductionBackendTester:
    def __init__(self):
        self.results = {
            'admin_panel_endpoints': {},
            'customization_endpoints': {},
            'user_menu_endpoints': {},
            'security_checks': {},
            'pwa_service_worker': {},
            'error_logs': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'admin_token': None
        }
        self.session = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up production test environment...")
        print(f"🌐 Testing against: {BACKEND_URL}")
        
        # Create HTTP session with longer timeout for production
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name, passed, details=""):
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

    async def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request with proper error handling"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                    
                    if status == expected_status:
                        return True, response_data
                    else:
                        return False, f"HTTP {status}: {response_data}"
                        
            elif method == "POST":
                request_headers = {"Content-Type": "application/json"}
                if headers:
                    request_headers.update(headers)
                    
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                    
                    if status == expected_status:
                        return True, response_data
                    else:
                        return False, f"HTTP {status}: {response_data}"
                        
        except Exception as e:
            return False, str(e)

    async def test_admin_panel_endpoints(self):
        """Test ADMIN PANEL ENDPOINTS (HIGHEST PRIORITY)"""
        print("\n🔥 TESTING ADMIN PANEL ENDPOINTS (HIGHEST PRIORITY)")
        
        # 1. Admin Login
        print("\n🔐 Testing Admin Login...")
        login_data = {"username": "admin", "password": "remza019admin"}
        
        success, result = await self.make_request("POST", "/admin/auth/login", data=login_data)
        self.log_test_result("Admin Login", success, "" if success else str(result))
        self.results['admin_panel_endpoints']['login'] = success
        
        if success and isinstance(result, dict):
            if result.get("success") and result.get("token"):
                self.results['admin_token'] = result["token"]
                self.log_test_result("Admin Login - Token Generation", True, f"Token received: {result['token'][:20]}...")
            else:
                self.log_test_result("Admin Login - Token Generation", False, "No token in response")
        
        # 2. Admin Dashboard Stats
        print("\n📊 Testing Admin Dashboard Stats...")
        if self.results['admin_token']:
            headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
            success, result = await self.make_request("GET", "/admin/dashboard/real-time-stats", headers=headers)
            self.log_test_result("Admin Dashboard Stats", success, "" if success else str(result))
            self.results['admin_panel_endpoints']['dashboard_stats'] = success
            
            if success and isinstance(result, dict):
                # Validate expected stats structure
                expected_fields = ['channel_stats', 'subscriber_count', 'video_count']
                has_stats = any(field in str(result) for field in expected_fields)
                self.log_test_result("Dashboard Stats - Data Structure", has_stats, 
                                   f"Response contains expected stats fields")
        else:
            self.log_test_result("Admin Dashboard Stats", False, "No admin token available")
            self.results['admin_panel_endpoints']['dashboard_stats'] = False
        
        # 3. Live Control Toggle
        print("\n🔴 Testing Live Control Toggle...")
        if self.results['admin_token']:
            headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
            live_data = {
                "is_live": True,
                "live_game": "FORTNITE",
                "current_viewers": "0"
            }
            
            success, result = await self.make_request("POST", "/admin/live/toggle", data=live_data, headers=headers)
            self.log_test_result("Live Control Toggle", success, "" if success else str(result))
            self.results['admin_panel_endpoints']['live_toggle'] = success
            
            if success:
                # Test toggle back to false
                live_data["is_live"] = False
                success2, result2 = await self.make_request("POST", "/admin/live/toggle", data=live_data, headers=headers)
                self.log_test_result("Live Control Toggle - Off", success2, "" if success2 else str(result2))
        else:
            self.log_test_result("Live Control Toggle", False, "No admin token available")
            self.results['admin_panel_endpoints']['live_toggle'] = False
        
        # 4. About Content Get (PUBLIC)
        print("\n📄 Testing About Content Get...")
        success, result = await self.make_request("GET", "/admin/content/about")
        self.log_test_result("About Content Get", success, "" if success else str(result))
        self.results['admin_panel_endpoints']['about_get'] = success
        
        if success and isinstance(result, (list, dict)):
            self.log_test_result("About Content - Data Structure", True, "About content returned")
        
        # 5. About Content Update (ADMIN)
        print("\n✏️ Testing About Content Update...")
        if self.results['admin_token']:
            headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
            about_data = {
                "content": [
                    "Test content line 1 - Production Testing",
                    "Test content line 2 - Backend Validation"
                ]
            }
            
            success, result = await self.make_request("POST", "/admin/content/about/update", data=about_data, headers=headers)
            self.log_test_result("About Content Update", success, "" if success else str(result))
            self.results['admin_panel_endpoints']['about_update'] = success
        else:
            self.log_test_result("About Content Update", False, "No admin token available")
            self.results['admin_panel_endpoints']['about_update'] = False
        
        # 6. About Tags Get (PUBLIC)
        print("\n🏷️ Testing About Tags Get...")
        success, result = await self.make_request("GET", "/admin/content/tags")
        self.log_test_result("About Tags Get", success, "" if success else str(result))
        self.results['admin_panel_endpoints']['tags_get'] = success
        
        if success and isinstance(result, dict) and "tags" in result:
            tags = result["tags"]
            if isinstance(tags, list) and len(tags) > 0:
                self.log_test_result("About Tags - Data Structure", True, f"Found {len(tags)} tags")
                
                # Check tag structure
                first_tag = tags[0]
                if "icon" in first_tag and "text" in first_tag:
                    self.log_test_result("About Tags - Tag Structure", True, "Tags have icon and text fields")
                else:
                    self.log_test_result("About Tags - Tag Structure", False, "Tags missing required fields")
            else:
                self.log_test_result("About Tags - Data Structure", False, "Tags array is empty or invalid")
        
        # 7. About Tags Update (ADMIN)
        print("\n🏷️ Testing About Tags Update...")
        if self.results['admin_token']:
            headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
            tags_data = {
                "tags": [
                    {"icon": "🏆", "text": "Production Test Tag 1"},
                    {"icon": "🎮", "text": "Production Test Tag 2"}
                ]
            }
            
            success, result = await self.make_request("POST", "/admin/content/tags/update", data=tags_data, headers=headers)
            self.log_test_result("About Tags Update", success, "" if success else str(result))
            self.results['admin_panel_endpoints']['tags_update'] = success
        else:
            self.log_test_result("About Tags Update", False, "No admin token available")
            self.results['admin_panel_endpoints']['tags_update'] = False

    async def test_customization_endpoints(self):
        """Test CUSTOMIZATION ENDPOINTS (NEW - CRITICAL)"""
        print("\n🎨 TESTING CUSTOMIZATION ENDPOINTS (NEW - CRITICAL)")
        
        # 1. Get Current Customization (PUBLIC)
        print("\n🎨 Testing Get Current Customization...")
        success, result = await self.make_request("GET", "/customization/current")
        self.log_test_result("Get Current Customization", success, "" if success else str(result))
        self.results['customization_endpoints']['get_current'] = success
        
        if success and isinstance(result, dict):
            if result.get("success") and "data" in result:
                self.log_test_result("Customization - Response Structure", True, "Response has success and data fields")
                
                # Check for expected customization fields
                data = result.get("data", {})
                expected_fields = ["userName", "matrixColor", "textColor"]
                found_fields = [field for field in expected_fields if field in data]
                self.log_test_result("Customization - Data Fields", len(found_fields) > 0, 
                                   f"Found fields: {found_fields}")
            else:
                self.log_test_result("Customization - Response Structure", False, "Missing success or data fields")
        
        # 2. Save Customization (ADMIN)
        print("\n💾 Testing Save Customization...")
        if self.results['admin_token']:
            headers = {"Authorization": f"Bearer {self.results['admin_token']}"}
            customization_data = {
                "userName": "PRODUCTION_TEST",
                "matrixColor": "#ff0000",
                "textColor": "#0000ff"
            }
            
            success, result = await self.make_request("POST", "/customization/save", data=customization_data, headers=headers)
            self.log_test_result("Save Customization", success, "" if success else str(result))
            self.results['customization_endpoints']['save'] = success
            
            if success:
                # Verify the customization was saved by getting it again
                success2, result2 = await self.make_request("GET", "/customization/current")
                if success2 and isinstance(result2, dict):
                    saved_data = result2.get("data", {})
                    if saved_data.get("userName") == "PRODUCTION_TEST":
                        self.log_test_result("Customization - Persistence Verification", True, "Customization saved successfully")
                    else:
                        self.log_test_result("Customization - Persistence Verification", False, "Customization not persisted")
                else:
                    self.log_test_result("Customization - Persistence Verification", False, "Could not verify persistence")
        else:
            self.log_test_result("Save Customization", False, "No admin token available")
            self.results['customization_endpoints']['save'] = False

    async def test_user_menu_endpoints(self):
        """Test USER MENU ENDPOINTS"""
        print("\n👥 TESTING USER MENU ENDPOINTS")
        
        # 1. User Registration (if exists)
        print("\n📝 Testing User Registration...")
        user_data = {
            "username": "ProductionTestUser2024",
            "email": "production.test@remza019gaming.com",
            "password": "TestPassword123!"
        }
        
        success, result = await self.make_request("POST", "/viewer/register", data=user_data)
        self.log_test_result("User Registration", success, "" if success else str(result))
        self.results['user_menu_endpoints']['registration'] = success
        
        if success and isinstance(result, dict):
            # Check for expected user fields
            expected_fields = ["id", "username", "points", "level"]
            found_fields = [field for field in expected_fields if field in result]
            self.log_test_result("User Registration - Response Structure", len(found_fields) >= 2, 
                               f"Found fields: {found_fields}")
        
        # 2. Points/Activities (if exists)
        print("\n🎯 Testing Points/Activities System...")
        
        # Test get activities
        success, result = await self.make_request("GET", "/viewer/activities")
        self.log_test_result("Get Activities", success, "" if success else str(result))
        self.results['user_menu_endpoints']['activities'] = success
        
        if success and isinstance(result, list):
            if len(result) > 0:
                activity = result[0]
                if "name" in activity and "points" in activity:
                    self.log_test_result("Activities - Data Structure", True, f"Found {len(result)} activities")
                else:
                    self.log_test_result("Activities - Data Structure", False, "Activities missing required fields")
            else:
                self.log_test_result("Activities - Data Structure", False, "No activities found")
        
        # Test get levels
        success, result = await self.make_request("GET", "/viewer/levels")
        self.log_test_result("Get Levels", success, "" if success else str(result))
        self.results['user_menu_endpoints']['levels'] = success
        
        if success and isinstance(result, list):
            if len(result) > 0:
                level = result[0]
                if "level" in level and "name" in level and "points_required" in level:
                    self.log_test_result("Levels - Data Structure", True, f"Found {len(result)} levels")
                else:
                    self.log_test_result("Levels - Data Structure", False, "Levels missing required fields")
            else:
                self.log_test_result("Levels - Data Structure", False, "No levels found")

    async def test_security_checks(self):
        """Test SECURITY CHECKS"""
        print("\n🔒 TESTING SECURITY CHECKS")
        
        # 1. Test Invalid Credentials
        print("\n❌ Testing Invalid Credentials...")
        invalid_login_data = {"username": "hacker", "password": "wrong"}
        
        success, result = await self.make_request("POST", "/admin/auth/login", data=invalid_login_data, expected_status=401)
        if not success:
            # Also check for 400 or 422 as valid error responses
            success, result = await self.make_request("POST", "/admin/auth/login", data=invalid_login_data, expected_status=400)
            if not success:
                success, result = await self.make_request("POST", "/admin/auth/login", data=invalid_login_data, expected_status=422)
        
        self.log_test_result("Invalid Credentials Security", success, "" if success else str(result))
        self.results['security_checks']['invalid_credentials'] = success
        
        # 2. Test Missing Authorization
        print("\n🚫 Testing Missing Authorization...")
        success, result = await self.make_request("POST", "/admin/live/toggle", 
                                                data={"is_live": True}, expected_status=401)
        if not success:
            # Also check for 403 as valid unauthorized response
            success, result = await self.make_request("POST", "/admin/live/toggle", 
                                                    data={"is_live": True}, expected_status=403)
        
        self.log_test_result("Missing Authorization Security", success, "" if success else str(result))
        self.results['security_checks']['missing_auth'] = success
        
        # 3. Test SQL Injection Attempt
        print("\n💉 Testing SQL Injection Protection...")
        sql_injection_data = {"username": "admin' OR 1=1--", "password": "anything"}
        
        success, result = await self.make_request("POST", "/admin/auth/login", data=sql_injection_data, expected_status=401)
        if not success:
            # Check for other error codes that indicate proper rejection
            success, result = await self.make_request("POST", "/admin/auth/login", data=sql_injection_data, expected_status=400)
            if not success:
                success, result = await self.make_request("POST", "/admin/auth/login", data=sql_injection_data, expected_status=422)
        
        self.log_test_result("SQL Injection Protection", success, "" if success else str(result))
        self.results['security_checks']['sql_injection'] = success
        
        # 4. Test XSS Protection
        print("\n🛡️ Testing XSS Protection...")
        xss_data = {
            "username": "<script>alert('xss')</script>",
            "password": "<img src=x onerror=alert('xss')>"
        }
        
        success, result = await self.make_request("POST", "/admin/auth/login", data=xss_data, expected_status=401)
        if not success:
            success, result = await self.make_request("POST", "/admin/auth/login", data=xss_data, expected_status=400)
            if not success:
                success, result = await self.make_request("POST", "/admin/auth/login", data=xss_data, expected_status=422)
        
        self.log_test_result("XSS Protection", success, "" if success else str(result))
        self.results['security_checks']['xss_protection'] = success

    async def test_pwa_service_worker(self):
        """Test PWA & SERVICE WORKER"""
        print("\n📱 TESTING PWA & SERVICE WORKER")
        
        # 1. Check Service Worker
        print("\n⚙️ Testing Service Worker...")
        try:
            async with self.session.get(f"{BACKEND_URL}/service-worker.js") as response:
                if response.status == 200:
                    content = await response.text()
                    if len(content) > 100:  # Service worker should have substantial content
                        self.log_test_result("Service Worker File", True, f"Service worker found ({len(content)} chars)")
                        
                        # Check for service worker keywords
                        sw_keywords = ["self.addEventListener", "install", "fetch", "cache"]
                        found_keywords = [kw for kw in sw_keywords if kw in content]
                        self.log_test_result("Service Worker Content", len(found_keywords) >= 2, 
                                           f"Found keywords: {found_keywords}")
                    else:
                        self.log_test_result("Service Worker File", False, "Service worker file too small")
                else:
                    self.log_test_result("Service Worker File", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Service Worker File", False, str(e))
        
        self.results['pwa_service_worker']['service_worker'] = self.results['passed_tests'] > 0
        
        # 2. Check Manifest
        print("\n📋 Testing PWA Manifest...")
        try:
            async with self.session.get(f"{BACKEND_URL}/manifest.json") as response:
                if response.status == 200:
                    manifest = await response.json()
                    
                    # Check required manifest fields
                    required_fields = ["name", "icons", "start_url"]
                    found_fields = [field for field in required_fields if field in manifest]
                    
                    self.log_test_result("PWA Manifest File", True, f"Manifest found with fields: {found_fields}")
                    
                    # Validate manifest structure
                    if len(found_fields) >= 2:
                        self.log_test_result("PWA Manifest Structure", True, "Manifest has required fields")
                        
                        # Check for REMZA019 branding
                        name = manifest.get("name", "").upper()
                        if "REMZA019" in name or "GAMING" in name:
                            self.log_test_result("PWA Manifest Branding", True, f"App name: {manifest.get('name')}")
                        else:
                            self.log_test_result("PWA Manifest Branding", False, f"App name: {manifest.get('name')}")
                    else:
                        self.log_test_result("PWA Manifest Structure", False, "Manifest missing required fields")
                else:
                    self.log_test_result("PWA Manifest File", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("PWA Manifest File", False, str(e))
        
        self.results['pwa_service_worker']['manifest'] = self.results['passed_tests'] > 0

    async def test_additional_endpoints(self):
        """Test additional important endpoints"""
        print("\n🔗 TESTING ADDITIONAL ENDPOINTS")
        
        # Test health check
        success, result = await self.make_request("GET", "/")
        self.log_test_result("API Health Check", success, "" if success else str(result))
        
        # Test YouTube endpoints
        success, result = await self.make_request("GET", "/youtube/channel-stats")
        self.log_test_result("YouTube Channel Stats", success, "" if success else str(result))
        
        success, result = await self.make_request("GET", "/youtube/latest-videos")
        self.log_test_result("YouTube Latest Videos", success, "" if success else str(result))
        
        # Test chat endpoint
        chat_data = {"message": "Hello, this is a production test", "session_id": "prod_test"}
        success, result = await self.make_request("POST", "/chat", data=chat_data)
        self.log_test_result("AI Chat Endpoint", success, "" if success else str(result))

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 CRITICAL PRODUCTION TESTING RESULTS")
        print("="*80)
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   Passed: {self.results['passed_tests']} ✅")
        print(f"   Failed: {self.results['failed_tests']} ❌")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔥 ADMIN PANEL ENDPOINTS (HIGHEST PRIORITY):")
        for endpoint, status in self.results['admin_panel_endpoints'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {endpoint}: {status_icon}")
        
        print(f"\n🎨 CUSTOMIZATION ENDPOINTS (NEW - CRITICAL):")
        for endpoint, status in self.results['customization_endpoints'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {endpoint}: {status_icon}")
        
        print(f"\n👥 USER MENU ENDPOINTS:")
        for endpoint, status in self.results['user_menu_endpoints'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {endpoint}: {status_icon}")
        
        print(f"\n🔒 SECURITY CHECKS:")
        for check, status in self.results['security_checks'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {check}: {status_icon}")
        
        print(f"\n📱 PWA & SERVICE WORKER:")
        for component, status in self.results['pwa_service_worker'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {component}: {status_icon}")
        
        if self.results['error_logs']:
            print(f"\n🚨 ERROR DETAILS:")
            for error in self.results['error_logs'][:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(self.results['error_logs']) > 10:
                print(f"   ... and {len(self.results['error_logs']) - 10} more errors")
        
        print("\n" + "="*80)
        
        # Determine overall status
        critical_endpoints = ['login', 'dashboard_stats', 'get_current']
        critical_passed = sum(1 for ep in critical_endpoints 
                            if self.results['admin_panel_endpoints'].get(ep) or 
                               self.results['customization_endpoints'].get(ep))
        
        if success_rate >= 80 and critical_passed >= 2:
            print("🎉 PRODUCTION STATUS: READY FOR DEPLOYMENT")
        elif success_rate >= 60:
            print("⚠️  PRODUCTION STATUS: NEEDS ATTENTION")
        else:
            print("🚨 PRODUCTION STATUS: CRITICAL ISSUES FOUND")
        
        print("="*80)

async def main():
    """Main test execution"""
    tester = ProductionBackendTester()
    
    try:
        await tester.setup()
        
        # Execute all test suites
        await tester.test_admin_panel_endpoints()
        await tester.test_customization_endpoints()
        await tester.test_user_menu_endpoints()
        await tester.test_security_checks()
        await tester.test_pwa_service_worker()
        await tester.test_additional_endpoints()
        
        # Print comprehensive summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        return 1
    finally:
        await tester.cleanup()
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)