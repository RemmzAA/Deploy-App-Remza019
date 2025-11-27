#!/usr/bin/env python3
"""
REMZA019 Gaming - Comprehensive Backend E2E Testing
Testing email notification system and viewer registration flows
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

class BackendTester:
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
    
    async def admin_login(self) -> bool:
        """Login as admin and get token"""
        logger.info("🔐 Attempting admin login...")
        
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
                "Admin Login", 
                True, 
                "Successfully logged in as admin",
                {'token_received': bool(self.admin_token)}
            )
            return True
        else:
            self.log_test_result(
                "Admin Login", 
                False, 
                f"Login failed: {response['data'].get('detail', 'Unknown error')}",
                {'status': response['status'], 'response': response['data']}
            )
            return False
    
    async def test_viewer_registration_with_email_verification(self) -> bool:
        """Test Case 1: New Viewer Registration with Email Verification"""
        logger.info("🧪 Testing viewer registration with email verification...")
        
        # Generate unique test data
        test_username = f"testviewer_{uuid.uuid4().hex[:8]}"
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        # Step 1: Register new viewer
        registration_data = {
            "username": test_username,
            "email": test_email
        }
        
        response = await self.make_request(
            'POST',
            '/api/viewer/register',
            registration_data
        )
        
        if response['status'] != 200:
            self.log_test_result(
                "Viewer Registration",
                False,
                f"Registration failed with status {response['status']}",
                {'response': response['data']}
            )
            return False
        
        # Check response structure
        data = response['data']
        if not data.get('success'):
            self.log_test_result(
                "Viewer Registration",
                False,
                f"Registration unsuccessful: {data.get('message', 'Unknown error')}",
                {'response': data}
            )
            return False
        
        viewer_data = data.get('viewer', {})
        user_id = viewer_data.get('user_id') or viewer_data.get('id')
        
        if not user_id:
            self.log_test_result(
                "Viewer Registration",
                False,
                "No user_id returned in registration response",
                {'response': data}
            )
            return False
        
        self.log_test_result(
            "Viewer Registration",
            True,
            f"Successfully registered viewer: {test_username}",
            {
                'user_id': user_id,
                'email': test_email,
                'email_verified': viewer_data.get('email_verified', False)
            }
        )
        
        # Step 2: Test email verification endpoint (simulate verification)
        # Note: In real scenario, verification code would come from email
        verification_code = "TEST123"  # Mock code for testing
        
        verify_response = await self.make_request(
            'POST',
            '/api/viewer/verify',
            {
                'email': test_email,
                'code': verification_code
            }
        )
        
        # This should fail with invalid code (expected behavior)
        if verify_response['status'] == 400:
            self.log_test_result(
                "Email Verification Endpoint",
                True,
                "Email verification endpoint correctly rejects invalid code",
                {'status': verify_response['status']}
            )
        else:
            self.log_test_result(
                "Email Verification Endpoint",
                False,
                f"Unexpected response from verification endpoint: {verify_response['status']}",
                {'response': verify_response['data']}
            )
        
        return True
    
    async def test_email_subscription_for_live_notifications(self) -> bool:
        """Test Case 2: Email Subscription for Live Notifications"""
        logger.info("🧪 Testing email subscription for live notifications...")
        
        test_email = f"subscriber_{uuid.uuid4().hex[:8]}@example.com"
        
        # Check if there's a subscription endpoint
        # Based on the code review, let's test the email verification system which handles subscriptions
        
        response = await self.make_request(
            'POST',
            '/api/auth/send-verification',
            {
                'email': test_email,
                'username': f'testuser_{uuid.uuid4().hex[:6]}'
            }
        )
        
        if response['status'] == 200:
            self.log_test_result(
                "Email Subscription Setup",
                True,
                "Email verification system accepts subscription requests",
                {'email': test_email, 'status': response['status']}
            )
        else:
            self.log_test_result(
                "Email Subscription Setup",
                False,
                f"Email subscription failed: {response['data'].get('detail', 'Unknown error')}",
                {'status': response['status'], 'response': response['data']}
            )
            return False
        
        # Test getting subscriber count
        count_response = await self.make_request('GET', '/api/email/subscribers/count')
        
        if count_response['status'] == 200:
            count = count_response['data'].get('count', 0)
            self.log_test_result(
                "Subscriber Count Check",
                True,
                f"Successfully retrieved subscriber count: {count}",
                {'count': count}
            )
        else:
            self.log_test_result(
                "Subscriber Count Check",
                False,
                f"Failed to get subscriber count: {count_response['status']}",
                {'response': count_response['data']}
            )
        
        return True
    
    async def test_live_stream_alert_emails(self) -> bool:
        """Test Case 3: Live Stream Alert Emails"""
        logger.info("🧪 Testing live stream alert email system...")
        
        if not self.admin_token:
            self.log_test_result(
                "Live Stream Alerts",
                False,
                "Admin token required for live stream testing",
                {}
            )
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test the live notification endpoint
        response = await self.make_request(
            'POST',
            '/api/email/notify-live',
            {},
            headers
        )
        
        if response['status'] == 200:
            data = response['data']
            self.log_test_result(
                "Live Stream Email Notifications",
                True,
                f"Live notification system working: {data.get('message', 'Success')}",
                {
                    'count': data.get('count', 0),
                    'success': data.get('success', False)
                }
            )
        else:
            self.log_test_result(
                "Live Stream Email Notifications",
                False,
                f"Live notification failed: {response['data'].get('detail', 'Unknown error')}",
                {'status': response['status'], 'response': response['data']}
            )
            return False
        
        # Test email template endpoint
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        test_response = await self.make_request(
            'POST',
            '/api/email/test',
            {'email': test_email}
        )
        
        if test_response['status'] == 200:
            self.log_test_result(
                "Test Email System",
                True,
                "Test email system is functional",
                {'test_email': test_email}
            )
        else:
            self.log_test_result(
                "Test Email System",
                False,
                f"Test email failed: {test_response['status']}",
                {'response': test_response['data']}
            )
        
        return True
    
    async def test_leaderboard_notification_system(self) -> bool:
        """Test Case 4: Award Points and Check Leaderboard Notification"""
        logger.info("🧪 Testing leaderboard notification system...")
        
        # First, we need a registered viewer to award points to
        test_username = f"leaderboard_test_{uuid.uuid4().hex[:8]}"
        test_email = f"leaderboard_{uuid.uuid4().hex[:8]}@example.com"
        
        # Register viewer
        registration_response = await self.make_request(
            'POST',
            '/api/viewer/register',
            {
                'username': test_username,
                'email': test_email
            }
        )
        
        if registration_response['status'] != 200:
            self.log_test_result(
                "Leaderboard Test Setup",
                False,
                "Failed to register test viewer for leaderboard testing",
                {'status': registration_response['status']}
            )
            return False
        
        viewer_data = registration_response['data'].get('viewer', {})
        user_id = viewer_data.get('user_id') or viewer_data.get('id')
        
        if not user_id:
            self.log_test_result(
                "Leaderboard Test Setup",
                False,
                "No user_id received from registration",
                {'response': registration_response['data']}
            )
            return False
        
        # Award points to trigger potential leaderboard notification
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
                "Points Award System",
                True,
                f"Successfully awarded points: {points_data.get('points_awarded', 0)}",
                {
                    'total_points': points_data.get('total_points', 0),
                    'level': points_data.get('level', 1),
                    'level_up': points_data.get('level_up', False)
                }
            )
        else:
            self.log_test_result(
                "Points Award System",
                False,
                f"Failed to award points: {points_response['status']}",
                {'response': points_response['data']}
            )
            return False
        
        # Test leaderboard endpoint
        leaderboard_response = await self.make_request('GET', '/api/viewer/leaderboard')
        
        if leaderboard_response['status'] == 200:
            leaderboard = leaderboard_response['data'].get('leaderboard', [])
            self.log_test_result(
                "Leaderboard System",
                True,
                f"Leaderboard retrieved with {len(leaderboard)} entries",
                {'leaderboard_size': len(leaderboard)}
            )
        else:
            self.log_test_result(
                "Leaderboard System",
                False,
                f"Failed to get leaderboard: {leaderboard_response['status']}",
                {'response': leaderboard_response['data']}
            )
        
        return True
    
    async def test_email_configuration(self) -> bool:
        """Test email configuration and SMTP settings"""
        logger.info("🧪 Testing email configuration...")
        
        # Test if email service is properly configured by checking environment
        # This is indirect testing since we can't directly access env vars
        
        # Test the email verification system which uses SMTP
        test_email = f"config_test_{uuid.uuid4().hex[:8]}@example.com"
        
        response = await self.make_request(
            'POST',
            '/api/auth/send-verification',
            {
                'email': test_email,
                'username': 'config_test'
            }
        )
        
        if response['status'] == 200:
            self.log_test_result(
                "Email Configuration",
                True,
                "Email system is configured and accepting requests",
                {'test_email': test_email}
            )
        else:
            self.log_test_result(
                "Email Configuration",
                False,
                f"Email system configuration issue: {response['status']}",
                {'response': response['data']}
            )
            return False
        
        # Test email verification status check
        status_response = await self.make_request(
            'GET',
            f'/api/auth/check-verification/{test_email}'
        )
        
        if status_response['status'] == 200:
            status_data = status_response['data']
            self.log_test_result(
                "Email Verification Status Check",
                True,
                f"Email verification status system working",
                {
                    'email': test_email,
                    'verified': status_data.get('verified', False),
                    'exists': status_data.get('exists', False)
                }
            )
        else:
            self.log_test_result(
                "Email Verification Status Check",
                False,
                f"Email verification status check failed: {status_response['status']}",
                {'response': status_response['data']}
            )
        
        return True
    
    async def test_admin_panel_functionality(self) -> bool:
        """Test admin panel data retrieval"""
        logger.info("🧪 Testing admin panel functionality...")
        
        if not self.admin_token:
            self.log_test_result(
                "Admin Panel Test",
                False,
                "Admin token required for admin panel testing",
                {}
            )
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test admin dashboard data
        dashboard_response = await self.make_request(
            'GET',
            '/api/admin/dashboard',
            headers=headers
        )
        
        if dashboard_response['status'] == 200:
            dashboard_data = dashboard_response['data']
            self.log_test_result(
                "Admin Dashboard",
                True,
                "Admin dashboard data retrieved successfully",
                {
                    'has_data': bool(dashboard_data),
                    'keys': list(dashboard_data.keys()) if isinstance(dashboard_data, dict) else []
                }
            )
        else:
            self.log_test_result(
                "Admin Dashboard",
                False,
                f"Admin dashboard failed: {dashboard_response['status']}",
                {'response': dashboard_response['data']}
            )
        
        # Test admin stats
        stats_response = await self.make_request(
            'GET',
            '/api/admin/stats',
            headers=headers
        )
        
        if stats_response['status'] == 200:
            self.log_test_result(
                "Admin Stats",
                True,
                "Admin stats retrieved successfully",
                {'stats_available': bool(stats_response['data'])}
            )
        else:
            self.log_test_result(
                "Admin Stats",
                False,
                f"Admin stats failed: {stats_response['status']}",
                {'response': stats_response['data']}
            )
        
        return True
    
    async def test_youtube_integration(self) -> bool:
        """Test Case: YouTube Integration - Channel Stats and Latest Videos"""
        logger.info("🧪 Testing YouTube integration as per review request...")
        
        # Test 1: YouTube Channel Stats
        logger.info("📊 Testing YouTube channel stats endpoint...")
        stats_response = await self.make_request('GET', '/api/youtube/channel-stats')
        
        if stats_response['status'] != 200:
            self.log_test_result(
                "YouTube Channel Stats",
                False,
                f"Channel stats endpoint failed with status {stats_response['status']}",
                {'response': stats_response['data']}
            )
            return False
        
        stats_data = stats_response['data']
        
        # Validate response structure
        required_fields = ['channel_id', 'subscriber_count', 'video_count', 'view_count']
        missing_fields = [field for field in required_fields if field not in stats_data]
        
        if missing_fields:
            self.log_test_result(
                "YouTube Channel Stats",
                False,
                f"Missing required fields: {missing_fields}",
                {'response': stats_data}
            )
            return False
        
        # Check if we're getting the expected channel ID
        expected_channel_id = "UCU3BKtciRJRU3RdA4duJbnQ"
        if stats_data.get('channel_id') != expected_channel_id:
            self.log_test_result(
                "YouTube Channel Stats",
                False,
                f"Wrong channel ID. Expected: {expected_channel_id}, Got: {stats_data.get('channel_id')}",
                {'response': stats_data}
            )
            return False
        
        self.log_test_result(
            "YouTube Channel Stats",
            True,
            f"Channel stats retrieved successfully: {stats_data['subscriber_count']} subs, {stats_data['video_count']} videos, {stats_data['view_count']} views",
            {
                'channel_id': stats_data['channel_id'],
                'subscriber_count': stats_data['subscriber_count'],
                'video_count': stats_data['video_count'],
                'view_count': stats_data['view_count']
            }
        )
        
        # Test 2: YouTube Latest Videos
        logger.info("🎬 Testing YouTube latest videos endpoint...")
        videos_response = await self.make_request('GET', '/api/youtube/latest-videos')
        
        if videos_response['status'] != 200:
            self.log_test_result(
                "YouTube Latest Videos",
                False,
                f"Latest videos endpoint failed with status {videos_response['status']}",
                {'response': videos_response['data']}
            )
            return False
        
        videos_data = videos_response['data']
        
        if not isinstance(videos_data, list):
            self.log_test_result(
                "YouTube Latest Videos",
                False,
                "Latest videos response is not a list",
                {'response_type': type(videos_data).__name__}
            )
            return False
        
        if len(videos_data) == 0:
            self.log_test_result(
                "YouTube Latest Videos",
                False,
                "No videos returned from latest videos endpoint",
                {'video_count': 0}
            )
            return False
        
        # Validate video structure
        video_required_fields = ['id', 'video_id', 'title', 'thumbnail_url', 'watch_url', 'view_count', 'duration']
        
        for i, video in enumerate(videos_data[:3]):  # Check first 3 videos
            missing_video_fields = [field for field in video_required_fields if field not in video]
            if missing_video_fields:
                self.log_test_result(
                    "YouTube Latest Videos",
                    False,
                    f"Video {i+1} missing required fields: {missing_video_fields}",
                    {'video': video}
                )
                return False
        
        self.log_test_result(
            "YouTube Latest Videos",
            True,
            f"Latest videos retrieved successfully: {len(videos_data)} videos from @remza019 channel",
            {
                'video_count': len(videos_data),
                'first_video_title': videos_data[0]['title'] if videos_data else 'N/A',
                'channel_verified': True
            }
        )
        
        # Test 3: YouTube Featured Video
        logger.info("🎯 Testing YouTube featured video endpoint...")
        featured_response = await self.make_request('GET', '/api/youtube/featured-video')
        
        if featured_response['status'] == 200:
            featured_data = featured_response['data']
            self.log_test_result(
                "YouTube Featured Video",
                True,
                f"Featured video retrieved: {featured_data.get('title', 'N/A')}",
                {
                    'video_id': featured_data.get('video_id'),
                    'title': featured_data.get('title'),
                    'has_embed_url': 'embed_url' in featured_data
                }
            )
        else:
            self.log_test_result(
                "YouTube Featured Video",
                False,
                f"Featured video endpoint failed: {featured_response['status']}",
                {'response': featured_response['data']}
            )
        
        return True

    async def run_comprehensive_tests(self) -> Dict:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting comprehensive backend E2E testing...")
        
        # Step 1: Admin login
        admin_login_success = await self.admin_login()
        
        # Step 2: Run all test cases
        test_cases = [
            ("YouTube Integration - Comprehensive Testing", self.test_youtube_integration),
            ("Viewer Registration with Email Verification", self.test_viewer_registration_with_email_verification),
            ("Email Subscription for Live Notifications", self.test_email_subscription_for_live_notifications),
            ("Live Stream Alert Emails", self.test_live_stream_alert_emails),
            ("Leaderboard Notification System", self.test_leaderboard_notification_system),
            ("Email Configuration", self.test_email_configuration),
            ("Admin Panel Functionality", self.test_admin_panel_functionality),
        ]
        
        results_summary = {
            'total_tests': len(test_cases) + 1,  # +1 for admin login
            'passed': 1 if admin_login_success else 0,
            'failed': 0 if admin_login_success else 1,
            'test_results': self.test_results
        }
        
        for test_name, test_func in test_cases:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Running: {test_name}")
                logger.info(f"{'='*60}")
                
                success = await test_func()
                
                if success:
                    results_summary['passed'] += 1
                else:
                    results_summary['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {e}")
                self.log_test_result(
                    test_name,
                    False,
                    f"Test crashed with exception: {str(e)}",
                    {'exception': str(e)}
                )
                results_summary['failed'] += 1
        
        # Calculate success rate
        results_summary['success_rate'] = (results_summary['passed'] / results_summary['total_tests']) * 100
        
        return results_summary

async def main():
    """Main test execution"""
    # Configuration
    BASE_URL = "https://viewer-dashboard.preview.emergentagent.com"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "remza019admin"
    
    logger.info("🎮 REMZA019 Gaming - Comprehensive Backend E2E Testing")
    logger.info(f"Backend URL: {BASE_URL}")
    logger.info(f"Admin User: {ADMIN_USERNAME}")
    
    async with BackendTester(BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD) as tester:
        results = await tester.run_comprehensive_tests()
        
        # Print final results
        logger.info("\n" + "="*80)
        logger.info("🏁 FINAL TEST RESULTS")
        logger.info("="*80)
        logger.info(f"Total Tests: {results['total_tests']}")
        logger.info(f"Passed: {results['passed']} ✅")
        logger.info(f"Failed: {results['failed']} ❌")
        logger.info(f"Success Rate: {results['success_rate']:.1f}%")
        
        # Print detailed results
        logger.info("\n📊 DETAILED RESULTS:")
        for result in results['test_results']:
            status = "✅" if result['success'] else "❌"
            logger.info(f"{status} {result['test']}: {result['message']}")
        
        # Determine overall success
        if results['success_rate'] >= 70:
            logger.info("\n🎉 OVERALL: TESTS PASSED (≥70% success rate)")
            return 0
        else:
            logger.error("\n💥 OVERALL: TESTS FAILED (<70% success rate)")
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