#!/usr/bin/env python3
"""
NIVO 1 - CELOVIT BACKEND TEST - Sve nove funkcionalnosti
Comprehensive testing for all NIVO 1 systems:
1. POLLS SYSTEM 🗳️
2. PREDICTIONS SYSTEM 🎯  
3. LEADERBOARD SYSTEM 🏆
4. EMAIL NOTIFICATIONS 📧
5. STATS DASHBOARD 📊
6. CHAT SYSTEM 💬
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

class NIVO1Tester:
    def __init__(self):
        self.results = {
            'polls_system': {'total': 0, 'passed': 0, 'failed': 0, 'tests': {}},
            'predictions_system': {'total': 0, 'passed': 0, 'failed': 0, 'tests': {}},
            'leaderboard_system': {'total': 0, 'passed': 0, 'failed': 0, 'tests': {}},
            'email_notifications': {'total': 0, 'passed': 0, 'failed': 0, 'tests': {}},
            'stats_dashboard': {'total': 0, 'passed': 0, 'failed': 0, 'tests': {}},
            'chat_system': {'total': 0, 'passed': 0, 'failed': 0, 'tests': {}},
            'overall': {'total': 0, 'passed': 0, 'failed': 0}
        }
        self.session = None
        self.admin_token = None
        
        # Test data storage
        self.test_poll_id = None
        self.test_poll_option_id = None
        self.test_prediction_id = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up NIVO 1 test environment...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Get admin authentication
        await self.authenticate_admin()

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    async def authenticate_admin(self):
        """Authenticate as admin for protected endpoints"""
        print("🔐 Authenticating as admin...")
        
        login_data = {"username": "admin", "password": "remza019admin"}
        
        try:
            async with self.session.post(f"{API_BASE_URL}/admin/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("token"):
                        self.admin_token = result["token"]
                        print("✅ Admin authentication successful")
                        return True
                    else:
                        print("❌ Admin authentication failed - no token received")
                        return False
                else:
                    print(f"❌ Admin authentication failed - HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False

    def log_test_result(self, system, test_name, passed, details=""):
        """Log test result for specific system"""
        self.results[system]['total'] += 1
        self.results['overall']['total'] += 1
        
        if passed:
            self.results[system]['passed'] += 1
            self.results['overall']['passed'] += 1
            print(f"✅ {test_name}")
        else:
            self.results[system]['failed'] += 1
            self.results['overall']['failed'] += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   Details: {details}")
        
        self.results[system]['tests'][test_name] = {
            'passed': passed,
            'details': details
        }

    async def make_request(self, method, endpoint, data=None, auth_required=False, expected_status=200):
        """Make HTTP request with optional authentication"""
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth_required and self.admin_token:
            headers["Authorization"] = f"Bearer {self.admin_token}"
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=headers if auth_required else None) as response:
                    status = response.status
                    if status == expected_status:
                        if response.content_type == 'application/json':
                            result = await response.json()
                        else:
                            result = await response.text()
                        return True, result
                    else:
                        return False, f"HTTP {status}"
            elif method == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        if response.content_type == 'application/json':
                            result = await response.json()
                        else:
                            result = await response.text()
                        return True, result
                    else:
                        return False, f"HTTP {status}"
            elif method == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        if response.content_type == 'application/json':
                            result = await response.json()
                        else:
                            result = await response.text()
                        return True, result
                    else:
                        return False, f"HTTP {status}"
        except Exception as e:
            return False, str(e)

    async def test_polls_system(self):
        """Test POLLS SYSTEM 🗳️ - 6 endpoints"""
        print("\n🗳️  TESTING POLLS SYSTEM")
        print("=" * 50)
        
        # 1. POST /api/polls/create (admin auth required)
        poll_data = {
            "question": "Best game?",
            "options": ["Fortnite", "Valorant", "CS2"]
        }
        
        success, result = await self.make_request("POST", "/polls/create", poll_data, auth_required=True)
        self.log_test_result('polls_system', "POST /api/polls/create (admin auth)", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict) and result.get('poll', {}).get('id'):
            self.test_poll_id = result['poll']['id']
            # Get first option ID for voting
            options = result['poll'].get('options', [])
            if options:
                self.test_poll_option_id = options[0]['id']
            print(f"   📝 Created poll ID: {self.test_poll_id}")
        
        # 2. GET /api/polls/active
        success, result = await self.make_request("GET", "/polls/active")
        self.log_test_result('polls_system', "GET /api/polls/active", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, list):
            print(f"   📊 Found {len(result)} active polls")
        
        # 3. POST /api/polls/vote
        if self.test_poll_id and self.test_poll_option_id:
            vote_data = {
                "poll_id": self.test_poll_id,
                "option_id": self.test_poll_option_id,
                "user_id": "test123",
                "username": "TestUser"
            }
            
            success, result = await self.make_request("POST", "/polls/vote", vote_data)
            self.log_test_result('polls_system', "POST /api/polls/vote", success, 
                               "" if success else str(result))
        else:
            self.log_test_result('polls_system', "POST /api/polls/vote", False, "No poll ID or option ID available")
        
        # 4. GET /api/polls/results/{poll_id}
        if self.test_poll_id:
            success, result = await self.make_request("GET", f"/polls/results/{self.test_poll_id}")
            self.log_test_result('polls_system', f"GET /api/polls/results/{self.test_poll_id}", success, 
                               "" if success else str(result))
            
            if success and isinstance(result, dict):
                print(f"   📈 Poll results retrieved successfully")
        else:
            self.log_test_result('polls_system', "GET /api/polls/results/{poll_id}", False, "No poll ID available")
        
        # 5. POST /api/polls/end/{poll_id} (admin auth)
        if self.test_poll_id:
            success, result = await self.make_request("POST", f"/polls/end/{self.test_poll_id}", 
                                                    auth_required=True)
            self.log_test_result('polls_system', f"POST /api/polls/end/{self.test_poll_id} (admin auth)", success, 
                               "" if success else str(result))
        else:
            self.log_test_result('polls_system', "POST /api/polls/end/{poll_id} (admin auth)", False, "No poll ID available")
        
        # 6. DELETE /api/polls/{poll_id} (admin auth)
        if self.test_poll_id:
            success, result = await self.make_request("DELETE", f"/polls/{self.test_poll_id}", 
                                                    auth_required=True)
            self.log_test_result('polls_system', f"DELETE /api/polls/{self.test_poll_id} (admin auth)", success, 
                               "" if success else str(result))
        else:
            self.log_test_result('polls_system', "DELETE /api/polls/{poll_id} (admin auth)", False, "No poll ID available")

    async def test_predictions_system(self):
        """Test PREDICTIONS SYSTEM 🎯 - 6 endpoints"""
        print("\n🎯 TESTING PREDICTIONS SYSTEM")
        print("=" * 50)
        
        # 1. POST /api/predictions/create (admin auth)
        prediction_data = {
            "question": "Will we win?",
            "option_a": "Yes",
            "option_b": "No"
        }
        
        success, result = await self.make_request("POST", "/predictions/create", prediction_data, auth_required=True)
        self.log_test_result('predictions_system', "POST /api/predictions/create (admin auth)", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict) and result.get('prediction', {}).get('id'):
            self.test_prediction_id = result['prediction']['id']
            print(f"   🎯 Created prediction ID: {self.test_prediction_id}")
        
        # 2. GET /api/predictions/active
        success, result = await self.make_request("GET", "/predictions/active")
        self.log_test_result('predictions_system', "GET /api/predictions/active", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, list):
            print(f"   📊 Found {len(result)} active predictions")
        
        # 3. POST /api/predictions/predict
        if self.test_prediction_id:
            predict_data = {
                "prediction_id": self.test_prediction_id,
                "choice": "a",
                "user_id": "test456",
                "username": "TestUser2"
            }
            
            success, result = await self.make_request("POST", "/predictions/predict", predict_data)
            self.log_test_result('predictions_system', "POST /api/predictions/predict", success, 
                               "" if success else str(result))
        else:
            self.log_test_result('predictions_system', "POST /api/predictions/predict", False, "No prediction ID available")
        
        # 4. GET /api/predictions/results/{prediction_id}
        if self.test_prediction_id:
            success, result = await self.make_request("GET", f"/predictions/results/{self.test_prediction_id}")
            self.log_test_result('predictions_system', f"GET /api/predictions/results/{self.test_prediction_id}", success, 
                               "" if success else str(result))
            
            if success and isinstance(result, dict):
                print(f"   📈 Prediction results retrieved successfully")
        else:
            self.log_test_result('predictions_system', "GET /api/predictions/results/{prediction_id}", False, "No prediction ID available")
        
        # 5. POST /api/predictions/resolve/{prediction_id} (admin auth)
        if self.test_prediction_id:
            resolve_data = {"result": "a"}
            
            success, result = await self.make_request("POST", f"/predictions/resolve/{self.test_prediction_id}", 
                                                    resolve_data, auth_required=True)
            self.log_test_result('predictions_system', f"POST /api/predictions/resolve/{self.test_prediction_id} (admin auth)", success, 
                               "" if success else str(result))
        else:
            self.log_test_result('predictions_system', "POST /api/predictions/resolve/{prediction_id} (admin auth)", False, "No prediction ID available")
        
        # 6. DELETE /api/predictions/{prediction_id} (admin auth)
        if self.test_prediction_id:
            success, result = await self.make_request("DELETE", f"/predictions/{self.test_prediction_id}", 
                                                    auth_required=True)
            self.log_test_result('predictions_system', f"DELETE /api/predictions/{self.test_prediction_id} (admin auth)", success, 
                               "" if success else str(result))
        else:
            self.log_test_result('predictions_system', "DELETE /api/predictions/{prediction_id} (admin auth)", False, "No prediction ID available")

    async def test_leaderboard_system(self):
        """Test LEADERBOARD SYSTEM 🏆 - 5 endpoints"""
        print("\n🏆 TESTING LEADERBOARD SYSTEM")
        print("=" * 50)
        
        # 1. POST /api/leaderboard/update (user 1)
        user1_data = {
            "user_id": "user1",
            "username": "TopPlayer",
            "points": 500,
            "level": 3
        }
        
        success, result = await self.make_request("POST", "/leaderboard/update", user1_data)
        self.log_test_result('leaderboard_system', "POST /api/leaderboard/update (user 1)", success, 
                           "" if success else str(result))
        
        # 2. POST /api/leaderboard/update (user 2)
        user2_data = {
            "user_id": "user2",
            "username": "ProGamer",
            "points": 300,
            "level": 2
        }
        
        success, result = await self.make_request("POST", "/leaderboard/update", user2_data)
        self.log_test_result('leaderboard_system', "POST /api/leaderboard/update (user 2)", success, 
                           "" if success else str(result))
        
        # 3. GET /api/leaderboard/top?limit=10
        success, result = await self.make_request("GET", "/leaderboard/top?limit=10")
        self.log_test_result('leaderboard_system', "GET /api/leaderboard/top?limit=10", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, list):
            print(f"   🏆 Found {len(result)} players in leaderboard")
            if result:
                top_player = result[0]
                print(f"   👑 Top player: {top_player.get('username', 'Unknown')} with {top_player.get('points', 0)} points")
        
        # 4. GET /api/leaderboard/user/user1
        success, result = await self.make_request("GET", "/leaderboard/user/user1")
        self.log_test_result('leaderboard_system', "GET /api/leaderboard/user/user1", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict):
            print(f"   👤 User1 stats: {result.get('points', 0)} points, level {result.get('level', 0)}")
        
        # 5. GET /api/leaderboard/stats
        success, result = await self.make_request("GET", "/leaderboard/stats")
        self.log_test_result('leaderboard_system', "GET /api/leaderboard/stats", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict):
            print(f"   📊 Leaderboard stats: {result}")

    async def test_email_notifications(self):
        """Test EMAIL NOTIFICATIONS 📧 - 2 endpoints"""
        print("\n📧 TESTING EMAIL NOTIFICATIONS")
        print("=" * 50)
        
        # 1. GET /api/email/subscribers/count
        success, result = await self.make_request("GET", "/email/subscribers/count")
        self.log_test_result('email_notifications', "GET /api/email/subscribers/count", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict):
            count = result.get('count', 0)
            print(f"   📊 Subscriber count: {count}")
        
        # 2. POST /api/email/test
        success, result = await self.make_request("POST", "/email/test?email=test@example.com")
        self.log_test_result('email_notifications', "POST /api/email/test", success, 
                           "" if success else str(result))
        
        if success:
            print("   📧 Test email functionality working (SMTP sending skipped if not configured)")

    async def test_stats_dashboard(self):
        """Test STATS DASHBOARD 📊 - 5 endpoints"""
        print("\n📊 TESTING STATS DASHBOARD")
        print("=" * 50)
        
        # 1. GET /api/stats/dashboard
        success, result = await self.make_request("GET", "/stats/dashboard")
        self.log_test_result('stats_dashboard', "GET /api/stats/dashboard", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict):
            print(f"   📊 Dashboard stats retrieved: {len(result)} metrics")
        
        # 2. GET /api/stats/points-distribution
        success, result = await self.make_request("GET", "/stats/points-distribution")
        self.log_test_result('stats_dashboard', "GET /api/stats/points-distribution", success, 
                           "" if success else str(result))
        
        if success:
            print("   📈 Points distribution data retrieved")
        
        # 3. GET /api/stats/activity-chart?days=7
        success, result = await self.make_request("GET", "/stats/activity-chart?days=7")
        self.log_test_result('stats_dashboard', "GET /api/stats/activity-chart?days=7", success, 
                           "" if success else str(result))
        
        if success:
            print("   📈 Activity chart data (7 days) retrieved")
        
        # 4. GET /api/stats/top-activities
        success, result = await self.make_request("GET", "/stats/top-activities")
        self.log_test_result('stats_dashboard', "GET /api/stats/top-activities", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, list):
            print(f"   🎯 Top activities: {len(result)} activities found")
        
        # 5. GET /api/stats/engagement-rate
        success, result = await self.make_request("GET", "/stats/engagement-rate")
        self.log_test_result('stats_dashboard', "GET /api/stats/engagement-rate", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict):
            rate = result.get('engagement_rate', 0)
            print(f"   📊 Engagement rate: {rate}%")

    async def test_chat_system(self):
        """Test CHAT SYSTEM 💬 - 2 endpoints (existing)"""
        print("\n💬 TESTING CHAT SYSTEM (EXISTING)")
        print("=" * 50)
        
        # 1. GET /api/chat/messages
        success, result = await self.make_request("GET", "/chat/messages")
        self.log_test_result('chat_system', "GET /api/chat/messages", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, list):
            print(f"   💬 Found {len(result)} chat messages")
        
        # 2. GET /api/chat/online-count
        success, result = await self.make_request("GET", "/chat/online-count")
        self.log_test_result('chat_system', "GET /api/chat/online-count", success, 
                           "" if success else str(result))
        
        if success and isinstance(result, dict):
            count = result.get('count', 0)
            print(f"   👥 Online users: {count}")

    async def run_all_tests(self):
        """Run all NIVO 1 system tests"""
        print("🚀 STARTING NIVO 1 - CELOVIT BACKEND TEST")
        print("=" * 60)
        print("Testing all new functionalities:")
        print("1. POLLS SYSTEM 🗳️")
        print("2. PREDICTIONS SYSTEM 🎯")
        print("3. LEADERBOARD SYSTEM 🏆")
        print("4. EMAIL NOTIFICATIONS 📧")
        print("5. STATS DASHBOARD 📊")
        print("6. CHAT SYSTEM 💬")
        print("=" * 60)
        
        await self.setup()
        
        if not self.admin_token:
            print("❌ CRITICAL: Admin authentication failed. Cannot test admin-protected endpoints.")
            return
        
        # Run all system tests
        await self.test_polls_system()
        await self.test_predictions_system()
        await self.test_leaderboard_system()
        await self.test_email_notifications()
        await self.test_stats_dashboard()
        await self.test_chat_system()
        
        await self.cleanup()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 NIVO 1 - CELOVIT BACKEND TEST RESULTS")
        print("=" * 60)
        
        systems = [
            ('polls_system', 'POLLS SYSTEM 🗳️'),
            ('predictions_system', 'PREDICTIONS SYSTEM 🎯'),
            ('leaderboard_system', 'LEADERBOARD SYSTEM 🏆'),
            ('email_notifications', 'EMAIL NOTIFICATIONS 📧'),
            ('stats_dashboard', 'STATS DASHBOARD 📊'),
            ('chat_system', 'CHAT SYSTEM 💬')
        ]
        
        for system_key, system_name in systems:
            system_results = self.results[system_key]
            total = system_results['total']
            passed = system_results['passed']
            failed = system_results['failed']
            
            if total > 0:
                success_rate = (passed / total) * 100
                status = "✅ OPERATIONAL" if success_rate >= 80 else "⚠️ PARTIAL" if success_rate >= 50 else "❌ FAILED"
                print(f"{system_name}: {status} ({passed}/{total} tests passed - {success_rate:.1f}%)")
            else:
                print(f"{system_name}: ❓ NOT TESTED")
        
        print("\n" + "=" * 60)
        overall = self.results['overall']
        overall_success_rate = (overall['passed'] / overall['total']) * 100 if overall['total'] > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {overall['total']}")
        print(f"   Passed: {overall['passed']}")
        print(f"   Failed: {overall['failed']}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            print("🎉 EXCELLENT: All NIVO 1 systems are fully operational!")
        elif overall_success_rate >= 75:
            print("✅ GOOD: Most NIVO 1 systems are working correctly")
        elif overall_success_rate >= 50:
            print("⚠️ PARTIAL: Some NIVO 1 systems need attention")
        else:
            print("❌ CRITICAL: Major issues with NIVO 1 systems")
        
        print("=" * 60)
        
        # Print failed tests details
        failed_tests = []
        for system_key, system_name in systems:
            for test_name, test_result in self.results[system_key]['tests'].items():
                if not test_result['passed']:
                    failed_tests.append(f"{system_name}: {test_name} - {test_result['details']}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS DETAILS:")
            for failed_test in failed_tests:
                print(f"   • {failed_test}")
        
        print("\n🔧 Admin credentials used: admin/remza019admin")
        print("📝 All endpoint tests completed as per NIVO 1 specification")

async def main():
    """Main test execution"""
    tester = NIVO1Tester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())