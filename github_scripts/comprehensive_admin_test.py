#!/usr/bin/env python3
"""
COMPREHENSIVE ADMIN PANEL & FEATURES TESTING
Testing all admin functionality, theme system, viewer system, and new features
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
    sys.exit(1)

API_BASE_URL = f"{BACKEND_URL}/api"

class ComprehensiveAdminTester:
    def __init__(self):
        self.results = {
            'admin_auth': {},
            'theme_system': {},
            'viewer_system': {},
            'customization': {},
            'youtube_content': {},
            'schedule': {},
            'content_management': {},
            'new_features': {},
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_logs': []
        }
        self.session = None
        self.admin_token = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up comprehensive admin test environment...")
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    def log_test_result(self, category, test_name, passed, details=""):
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
        
        if category not in self.results:
            self.results[category] = {}
        self.results[category][test_name] = passed

    async def test_api_endpoint(self, endpoint, method="GET", data=None, headers=None, expected_status=200):
        """Test individual API endpoint"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            request_headers = {"Content-Type": "application/json"}
            if headers:
                request_headers.update(headers)
            
            if method == "GET":
                async with self.session.get(url, headers=request_headers) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data
                        except:
                            response_text = await response.text()
                            return True, response_text
                    else:
                        return False, f"HTTP {status}"
            elif method == "POST":
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data
                        except:
                            response_text = await response.text()
                            return True, response_text
                    else:
                        return False, f"HTTP {status}"
            elif method == "DELETE":
                async with self.session.delete(url, headers=request_headers) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data
                        except:
                            response_text = await response.text()
                            return True, response_text
                    else:
                        return False, f"HTTP {status}"
        except Exception as e:
            return False, str(e)

    async def test_admin_authentication(self):
        """Test admin authentication system"""
        print("\n🔐 Testing Admin Authentication System...")
        
        # Test admin login
        login_data = {"username": "admin", "password": "remza019admin"}
        success, result = await self.test_api_endpoint("/admin/auth/login", method="POST", data=login_data)
        self.log_test_result('admin_auth', "Admin login with correct credentials", success, "" if success else str(result))
        
        if success and isinstance(result, dict) and result.get("token"):
            self.admin_token = result["token"]
            self.log_test_result('admin_auth', "JWT token generation", True, f"Token received: {self.admin_token[:20]}...")
            
            # Test token validation
            auth_headers = {"Authorization": f"Bearer {self.admin_token}"}
            success2, result2 = await self.test_api_endpoint("/admin/dashboard/real-time-stats", headers=auth_headers)
            self.log_test_result('admin_auth', "Token validation", success2, "" if success2 else str(result2))
        else:
            self.log_test_result('admin_auth', "JWT token generation", False, "No token in response")
        
        # Test invalid credentials
        invalid_login = {"username": "admin", "password": "wrongpassword"}
        success, result = await self.test_api_endpoint("/admin/auth/login", method="POST", data=invalid_login, expected_status=401)
        self.log_test_result('admin_auth', "Invalid credentials rejection", success, "" if success else str(result))

    async def test_theme_system(self):
        """Test theme system endpoints"""
        print("\n🎨 Testing Theme System...")
        
        # Test list all themes
        success, result = await self.test_api_endpoint("/themes/list")
        self.log_test_result('theme_system', "GET /api/themes/list", success, "" if success else str(result))
        
        if success:
            if isinstance(result, dict) and "themes" in result:
                themes = result["themes"]
                self.log_test_result('theme_system', "Themes list structure", isinstance(themes, list), f"Got {type(themes)}")
                if themes:
                    theme_names = [theme.get("name") for theme in themes]
                    self.log_test_result('theme_system', "Theme objects have names", all(name for name in theme_names))
            else:
                self.log_test_result('theme_system', "Themes list structure", False, "Missing 'themes' field")
        
        # Test get current theme
        success, result = await self.test_api_endpoint("/themes/current")
        self.log_test_result('theme_system', "GET /api/themes/current", success, "" if success else str(result))
        
        if success and isinstance(result, dict):
            required_fields = ["name", "colors", "fonts"]
            has_fields = all(field in result for field in required_fields)
            self.log_test_result('theme_system', "Current theme structure", has_fields, f"Missing: {[f for f in required_fields if f not in result]}")
        
        # Test apply theme (requires auth)
        if self.admin_token:
            auth_headers = {"Authorization": f"Bearer {self.admin_token}"}
            apply_data = {"theme_name": "dark"}
            success, result = await self.test_api_endpoint("/themes/apply", method="POST", data=apply_data, headers=auth_headers)
            self.log_test_result('theme_system', "POST /api/themes/apply (authenticated)", success, "" if success else str(result))
            
            # Test customize theme
            customize_data = {
                "colors": {
                    "primary": "#10b981",
                    "secondary": "#059669",
                    "accent": "#34d399"
                },
                "fonts": {
                    "heading": "Inter",
                    "body": "Inter"
                }
            }
            success, result = await self.test_api_endpoint("/themes/customize", method="POST", data=customize_data, headers=auth_headers)
            self.log_test_result('theme_system', "POST /api/themes/customize (authenticated)", success, "" if success else str(result))
            
            # Test reset theme
            success, result = await self.test_api_endpoint("/themes/reset", method="POST", headers=auth_headers)
            self.log_test_result('theme_system', "POST /api/themes/reset (authenticated)", success, "" if success else str(result))
        else:
            self.log_test_result('theme_system', "Theme system authentication tests", False, "No admin token available")

    async def test_viewer_system(self):
        """Test viewer system endpoints"""
        print("\n👥 Testing Viewer System...")
        
        # Test viewer registration
        viewer_data = {
            "username": "TestGamer2024",
            "email": "testgamer@example.com",
            "password": "testpassword123"
        }
        success, result = await self.test_api_endpoint("/viewer/register", method="POST", data=viewer_data)
        self.log_test_result('viewer_system', "POST /api/viewer/register", success, "" if success else str(result))
        
        if success and isinstance(result, dict):
            required_fields = ["id", "username", "points", "level"]
            has_fields = all(field in result for field in required_fields)
            self.log_test_result('viewer_system', "Viewer registration response structure", has_fields)
            
            # Check initial points (should be 10 for registration bonus)
            if "points" in result:
                initial_points = result["points"]
                self.log_test_result('viewer_system', "Registration bonus points", initial_points == 10, f"Got {initial_points} points")
        
        # Test get viewer levels
        success, result = await self.test_api_endpoint("/viewer/levels")
        self.log_test_result('viewer_system', "GET /api/viewer/levels", success, "" if success else str(result))
        
        if success and isinstance(result, list):
            self.log_test_result('viewer_system', "Levels system structure", len(result) >= 6, f"Got {len(result)} levels")
            if result:
                level_fields = ["level", "name", "points_required", "features"]
                first_level = result[0]
                has_level_fields = all(field in first_level for field in level_fields)
                self.log_test_result('viewer_system', "Level objects structure", has_level_fields)
        
        # Test get activities
        success, result = await self.test_api_endpoint("/viewer/activities")
        self.log_test_result('viewer_system', "GET /api/viewer/activities", success, "" if success else str(result))
        
        if success and isinstance(result, list):
            activity_types = [activity.get("type") for activity in result]
            expected_activities = ["stream_view", "chat_message", "like_video", "share_stream", "subscribe"]
            has_expected = any(activity in activity_types for activity in expected_activities)
            self.log_test_result('viewer_system', "Activity types available", has_expected, f"Found: {activity_types}")
        
        # Test get leaderboard
        success, result = await self.test_api_endpoint("/viewer/leaderboard")
        self.log_test_result('viewer_system', "GET /api/viewer/leaderboard", success, "" if success else str(result))
        
        if success and isinstance(result, list):
            self.log_test_result('viewer_system', "Leaderboard structure", True, f"Got {len(result)} entries")

    async def test_customization_system(self):
        """Test customization system endpoints"""
        print("\n🎛️ Testing Customization System...")
        
        # Test get current customization
        success, result = await self.test_api_endpoint("/customization/current")
        self.log_test_result('customization', "GET /api/customization/current", success, "" if success else str(result))
        
        if success and isinstance(result, dict):
            customization_fields = ["site_name", "matrix_color", "text_color", "logo_url", "social_links"]
            has_fields = any(field in result for field in customization_fields)
            self.log_test_result('customization', "Customization structure", has_fields, f"Available fields: {list(result.keys())}")
        
        # Test save customization (requires auth)
        if self.admin_token:
            auth_headers = {"Authorization": f"Bearer {self.admin_token}"}
            customization_data = {
                "site_name": "REMZA019 Gaming Test",
                "matrix_color": "#00ff00",
                "text_color": "#ffffff",
                "youtube_channel_id": "UCTestChannel",
                "discord_link": "https://discord.gg/test",
                "social_links": {
                    "twitter": "https://twitter.com/remza019",
                    "instagram": "https://instagram.com/remza019",
                    "twitch": "https://twitch.tv/remza019",
                    "tiktok": "https://tiktok.com/@remza019"
                }
            }
            success, result = await self.test_api_endpoint("/customization/save", method="POST", data=customization_data, headers=auth_headers)
            self.log_test_result('customization', "POST /api/customization/save (authenticated)", success, "" if success else str(result))
        else:
            self.log_test_result('customization', "Customization save test", False, "No admin token available")

    async def test_youtube_content(self):
        """Test YouTube and content endpoints"""
        print("\n🎥 Testing YouTube & Content System...")
        
        # Test latest videos
        success, result = await self.test_api_endpoint("/youtube/latest")
        self.log_test_result('youtube_content', "GET /api/youtube/latest", success, "" if success else str(result))
        
        if success and isinstance(result, list):
            self.log_test_result('youtube_content', "Latest videos structure", True, f"Got {len(result)} videos")
            if result:
                video_fields = ["video_id", "title", "thumbnail_url", "watch_url"]
                first_video = result[0]
                has_video_fields = all(field in first_video for field in video_fields)
                self.log_test_result('youtube_content', "Video objects structure", has_video_fields)
        
        # Test real-time stats (requires auth)
        if self.admin_token:
            auth_headers = {"Authorization": f"Bearer {self.admin_token}"}
            success, result = await self.test_api_endpoint("/admin/dashboard/real-time-stats", headers=auth_headers)
            self.log_test_result('youtube_content', "GET /api/admin/dashboard/real-time-stats", success, "" if success else str(result))
            
            if success and isinstance(result, dict):
                stats_fields = ["subscriber_count", "video_count", "total_views"]
                has_stats = any(field in result for field in stats_fields)
                self.log_test_result('youtube_content', "Real-time stats structure", has_stats)
            
            # Test live toggle
            success, result = await self.test_api_endpoint("/admin/live/toggle", method="POST", headers=auth_headers)
            self.log_test_result('youtube_content', "POST /api/admin/live/toggle", success, "" if success else str(result))
        else:
            self.log_test_result('youtube_content', "Admin content tests", False, "No admin token available")

    async def test_schedule_management(self):
        """Test schedule management endpoints"""
        print("\n📅 Testing Schedule Management...")
        
        # Test get schedule (requires auth)
        if self.admin_token:
            auth_headers = {"Authorization": f"Bearer {self.admin_token}"}
            success, result = await self.test_api_endpoint("/admin/schedule", headers=auth_headers)
            self.log_test_result('schedule', "GET /api/admin/schedule", success, "" if success else str(result))
            
            if success and isinstance(result, dict):
                # Should have days of the week
                days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                has_days = any(day in result for day in days)
                self.log_test_result('schedule', "Schedule structure", has_days, f"Available keys: {list(result.keys())}")
            
            # Test update schedule
            schedule_data = {
                "day": "monday",
                "time": "19:00",
                "game": "FORTNITE Battle Royale",
                "description": "Test stream session"
            }
            success, result = await self.test_api_endpoint("/admin/schedule/update", method="POST", data=schedule_data, headers=auth_headers)
            self.log_test_result('schedule', "POST /api/admin/schedule/update", success, "" if success else str(result))
            
            # Test delete schedule entry
            success, result = await self.test_api_endpoint("/admin/schedule/monday", method="DELETE", headers=auth_headers)
            self.log_test_result('schedule', "DELETE /api/admin/schedule/{day}", success, "" if success else str(result))
        else:
            self.log_test_result('schedule', "Schedule management tests", False, "No admin token available")

    async def test_content_management(self):
        """Test content management endpoints"""
        print("\n📝 Testing Content Management...")
        
        # Test get about content
        success, result = await self.test_api_endpoint("/admin/content/about")
        self.log_test_result('content_management', "GET /api/admin/content/about", success, "" if success else str(result))
        
        if success and isinstance(result, dict):
            content_fields = ["title", "content", "tags"]
            has_fields = any(field in result for field in content_fields)
            self.log_test_result('content_management', "About content structure", has_fields)
        
        # Test update about content (requires auth)
        if self.admin_token:
            auth_headers = {"Authorization": f"Bearer {self.admin_token}"}
            about_data = {
                "title": "About REMZA019 Gaming - Test Update",
                "content": "Test content update for comprehensive testing",
                "tags": ["gaming", "fortnite", "streaming", "test"]
            }
            success, result = await self.test_api_endpoint("/admin/content/about/update", method="POST", data=about_data, headers=auth_headers)
            self.log_test_result('content_management', "POST /api/admin/content/about/update", success, "" if success else str(result))
            
            # Test get tags
            success, result = await self.test_api_endpoint("/admin/content/tags")
            self.log_test_result('content_management', "GET /api/admin/content/tags", success, "" if success else str(result))
            
            if success and isinstance(result, dict) and "tags" in result:
                tags = result["tags"]
                self.log_test_result('content_management', "Tags structure", isinstance(tags, list))
            
            # Test update tags
            tags_data = {
                "tags": [
                    {"icon": "🏆", "text": "Test Tag 1"},
                    {"icon": "🎮", "text": "Test Tag 2"},
                    {"icon": "🔥", "text": "Test Tag 3"}
                ]
            }
            success, result = await self.test_api_endpoint("/admin/content/tags/update", method="POST", data=tags_data, headers=auth_headers)
            self.log_test_result('content_management', "POST /api/admin/content/tags/update", success, "" if success else str(result))
        else:
            self.log_test_result('content_management', "Content management auth tests", False, "No admin token available")

    async def test_new_features(self):
        """Test new feature endpoints if available"""
        print("\n🆕 Testing New Features...")
        
        # Test analytics endpoints
        analytics_endpoints = [
            "/analytics/overview",
            "/analytics/viewers",
            "/analytics/engagement"
        ]
        
        for endpoint in analytics_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result('new_features', f"GET /api{endpoint}", success, "" if success else str(result))
        
        # Test clips endpoints
        clips_endpoints = [
            "/clips/recent",
            "/clips/popular"
        ]
        
        for endpoint in clips_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result('new_features', f"GET /api{endpoint}", success, "" if success else str(result))
        
        # Test merchandise endpoints
        merch_endpoints = [
            "/merchandise/products",
            "/merchandise/categories"
        ]
        
        for endpoint in merch_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result('new_features', f"GET /api{endpoint}", success, "" if success else str(result))
        
        # Test referral system
        referral_endpoints = [
            "/referral/stats",
            "/referral/leaderboard"
        ]
        
        for endpoint in referral_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result('new_features', f"GET /api{endpoint}", success, "" if success else str(result))
        
        # Test subscription endpoints
        subscription_endpoints = [
            "/subscription/tiers",
            "/subscription/benefits"
        ]
        
        for endpoint in subscription_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result('new_features', f"GET /api{endpoint}", success, "" if success else str(result))
        
        # Test tournament endpoints
        tournament_endpoints = [
            "/tournament/active",
            "/tournament/upcoming"
        ]
        
        for endpoint in tournament_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result('new_features', f"GET /api{endpoint}", success, "" if success else str(result))
        
        # Test Twitch integration
        twitch_endpoints = [
            "/twitch/status",
            "/twitch/clips"
        ]
        
        for endpoint in twitch_endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result('new_features', f"GET /api{endpoint}", success, "" if success else str(result))

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Admin Panel & Features Testing...")
        print(f"🔗 Testing against: {BACKEND_URL}")
        
        await self.setup()
        
        try:
            # Run all test categories
            await self.test_admin_authentication()
            await self.test_theme_system()
            await self.test_viewer_system()
            await self.test_customization_system()
            await self.test_youtube_content()
            await self.test_schedule_management()
            await self.test_content_management()
            await self.test_new_features()
            
        finally:
            await self.cleanup()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE ADMIN PANEL & FEATURES TEST SUMMARY")
        print("="*80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   Passed: {self.results['passed_tests']} ✅")
        print(f"   Failed: {self.results['failed_tests']} ❌")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Category breakdown
        categories = [
            ('admin_auth', 'Admin Authentication'),
            ('theme_system', 'Theme System'),
            ('viewer_system', 'Viewer System'),
            ('customization', 'Customization'),
            ('youtube_content', 'YouTube & Content'),
            ('schedule', 'Schedule Management'),
            ('content_management', 'Content Management'),
            ('new_features', 'New Features')
        ]
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category_key, category_name in categories:
            if category_key in self.results:
                category_results = self.results[category_key]
                if category_results:
                    passed = sum(1 for result in category_results.values() if result)
                    total = len(category_results)
                    rate = (passed / total * 100) if total > 0 else 0
                    status = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
                    print(f"   {status} {category_name}: {passed}/{total} ({rate:.1f}%)")
        
        # Critical issues
        if self.results['failed_tests'] > 0:
            print(f"\n🚨 CRITICAL ISSUES:")
            for error in self.results['error_logs'][:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(self.results['error_logs']) > 10:
                print(f"   ... and {len(self.results['error_logs']) - 10} more issues")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   🎉 Excellent! Admin panel is production-ready.")
        elif success_rate >= 70:
            print("   👍 Good! Minor issues need attention before production.")
        elif success_rate >= 50:
            print("   ⚠️  Moderate issues detected. Review failed tests.")
        else:
            print("   🚨 Major issues detected. Significant work needed.")
        
        print("="*80)

async def main():
    """Main test execution"""
    tester = ComprehensiveAdminTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())