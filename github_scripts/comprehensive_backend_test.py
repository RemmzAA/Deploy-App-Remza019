#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for REMZA019 Gaming Platform
Tests all fixed features and new APIs as requested in the review
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
backend_env_path = Path("/app/backend/.env")
frontend_env_path = Path("/app/frontend/.env")

if backend_env_path.exists():
    load_dotenv(backend_env_path)

# Get URLs from environment
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'remza019_gaming')

# Read frontend .env for backend URL
BACKEND_URL = None
if frontend_env_path.exists():
    with open(frontend_env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break

if not BACKEND_URL:
    print("❌ ERROR: Could not find REACT_APP_BACKEND_URL in frontend/.env")
    print("🔧 Using fallback URL: http://localhost:8001")
    BACKEND_URL = "http://localhost:8001"

API_BASE_URL = f"{BACKEND_URL}/api"

class ComprehensiveBackendTester:
    def __init__(self):
        self.results = {
            'server_status': False,
            'mongodb_connection': False,
            'environment_config': False,
            'api_endpoints': {},
            'error_logs': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_failures': [],
            'priority_results': {}
        }
        self.session = None
        self.mongo_client = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Setup MongoDB client
        try:
            self.mongo_client = AsyncIOMotorClient(MONGO_URL)
        except Exception as e:
            self.results['error_logs'].append(f"MongoDB client setup failed: {str(e)}")

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()

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
                self.results['error_logs'].append(f"{test_name}: {details}")
            
            if is_critical:
                self.results['critical_failures'].append(f"{test_name}: {details}")

    async def test_api_endpoint(self, endpoint, method="GET", data=None, expected_status=200, headers=None):
        """Test individual API endpoint"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        response_data = await response.json()
                        return True, response_data
                    else:
                        return False, f"HTTP {status}"
            elif method == "POST":
                request_headers = {"Content-Type": "application/json"}
                if headers:
                    request_headers.update(headers)
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    status = response.status
                    if status == expected_status:
                        response_data = await response.json()
                        return True, response_data
                    else:
                        return False, f"HTTP {status}"
            elif method == "PUT":
                request_headers = {"Content-Type": "application/json"}
                if headers:
                    request_headers.update(headers)
                async with self.session.put(url, json=data, headers=request_headers) as response:
                    status = response.status
                    if status == expected_status:
                        response_data = await response.json()
                        return True, response_data
                    else:
                        return False, f"HTTP {status}"
        except Exception as e:
            return False, str(e)

    async def test_theme_system_apis(self):
        """Test Theme System APIs (FIXED) - Priority from review request"""
        print("\n🎨 Testing Theme System APIs (FIXED) - HIGH PRIORITY...")
        
        theme_results = {}
        
        # Test GET /api/themes/list
        success, result = await self.test_api_endpoint("/themes/list")
        self.log_test_result("GET /api/themes/list", success, "" if success else str(result), is_critical=True)
        self.results['api_endpoints']['/themes/list'] = success
        theme_results['list'] = success
        
        if success:
            # Validate themes list structure (it returns a dict with themes array)
            if isinstance(result, dict) and 'themes' in result:
                themes = result['themes']
                if isinstance(themes, list):
                    self.log_test_result("Themes list returns correct structure", True)
                    if themes:
                        theme = themes[0]
                        required_fields = ['id', 'name', 'description']
                        has_required_fields = all(field in theme for field in required_fields)
                        self.log_test_result("Theme objects have required fields", has_required_fields)
                else:
                    self.log_test_result("Themes list returns correct structure", False, f"themes field is {type(themes)}")
            else:
                self.log_test_result("Themes list returns correct structure", False, f"Got {type(result)}, missing 'themes' field")
        
        # Test GET /api/themes/current
        success, result = await self.test_api_endpoint("/themes/current")
        self.log_test_result("GET /api/themes/current", success, "" if success else str(result), is_critical=True)
        self.results['api_endpoints']['/themes/current'] = success
        theme_results['current'] = success
        
        if success:
            # Validate current theme structure
            if isinstance(result, dict) and 'theme' in result:
                self.log_test_result("Current theme response structure", True)
            else:
                self.log_test_result("Current theme response structure", False, "Missing 'theme' field")
        
        # Test POST /api/themes/apply (with flexible schema)
        theme_data = {
            "theme_id": "matrix_green",
            "colors": {
                "primary": "#00ff41",
                "secondary": "#008f11",
                "background": "#000000"
            }
        }
        
        success, result = await self.test_api_endpoint("/themes/apply", method="POST", data=theme_data)
        self.log_test_result("POST /api/themes/apply (flexible schema)", success, "" if success else str(result), is_critical=True)
        self.results['api_endpoints']['/themes/apply'] = success
        theme_results['apply'] = success
        
        self.results['priority_results']['theme_system'] = theme_results

    async def test_viewer_registration_points(self):
        """Test Viewer Registration & Points System (FIXED) - Priority from review request"""
        print("\n👥 Testing Viewer Registration & Points System (FIXED) - HIGH PRIORITY...")
        
        viewer_results = {}
        
        # Test POST /api/viewer/register with correct user_id field
        import time
        unique_id = int(time.time())
        viewer_data = {
            "username": f"TestGamer{unique_id}",
            "email": f"testgamer{unique_id}@remza019gaming.com"
        }
        
        success, result = await self.test_api_endpoint("/viewer/register", method="POST", data=viewer_data)
        self.log_test_result("POST /api/viewer/register", success, "" if success else str(result), is_critical=True)
        self.results['api_endpoints']['/viewer/register'] = success
        viewer_results['register'] = success
        
        if success:
            # Test points award system with correct user_id field
            if isinstance(result, dict) and 'viewer' in result:
                viewer = result['viewer']
                # Check for user_id field (not _id)
                has_user_id = 'user_id' in viewer and 'id' in viewer
                self.log_test_result("Viewer registration returns user_id field", has_user_id)
                viewer_results['user_id_field'] = has_user_id
                
                # Check for points field
                has_points = 'points' in viewer
                self.log_test_result("Viewer registration includes points", has_points)
                viewer_results['points_field'] = has_points
                
                if has_points:
                    points = viewer.get('points', 0)
                    points_awarded = points >= 10
                    self.log_test_result("Registration bonus points awarded", points_awarded, 
                                       f"Points awarded: {points}")
                    viewer_results['points_awarded'] = points_awarded
            else:
                self.log_test_result("Viewer registration response structure", False, "Missing 'viewer' field")
        
        self.results['priority_results']['viewer_system'] = viewer_results

    async def test_new_feature_apis(self):
        """Test New Feature APIs (NOW LOADED) - Priority from review request"""
        print("\n🆕 Testing New Feature APIs (NOW LOADED) - HIGH PRIORITY...")
        
        new_api_results = {}
        
        # List of new APIs to test (corrected endpoints from OpenAPI)
        new_apis = [
            ("/clips/trending", "Clips Trending API"),
            ("/clips/highlights/official", "Clips Highlights Official API"),
            ("/auto-highlights/analyze", "Auto Highlights Analyze API"),
            ("/multi-streamer/stats", "Multi-Streamer Stats API"),
            ("/multi-streamer/streamers/available", "Multi-Streamer Available API"),
            ("/referrals/activity-bonus", "Referrals Activity Bonus API"),
            ("/subscriptions/plans", "Subscription Plans API"),
            ("/tournaments/active", "Tournament Active API"),
            ("/twitch/channel", "Twitch Channel API"),
            ("/social/friends", "Social Friends API")
        ]
        
        for endpoint, description in new_apis:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result(description, success, "" if success else str(result), is_critical=True)
            self.results['api_endpoints'][endpoint] = success
            new_api_results[endpoint] = success
            
            # Additional validation for specific endpoints
            if success:
                if endpoint == "/analytics/stats" and isinstance(result, dict):
                    has_stats = any(key in result for key in ['views', 'subscribers', 'engagement'])
                    self.log_test_result(f"{description} - data structure", has_stats)
                
                elif endpoint == "/clips/list" and isinstance(result, list):
                    self.log_test_result(f"{description} - returns array", True)
                
                elif endpoint == "/merchandise/products" and isinstance(result, list):
                    self.log_test_result(f"{description} - returns products array", True)
                
                elif endpoint == "/subscription/plans" and isinstance(result, list):
                    self.log_test_result(f"{description} - returns plans array", True)
                
                elif endpoint == "/tournament/list" and isinstance(result, list):
                    self.log_test_result(f"{description} - returns tournaments array", True)
        
        self.results['priority_results']['new_feature_apis'] = new_api_results

    async def test_admin_functionality(self):
        """Test Admin Functionality - Priority from review request"""
        print("\n⚙️ Testing Admin Functionality - HIGH PRIORITY...")
        
        admin_results = {}
        
        # First login as admin
        login_data = {"username": "admin", "password": "remza019admin"}
        login_success, login_result = await self.test_api_endpoint("/admin/auth/login", method="POST", data=login_data)
        self.log_test_result("Admin login", login_success, "" if login_success else str(login_result), is_critical=True)
        admin_results['login'] = login_success
        
        if login_success and isinstance(login_result, dict) and login_result.get("token"):
            token = login_result["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test admin endpoints
            admin_endpoints = [
                ("/admin/dashboard/stats", "Admin Dashboard Stats"),
                ("/admin/content/about", "Admin Content Management"),
                ("/admin/schedule", "Admin Schedule Management"),
                ("/admin/live/toggle", "Admin Live Toggle")
            ]
            
            for endpoint, description in admin_endpoints:
                # Test GET endpoints
                url = f"{API_BASE_URL}{endpoint}"
                try:
                    async with self.session.get(url, headers=headers) as response:
                        success = response.status == 200
                        if success:
                            result = await response.json()
                        else:
                            result = f"HTTP {response.status}"
                        
                        self.log_test_result(description, success, "" if success else str(result), is_critical=True)
                        self.results['api_endpoints'][endpoint] = success
                        admin_results[endpoint] = success
                        
                except Exception as e:
                    self.log_test_result(description, False, str(e), is_critical=True)
                    self.results['api_endpoints'][endpoint] = False
                    admin_results[endpoint] = False
        else:
            self.log_test_result("Admin functionality testing", False, "Could not authenticate admin", is_critical=True)
            admin_results['authentication_failed'] = True
        
        self.results['priority_results']['admin_functionality'] = admin_results

    async def test_core_gaming_features(self):
        """Test Core Gaming Features - Priority from review request"""
        print("\n🎮 Testing Core Gaming Features - HIGH PRIORITY...")
        
        gaming_results = {}
        
        # Test core gaming endpoints
        gaming_endpoints = [
            ("/leaderboard/top", "Leaderboard System"),
            ("/polls/active", "Polls System"),
            ("/predictions/current", "Predictions System"),
            ("/chat/messages", "Chat System"),
            ("/donations/packages", "Donations System")
        ]
        
        for endpoint, description in gaming_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result(description, success, "" if success else str(result), is_critical=True)
            self.results['api_endpoints'][endpoint] = success
            gaming_results[endpoint] = success
            
            # Additional validation for specific endpoints
            if success:
                if endpoint == "/leaderboard/top" and isinstance(result, list):
                    self.log_test_result(f"{description} - returns leaderboard array", True)
                
                elif endpoint == "/polls/active" and isinstance(result, list):
                    self.log_test_result(f"{description} - returns polls array", True)
                
                elif endpoint == "/donations/packages" and isinstance(result, list):
                    if result:
                        package = result[0]
                        has_required_fields = all(field in package for field in ['name', 'amount', 'description'])
                        self.log_test_result(f"{description} - package structure", has_required_fields)
        
        self.results['priority_results']['core_gaming_features'] = gaming_results

    async def test_server_status(self):
        """Test if FastAPI server is running and accessible"""
        print("\n🚀 Testing FastAPI Server Status...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    expected_message = "019 Digital Solutions API"
                    if data.get('message') == expected_message:
                        self.log_test_result("Server health check", True)
                        self.log_test_result("API root endpoint response", True)
                        self.results['server_status'] = True
                    else:
                        self.log_test_result("API root endpoint response", False, f"Unexpected response: {data}")
                else:
                    self.log_test_result("Server health check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Server health check", False, str(e))

    async def test_mongodb_connection(self):
        """Test MongoDB database connection"""
        print("\n🗄️ Testing MongoDB Connection...")
        
        try:
            # Test connection
            await self.mongo_client.admin.command('ping')
            self.log_test_result("MongoDB ping", True)
            
            # Test database access
            db = self.mongo_client[DB_NAME]
            collections = await db.list_collection_names()
            self.log_test_result("Database access", True)
            
            # Test write operation
            test_doc = {"test": "backend_test", "timestamp": datetime.utcnow()}
            result = await db.test_collection.insert_one(test_doc)
            if result.inserted_id:
                self.log_test_result("Database write operation", True)
                
                # Clean up test document
                await db.test_collection.delete_one({"_id": result.inserted_id})
                self.log_test_result("Database cleanup", True)
            else:
                self.log_test_result("Database write operation", False)
            
            self.results['mongodb_connection'] = True
            
        except Exception as e:
            self.log_test_result("MongoDB connection", False, str(e))

    async def run_comprehensive_tests(self):
        """Run comprehensive backend tests focusing on review priorities"""
        print("🚀 Starting COMPREHENSIVE BACKEND TESTING - ALL FIXES APPLIED")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"🔗 API Base URL: {API_BASE_URL}")
        print(f"🗄️ MongoDB URL: {MONGO_URL}")
        print(f"📊 Database Name: {DB_NAME}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Core infrastructure tests
            await self.test_server_status()
            await self.test_mongodb_connection()
            
            # PRIORITY TESTS FROM REVIEW REQUEST
            print("\n🎯 TESTING PRIORITY FIXES FROM REVIEW REQUEST...")
            await self.test_theme_system_apis()
            await self.test_viewer_registration_points()
            await self.test_new_feature_apis()
            await self.test_admin_functionality()
            await self.test_core_gaming_features()
            
        finally:
            await self.cleanup()
        
        # Print final results
        self.print_comprehensive_results()
        return self.results

    def print_comprehensive_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE BACKEND TESTING RESULTS")
        print("=" * 80)
        
        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Priority results summary
        print(f"\n🎯 PRIORITY FEATURES STATUS:")
        
        if 'theme_system' in self.results['priority_results']:
            theme_results = self.results['priority_results']['theme_system']
            theme_success = all(theme_results.values())
            print(f"   🎨 Theme System: {'✅ SUCCESS' if theme_success else '❌ FAILED'}")
        
        if 'viewer_system' in self.results['priority_results']:
            viewer_results = self.results['priority_results']['viewer_system']
            viewer_success = viewer_results.get('register', False)
            print(f"   👥 Viewer Registration: {'✅ SUCCESS' if viewer_success else '❌ FAILED'}")
        
        if 'new_feature_apis' in self.results['priority_results']:
            new_api_results = self.results['priority_results']['new_feature_apis']
            new_api_success = sum(new_api_results.values()) / len(new_api_results) if new_api_results else 0
            print(f"   🆕 New Feature APIs: {'✅ SUCCESS' if new_api_success >= 0.8 else '❌ FAILED'} ({new_api_success*100:.0f}%)")
        
        if 'admin_functionality' in self.results['priority_results']:
            admin_results = self.results['priority_results']['admin_functionality']
            admin_success = admin_results.get('login', False)
            print(f"   ⚙️ Admin Functionality: {'✅ SUCCESS' if admin_success else '❌ FAILED'}")
        
        if 'core_gaming_features' in self.results['priority_results']:
            gaming_results = self.results['priority_results']['core_gaming_features']
            gaming_success = sum(gaming_results.values()) / len(gaming_results) if gaming_results else 0
            print(f"   🎮 Core Gaming Features: {'✅ SUCCESS' if gaming_success >= 0.8 else '❌ FAILED'} ({gaming_success*100:.0f}%)")
        
        # Critical failures
        if self.results['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in self.results['critical_failures']:
                print(f"   • {failure}")
        
        # Component status
        print(f"\n🔧 Component Status:")
        print(f"   Server Status: {'✅' if self.results['server_status'] else '❌'}")
        print(f"   MongoDB Connection: {'✅' if self.results['mongodb_connection'] else '❌'}")
        
        working_endpoints = sum(1 for status in self.results['api_endpoints'].values() if status)
        total_endpoints = len(self.results['api_endpoints'])
        print(f"   API Endpoints: {working_endpoints}/{total_endpoints} working")
        
        print("\n" + "=" * 80)

async def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    results = await tester.run_comprehensive_tests()
    
    # Return exit code based on critical failures
    if results['critical_failures']:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())