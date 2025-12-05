#!/usr/bin/env python3
"""
Launch Readiness Testing Suite for 019 Solutions Website
Critical testing for portfolio API, services API, contact form, and database connectivity
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
DB_NAME = os.environ.get('DB_NAME', 'test_database')

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

class LaunchReadinessTester:
    def __init__(self):
        self.results = {
            'portfolio_api': False,
            'services_api': False,
            'contact_form': False,
            'database_connectivity': False,
            'all_endpoints': {},
            'critical_issues': [],
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0
        }
        self.session = None
        self.mongo_client = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up launch readiness test environment...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Setup MongoDB client
        try:
            self.mongo_client = AsyncIOMotorClient(MONGO_URL)
        except Exception as e:
            self.results['critical_issues'].append(f"MongoDB client setup failed: {str(e)}")

    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()

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
                self.results['critical_issues'].append(f"{test_name}: {details}")

    async def test_api_endpoint(self, endpoint, method="GET", data=None, expected_status=200):
        """Test individual API endpoint"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url) as response:
                    status = response.status
                    if status == expected_status:
                        response_data = await response.json()
                        return True, response_data
                    else:
                        return False, f"HTTP {status}"
            elif method == "POST":
                headers = {"Content-Type": "application/json"}
                async with self.session.post(url, json=data, headers=headers) as response:
                    status = response.status
                    if status == expected_status:
                        response_data = await response.json()
                        return True, response_data
                    else:
                        return False, f"HTTP {status}"
        except Exception as e:
            return False, str(e)

    async def test_portfolio_api(self):
        """Test /api/projects endpoint - CRITICAL FOR LAUNCH"""
        print("\n🎯 Testing Portfolio API (/api/projects) - LAUNCH CRITICAL...")
        
        success, result = await self.test_api_endpoint("/projects")
        self.log_test_result("Portfolio API endpoint accessibility", success, "" if success else str(result))
        
        if success and isinstance(result, list):
            self.log_test_result("Portfolio API returns project list", True)
            
            # Verify all portfolio project data is properly structured
            required_fields = ['id', 'title', 'description', 'image', 'technologies', 'category', 'live_demo']
            all_projects_valid = True
            live_urls = []
            
            for i, project in enumerate(result):
                project_valid = all(field in project for field in required_fields)
                if not project_valid:
                    missing_fields = [field for field in required_fields if field not in project]
                    self.log_test_result(f"Project {i+1} data structure", False, f"Missing fields: {missing_fields}")
                    all_projects_valid = False
                else:
                    self.log_test_result(f"Project {i+1} data structure", True)
                    
                    # Check for live URLs (not dummy links)
                    live_demo = project.get('live_demo', '')
                    live_urls.append(live_demo)
                    
                    if live_demo and not live_demo.startswith('#') and 'http' in live_demo:
                        self.log_test_result(f"Project {i+1} has valid live URL", True, f"URL: {live_demo}")
                    else:
                        self.log_test_result(f"Project {i+1} has valid live URL", False, f"Invalid URL: {live_demo}")
                        all_projects_valid = False
            
            self.log_test_result("All portfolio projects properly structured", all_projects_valid)
            self.results['portfolio_api'] = all_projects_valid
            
            print(f"📋 Found {len(result)} portfolio projects with URLs:")
            for i, url in enumerate(live_urls, 1):
                print(f"   {i}. {url}")
                
        else:
            self.log_test_result("Portfolio API returns project list", False, "Invalid response format")
            self.results['portfolio_api'] = False

    async def test_services_api(self):
        """Test /api/services endpoint - CRITICAL FOR LAUNCH"""
        print("\n🛠️  Testing Services API (/api/services) - LAUNCH CRITICAL...")
        
        success, result = await self.test_api_endpoint("/services")
        self.log_test_result("Services API endpoint accessibility", success, "" if success else str(result))
        
        if success and isinstance(result, list):
            self.log_test_result("Services API returns service list", True)
            
            # Verify all service data is complete
            required_fields = ['id', 'name', 'description', 'features', 'icon']
            all_services_valid = True
            
            for i, service in enumerate(result):
                service_valid = all(field in service for field in required_fields)
                if not service_valid:
                    missing_fields = [field for field in required_fields if field not in service]
                    self.log_test_result(f"Service {i+1} data structure", False, f"Missing fields: {missing_fields}")
                    all_services_valid = False
                else:
                    self.log_test_result(f"Service {i+1} data structure", True)
                    
                    # Verify service has meaningful content
                    if len(service.get('description', '')) < 10:
                        self.log_test_result(f"Service {i+1} has adequate description", False, "Description too short")
                        all_services_valid = False
                    else:
                        self.log_test_result(f"Service {i+1} has adequate description", True)
                        
                    if not service.get('features') or len(service.get('features', [])) < 2:
                        self.log_test_result(f"Service {i+1} has adequate features", False, "Insufficient features")
                        all_services_valid = False
                    else:
                        self.log_test_result(f"Service {i+1} has adequate features", True)
            
            self.log_test_result("All services data complete", all_services_valid)
            self.results['services_api'] = all_services_valid
            
            print(f"📋 Found {len(result)} services:")
            for i, service in enumerate(result, 1):
                print(f"   {i}. {service.get('name', 'Unknown')} - {service.get('icon', 'No icon')}")
                
        else:
            self.log_test_result("Services API returns service list", False, "Invalid response format")
            self.results['services_api'] = False

    async def test_contact_form(self):
        """Test /api/contact endpoint - CRITICAL FOR LAUNCH"""
        print("\n📧 Testing Contact Form API (/api/contact) - LAUNCH CRITICAL...")
        
        # Test contact form submission with realistic data
        contact_data = {
            "name": "John Smith",
            "email": "john.smith@techcorp.com",
            "company": "TechCorp Solutions",
            "service_interest": "Full-Stack Development",
            "message": "We are interested in developing a modern web application for our business. Could you provide more information about your full-stack development services and pricing?",
            "budget_range": "$10,000 - $25,000"
        }
        
        success, result = await self.test_api_endpoint("/contact", method="POST", data=contact_data, expected_status=200)
        self.log_test_result("Contact form submission", success, "" if success else str(result))
        
        if success and isinstance(result, dict):
            # Verify response structure
            if result.get('success') and result.get('message') and result.get('data'):
                self.log_test_result("Contact form response structure", True)
                
                # Verify submitted data is preserved
                submitted_data = result.get('data', {})
                if submitted_data.get('name') == contact_data['name'] and submitted_data.get('email') == contact_data['email']:
                    self.log_test_result("Contact form data preservation", True)
                    self.results['contact_form'] = True
                else:
                    self.log_test_result("Contact form data preservation", False, "Submitted data not preserved correctly")
                    self.results['contact_form'] = False
            else:
                self.log_test_result("Contact form response structure", False, "Missing required response fields")
                self.results['contact_form'] = False
        else:
            self.log_test_result("Contact form response format", False, "Invalid response format")
            self.results['contact_form'] = False

    async def test_database_connectivity(self):
        """Test MongoDB connection and data persistence - CRITICAL FOR LAUNCH"""
        print("\n🗄️  Testing Database Connectivity - LAUNCH CRITICAL...")
        
        try:
            # Test connection
            await self.mongo_client.admin.command('ping')
            self.log_test_result("MongoDB connection", True)
            
            # Test database access
            db = self.mongo_client[DB_NAME]
            collections = await db.list_collection_names()
            self.log_test_result("Database access", True)
            
            # Test write operation
            test_doc = {
                "test_type": "launch_readiness",
                "timestamp": datetime.utcnow(),
                "data": "Testing database write operation for launch readiness"
            }
            result = await db.launch_test.insert_one(test_doc)
            if result.inserted_id:
                self.log_test_result("Database write operation", True)
                
                # Test read operation
                found_doc = await db.launch_test.find_one({"_id": result.inserted_id})
                if found_doc:
                    self.log_test_result("Database read operation", True)
                    
                    # Clean up test document
                    await db.launch_test.delete_one({"_id": result.inserted_id})
                    self.log_test_result("Database cleanup", True)
                    
                    self.results['database_connectivity'] = True
                else:
                    self.log_test_result("Database read operation", False)
                    self.results['database_connectivity'] = False
            else:
                self.log_test_result("Database write operation", False)
                self.results['database_connectivity'] = False
                
        except Exception as e:
            self.log_test_result("Database connectivity", False, str(e))
            self.results['database_connectivity'] = False

    async def test_all_endpoints(self):
        """Test all available endpoints for functionality - CRITICAL FOR LAUNCH"""
        print("\n🔗 Testing All API Endpoints - LAUNCH CRITICAL...")
        
        # All endpoints that should be working
        endpoints = [
            ("/", "Root API endpoint"),
            ("/projects", "Portfolio projects"),
            ("/services", "Services list"),
            ("/testimonials", "Client testimonials"),
            ("/blog", "Blog posts"),
            ("/freelancers", "Freelancer profiles"),
            ("/stats", "Company statistics")
        ]
        
        all_working = True
        
        for endpoint, description in endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            self.log_test_result(f"{description} ({endpoint})", success, "" if success else str(result))
            self.results['all_endpoints'][endpoint] = success
            
            if not success:
                all_working = False
                
            # Additional validation for critical endpoints
            if success and endpoint == "/":
                if isinstance(result, dict) and result.get('message') == "019 Digital Solutions API":
                    self.log_test_result("Root endpoint message validation", True)
                else:
                    self.log_test_result("Root endpoint message validation", False, "Incorrect API message")
                    all_working = False
        
        self.log_test_result("All API endpoints functional", all_working)
        return all_working

    async def run_launch_readiness_tests(self):
        """Run all launch readiness tests"""
        print("🚀 LAUNCH READINESS TESTING - 019 SOLUTIONS WEBSITE")
        print("=" * 80)
        print("Testing critical requirements for launch:")
        print("1. Portfolio API with live URLs")
        print("2. Services API with complete data")
        print("3. Contact form functionality")
        print("4. Database connectivity and persistence")
        print("5. All API endpoints working")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run critical tests
            await self.test_portfolio_api()
            await self.test_services_api()
            await self.test_contact_form()
            await self.test_database_connectivity()
            await self.test_all_endpoints()
            
        finally:
            await self.cleanup()
        
        # Print summary
        self.print_launch_summary()
        return self.results

    def print_launch_summary(self):
        """Print launch readiness summary"""
        print("\n" + "=" * 80)
        print("🏁 LAUNCH READINESS SUMMARY")
        print("=" * 80)
        
        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 CRITICAL COMPONENTS STATUS:")
        print(f"   Portfolio API (/api/projects): {'✅ READY' if self.results['portfolio_api'] else '❌ NOT READY'}")
        print(f"   Services API (/api/services): {'✅ READY' if self.results['services_api'] else '❌ NOT READY'}")
        print(f"   Contact Form (/api/contact): {'✅ READY' if self.results['contact_form'] else '❌ NOT READY'}")
        print(f"   Database Connectivity: {'✅ READY' if self.results['database_connectivity'] else '❌ NOT READY'}")
        
        working_endpoints = sum(1 for status in self.results['all_endpoints'].values() if status)
        total_endpoints = len(self.results['all_endpoints'])
        print(f"   All API Endpoints: {working_endpoints}/{total_endpoints} working")
        
        # Overall launch readiness
        critical_components = [
            self.results['portfolio_api'],
            self.results['services_api'], 
            self.results['contact_form'],
            self.results['database_connectivity']
        ]
        
        launch_ready = all(critical_components) and working_endpoints == total_endpoints
        
        print(f"\n🚀 LAUNCH READINESS: {'✅ READY FOR LAUNCH' if launch_ready else '❌ NOT READY FOR LAUNCH'}")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES TO FIX:")
            for issue in self.results['critical_issues']:
                print(f"   • {issue}")
        
        if launch_ready:
            print("\n🎉 All critical systems are functional!")
            print("   • Portfolio projects have valid live URLs")
            print("   • Services data is complete and structured")
            print("   • Contact form processes submissions correctly")
            print("   • Database operations are working")
            print("   • All API endpoints respond with 200 status codes")
        
        print("\n" + "=" * 80)

async def main():
    """Main test runner"""
    tester = LaunchReadinessTester()
    results = await tester.run_launch_readiness_tests()
    
    # Return exit code based on critical components
    critical_ready = all([
        results['portfolio_api'],
        results['services_api'],
        results['contact_form'],
        results['database_connectivity']
    ])
    
    if critical_ready and results['failed_tests'] == 0:
        print("🎉 Website is READY FOR LAUNCH!")
        return 0
    else:
        print("⚠️  Website is NOT READY for launch - critical issues found!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)