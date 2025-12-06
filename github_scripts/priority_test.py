#!/usr/bin/env python3
"""
Priority Backend Testing for REMZA019 Gaming - Donation & Viewer Systems
Tests the critical new features as requested in the review
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://deployed-app.preview.emergentagent.com"
API_BASE_URL = f"{BACKEND_URL}/api"

class PriorityTester:
    def __init__(self):
        self.results = {
            'donation_tests': {},
            'viewer_tests': {},
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_issues': []
        }
        self.session = None

    async def setup(self):
        """Setup test environment"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()

    def log_result(self, test_name, passed, details=""):
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
                self.results['critical_issues'].append(f"{test_name}: {details}")

    async def test_api_endpoint(self, endpoint, method="GET", data=None, expected_status=200):
        """Test individual API endpoint"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url) as response:
                    if response.status == expected_status:
                        return True, await response.json()
                    else:
                        return False, f"HTTP {response.status}"
            elif method == "POST":
                headers = {"Content-Type": "application/json"}
                async with self.session.post(url, json=data, headers=headers) as response:
                    if response.status == expected_status:
                        return True, await response.json()
                    else:
                        return False, f"HTTP {response.status}"
        except Exception as e:
            return False, str(e)

    async def test_donation_system(self):
        """Test REMZA019 Gaming Donation System API - PRIORITY 1"""
        print("\n💰 PRIORITY 1: Testing Donation System API...")
        
        # Test 1: GET /api/donations/packages
        success, result = await self.test_api_endpoint("/donations/packages")
        self.log_result("Donation packages endpoint", success, "" if success else str(result))
        self.results['donation_tests']['packages'] = success
        
        if success:
            packages = result.get("packages", {})
            expected_packages = ["coffee", "pizza", "gaming_gear", "streaming_support", "custom"]
            
            # Validate all 5 packages exist
            all_packages_exist = all(pkg in packages for pkg in expected_packages)
            self.log_result("All 5 donation packages present", all_packages_exist)
            
            # Validate package structure
            if "coffee" in packages:
                coffee = packages["coffee"]
                coffee_valid = all(field in coffee for field in ["amount", "currency", "name", "description"])
                self.log_result("Coffee package structure valid", coffee_valid)
                if coffee_valid and coffee["amount"] == 5.0:
                    self.log_result("Coffee package amount correct ($5)", True)
                else:
                    self.log_result("Coffee package amount correct ($5)", False, f"Got ${coffee.get('amount', 'N/A')}")
        
        # Test 2: POST /api/donations/checkout - Coffee package
        coffee_checkout = {
            "package_id": "coffee",
            "donor_name": "Test Supporter",
            "donor_email": "test@remza019gaming.com",
            "message": "Keep up the great FORTNITE content!",
            "origin_url": "https://deployed-app.preview.emergentagent.com"
        }
        
        success, result = await self.test_api_endpoint("/donations/checkout", method="POST", data=coffee_checkout)
        self.log_result("Coffee donation checkout", success, "" if success else str(result))
        self.results['donation_tests']['checkout'] = success
        
        session_id = None
        if success:
            required_fields = ["success", "checkout_url", "session_id", "amount", "currency"]
            has_fields = all(field in result for field in required_fields)
            self.log_result("Checkout response structure", has_fields)
            
            if result.get("success") and result.get("session_id"):
                session_id = result["session_id"]
                self.log_result("Checkout session created", True)
        
        # Test 3: GET /api/donations/status/{session_id}
        if session_id:
            success, result = await self.test_api_endpoint(f"/donations/status/{session_id}")
            self.log_result("Donation status endpoint", success, "" if success else str(result))
            self.results['donation_tests']['status'] = success
        
        # Test 4: Custom amount checkout
        custom_checkout = {
            "package_id": "custom",
            "amount": 25.50,
            "donor_name": "Custom Supporter",
            "donor_email": "custom@remza019gaming.com",
            "message": "Custom support for REMZA019!",
            "origin_url": "https://deployed-app.preview.emergentagent.com"
        }
        
        success, result = await self.test_api_endpoint("/donations/checkout", method="POST", data=custom_checkout)
        self.log_result("Custom amount donation checkout", success, "" if success else str(result))
        self.results['donation_tests']['custom_checkout'] = success
        
        # Test 5: GET /api/donations/recent
        success, result = await self.test_api_endpoint("/donations/recent?limit=5")
        self.log_result("Recent donations endpoint", success, "" if success else str(result))
        self.results['donation_tests']['recent'] = success
        
        # Test 6: GET /api/donations/stats
        success, result = await self.test_api_endpoint("/donations/stats")
        self.log_result("Donation stats endpoint", success, "" if success else str(result))
        self.results['donation_tests']['stats'] = success
        
        if success:
            stats_fields = ["total_amount", "total_donations", "currency"]
            has_stats = all(field in result for field in stats_fields)
            self.log_result("Donation stats structure", has_stats)

    async def test_viewer_system(self):
        """Test REMZA019 Gaming Viewer System API - PRIORITY 2"""
        print("\n🎮 PRIORITY 2: Testing Viewer System API...")
        
        # Test 1: POST /api/viewer/register
        registration = {
            "username": f"TestGamer{datetime.now().strftime('%H%M%S')}",
            "email": f"testgamer{datetime.now().strftime('%H%M%S')}@remza019gaming.com"
        }
        
        success, result = await self.test_api_endpoint("/viewer/register", method="POST", data=registration)
        self.log_result("Viewer registration endpoint", success, "" if success else str(result))
        self.results['viewer_tests']['registration'] = success
        
        user_id = None
        if success and result.get("success") and result.get("viewer"):
            viewer = result["viewer"]
            required_fields = ["id", "username", "points", "level", "unlocked_features"]
            has_fields = all(field in viewer for field in required_fields)
            self.log_result("Registration response structure", has_fields)
            user_id = viewer.get("id")
            
            # Check initial values
            if viewer.get("points") == 10:  # Registration bonus
                self.log_result("Registration bonus awarded (10 points)", True)
            else:
                self.log_result("Registration bonus awarded (10 points)", False, f"Got {viewer.get('points')} points")
        
        # Test 2: GET /api/viewer/profile/{user_id}
        if user_id:
            success, result = await self.test_api_endpoint(f"/viewer/profile/{user_id}")
            self.log_result("Viewer profile endpoint", success, "" if success else str(result))
            self.results['viewer_tests']['profile'] = success
            
            if success:
                profile_fields = ["id", "username", "points", "level", "level_name", "unlocked_features"]
                has_fields = all(field in result for field in profile_fields)
                self.log_result("Profile response structure", has_fields)
        
        # Test 3: GET /api/viewer/levels
        success, result = await self.test_api_endpoint("/viewer/levels")
        self.log_result("Level system endpoint", success, "" if success else str(result))
        self.results['viewer_tests']['levels'] = success
        
        if success:
            levels = result.get("levels", {})
            expected_levels = ["1", "2", "3", "4", "5", "6"]
            has_all_levels = all(level in levels for level in expected_levels)
            self.log_result("6-level system complete", has_all_levels)
            
            # Check level names
            if "1" in levels and levels["1"].get("name") == "Rookie Viewer":
                self.log_result("Level 1 name correct (Rookie Viewer)", True)
            else:
                self.log_result("Level 1 name correct (Rookie Viewer)", False)
                
            if "6" in levels and levels["6"].get("name") == "Gaming Legend":
                self.log_result("Level 6 name correct (Gaming Legend)", True)
            else:
                self.log_result("Level 6 name correct (Gaming Legend)", False)
        
        # Test 4: GET /api/viewer/activities
        success, result = await self.test_api_endpoint("/viewer/activities")
        self.log_result("Available activities endpoint", success, "" if success else str(result))
        self.results['viewer_tests']['activities'] = success
        
        if success:
            activities = result.get("activities", [])
            activity_types = [act.get("type") for act in activities]
            expected_activities = ["stream_view", "chat_message", "like_video", "share_stream", "subscribe"]
            
            has_key_activities = all(act in activity_types for act in expected_activities)
            self.log_result("Key activities available", has_key_activities)
        
        # Test 5: GET /api/viewer/leaderboard
        success, result = await self.test_api_endpoint("/viewer/leaderboard?limit=10")
        self.log_result("Viewer leaderboard endpoint", success, "" if success else str(result))
        self.results['viewer_tests']['leaderboard'] = success
        
        # Test 6: GET /api/viewer/chat/messages
        success, result = await self.test_api_endpoint("/viewer/chat/messages?limit=10")
        self.log_result("Chat messages endpoint", success, "" if success else str(result))
        self.results['viewer_tests']['chat'] = success

    async def test_error_handling(self):
        """Test error handling for both systems"""
        print("\n🚨 Testing Error Handling...")
        
        # Test invalid donation package
        invalid_donation = {
            "package_id": "invalid_package",
            "donor_name": "Test User",
            "donor_email": "test@example.com",
            "message": "Test message",
            "origin_url": "https://deployed-app.preview.emergentagent.com"
        }
        
        success, result = await self.test_api_endpoint("/donations/checkout", method="POST", data=invalid_donation, expected_status=400)
        self.log_result("Invalid donation package error handling", success)
        
        # Test custom amount too low
        low_amount = {
            "package_id": "custom",
            "amount": 0.50,  # Below $1 minimum
            "donor_name": "Test User",
            "donor_email": "test@example.com",
            "message": "Test message",
            "origin_url": "https://deployed-app.preview.emergentagent.com"
        }
        
        success, result = await self.test_api_endpoint("/donations/checkout", method="POST", data=low_amount, expected_status=400)
        self.log_result("Low custom amount error handling", success)
        
        # Test non-existent viewer profile
        success, result = await self.test_api_endpoint("/viewer/profile/nonexistent_user_id", expected_status=404)
        self.log_result("Non-existent viewer error handling", success)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 REMZA019 Gaming Backend Testing Summary")
        print("="*80)
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   ✅ Passed: {self.results['passed_tests']}")
        print(f"   ❌ Failed: {self.results['failed_tests']}")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n💰 Donation System Results:")
        donation_passed = sum(1 for v in self.results['donation_tests'].values() if v)
        donation_total = len(self.results['donation_tests'])
        print(f"   Tests: {donation_passed}/{donation_total} passed")
        for test, result in self.results['donation_tests'].items():
            status = "✅" if result else "❌"
            print(f"   {status} {test}")
        
        print(f"\n🎮 Viewer System Results:")
        viewer_passed = sum(1 for v in self.results['viewer_tests'].values() if v)
        viewer_total = len(self.results['viewer_tests'])
        print(f"   Tests: {viewer_passed}/{viewer_total} passed")
        for test, result in self.results['viewer_tests'].items():
            status = "✅" if result else "❌"
            print(f"   {status} {test}")
        
        if self.results['critical_issues']:
            print(f"\n🚨 Critical Issues Found:")
            for issue in self.results['critical_issues']:
                print(f"   ❌ {issue}")
        else:
            print(f"\n🎉 No Critical Issues Found!")
        
        print("\n" + "="*80)

    async def run_priority_tests(self):
        """Run priority backend tests"""
        print("🚀 REMZA019 Gaming Priority Backend Testing")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("="*80)
        
        await self.setup()
        
        try:
            await self.test_donation_system()
            await self.test_viewer_system()
            await self.test_error_handling()
        finally:
            await self.cleanup()
        
        self.print_summary()
        
        # Return success status
        return self.results['failed_tests'] == 0

async def main():
    """Main test runner"""
    tester = PriorityTester()
    success = await tester.run_priority_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())