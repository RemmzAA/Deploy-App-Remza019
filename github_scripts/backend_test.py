#!/usr/bin/env python3
"""
VIEWER CONFIG API TESTING - REMZA019 Gaming Backend
Testing newly implemented Viewer Config system endpoints

Test Focus:
1. GET /api/viewer-config/current - Get complete viewer config
2. GET /api/viewer-config/points - Get points configuration (9 activities)
3. GET /api/viewer-config/levels - Get level system (6 levels)
4. GET /api/viewer-config/stats - Get viewer statistics (with admin auth)

Backend URL: Use REACT_APP_BACKEND_URL from /app/frontend/.env
Success Criteria: All endpoints return 200 OK, correct data structures, proper config data
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend .env
BACKEND_URL = "https://deployed-app.preview.emergentagent.com"

class ViewerConfigTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        self.admin_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str, data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
        if data and success:
            if isinstance(data, dict):
                if "config" in data:
                    config = data["config"]
                    if isinstance(config, dict):
                        print(f"   ⚙️ Config sections: {list(config.keys())}")
                elif "points_config" in data:
                    points = data["points_config"]
                    if isinstance(points, dict):
                        print(f"   🎯 Found {len(points)} point activities")
                elif "level_system" in data:
                    levels = data["level_system"]
                    if isinstance(levels, dict):
                        print(f"   📊 Found {len(levels)} levels")
                elif "stats" in data:
                    stats = data["stats"]
                    if isinstance(stats, dict):
                        print(f"   📈 Stats keys: {list(stats.keys())}")
    
    async def admin_login(self):
        """Login as admin to get JWT token"""
        try:
            login_data = {
                "username": "admin",
                "password": "remza019admin"
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/admin/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    if result.get("success") and result.get("token"):
                        self.admin_token = result["token"]
                        self.log_test("Admin Login", True, f"Successfully logged in as admin")
                        return True
                    else:
                        self.log_test("Admin Login", False, f"Login failed: {result.get('message', 'Unknown error')}")
                        return False
                else:
                    text = await response.text()
                    self.log_test("Admin Login", False, f"HTTP {response.status}: {text}")
                    return False
                    
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    async def test_viewer_config_current(self):
        """Test GET /api/viewer-config/current - Get complete viewer config"""
        try:
            async with self.session.get(f"{self.backend_url}/api/viewer-config/current") as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if "success" not in data:
                        self.log_test("Viewer Config Current - Structure", False, "Response missing 'success' key", data)
                        return False
                    
                    if not data.get("success"):
                        # Check if it's a "no config found" case
                        if "No config found" in data.get("message", ""):
                            self.log_test("Viewer Config Current - No Config", False, 
                                        "No viewer config found in database - needs initialization", data)
                            return False
                        else:
                            self.log_test("Viewer Config Current - Success", False, 
                                        f"API returned success: false - {data.get('message', 'Unknown error')}", data)
                            return False
                    
                    # Check for config data
                    if "config" not in data:
                        self.log_test("Viewer Config Current - Config Missing", False, "Response missing 'config' key", data)
                        return False
                    
                    config = data["config"]
                    
                    # Validate config structure - should have main sections
                    expected_sections = ["points_config", "level_system", "rewards", "system_settings"]
                    found_sections = [section for section in expected_sections if section in config]
                    
                    self.log_test("Viewer Config Current - Sections", True, 
                                f"Found config sections: {found_sections}", data)
                    
                    # Check for points_config specifically
                    if "points_config" in config:
                        points_config = config["points_config"]
                        if isinstance(points_config, dict):
                            self.log_test("Viewer Config Current - Points Config", True, 
                                        f"Points config found with {len(points_config)} activities", data)
                        else:
                            self.log_test("Viewer Config Current - Points Config Type", False, 
                                        "Points config is not a dictionary", data)
                    
                    # Check for level_system specifically
                    if "level_system" in config:
                        level_system = config["level_system"]
                        if isinstance(level_system, dict):
                            self.log_test("Viewer Config Current - Level System", True, 
                                        f"Level system found with {len(level_system)} levels", data)
                        else:
                            self.log_test("Viewer Config Current - Level System Type", False, 
                                        "Level system is not a dictionary", data)
                    
                    return True
                    
                else:
                    text = await response.text()
                    self.log_test("Viewer Config Current", False, f"HTTP {response.status}: {text}")
                    return False
                    
        except Exception as e:
            self.log_test("Viewer Config Current", False, f"Exception: {str(e)}")
            return False
    
    async def test_viewer_config_points(self):
        """Test GET /api/viewer-config/points - Get points configuration (9 activities)"""
        try:
            async with self.session.get(f"{self.backend_url}/api/viewer-config/points") as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if "success" not in data:
                        self.log_test("Viewer Config Points - Structure", False, "Response missing 'success' key", data)
                        return False
                    
                    if not data.get("success"):
                        self.log_test("Viewer Config Points - Success", False, 
                                    f"API returned success: false - {data.get('message', 'Unknown error')}", data)
                        return False
                    
                    # Check for points_config data
                    if "points_config" not in data:
                        self.log_test("Viewer Config Points - Config Missing", False, "Response missing 'points_config' key", data)
                        return False
                    
                    points_config = data["points_config"]
                    
                    # Check if points_config is a dictionary
                    if not isinstance(points_config, dict):
                        self.log_test("Viewer Config Points - Type", False, "Points config is not a dictionary", data)
                        return False
                    
                    # Validate activity count (should be 9 as per review request)
                    expected_count = 9
                    actual_count = len(points_config)
                    
                    if actual_count != expected_count:
                        self.log_test("Viewer Config Points - Count", False, 
                                    f"Expected {expected_count} point activities, got {actual_count}", data)
                    else:
                        self.log_test("Viewer Config Points - Count", True, 
                                    f"Correct activity count: {actual_count}", data)
                    
                    # Validate activity structure
                    required_fields = ["points", "name", "enabled", "icon"]
                    
                    for activity_key, activity_config in points_config.items():
                        if not isinstance(activity_config, dict):
                            self.log_test(f"Viewer Config Points - {activity_key} Type", False, 
                                        f"Activity config is not a dictionary", activity_config)
                            return False
                        
                        missing_fields = [field for field in required_fields if field not in activity_config]
                        if missing_fields:
                            self.log_test(f"Viewer Config Points - {activity_key} Structure", False, 
                                        f"Missing fields: {missing_fields}", activity_config)
                            return False
                    
                    self.log_test("Viewer Config Points - Structure Validation", True, 
                                "All activities have required fields (points, name, enabled, icon)", data)
                    
                    # List found activities
                    activities = list(points_config.keys())
                    self.log_test("Viewer Config Points - Activities", True, 
                                f"Found activities: {activities}", data)
                    
                    return True
                    
                else:
                    text = await response.text()
                    self.log_test("Viewer Config Points", False, f"HTTP {response.status}: {text}")
                    return False
                    
        except Exception as e:
            self.log_test("Viewer Config Points", False, f"Exception: {str(e)}")
            return False
    
    async def test_viewer_config_levels(self):
        """Test GET /api/viewer-config/levels - Get level system (6 levels)"""
        try:
            async with self.session.get(f"{self.backend_url}/api/viewer-config/levels") as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if "success" not in data:
                        self.log_test("Viewer Config Levels - Structure", False, "Response missing 'success' key", data)
                        return False
                    
                    if not data.get("success"):
                        self.log_test("Viewer Config Levels - Success", False, 
                                    f"API returned success: false - {data.get('message', 'Unknown error')}", data)
                        return False
                    
                    # Check for level_system data
                    if "level_system" not in data:
                        self.log_test("Viewer Config Levels - System Missing", False, "Response missing 'level_system' key", data)
                        return False
                    
                    level_system = data["level_system"]
                    
                    # Check if level_system is a dictionary
                    if not isinstance(level_system, dict):
                        self.log_test("Viewer Config Levels - Type", False, "Level system is not a dictionary", data)
                        return False
                    
                    # Validate level count (should be 6 as per review request)
                    expected_count = 6
                    actual_count = len(level_system)
                    
                    if actual_count != expected_count:
                        self.log_test("Viewer Config Levels - Count", False, 
                                    f"Expected {expected_count} levels, got {actual_count}", data)
                    else:
                        self.log_test("Viewer Config Levels - Count", True, 
                                    f"Correct level count: {actual_count}", data)
                    
                    # Validate level structure
                    required_fields = ["required", "name", "features", "icon"]
                    
                    for level_key, level_config in level_system.items():
                        if not isinstance(level_config, dict):
                            self.log_test(f"Viewer Config Levels - {level_key} Type", False, 
                                        f"Level config is not a dictionary", level_config)
                            return False
                        
                        missing_fields = [field for field in required_fields if field not in level_config]
                        if missing_fields:
                            self.log_test(f"Viewer Config Levels - {level_key} Structure", False, 
                                        f"Missing fields: {missing_fields}", level_config)
                            return False
                    
                    self.log_test("Viewer Config Levels - Structure Validation", True, 
                                "All levels have required fields (required, name, features, icon)", data)
                    
                    # Check for level progression (1-6)
                    expected_levels = ["1", "2", "3", "4", "5", "6"]
                    found_levels = list(level_system.keys())
                    
                    missing_levels = [level for level in expected_levels if level not in found_levels]
                    if missing_levels:
                        self.log_test("Viewer Config Levels - Level Range", False, 
                                    f"Missing levels: {missing_levels}", data)
                    else:
                        self.log_test("Viewer Config Levels - Level Range", True, 
                                    "All levels 1-6 present in system", data)
                    
                    # List level names
                    level_names = [level_config.get("name", "Unknown") for level_config in level_system.values()]
                    self.log_test("Viewer Config Levels - Level Names", True, 
                                f"Found level names: {level_names}", data)
                    
                    return True
                    
                else:
                    text = await response.text()
                    self.log_test("Viewer Config Levels", False, f"HTTP {response.status}: {text}")
                    return False
                    
        except Exception as e:
            self.log_test("Viewer Config Levels", False, f"Exception: {str(e)}")
            return False
    
    async def test_viewer_config_stats(self):
        """Test GET /api/viewer-config/stats - Get viewer statistics (with admin auth)"""
        try:
            # Need admin authentication for this endpoint
            if not self.admin_token:
                await self.admin_login()
            
            if not self.admin_token:
                self.log_test("Viewer Config Stats", False, "Admin authentication required but failed")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            async with self.session.get(f"{self.backend_url}/api/viewer-config/stats", headers=headers) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if "success" not in data:
                        self.log_test("Viewer Config Stats - Structure", False, "Response missing 'success' key", data)
                        return False
                    
                    if not data.get("success"):
                        self.log_test("Viewer Config Stats - Success", False, 
                                    f"API returned success: false - {data.get('message', 'Unknown error')}", data)
                        return False
                    
                    # Check for stats data
                    if "stats" not in data:
                        self.log_test("Viewer Config Stats - Stats Missing", False, "Response missing 'stats' key", data)
                        return False
                    
                    stats = data["stats"]
                    
                    # Check if stats is a dictionary
                    if not isinstance(stats, dict):
                        self.log_test("Viewer Config Stats - Type", False, "Stats is not a dictionary", data)
                        return False
                    
                    # Validate expected stats fields
                    expected_fields = ["total_viewers", "level_distribution", "total_points_awarded", "total_activities", "recent_registrations_7d"]
                    
                    missing_fields = [field for field in expected_fields if field not in stats]
                    if missing_fields:
                        self.log_test("Viewer Config Stats - Fields", False, 
                                    f"Missing stats fields: {missing_fields}", data)
                    else:
                        self.log_test("Viewer Config Stats - Fields", True, 
                                    "All expected stats fields present", data)
                    
                    # Validate level_distribution structure
                    if "level_distribution" in stats:
                        level_dist = stats["level_distribution"]
                        if isinstance(level_dist, dict):
                            expected_level_keys = ["level_1", "level_2", "level_3", "level_4", "level_5", "level_6"]
                            found_level_keys = [key for key in expected_level_keys if key in level_dist]
                            
                            self.log_test("Viewer Config Stats - Level Distribution", True, 
                                        f"Found level distribution keys: {found_level_keys}", data)
                        else:
                            self.log_test("Viewer Config Stats - Level Distribution Type", False, 
                                        "Level distribution is not a dictionary", data)
                    
                    # Display key stats
                    total_viewers = stats.get("total_viewers", 0)
                    total_points = stats.get("total_points_awarded", 0)
                    total_activities = stats.get("total_activities", 0)
                    
                    self.log_test("Viewer Config Stats - Summary", True, 
                                f"Total viewers: {total_viewers}, Total points: {total_points}, Total activities: {total_activities}", data)
                    
                    return True
                    
                else:
                    text = await response.text()
                    self.log_test("Viewer Config Stats", False, f"HTTP {response.status}: {text}")
                    return False
                    
        except Exception as e:
            self.log_test("Viewer Config Stats", False, f"Exception: {str(e)}")
            return False
    
    async def test_backend_health(self):
        """Test basic backend health"""
        try:
            async with self.session.get(f"{self.backend_url}/api/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Backend Health Check", True, f"Backend is responding: {data.get('message', 'OK')}")
                    return True
                else:
                    text = await response.text()
                    self.log_test("Backend Health Check", False, f"HTTP {response.status}: {text}")
                    return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all viewer config tests"""
        print(f"🎯 VIEWER CONFIG API TESTING - REMZA019 Gaming Backend")
        print(f"🔗 Backend URL: {self.backend_url}")
        print(f"📅 Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("Viewer Config Current", self.test_viewer_config_current),
            ("Viewer Config Points", self.test_viewer_config_points),
            ("Viewer Config Levels", self.test_viewer_config_levels),
            ("Viewer Config Stats", self.test_viewer_config_stats),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}/{total} ({(passed/total)*100:.1f}%)")
        print(f"❌ Failed: {total-passed}/{total}")
        
        if passed == total:
            print(f"🎉 ALL TESTS PASSED - Viewer Config API endpoints are fully operational!")
        else:
            print(f"⚠️  Some tests failed - Review the detailed results above")
        
        return passed, total

async def main():
    """Main test execution"""
    async with ViewerConfigTester() as tester:
        passed, total = await tester.run_all_tests()
        
        # Exit with appropriate code
        if passed == total:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure

if __name__ == "__main__":
    asyncio.run(main())