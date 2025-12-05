#!/usr/bin/env python3
"""
COMPREHENSIVE 100% BACKEND TESTING - ALL ENDPOINTS
Testing Suite for REMZA019 Gaming Platform - Focus on Critical Endpoints

This test suite focuses on the specific endpoints mentioned in the review request:
1. Version API (newly fixed)
2. Theme API  
3. Admin Schedule API
4. Customization API
5. Viewer API

Admin Credentials: admin/remza019admin
Backend URL: From REACT_APP_BACKEND_URL in frontend/.env
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
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "remza019admin"

class ComprehensiveEndpointTester:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_failures': [],
            'endpoint_results': {},
            'admin_token': None
        }
        self.session = None

    async def setup(self):
        """Setup test environment"""
        print(f"🔧 Setting up comprehensive endpoint testing...")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"🔗 API Base URL: {API_BASE_URL}")
        
        # Create HTTP session with longer timeout for comprehensive testing
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
        else:
            self.results['failed_tests'] += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   Details: {details}")
            
            if is_critical:
                self.results['critical_failures'].append({
                    'test': test_name,
                    'details': details,
                    'timestamp': datetime.now().isoformat()
                })

    async def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        print("\n🔐 Authenticating as Admin...")
        
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        try:
            url = f"{API_BASE_URL}/admin/auth/login"
            async with self.session.post(url, json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('token'):
                        self.results['admin_token'] = result['token']
                        self.log_test_result("Admin authentication", True, f"Token obtained: {result['token'][:20]}...")
                        return True
                    else:
                        self.log_test_result("Admin authentication", False, "No token in response", is_critical=True)
                        return False
                else:
                    self.log_test_result("Admin authentication", False, f"HTTP {response.status}", is_critical=True)
                    return False
        except Exception as e:
            self.log_test_result("Admin authentication", False, str(e), is_critical=True)
            return False

    async def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200, auth_required=False, description=""):
        """Test individual endpoint with comprehensive validation"""
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication if required
        if auth_required and self.results['admin_token']:
            headers["Authorization"] = f"Bearer {self.results['admin_token']}"
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=headers if auth_required else None) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data, status
                        except:
                            response_text = await response.text()
                            return True, response_text, status
                    else:
                        response_text = await response.text()
                        return False, f"HTTP {status}: {response_text}", status
                        
            elif method == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data, status
                        except:
                            response_text = await response.text()
                            return True, response_text, status
                    else:
                        response_text = await response.text()
                        return False, f"HTTP {status}: {response_text}", status
                        
            elif method == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        try:
                            response_data = await response.json()
                            return True, response_data, status
                        except:
                            response_text = await response.text()
                            return True, response_text, status
                    else:
                        response_text = await response.text()
                        return False, f"HTTP {status}: {response_text}", status
                        
        except Exception as e:
            return False, str(e), 0

    async def test_version_api(self):
        """Test Version API endpoints (newly fixed)"""
        print("\n🔄 Testing Version API Endpoints (NEWLY FIXED)...")
        
        version_endpoints = [
            ("/version/current", "GET", "Version current endpoint"),
            ("/version/check-update", "GET", "Version check update endpoint"),
            ("/version/info", "GET", "Version info endpoint")
        ]
        
        for endpoint, method, description in version_endpoints:
            success, result, status = await self.test_endpoint(endpoint, method=method)
            self.log_test_result(f"Version API: {description}", success, 
                               "" if success else str(result), is_critical=True)
            self.results['endpoint_results'][endpoint] = {
                'success': success,
                'status': status,
                'result': result if success else str(result)
            }
            
            # Additional validation for version endpoints
            if success and isinstance(result, dict):
                if endpoint == "/version/current":
                    has_version = 'version' in result or 'current_version' in result
                    self.log_test_result("Version current - has version info", has_version)
                elif endpoint == "/version/info":
                    has_info = 'version' in result or 'build' in result or 'release' in result
                    self.log_test_result("Version info - has detailed info", has_info)

    async def test_theme_api(self):
        """Test Theme API endpoints"""
        print("\n🎨 Testing Theme API Endpoints...")
        
        # Test GET /api/themes/list - should return 6 themes
        success, result, status = await self.test_endpoint("/themes/list")
        self.log_test_result("Theme API: GET /api/themes/list", success, 
                           "" if success else str(result), is_critical=True)
        self.results['endpoint_results']['/themes/list'] = {
            'success': success,
            'status': status,
            'result': result if success else str(result)
        }
        
        if success:
            # Validate 6 themes are returned
            if isinstance(result, dict) and 'themes' in result:
                themes = result['themes']
                theme_count = len(themes) if isinstance(themes, list) else 0
                self.log_test_result("Theme list - 6 themes available", theme_count == 6,
                                   f"Found {theme_count} themes, expected 6")
                
                # Check for expected theme names
                if isinstance(themes, list) and themes:
                    theme_names = [theme.get('name', '') for theme in themes]
                    expected_themes = ['Matrix Green', 'Cyber Purple', 'Neon Blue', 'Toxic Green', 'Blood Red', 'Midnight Dark']
                    themes_found = sum(1 for expected in expected_themes if any(expected.lower() in name.lower() for name in theme_names))
                    self.log_test_result("Theme list - expected theme names", themes_found >= 4,
                                       f"Found {themes_found}/6 expected themes")
            else:
                self.log_test_result("Theme list - proper structure", False, "No 'themes' array in response")
        
        # Test GET /api/themes/current - get active theme
        success, result, status = await self.test_endpoint("/themes/current")
        self.log_test_result("Theme API: GET /api/themes/current", success,
                           "" if success else str(result), is_critical=True)
        self.results['endpoint_results']['/themes/current'] = {
            'success': success,
            'status': status,
            'result': result if success else str(result)
        }
        
        if success and isinstance(result, dict):
            has_current_theme = 'current_theme' in result or 'theme' in result or 'name' in result
            self.log_test_result("Theme current - has active theme info", has_current_theme)
        
        # Test POST /api/themes/apply - apply theme (with admin auth)
        if self.results['admin_token']:
            theme_apply_data = {
                "theme_name": "Cyber Purple"
            }
            
            success, result, status = await self.test_endpoint("/themes/apply", method="POST", 
                                                             data=theme_apply_data, auth_required=True)
            self.log_test_result("Theme API: POST /api/themes/apply (with admin auth)", success,
                               "" if success else str(result), is_critical=True)
            self.results['endpoint_results']['/themes/apply'] = {
                'success': success,
                'status': status,
                'result': result if success else str(result)
            }
            
            if success and isinstance(result, dict):
                theme_applied = result.get('success') or 'applied' in str(result).lower()
                self.log_test_result("Theme apply - successful application", theme_applied)
        else:
            self.log_test_result("Theme API: POST /api/themes/apply", False, "No admin token available", is_critical=True)

    async def test_admin_schedule_api(self):
        """Test Admin Schedule API endpoints"""
        print("\n📅 Testing Admin Schedule API Endpoints...")
        
        if not self.results['admin_token']:
            self.log_test_result("Admin Schedule API", False, "No admin token available", is_critical=True)
            return
        
        # Test GET /api/admin/schedule - get all schedules
        success, result, status = await self.test_endpoint("/admin/schedule", auth_required=True)
        self.log_test_result("Admin Schedule API: GET /api/admin/schedule", success,
                           "" if success else str(result), is_critical=True)
        self.results['endpoint_results']['/admin/schedule'] = {
            'success': success,
            'status': status,
            'result': result if success else str(result)
        }
        
        if success:
            # Validate schedule structure
            if isinstance(result, dict):
                has_schedule_data = 'schedule' in result or 'days' in result or any(day in result for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
                self.log_test_result("Admin schedule - has schedule data", has_schedule_data)
            elif isinstance(result, list):
                self.log_test_result("Admin schedule - returns schedule array", True)
        
        # Test POST /api/admin/schedule/update - update schedule
        schedule_update_data = {
            "day": "monday",
            "time": "19:00",
            "game": "FORTNITE Battle Royale",
            "description": "Test schedule update"
        }
        
        success, result, status = await self.test_endpoint("/admin/schedule/update", method="POST",
                                                         data=schedule_update_data, auth_required=True)
        self.log_test_result("Admin Schedule API: POST /api/admin/schedule/update", success,
                           "" if success else str(result), is_critical=True)
        self.results['endpoint_results']['/admin/schedule/update'] = {
            'success': success,
            'status': status,
            'result': result if success else str(result)
        }
        
        if success and isinstance(result, dict):
            update_successful = result.get('success') or 'updated' in str(result).lower()
            self.log_test_result("Admin schedule update - successful update", update_successful)
        
        # Test DELETE /api/admin/schedule/{day} - delete schedule
        test_day = "tuesday"
        success, result, status = await self.test_endpoint(f"/admin/schedule/{test_day}", method="DELETE", auth_required=True)
        self.log_test_result(f"Admin Schedule API: DELETE /api/admin/schedule/{test_day}", success,
                           "" if success else str(result), is_critical=True)
        self.results['endpoint_results'][f'/admin/schedule/{test_day}'] = {
            'success': success,
            'status': status,
            'result': result if success else str(result)
        }
        
        if success and isinstance(result, dict):
            delete_successful = result.get('success') or 'deleted' in str(result).lower()
            self.log_test_result("Admin schedule delete - successful deletion", delete_successful)

    async def test_customization_api(self):
        """Test Customization API endpoints"""
        print("\n🎨 Testing Customization API Endpoints...")
        
        # Test GET /api/customization/current - get customization
        success, result, status = await self.test_endpoint("/customization/current")
        self.log_test_result("Customization API: GET /api/customization/current", success,
                           "" if success else str(result), is_critical=True)
        self.results['endpoint_results']['/customization/current'] = {
            'success': success,
            'status': status,
            'result': result if success else str(result)
        }
        
        if success and isinstance(result, dict):
            # Check for customization fields
            customization_fields = ['siteName', 'matrixColor', 'textColor', 'logoUrl', 'socialLinks']
            has_customization_fields = any(field in result for field in customization_fields)
            self.log_test_result("Customization current - has customization fields", has_customization_fields,
                               f"Available fields: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        # Test POST /api/admin/customization/update - update customization (with admin auth)
        if self.results['admin_token']:
            customization_update_data = {
                "siteName": "REMZA019 Gaming Test",
                "matrixColor": "#00ff00",
                "textColor": "#ffffff",
                "socialLinks": {
                    "discord": "https://discord.gg/remza019",
                    "youtube": "https://youtube.com/@remza019",
                    "twitch": "https://twitch.tv/remza019"
                }
            }
            
            success, result, status = await self.test_endpoint("/admin/customization/update", method="POST",
                                                             data=customization_update_data, auth_required=True)
            self.log_test_result("Customization API: POST /api/admin/customization/update", success,
                               "" if success else str(result), is_critical=True)
            self.results['endpoint_results']['/admin/customization/update'] = {
                'success': success,
                'status': status,
                'result': result if success else str(result)
            }
            
            if success and isinstance(result, dict):
                update_successful = result.get('success') or 'updated' in str(result).lower()
                self.log_test_result("Customization update - successful update", update_successful)
        else:
            self.log_test_result("Customization API: POST /api/admin/customization/update", False, 
                               "No admin token available", is_critical=True)

    async def test_viewer_api(self):
        """Test Viewer API endpoints"""
        print("\n👥 Testing Viewer API Endpoints...")
        
        # Test POST /api/viewer/register - register viewer
        viewer_register_data = {
            "username": "TestGamer2024",
            "email": "testgamer@remza019gaming.com",
            "password": "testpassword123"
        }
        
        success, result, status = await self.test_endpoint("/viewer/register", method="POST", data=viewer_register_data)
        self.log_test_result("Viewer API: POST /api/viewer/register", success,
                           "" if success else str(result), is_critical=True)
        self.results['endpoint_results']['/viewer/register'] = {
            'success': success,
            'status': status,
            'result': result if success else str(result)
        }
        
        viewer_id = None
        if success and isinstance(result, dict):
            # Check for viewer registration response
            has_viewer_data = 'id' in result or 'user_id' in result or 'viewer_id' in result
            self.log_test_result("Viewer register - returns viewer ID", has_viewer_data)
            
            # Extract viewer ID for further testing
            viewer_id = result.get('id') or result.get('user_id') or result.get('viewer_id')
            
            # Check for points system
            has_points = 'points' in result
            self.log_test_result("Viewer register - includes points system", has_points)
        
        # Test GET /api/viewer/{user_id} - get viewer info
        if viewer_id:
            success, result, status = await self.test_endpoint(f"/viewer/{viewer_id}")
            self.log_test_result(f"Viewer API: GET /api/viewer/{viewer_id}", success,
                               "" if success else str(result), is_critical=True)
            self.results['endpoint_results'][f'/viewer/{viewer_id}'] = {
                'success': success,
                'status': status,
                'result': result if success else str(result)
            }
            
            if success and isinstance(result, dict):
                # Validate viewer info structure
                viewer_fields = ['username', 'points', 'level', 'created_at']
                has_viewer_fields = any(field in result for field in viewer_fields)
                self.log_test_result("Viewer info - has viewer fields", has_viewer_fields)
            
            # Test POST /api/viewer/{user_id}/award-points - award points
            award_points_data = {
                "points": 50,
                "activity": "stream_view",
                "description": "Test point award"
            }
            
            success, result, status = await self.test_endpoint(f"/viewer/{viewer_id}/award-points", 
                                                             method="POST", data=award_points_data)
            self.log_test_result(f"Viewer API: POST /api/viewer/{viewer_id}/award-points", success,
                               "" if success else str(result), is_critical=True)
            self.results['endpoint_results'][f'/viewer/{viewer_id}/award-points'] = {
                'success': success,
                'status': status,
                'result': result if success else str(result)
            }
            
            if success and isinstance(result, dict):
                points_awarded = 'points' in result or 'total_points' in result or result.get('success')
                self.log_test_result("Viewer award points - successful point award", points_awarded)
        else:
            # Test with a mock user ID if registration failed
            mock_user_id = "test_user_123"
            success, result, status = await self.test_endpoint(f"/viewer/{mock_user_id}")
            self.log_test_result(f"Viewer API: GET /api/viewer/{mock_user_id} (mock ID)", success,
                               "" if success else str(result))

    async def test_additional_critical_endpoints(self):
        """Test additional critical endpoints for comprehensive coverage"""
        print("\n🔍 Testing Additional Critical Endpoints...")
        
        # Test basic API health
        success, result, status = await self.test_endpoint("/")
        self.log_test_result("API Health: GET /api/", success, "" if success else str(result), is_critical=True)
        
        # Test YouTube API endpoints (critical for gaming platform)
        youtube_endpoints = [
            ("/youtube/latest-videos", "YouTube latest videos"),
            ("/youtube/channel-stats", "YouTube channel stats"),
            ("/youtube/featured-video", "YouTube featured video")
        ]
        
        for endpoint, description in youtube_endpoints:
            success, result, status = await self.test_endpoint(endpoint)
            self.log_test_result(f"YouTube API: {description}", success, "" if success else str(result))
            self.results['endpoint_results'][endpoint] = {
                'success': success,
                'status': status,
                'result': result if success else str(result)
            }

    async def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE 100% BACKEND TESTING - FINAL REPORT")
        print("="*80)
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   Passed: {self.results['passed_tests']}")
        print(f"   Failed: {self.results['failed_tests']}")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🚨 CRITICAL FAILURES: {len(self.results['critical_failures'])}")
        if self.results['critical_failures']:
            for failure in self.results['critical_failures']:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        
        print(f"\n🔗 ENDPOINT RESULTS SUMMARY:")
        
        # Group by API category
        categories = {
            'Version API': ['/version/current', '/version/check-update', '/version/info'],
            'Theme API': ['/themes/list', '/themes/current', '/themes/apply'],
            'Admin Schedule API': ['/admin/schedule', '/admin/schedule/update'],
            'Customization API': ['/customization/current', '/admin/customization/update'],
            'Viewer API': ['/viewer/register'],
            'YouTube API': ['/youtube/latest-videos', '/youtube/channel-stats', '/youtube/featured-video']
        }
        
        for category, endpoints in categories.items():
            print(f"\n   {category}:")
            for endpoint in endpoints:
                if endpoint in self.results['endpoint_results']:
                    result = self.results['endpoint_results'][endpoint]
                    status_icon = "✅" if result['success'] else "❌"
                    print(f"     {status_icon} {endpoint} (HTTP {result['status']})")
                else:
                    # Check for dynamic endpoints (with IDs)
                    found = False
                    for tested_endpoint in self.results['endpoint_results']:
                        if endpoint.replace('{', '').replace('}', '') in tested_endpoint:
                            result = self.results['endpoint_results'][tested_endpoint]
                            status_icon = "✅" if result['success'] else "❌"
                            print(f"     {status_icon} {tested_endpoint} (HTTP {result['status']})")
                            found = True
                            break
                    if not found:
                        print(f"     ⚪ {endpoint} (Not tested)")
        
        print(f"\n🎯 CRITICAL ENDPOINT STATUS:")
        critical_endpoints = [
            '/version/current', '/version/check-update', '/version/info',
            '/themes/list', '/themes/current', '/themes/apply',
            '/admin/schedule', '/customization/current'
        ]
        
        critical_success = 0
        critical_total = 0
        
        for endpoint in critical_endpoints:
            critical_total += 1
            if endpoint in self.results['endpoint_results']:
                if self.results['endpoint_results'][endpoint]['success']:
                    critical_success += 1
                    print(f"   ✅ {endpoint}")
                else:
                    print(f"   ❌ {endpoint}")
            else:
                print(f"   ⚪ {endpoint} (Not tested)")
        
        critical_rate = (critical_success / critical_total * 100) if critical_total > 0 else 0
        print(f"\n🎯 CRITICAL ENDPOINTS SUCCESS RATE: {critical_rate:.1f}% ({critical_success}/{critical_total})")
        
        # Final assessment
        if critical_rate >= 90:
            print(f"\n🎉 ASSESSMENT: EXCELLENT - Backend is production-ready!")
        elif critical_rate >= 75:
            print(f"\n✅ ASSESSMENT: GOOD - Backend is mostly functional with minor issues")
        elif critical_rate >= 50:
            print(f"\n⚠️  ASSESSMENT: NEEDS ATTENTION - Several critical endpoints failing")
        else:
            print(f"\n❌ ASSESSMENT: CRITICAL ISSUES - Major backend problems detected")
        
        return {
            'success_rate': success_rate,
            'critical_rate': critical_rate,
            'total_tests': self.results['total_tests'],
            'passed_tests': self.results['passed_tests'],
            'failed_tests': self.results['failed_tests'],
            'critical_failures': len(self.results['critical_failures'])
        }

async def main():
    """Main test execution"""
    tester = ComprehensiveEndpointTester()
    
    try:
        await tester.setup()
        
        # Authenticate admin first
        admin_auth_success = await tester.authenticate_admin()
        
        # Run all endpoint tests
        await tester.test_version_api()
        await tester.test_theme_api()
        await tester.test_admin_schedule_api()
        await tester.test_customization_api()
        await tester.test_viewer_api()
        await tester.test_additional_critical_endpoints()
        
        # Generate final report
        report = await tester.generate_comprehensive_report()
        
        return report
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return None
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    print("🚀 Starting COMPREHENSIVE 100% BACKEND TESTING - ALL ENDPOINTS")
    print("="*80)
    
    # Run the test suite
    report = asyncio.run(main())
    
    if report:
        # Exit with appropriate code
        if report['critical_rate'] >= 75:
            print(f"\n✅ Testing completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Testing completed with critical issues!")
            sys.exit(1)
    else:
        print(f"\n💥 Testing failed to complete!")
        sys.exit(1)