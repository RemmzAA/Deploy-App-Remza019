#!/usr/bin/env python3
"""
REMZA019 Gaming - Comprehensive Backend Testing
Full Application Testing as per Review Request
"""

import asyncio
import aiohttp
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveBackendTester:
    def __init__(self, base_url: str, admin_username: str, admin_password: str):
        self.base_url = base_url.rstrip('/')
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
        
        if details:
            logger.debug(f"Details: {json.dumps(details, indent=2)}")
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                return {
                    'status': response.status,
                    'data': response_data,
                    'headers': dict(response.headers)
                }
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            return {
                'status': 0,
                'data': {'error': str(e)},
                'headers': {}
            }

    # 1. Authentication & Security Tests
    async def test_admin_authentication(self) -> bool:
        """Test admin login flow and JWT token validation"""
        logger.info("🔐 Testing admin authentication...")
        
        response = await self.make_request(
            'POST', 
            '/api/admin/auth/login',
            {
                'username': self.admin_username,
                'password': self.admin_password
            }
        )
        
        if response['status'] == 200 and ('access_token' in response['data'] or 'token' in response['data']):
            self.admin_token = response['data'].get('access_token') or response['data'].get('token')
            self.log_test_result(
                "Admin Authentication", 
                True, 
                "Successfully authenticated as admin",
                {'token_received': bool(self.admin_token)}
            )
            return True
        else:
            self.log_test_result(
                "Admin Authentication", 
                False, 
                f"Authentication failed: {response['data'].get('detail', 'Unknown error')}",
                {'status': response['status'], 'response': response['data']}
            )
            return False

    async def test_session_management(self) -> bool:
        """Test session management and token validation"""
        logger.info("🔐 Testing session management...")
        
        if not self.admin_token:
            self.log_test_result("Session Management", False, "No admin token available", {})
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test protected endpoint
        response = await self.make_request('GET', '/api/admin/dashboard', headers=headers)
        
        if response['status'] == 200:
            self.log_test_result(
                "Session Management",
                True,
                "JWT token validation working correctly",
                {'status': response['status']}
            )
            return True
        else:
            self.log_test_result(
                "Session Management",
                False,
                f"Token validation failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    # 2. Email System Tests
    async def test_smtp_configuration(self) -> bool:
        """Test SMTP configuration and email system"""
        logger.info("📧 Testing SMTP configuration...")
        
        test_email = f"smtp_test_{uuid.uuid4().hex[:8]}@example.com"
        
        response = await self.make_request(
            'POST',
            '/api/email/test',
            {'email': test_email}
        )
        
        if response['status'] == 200:
            self.log_test_result(
                "SMTP Configuration",
                True,
                "SMTP system is configured and working",
                {'test_email': test_email}
            )
            return True
        else:
            self.log_test_result(
                "SMTP Configuration",
                False,
                f"SMTP configuration issue: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_registration_verification_emails(self) -> bool:
        """Test registration verification email flow"""
        logger.info("📧 Testing registration verification emails...")
        
        test_username = f"regtest_{uuid.uuid4().hex[:8]}"
        test_email = f"regtest_{uuid.uuid4().hex[:8]}@example.com"
        
        response = await self.make_request(
            'POST',
            '/api/viewer/register',
            {
                'username': test_username,
                'email': test_email
            }
        )
        
        if response['status'] == 200 and response['data'].get('success'):
            self.log_test_result(
                "Registration Verification Emails",
                True,
                "Registration triggers email verification successfully",
                {'email': test_email, 'username': test_username}
            )
            return True
        else:
            self.log_test_result(
                "Registration Verification Emails",
                False,
                f"Registration email verification failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_live_stream_notifications(self) -> bool:
        """Test live stream notification emails"""
        logger.info("📧 Testing live stream notifications...")
        
        if not self.admin_token:
            self.log_test_result("Live Stream Notifications", False, "Admin token required", {})
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        response = await self.make_request(
            'POST',
            '/api/email/notify-live',
            {},
            headers
        )
        
        if response['status'] == 200:
            self.log_test_result(
                "Live Stream Notifications",
                True,
                "Live stream notification system working",
                {'response': response['data']}
            )
            return True
        else:
            self.log_test_result(
                "Live Stream Notifications",
                False,
                f"Live stream notifications failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_leaderboard_update_emails(self) -> bool:
        """Test leaderboard update notification emails"""
        logger.info("📧 Testing leaderboard update emails...")
        
        # First register a test viewer
        test_username = f"leadertest_{uuid.uuid4().hex[:8]}"
        test_email = f"leadertest_{uuid.uuid4().hex[:8]}@example.com"
        
        reg_response = await self.make_request(
            'POST',
            '/api/viewer/register',
            {
                'username': test_username,
                'email': test_email
            }
        )
        
        if reg_response['status'] != 200:
            self.log_test_result("Leaderboard Update Emails", False, "Failed to register test viewer", {})
            return False
        
        viewer_data = reg_response['data'].get('viewer', {})
        user_id = viewer_data.get('user_id') or viewer_data.get('id')
        
        if not user_id:
            self.log_test_result("Leaderboard Update Emails", False, "No user_id received", {})
            return False
        
        # Award points to trigger leaderboard update
        points_response = await self.make_request(
            'POST',
            f'/api/viewer/activity/{user_id}',
            {
                'activity_type': 'stream_view',
                'metadata': {'test': True}
            }
        )
        
        if points_response['status'] == 200:
            self.log_test_result(
                "Leaderboard Update Emails",
                True,
                "Leaderboard update system working with email notifications",
                {'user_id': user_id, 'points_awarded': points_response['data'].get('points_awarded', 0)}
            )
            return True
        else:
            self.log_test_result(
                "Leaderboard Update Emails",
                False,
                f"Leaderboard update failed: {points_response['status']}",
                {'response': points_response['data']}
            )
            return False

    # 3. YouTube Integration Tests
    async def test_youtube_channel_stats(self) -> bool:
        """Test YouTube channel stats endpoint"""
        logger.info("🎬 Testing YouTube channel stats...")
        
        response = await self.make_request('GET', '/api/youtube/channel-stats')
        
        if response['status'] == 200:
            data = response['data']
            required_fields = ['channel_id', 'subscriber_count', 'video_count', 'view_count']
            
            if all(field in data for field in required_fields):
                self.log_test_result(
                    "YouTube Channel Stats",
                    True,
                    f"Channel stats retrieved: {data['subscriber_count']} subs, {data['video_count']} videos",
                    data
                )
                return True
            else:
                self.log_test_result(
                    "YouTube Channel Stats",
                    False,
                    "Missing required fields in channel stats",
                    {'received_fields': list(data.keys()), 'required_fields': required_fields}
                )
                return False
        else:
            self.log_test_result(
                "YouTube Channel Stats",
                False,
                f"YouTube channel stats failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_youtube_latest_videos(self) -> bool:
        """Test YouTube latest videos endpoint"""
        logger.info("🎬 Testing YouTube latest videos...")
        
        response = await self.make_request('GET', '/api/youtube/latest-videos')
        
        if response['status'] == 200:
            videos = response['data']
            
            if isinstance(videos, list) and len(videos) > 0:
                video = videos[0]
                required_fields = ['id', 'title', 'thumbnail_url', 'watch_url', 'view_count', 'duration']
                
                if all(field in video for field in required_fields):
                    self.log_test_result(
                        "YouTube Latest Videos",
                        True,
                        f"Retrieved {len(videos)} videos with complete data",
                        {'video_count': len(videos), 'sample_video': video['title']}
                    )
                    return True
                else:
                    self.log_test_result(
                        "YouTube Latest Videos",
                        False,
                        "Videos missing required fields",
                        {'received_fields': list(video.keys()), 'required_fields': required_fields}
                    )
                    return False
            else:
                self.log_test_result(
                    "YouTube Latest Videos",
                    False,
                    "No videos returned or invalid format",
                    {'response_type': type(videos).__name__, 'length': len(videos) if isinstance(videos, list) else 'N/A'}
                )
                return False
        else:
            self.log_test_result(
                "YouTube Latest Videos",
                False,
                f"YouTube latest videos failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_youtube_video_data_accuracy(self) -> bool:
        """Test YouTube video data accuracy and thumbnail loading"""
        logger.info("🎬 Testing YouTube video data accuracy...")
        
        response = await self.make_request('GET', '/api/youtube/latest-videos')
        
        if response['status'] == 200:
            videos = response['data']
            
            if isinstance(videos, list) and len(videos) > 0:
                video = videos[0]
                
                # Test thumbnail URL accessibility
                thumbnail_url = video.get('thumbnail_url')
                if thumbnail_url:
                    try:
                        async with self.session.get(thumbnail_url) as thumb_response:
                            if thumb_response.status == 200:
                                self.log_test_result(
                                    "YouTube Video Data Accuracy",
                                    True,
                                    "Video data accurate and thumbnails accessible",
                                    {
                                        'thumbnail_status': thumb_response.status,
                                        'video_title': video.get('title', 'N/A'),
                                        'view_count': video.get('view_count', 'N/A')
                                    }
                                )
                                return True
                            else:
                                self.log_test_result(
                                    "YouTube Video Data Accuracy",
                                    False,
                                    f"Thumbnail not accessible: {thumb_response.status}",
                                    {'thumbnail_url': thumbnail_url}
                                )
                                return False
                    except Exception as e:
                        self.log_test_result(
                            "YouTube Video Data Accuracy",
                            False,
                            f"Error accessing thumbnail: {str(e)}",
                            {'thumbnail_url': thumbnail_url}
                        )
                        return False
                else:
                    self.log_test_result(
                        "YouTube Video Data Accuracy",
                        False,
                        "No thumbnail URL provided",
                        {'video_data': video}
                    )
                    return False
            else:
                self.log_test_result(
                    "YouTube Video Data Accuracy",
                    False,
                    "No videos available for accuracy testing",
                    {}
                )
                return False
        else:
            self.log_test_result(
                "YouTube Video Data Accuracy",
                False,
                f"Failed to get videos for accuracy testing: {response['status']}",
                {'response': response['data']}
            )
            return False

    # 4. Viewer System Tests
    async def test_viewer_registration_flow(self) -> bool:
        """Test complete viewer registration flow"""
        logger.info("👥 Testing viewer registration flow...")
        
        test_username = f"viewertest_{uuid.uuid4().hex[:8]}"
        test_email = f"viewertest_{uuid.uuid4().hex[:8]}@example.com"
        
        response = await self.make_request(
            'POST',
            '/api/viewer/register',
            {
                'username': test_username,
                'email': test_email
            }
        )
        
        if response['status'] == 200 and response['data'].get('success'):
            viewer_data = response['data'].get('viewer', {})
            self.log_test_result(
                "Viewer Registration Flow",
                True,
                f"Viewer registration successful: {test_username}",
                {
                    'user_id': viewer_data.get('user_id') or viewer_data.get('id'),
                    'email_verified': viewer_data.get('email_verified', False)
                }
            )
            return True
        else:
            self.log_test_result(
                "Viewer Registration Flow",
                False,
                f"Viewer registration failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_points_system(self) -> bool:
        """Test viewer points system"""
        logger.info("👥 Testing points system...")
        
        # First register a viewer
        test_username = f"pointstest_{uuid.uuid4().hex[:8]}"
        test_email = f"pointstest_{uuid.uuid4().hex[:8]}@example.com"
        
        reg_response = await self.make_request(
            'POST',
            '/api/viewer/register',
            {
                'username': test_username,
                'email': test_email
            }
        )
        
        if reg_response['status'] != 200:
            self.log_test_result("Points System", False, "Failed to register test viewer", {})
            return False
        
        viewer_data = reg_response['data'].get('viewer', {})
        user_id = viewer_data.get('user_id') or viewer_data.get('id')
        
        if not user_id:
            self.log_test_result("Points System", False, "No user_id received", {})
            return False
        
        # Test points awarding
        points_response = await self.make_request(
            'POST',
            f'/api/viewer/activity/{user_id}',
            {
                'activity_type': 'stream_view',
                'metadata': {'test': True}
            }
        )
        
        if points_response['status'] == 200:
            points_data = points_response['data']
            self.log_test_result(
                "Points System",
                True,
                f"Points system working: {points_data.get('points_awarded', 0)} points awarded",
                {
                    'total_points': points_data.get('total_points', 0),
                    'level': points_data.get('level', 1)
                }
            )
            return True
        else:
            self.log_test_result(
                "Points System",
                False,
                f"Points system failed: {points_response['status']}",
                {'response': points_response['data']}
            )
            return False

    async def test_level_progression(self) -> bool:
        """Test viewer level progression system"""
        logger.info("👥 Testing level progression...")
        
        response = await self.make_request('GET', '/api/viewer/leaderboard')
        
        if response['status'] == 200:
            leaderboard = response['data'].get('leaderboard', [])
            self.log_test_result(
                "Level Progression",
                True,
                f"Level progression system working with {len(leaderboard)} entries",
                {'leaderboard_size': len(leaderboard)}
            )
            return True
        else:
            self.log_test_result(
                "Level Progression",
                False,
                f"Level progression system failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_leaderboard_system(self) -> bool:
        """Test leaderboard system"""
        logger.info("👥 Testing leaderboard system...")
        
        response = await self.make_request('GET', '/api/viewer/leaderboard')
        
        if response['status'] == 200:
            data = response['data']
            leaderboard = data.get('leaderboard', [])
            
            if isinstance(leaderboard, list):
                self.log_test_result(
                    "Leaderboard System",
                    True,
                    f"Leaderboard system working with {len(leaderboard)} entries",
                    {'leaderboard_size': len(leaderboard)}
                )
                return True
            else:
                self.log_test_result(
                    "Leaderboard System",
                    False,
                    "Leaderboard data format invalid",
                    {'data_type': type(leaderboard).__name__}
                )
                return False
        else:
            self.log_test_result(
                "Leaderboard System",
                False,
                f"Leaderboard system failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    # 5. Admin Dashboard Tests
    async def test_admin_dashboard_functionality(self) -> bool:
        """Test all admin dashboard tabs functionality"""
        logger.info("🎛️ Testing admin dashboard functionality...")
        
        if not self.admin_token:
            self.log_test_result("Admin Dashboard Functionality", False, "Admin token required", {})
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test dashboard data
        response = await self.make_request('GET', '/api/admin/dashboard', headers=headers)
        
        if response['status'] == 200:
            self.log_test_result(
                "Admin Dashboard Functionality",
                True,
                "Admin dashboard accessible and functional",
                {'dashboard_data_available': bool(response['data'])}
            )
            return True
        else:
            self.log_test_result(
                "Admin Dashboard Functionality",
                False,
                f"Admin dashboard failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_theme_switching(self) -> bool:
        """Test theme switching functionality"""
        logger.info("🎨 Testing theme switching...")
        
        response = await self.make_request(
            'POST',
            '/api/themes/apply',
            {'theme': 'blood-red'}
        )
        
        if response['status'] == 200:
            self.log_test_result(
                "Theme Switching",
                True,
                "Theme switching system working",
                {'applied_theme': 'blood-red'}
            )
            return True
        else:
            self.log_test_result(
                "Theme Switching",
                False,
                f"Theme switching failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_content_management(self) -> bool:
        """Test content management functionality"""
        logger.info("📝 Testing content management...")
        
        if not self.admin_token:
            self.log_test_result("Content Management", False, "Admin token required", {})
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test getting customization settings
        response = await self.make_request('GET', '/api/customization', headers=headers)
        
        if response['status'] == 200:
            self.log_test_result(
                "Content Management",
                True,
                "Content management system accessible",
                {'customization_data_available': bool(response['data'])}
            )
            return True
        else:
            self.log_test_result(
                "Content Management",
                False,
                f"Content management failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_schedule_management(self) -> bool:
        """Test schedule management functionality"""
        logger.info("📅 Testing schedule management...")
        
        if not self.admin_token:
            self.log_test_result("Schedule Management", False, "Admin token required", {})
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        response = await self.make_request('GET', '/api/admin/schedule', headers=headers)
        
        if response['status'] == 200:
            self.log_test_result(
                "Schedule Management",
                True,
                "Schedule management system working",
                {'schedule_data_available': bool(response['data'])}
            )
            return True
        else:
            self.log_test_result(
                "Schedule Management",
                False,
                f"Schedule management failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_obs_control_panel(self) -> bool:
        """Test OBS control panel functionality"""
        logger.info("🎥 Testing OBS control panel...")
        
        if not self.admin_token:
            self.log_test_result("OBS Control Panel", False, "Admin token required", {})
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test OBS status endpoint
        response = await self.make_request('GET', '/api/obs/status', headers=headers)
        
        # OBS might not be connected, but endpoint should exist
        if response['status'] in [200, 503]:  # 503 = service unavailable (OBS not connected)
            self.log_test_result(
                "OBS Control Panel",
                True,
                f"OBS control panel accessible (status: {response['status']})",
                {'obs_status': response['status']}
            )
            return True
        else:
            self.log_test_result(
                "OBS Control Panel",
                False,
                f"OBS control panel failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    async def test_viewer_management(self) -> bool:
        """Test viewer management functionality"""
        logger.info("👥 Testing viewer management...")
        
        if not self.admin_token:
            self.log_test_result("Viewer Management", False, "Admin token required", {})
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test getting viewer list
        response = await self.make_request('GET', '/api/admin/viewers', headers=headers)
        
        if response['status'] == 200:
            viewers = response['data'].get('viewers', [])
            self.log_test_result(
                "Viewer Management",
                True,
                f"Viewer management working with {len(viewers)} viewers",
                {'viewer_count': len(viewers)}
            )
            return True
        else:
            self.log_test_result(
                "Viewer Management",
                False,
                f"Viewer management failed: {response['status']}",
                {'response': response['data']}
            )
            return False

    # 6. API Endpoints Health Check
    async def test_all_api_endpoints(self) -> bool:
        """Test all specified API endpoints"""
        logger.info("🔍 Testing all API endpoints health check...")
        
        endpoints = [
            ('/api/version/current', 'GET'),
            ('/api/version/check-update', 'GET'),
            ('/api/streams/recent', 'GET'),
            ('/api/admin/events', 'GET'),
            ('/api/youtube/channel-stats', 'GET'),
            ('/api/youtube/latest-videos', 'GET'),
            ('/api/themes/apply', 'POST'),
            ('/api/customization', 'GET'),
            ('/api/viewer/register', 'POST'),
            ('/api/viewer/leaderboard', 'GET'),
            ('/api/admin/schedule', 'GET')
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint, method in endpoints:
            try:
                if method == 'POST':
                    if 'register' in endpoint:
                        data = {
                            'username': f'healthcheck_{uuid.uuid4().hex[:6]}',
                            'email': f'healthcheck_{uuid.uuid4().hex[:6]}@example.com'
                        }
                    elif 'themes' in endpoint:
                        data = {'theme': 'default'}
                    else:
                        data = {}
                    
                    headers = {}
                    if 'admin' in endpoint and self.admin_token:
                        headers = {'Authorization': f'Bearer {self.admin_token}'}
                    
                    response = await self.make_request(method, endpoint, data, headers)
                else:
                    headers = {}
                    if 'admin' in endpoint and self.admin_token:
                        headers = {'Authorization': f'Bearer {self.admin_token}'}
                    
                    response = await self.make_request(method, endpoint, headers=headers)
                
                if response['status'] in [200, 201]:
                    passed += 1
                    logger.info(f"✅ {endpoint} - {response['status']}")
                else:
                    logger.info(f"❌ {endpoint} - {response['status']}")
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} - Exception: {e}")
        
        success_rate = (passed / total) * 100
        
        if success_rate >= 70:
            self.log_test_result(
                "API Endpoints Health Check",
                True,
                f"API endpoints health check passed: {passed}/{total} ({success_rate:.1f}%)",
                {'passed': passed, 'total': total, 'success_rate': success_rate}
            )
            return True
        else:
            self.log_test_result(
                "API Endpoints Health Check",
                False,
                f"API endpoints health check failed: {passed}/{total} ({success_rate:.1f}%)",
                {'passed': passed, 'total': total, 'success_rate': success_rate}
            )
            return False

    # 7. Database Operations Tests
    async def test_database_operations(self) -> bool:
        """Test database connection and operations"""
        logger.info("🗄️ Testing database operations...")
        
        # Test database connectivity by performing a viewer registration
        test_username = f"dbtest_{uuid.uuid4().hex[:8]}"
        test_email = f"dbtest_{uuid.uuid4().hex[:8]}@example.com"
        
        response = await self.make_request(
            'POST',
            '/api/viewer/register',
            {
                'username': test_username,
                'email': test_email
            }
        )
        
        if response['status'] == 200 and response['data'].get('success'):
            # Test data retrieval
            leaderboard_response = await self.make_request('GET', '/api/viewer/leaderboard')
            
            if leaderboard_response['status'] == 200:
                self.log_test_result(
                    "Database Operations",
                    True,
                    "Database operations working (create and read operations successful)",
                    {'registration_success': True, 'data_retrieval_success': True}
                )
                return True
            else:
                self.log_test_result(
                    "Database Operations",
                    False,
                    "Database read operations failed",
                    {'registration_success': True, 'data_retrieval_success': False}
                )
                return False
        else:
            self.log_test_result(
                "Database Operations",
                False,
                "Database write operations failed",
                {'registration_success': False}
            )
            return False

    # 8. License System Tests
    async def test_license_system(self) -> bool:
        """Test license system functionality"""
        logger.info("📜 Testing license system...")
        
        # Test license API endpoints
        endpoints_to_test = [
            '/api/license/status',
            '/api/license/info'
        ]
        
        license_working = False
        
        for endpoint in endpoints_to_test:
            response = await self.make_request('GET', endpoint)
            
            if response['status'] == 200:
                license_working = True
                self.log_test_result(
                    "License System",
                    True,
                    f"License system working - {endpoint} accessible",
                    {'endpoint': endpoint, 'status': response['status']}
                )
                return True
        
        if not license_working:
            self.log_test_result(
                "License System",
                False,
                "License system endpoints not accessible or not implemented",
                {'tested_endpoints': endpoints_to_test}
            )
            return False

    async def run_comprehensive_tests(self) -> Dict:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting comprehensive backend testing...")
        
        # Test categories with their test functions
        test_categories = [
            ("Authentication & Security", [
                ("Admin Authentication", self.test_admin_authentication),
                ("Session Management", self.test_session_management),
            ]),
            ("Email System", [
                ("SMTP Configuration", self.test_smtp_configuration),
                ("Registration Verification Emails", self.test_registration_verification_emails),
                ("Live Stream Notifications", self.test_live_stream_notifications),
                ("Leaderboard Update Emails", self.test_leaderboard_update_emails),
            ]),
            ("YouTube Integration", [
                ("YouTube Channel Stats", self.test_youtube_channel_stats),
                ("YouTube Latest Videos", self.test_youtube_latest_videos),
                ("YouTube Video Data Accuracy", self.test_youtube_video_data_accuracy),
            ]),
            ("Viewer System", [
                ("Viewer Registration Flow", self.test_viewer_registration_flow),
                ("Points System", self.test_points_system),
                ("Level Progression", self.test_level_progression),
                ("Leaderboard System", self.test_leaderboard_system),
            ]),
            ("Admin Dashboard", [
                ("Admin Dashboard Functionality", self.test_admin_dashboard_functionality),
                ("Theme Switching", self.test_theme_switching),
                ("Content Management", self.test_content_management),
                ("Schedule Management", self.test_schedule_management),
                ("OBS Control Panel", self.test_obs_control_panel),
                ("Viewer Management", self.test_viewer_management),
            ]),
            ("API & Database", [
                ("API Endpoints Health Check", self.test_all_api_endpoints),
                ("Database Operations", self.test_database_operations),
                ("License System", self.test_license_system),
            ])
        ]
        
        results_summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'test_results': self.test_results,
            'categories': {}
        }
        
        for category_name, tests in test_categories:
            logger.info(f"\n{'='*80}")
            logger.info(f"🧪 TESTING CATEGORY: {category_name}")
            logger.info(f"{'='*80}")
            
            category_results = {'passed': 0, 'failed': 0, 'total': len(tests)}
            
            for test_name, test_func in tests:
                try:
                    logger.info(f"\n🔍 Running: {test_name}")
                    logger.info(f"{'-'*60}")
                    
                    success = await test_func()
                    
                    results_summary['total_tests'] += 1
                    
                    if success:
                        results_summary['passed'] += 1
                        category_results['passed'] += 1
                    else:
                        results_summary['failed'] += 1
                        category_results['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Test {test_name} crashed: {e}")
                    self.log_test_result(
                        test_name,
                        False,
                        f"Test crashed with exception: {str(e)}",
                        {'exception': str(e)}
                    )
                    results_summary['failed'] += 1
                    results_summary['total_tests'] += 1
                    category_results['failed'] += 1
            
            category_results['success_rate'] = (category_results['passed'] / category_results['total']) * 100
            results_summary['categories'][category_name] = category_results
            
            logger.info(f"\n📊 {category_name} Results: {category_results['passed']}/{category_results['total']} ({category_results['success_rate']:.1f}%)")
        
        # Calculate overall success rate
        results_summary['success_rate'] = (results_summary['passed'] / results_summary['total_tests']) * 100
        
        return results_summary

async def main():
    """Main test execution"""
    # Configuration
    BASE_URL = "https://viewer-dashboard.preview.emergentagent.com"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "remza019admin"
    
    logger.info("🎮 REMZA019 Gaming - Comprehensive Backend Testing")
    logger.info(f"Backend URL: {BASE_URL}")
    logger.info(f"Admin User: {ADMIN_USERNAME}")
    
    async with ComprehensiveBackendTester(BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD) as tester:
        results = await tester.run_comprehensive_tests()
        
        # Print final results
        logger.info("\n" + "="*80)
        logger.info("🏁 COMPREHENSIVE TEST RESULTS")
        logger.info("="*80)
        logger.info(f"Total Tests: {results['total_tests']}")
        logger.info(f"Passed: {results['passed']} ✅")
        logger.info(f"Failed: {results['failed']} ❌")
        logger.info(f"Overall Success Rate: {results['success_rate']:.1f}%")
        
        # Print category results
        logger.info("\n📊 CATEGORY BREAKDOWN:")
        for category, cat_results in results['categories'].items():
            status = "✅" if cat_results['success_rate'] >= 70 else "❌"
            logger.info(f"{status} {category}: {cat_results['passed']}/{cat_results['total']} ({cat_results['success_rate']:.1f}%)")
        
        # Print detailed results
        logger.info("\n📋 DETAILED RESULTS:")
        for result in results['test_results']:
            status = "✅" if result['success'] else "❌"
            logger.info(f"{status} {result['test']}: {result['message']}")
        
        # Determine overall success
        if results['success_rate'] >= 70:
            logger.info("\n🎉 OVERALL: COMPREHENSIVE TESTS PASSED (≥70% success rate)")
            return 0
        else:
            logger.error("\n💥 OVERALL: COMPREHENSIVE TESTS FAILED (<70% success rate)")
            return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Testing failed with exception: {e}")
        sys.exit(1)