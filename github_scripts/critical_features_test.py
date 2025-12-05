#!/usr/bin/env python3
"""
Critical Features Testing Suite for 019 Solutions Website
Tests the specific missing features mentioned in the review request:
1. Revolutionary 3D Hero Section Backend Support
2. Freelancer Panel Search Functionality  
3. Payment System Integration
4. Portfolio Project Links Verification
5. Services Data with Modern Icons
6. Contact Form Comprehensive Testing
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

class CriticalFeaturesTester:
    def __init__(self):
        self.results = {
            'revolutionary_3d_hero_backend': False,
            'freelancer_search_functionality': False,
            'payment_system_integration': False,
            'portfolio_links_verification': False,
            'services_modern_icons': False,
            'contact_form_comprehensive': False,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_logs': []
        }
        self.session = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up critical features test environment...")
        timeout = aiohttp.ClientTimeout(total=30)
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

    async def test_revolutionary_3d_hero_backend_support(self):
        """Test if backend provides special data or endpoints for 3D hero animations"""
        print("\n🎯 Testing Revolutionary 3D Hero Section Backend Support...")
        
        # Check if there are any special endpoints for 3D content
        special_endpoints = [
            "/3d-assets",
            "/hero-animations", 
            "/particle-effects",
            "/3d-content",
            "/hero-data",
            "/animations",
            "/visual-effects"
        ]
        
        found_3d_endpoints = []
        for endpoint in special_endpoints:
            success, result = await self.test_api_endpoint(endpoint, expected_status=200)
            if success:
                found_3d_endpoints.append(endpoint)
                self.log_test_result(f"3D Hero endpoint {endpoint}", True)
            
        # Check if existing endpoints provide 3D-related data
        success, services_data = await self.test_api_endpoint("/services")
        if success:
            # Look for 3D-related services or features
            has_3d_features = False
            for service in services_data:
                service_text = f"{service.get('name', '')} {service.get('description', '')} {' '.join(service.get('features', []))}"
                if any(keyword in service_text.lower() for keyword in ['3d', 'animation', 'particle', 'visual effects', 'graphics']):
                    has_3d_features = True
                    break
            
            self.log_test_result("Services contain 3D/animation features", has_3d_features, 
                               "No 3D-related features found in services" if not has_3d_features else "")
        
        # Check stats endpoint for 3D-related metrics
        success, stats_data = await self.test_api_endpoint("/stats")
        if success:
            has_3d_stats = any(key for key in stats_data.keys() if '3d' in key.lower() or 'animation' in key.lower())
            self.log_test_result("Stats contain 3D-related metrics", has_3d_stats,
                               "No 3D-related statistics found" if not has_3d_stats else "")
        
        # Overall assessment
        self.results['revolutionary_3d_hero_backend'] = len(found_3d_endpoints) > 0 or has_3d_features
        self.log_test_result("Revolutionary 3D Hero Backend Support", self.results['revolutionary_3d_hero_backend'],
                           "Backend lacks specialized 3D/animation endpoints and data" if not self.results['revolutionary_3d_hero_backend'] else "")

    async def test_freelancer_search_functionality(self):
        """Test freelancer panel search and filtering capabilities"""
        print("\n👥 Testing Freelancer Panel Search Functionality...")
        
        # Test basic freelancers endpoint
        success, freelancers_data = await self.test_api_endpoint("/freelancers")
        if not success:
            self.log_test_result("Freelancers endpoint accessibility", False, "Freelancers endpoint not accessible")
            self.results['freelancer_search_functionality'] = False
            return
        
        self.log_test_result("Freelancers endpoint accessibility", True)
        
        # Check if freelancers data has required fields for search
        required_search_fields = ['name', 'title', 'bio', 'skills', 'availability', 'hourly_rate']
        has_search_fields = True
        missing_fields = []
        
        if freelancers_data and len(freelancers_data) > 0:
            for freelancer in freelancers_data:
                for field in required_search_fields:
                    if field not in freelancer:
                        has_search_fields = False
                        if field not in missing_fields:
                            missing_fields.append(field)
        else:
            has_search_fields = False
            missing_fields = ["No freelancer data available"]
        
        self.log_test_result("Freelancers have required search fields", has_search_fields,
                           f"Missing fields: {', '.join(missing_fields)}" if missing_fields else "")
        
        # Test search functionality with query parameters
        search_tests = [
            ("?search=developer", "Search by keyword"),
            ("?skills=React", "Filter by skills"),
            ("?availability=Available", "Filter by availability"),
            ("?rate_min=50&rate_max=100", "Filter by hourly rate range")
        ]
        
        search_functionality_working = 0
        for query_params, test_name in search_tests:
            success, result = await self.test_api_endpoint(f"/freelancers{query_params}")
            if success:
                search_functionality_working += 1
                self.log_test_result(f"Freelancer {test_name}", True)
            else:
                self.log_test_result(f"Freelancer {test_name}", False, "Search parameters not supported")
        
        # Check if there's a dedicated search endpoint
        success, result = await self.test_api_endpoint("/freelancers/search", method="POST", 
                                                     data={"query": "React developer", "skills": ["React", "Node.js"]})
        if success:
            search_functionality_working += 1
            self.log_test_result("Dedicated freelancer search endpoint", True)
        else:
            self.log_test_result("Dedicated freelancer search endpoint", False, "No dedicated search endpoint found")
        
        # Overall assessment
        self.results['freelancer_search_functionality'] = has_search_fields and search_functionality_working > 0
        self.log_test_result("Freelancer Search Functionality", self.results['freelancer_search_functionality'],
                           "Search functionality not implemented or incomplete" if not self.results['freelancer_search_functionality'] else "")

    async def test_payment_system_integration(self):
        """Test payment system endpoints thoroughly"""
        print("\n💳 Testing Payment System Integration...")
        
        # Test all payment endpoints
        payment_endpoints = [
            "/payments/create-payment-intent",
            "/payments/confirm-payment", 
            "/payments/{payment_id}"
        ]
        
        payment_functionality_score = 0
        
        # Test create payment intent
        payment_data = {
            "amount": 2500.00,
            "currency": "eur",
            "payment_method": "card",
            "description": "019 Solutions - Full-Stack Development Service",
            "customer_email": "client@019solutions.com",
            "card_number": "4242424242424242",
            "card_expiry": "12/25",
            "card_cvc": "123",
            "card_name": "Test Client"
        }
        
        success, result = await self.test_api_endpoint("/payments/create-payment-intent", method="POST", data=payment_data)
        if success and isinstance(result, dict) and result.get('success') and result.get('payment_intent_id'):
            payment_functionality_score += 1
            self.log_test_result("Create payment intent endpoint", True)
            payment_intent_id = result.get('payment_intent_id')
            
            # Test confirm payment
            success2, result2 = await self.test_api_endpoint(f"/payments/confirm-payment?payment_intent_id={payment_intent_id}", method="POST")
            if success2 and isinstance(result2, dict) and result2.get('success') and result2.get('payment_id'):
                payment_functionality_score += 1
                self.log_test_result("Confirm payment endpoint", True)
                payment_id = result2.get('payment_id')
                
                # Test get payment status
                success3, result3 = await self.test_api_endpoint(f"/payments/{payment_id}")
                if success3 and isinstance(result3, dict) and result3.get('status'):
                    payment_functionality_score += 1
                    self.log_test_result("Get payment status endpoint", True)
                else:
                    self.log_test_result("Get payment status endpoint", False, "Payment status retrieval failed")
            else:
                self.log_test_result("Confirm payment endpoint", False, "Payment confirmation failed")
        else:
            self.log_test_result("Create payment intent endpoint", False, "Payment intent creation failed")
        
        # Test payment methods support
        payment_methods = ["card", "paypal"]
        for method in payment_methods:
            test_data = payment_data.copy()
            test_data["payment_method"] = method
            success, result = await self.test_api_endpoint("/payments/create-payment-intent", method="POST", data=test_data)
            if success:
                self.log_test_result(f"Payment method support: {method}", True)
            else:
                self.log_test_result(f"Payment method support: {method}", False, f"{method} payment method not supported")
        
        # Test error handling
        invalid_payment_data = {"amount": -100, "currency": "invalid"}
        success, result = await self.test_api_endpoint("/payments/create-payment-intent", method="POST", 
                                                     data=invalid_payment_data, expected_status=422)
        self.log_test_result("Payment validation error handling", success, "Payment validation not working" if not success else "")
        
        # Overall assessment
        self.results['payment_system_integration'] = payment_functionality_score >= 3
        self.log_test_result("Payment System Integration", self.results['payment_system_integration'],
                           f"Payment system incomplete: {payment_functionality_score}/3 core functions working" if not self.results['payment_system_integration'] else "")

    async def test_portfolio_links_verification(self):
        """Test portfolio project links against expected URLs"""
        print("\n🔗 Testing Portfolio Project Links Verification...")
        
        # Expected URLs from review requirements
        expected_urls = [
            "https://019solutions.com/trading-demo",
            "https://remza019.ch", 
            "https://adriatic-dreams.ch",
            "https://berlin-apartments.ch"
        ]
        
        success, projects_data = await self.test_api_endpoint("/projects")
        if not success:
            self.log_test_result("Portfolio projects endpoint", False, "Projects endpoint not accessible")
            self.results['portfolio_links_verification'] = False
            return
        
        self.log_test_result("Portfolio projects endpoint", True)
        
        # Extract live demo URLs from projects
        found_urls = []
        if projects_data:
            for project in projects_data:
                live_demo = project.get('live_demo', '')
                if live_demo:
                    found_urls.append(live_demo)
        
        self.log_test_result("Projects have live demo URLs", len(found_urls) > 0, 
                           "No live demo URLs found in projects" if len(found_urls) == 0 else "")
        
        # Check if found URLs match expected URLs
        matching_urls = 0
        for expected_url in expected_urls:
            if expected_url in found_urls:
                matching_urls += 1
                self.log_test_result(f"Expected URL found: {expected_url}", True)
            else:
                self.log_test_result(f"Expected URL missing: {expected_url}", False, f"Found URLs: {found_urls}")
        
        # Check for incorrect URLs
        incorrect_urls = [url for url in found_urls if url not in expected_urls]
        if incorrect_urls:
            self.log_test_result("No incorrect URLs found", False, f"Incorrect URLs: {incorrect_urls}")
        else:
            self.log_test_result("No incorrect URLs found", True)
        
        # Overall assessment
        self.results['portfolio_links_verification'] = matching_urls == len(expected_urls) and len(incorrect_urls) == 0
        self.log_test_result("Portfolio Links Verification", self.results['portfolio_links_verification'],
                           f"URL mismatch: {matching_urls}/{len(expected_urls)} correct URLs, {len(incorrect_urls)} incorrect URLs" if not self.results['portfolio_links_verification'] else "")

    async def test_services_modern_icons(self):
        """Test services data for modern icons configuration"""
        print("\n🎨 Testing Services Data with Modern Icons...")
        
        # Expected modern service icons
        expected_icons = ["STACK", "MOBILE", "STORE", "SPEED", "GAME", "AI", "BUILD"]
        
        success, services_data = await self.test_api_endpoint("/services")
        if not success:
            self.log_test_result("Services endpoint accessibility", False, "Services endpoint not accessible")
            self.results['services_modern_icons'] = False
            return
        
        self.log_test_result("Services endpoint accessibility", True)
        
        # Check if services have icon field
        services_with_icons = 0
        found_icons = []
        missing_icons = []
        
        if services_data:
            for service in services_data:
                if 'icon' in service and service['icon']:
                    services_with_icons += 1
                    icon = service['icon']
                    found_icons.append(icon)
                    
                    # Check if it's one of the expected modern icons
                    if icon in expected_icons:
                        self.log_test_result(f"Modern icon found: {icon}", True)
                    else:
                        self.log_test_result(f"Non-standard icon: {icon}", False, f"Expected one of: {expected_icons}")
        
        # Check for missing expected icons
        for expected_icon in expected_icons:
            if expected_icon not in found_icons:
                missing_icons.append(expected_icon)
        
        self.log_test_result("All services have icon field", services_with_icons == len(services_data),
                           f"Only {services_with_icons}/{len(services_data)} services have icons" if services_with_icons != len(services_data) else "")
        
        self.log_test_result("All expected modern icons present", len(missing_icons) == 0,
                           f"Missing icons: {missing_icons}" if missing_icons else "")
        
        # Check service completeness (name, description, features, icon)
        complete_services = 0
        required_fields = ['name', 'description', 'features', 'icon']
        
        for service in services_data:
            if all(field in service and service[field] for field in required_fields):
                complete_services += 1
        
        self.log_test_result("All services have complete data", complete_services == len(services_data),
                           f"Only {complete_services}/{len(services_data)} services are complete" if complete_services != len(services_data) else "")
        
        # Overall assessment
        self.results['services_modern_icons'] = (services_with_icons == len(services_data) and 
                                               len(missing_icons) == 0 and 
                                               complete_services == len(services_data))
        self.log_test_result("Services Modern Icons Configuration", self.results['services_modern_icons'],
                           "Services data incomplete or missing modern icons" if not self.results['services_modern_icons'] else "")

    async def test_contact_form_comprehensive(self):
        """Test contact form endpoint with various scenarios"""
        print("\n📧 Testing Contact Form Comprehensive Functionality...")
        
        # Test valid contact form submission
        valid_contact_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "company": "Tech Solutions Inc",
            "service_interest": "Full-Stack Development",
            "message": "I'm interested in developing a modern web application for my business.",
            "budget_range": "$5,000 - $10,000"
        }
        
        success, result = await self.test_api_endpoint("/contact", method="POST", data=valid_contact_data)
        if success:
            self.log_test_result("Valid contact form submission", True)
            
            # Check response structure
            if isinstance(result, dict) and result.get('success') and result.get('message'):
                self.log_test_result("Contact form response structure", True)
            else:
                self.log_test_result("Contact form response structure", False, "Invalid response structure")
        else:
            self.log_test_result("Valid contact form submission", False, "Contact form submission failed")
        
        # Test required fields validation
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            incomplete_data = valid_contact_data.copy()
            del incomplete_data[field]
            
            success, result = await self.test_api_endpoint("/contact", method="POST", data=incomplete_data, expected_status=422)
            self.log_test_result(f"Required field validation: {field}", success,
                               f"Missing {field} should return validation error" if not success else "")
        
        # Test email format validation
        invalid_email_data = valid_contact_data.copy()
        invalid_email_data['email'] = "invalid-email-format"
        
        success, result = await self.test_api_endpoint("/contact", method="POST", data=invalid_email_data, expected_status=422)
        self.log_test_result("Email format validation", success,
                           "Invalid email format should return validation error" if not success else "")
        
        # Test different service interests
        service_options = ["Full-Stack Development", "Responsive Design", "E-commerce Solutions", 
                          "Performance Optimization", "Gaming Solutions", "AI Integration", "Hardware Consulting"]
        
        services_working = 0
        for service in service_options:
            test_data = valid_contact_data.copy()
            test_data['service_interest'] = service
            
            success, result = await self.test_api_endpoint("/contact", method="POST", data=test_data)
            if success:
                services_working += 1
                self.log_test_result(f"Service interest: {service}", True)
            else:
                self.log_test_result(f"Service interest: {service}", False, "Service option not accepted")
        
        # Test budget range options
        budget_options = ["Under $1,000", "$1,000 - $5,000", "$5,000 - $10,000", "$10,000 - $25,000", "Over $25,000"]
        
        budgets_working = 0
        for budget in budget_options:
            test_data = valid_contact_data.copy()
            test_data['budget_range'] = budget
            
            success, result = await self.test_api_endpoint("/contact", method="POST", data=test_data)
            if success:
                budgets_working += 1
                self.log_test_result(f"Budget range: {budget}", True)
            else:
                self.log_test_result(f"Budget range: {budget}", False, "Budget option not accepted")
        
        # Overall assessment
        form_functionality_score = (
            (1 if success else 0) +  # Basic submission
            (1 if services_working >= len(service_options) * 0.8 else 0) +  # Service options
            (1 if budgets_working >= len(budget_options) * 0.8 else 0)  # Budget options
        )
        
        self.results['contact_form_comprehensive'] = form_functionality_score >= 2
        self.log_test_result("Contact Form Comprehensive Functionality", self.results['contact_form_comprehensive'],
                           f"Contact form functionality incomplete: {form_functionality_score}/3 areas working" if not self.results['contact_form_comprehensive'] else "")

    async def run_all_critical_tests(self):
        """Run all critical feature tests"""
        print("🎯 Starting 019 Solutions Critical Features Testing Suite")
        print("=" * 80)
        print("Testing the specific missing features mentioned in the review request:")
        print("1. Revolutionary 3D Hero Section Backend Support")
        print("2. Freelancer Panel Search Functionality")
        print("3. Payment System Integration")
        print("4. Portfolio Project Links Verification")
        print("5. Services Data with Modern Icons")
        print("6. Contact Form Comprehensive Testing")
        print("=" * 80)
        
        await self.setup()
        
        try:
            await self.test_revolutionary_3d_hero_backend_support()
            await self.test_freelancer_search_functionality()
            await self.test_payment_system_integration()
            await self.test_portfolio_links_verification()
            await self.test_services_modern_icons()
            await self.test_contact_form_comprehensive()
            
        finally:
            await self.cleanup()
        
        # Print summary
        self.print_summary()
        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🏁 CRITICAL FEATURES TESTING SUMMARY")
        print("=" * 80)
        
        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 Critical Features Status:")
        print(f"   Revolutionary 3D Hero Backend: {'✅' if self.results['revolutionary_3d_hero_backend'] else '❌'}")
        print(f"   Freelancer Search Functionality: {'✅' if self.results['freelancer_search_functionality'] else '❌'}")
        print(f"   Payment System Integration: {'✅' if self.results['payment_system_integration'] else '❌'}")
        print(f"   Portfolio Links Verification: {'✅' if self.results['portfolio_links_verification'] else '❌'}")
        print(f"   Services Modern Icons: {'✅' if self.results['services_modern_icons'] else '❌'}")
        print(f"   Contact Form Comprehensive: {'✅' if self.results['contact_form_comprehensive'] else '❌'}")
        
        # Count working critical features
        working_features = sum([
            self.results['revolutionary_3d_hero_backend'],
            self.results['freelancer_search_functionality'], 
            self.results['payment_system_integration'],
            self.results['portfolio_links_verification'],
            self.results['services_modern_icons'],
            self.results['contact_form_comprehensive']
        ])
        
        print(f"\n📈 Critical Features Working: {working_features}/6")
        
        if self.results['error_logs']:
            print(f"\n🚨 Critical Issues Found:")
            for error in self.results['error_logs']:
                print(f"   • {error}")
        
        print("\n" + "=" * 80)

async def main():
    """Main test runner"""
    tester = CriticalFeaturesTester()
    results = await tester.run_all_critical_tests()
    
    # Return exit code based on results
    working_features = sum([
        results['revolutionary_3d_hero_backend'],
        results['freelancer_search_functionality'], 
        results['payment_system_integration'],
        results['portfolio_links_verification'],
        results['services_modern_icons'],
        results['contact_form_comprehensive']
    ])
    
    if working_features == 6:
        print("🎉 All critical features are working!")
        return 0
    else:
        print(f"⚠️  {6 - working_features} critical features have issues!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)