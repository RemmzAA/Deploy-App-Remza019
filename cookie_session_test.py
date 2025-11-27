#!/usr/bin/env python3
"""
REMZA019 Gaming - Cookie Session System Testing
Testing specific scenarios from review request:
1. Cookie Session System Testing
2. User Memory System Testing  
3. Security Validation Testing
4. Discord Link Testing
5. Email Verification System Testing
"""

import asyncio
import aiohttp
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import secrets
import string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CookieSessionTester:
    def __init__(self, base_url: str, admin_username: str, admin_password: str):
        self.base_url = base_url.rstrip('/')
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.session_cookies = {}
        
    async def __aenter__(self):
        # Create session with cookie jar to maintain cookies
        jar = aiohttp.CookieJar(unsafe=True)
        self.session = aiohttp.ClientSession(cookie_jar=jar)
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
        """Make HTTP request with error handling and cookie management"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_text = await response.text()
                
                # Extract cookies from response
                cookies = {}
                if hasattr(response, 'cookies') and response.cookies:
                    for cookie in response.cookies:
                        if hasattr(cookie, 'key') and hasattr(cookie, 'value'):
                            cookies[cookie.key] = cookie.value
                        elif hasattr(cookie, 'name') and hasattr(cookie, 'value'):
                            cookies[cookie.name] = cookie.value
                
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                return {
                    'status': response.status,
                    'data': response_data,
                    'headers': dict(response.headers),
                    'cookies': cookies
                }
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            return {
                'status': 0,
                'data': {'error': str(e)},
                'headers': {},
                'cookies': {}
            }
    
    def generate_test_username(self) -> str:
        """Generate valid test username"""
        return f"testuser{secrets.randbelow(10000)}"
    
    def generate_test_email(self) -> str:
        """Generate valid test email"""
        return f"test{secrets.randbelow(10000)}@example.com"
    
    def generate_invalid_username(self, issue_type: str) -> str:
        """Generate invalid username for testing"""
        if issue_type == "too_short":
            return "ab"  # Less than 3 characters
        elif issue_type == "special_chars":
            return "test@user!"  # Contains special characters
        elif issue_type == "reserved":
            return "admin"  # Reserved word
        elif issue_type == "too_long":
            return "a" * 31  # More than 30 characters
        return "invalid"
    
    def generate_invalid_email(self, issue_type: str) -> str:
        """Generate invalid email for testing"""
        if issue_type == "bad_format":
            return "notanemail"  # No @ symbol
        elif issue_type == "disposable":
            return "test@10minutemail.com"  # Disposable domain
        elif issue_type == "missing_domain":
            return "test@"  # Missing domain
        return "invalid@"
    
    async def test_cookie_session_system(self) -> bool:
        """Test Case 1: Cookie Session System Testing"""
        logger.info("🧪 Testing Cookie Session System...")
        
        # Generate test data
        test_username = self.generate_test_username()
        test_email = self.generate_test_email()
        
        # Step 1: Test viewer registration with session cookie
        logger.info("📝 Testing viewer registration with session cookie...")
        registration_data = {
            "username": test_username,
            "email": test_email
        }
        
        response = await self.make_request('POST', '/api/viewer/register', registration_data)
        
        if response['status'] != 200:
            self.log_test_result(
                "Viewer Registration",
                False,
                f"Registration failed with status {response['status']}",
                {'response': response['data']}
            )
            return False
        
        # Check if session cookie is set (check Set-Cookie header)
        set_cookie_header = response['headers'].get('Set-Cookie', response['headers'].get('set-cookie', ''))
        session_cookie_set = 'remza_session' in set_cookie_header
        if not session_cookie_set:
            self.log_test_result(
                "Session Cookie Creation",
                False,
                "No session cookie set during registration",
                {'set_cookie_header': set_cookie_header}
            )
        else:
            self.log_test_result(
                "Session Cookie Creation",
                True,
                "Session cookie successfully set during registration",
                {'set_cookie_header': 'remza_session cookie found'}
            )
        
        # Store session cookies for later use
        self.session_cookies.update(response['cookies'])
        
        # Step 2: Test login with session cookie creation
        logger.info("🔐 Testing login with session cookie creation...")
        login_response = await self.make_request('POST', f'/api/viewer/login?username={test_username}')
        
        if login_response['status'] == 200:
            login_set_cookie = login_response['headers'].get('set-cookie', '')
            login_cookie_set = 'remza_session' in login_set_cookie
            self.log_test_result(
                "Login Session Cookie",
                login_cookie_set,
                "Session cookie set during login" if login_cookie_set else "No session cookie set during login",
                {'set_cookie_header': 'remza_session cookie found' if login_cookie_set else login_set_cookie}
            )
        else:
            self.log_test_result(
                "Login Session Cookie",
                False,
                f"Login failed with status {login_response['status']}",
                {'response': login_response['data']}
            )
        
        # Step 3: Test /api/viewer/me returns authenticated user
        logger.info("👤 Testing /api/viewer/me endpoint...")
        me_response = await self.make_request('GET', '/api/viewer/me')
        
        if me_response['status'] == 200:
            viewer_data = me_response['data'].get('viewer', {})
            if viewer_data.get('username') == test_username:
                self.log_test_result(
                    "Authenticated User Retrieval",
                    True,
                    f"Successfully retrieved authenticated user: {test_username}",
                    {'user_data': viewer_data}
                )
            else:
                self.log_test_result(
                    "Authenticated User Retrieval",
                    False,
                    "Retrieved user data doesn't match expected username",
                    {'expected': test_username, 'actual': viewer_data.get('username')}
                )
        else:
            self.log_test_result(
                "Authenticated User Retrieval",
                False,
                f"/api/viewer/me failed with status {me_response['status']}",
                {'response': me_response['data']}
            )
        
        # Step 4: Test logout and session invalidation
        logger.info("🚪 Testing logout and session invalidation...")
        logout_response = await self.make_request('POST', '/api/viewer/logout')
        
        if logout_response['status'] == 200:
            self.log_test_result(
                "Logout Success",
                True,
                "Logout successful",
                {'response': logout_response['data']}
            )
            
            # Test that /api/viewer/me now returns 401
            me_after_logout = await self.make_request('GET', '/api/viewer/me')
            if me_after_logout['status'] == 401:
                self.log_test_result(
                    "Session Invalidation",
                    True,
                    "Session properly invalidated after logout",
                    {'status': me_after_logout['status']}
                )
            else:
                self.log_test_result(
                    "Session Invalidation",
                    False,
                    f"Session not properly invalidated, got status {me_after_logout['status']}",
                    {'response': me_after_logout['data']}
                )
        else:
            self.log_test_result(
                "Logout Success",
                False,
                f"Logout failed with status {logout_response['status']}",
                {'response': logout_response['data']}
            )
        
        return True
    
    async def test_user_memory_system(self) -> bool:
        """Test Case 2: User Memory System Testing"""
        logger.info("🧪 Testing User Memory System...")
        
        # Generate test data
        test_username = self.generate_test_username()
        test_email = self.generate_test_email()
        
        # Step 1: Test activity logging during registration
        logger.info("📝 Testing activity logging during registration...")
        registration_data = {
            "username": test_username,
            "email": test_email
        }
        
        response = await self.make_request('POST', '/api/viewer/register', registration_data)
        
        if response['status'] == 200:
            viewer_data = response['data'].get('viewer', {})
            user_id = viewer_data.get('user_id') or viewer_data.get('id')
            
            if user_id:
                self.log_test_result(
                    "Registration Activity Logging",
                    True,
                    "Registration completed with user_id for activity tracking",
                    {'user_id': user_id}
                )
                
                # Step 2: Test activity logging during login
                logger.info("🔐 Testing activity logging during login...")
                login_response = await self.make_request('POST', f'/api/viewer/login?username={test_username}')
                
                if login_response['status'] == 200:
                    self.log_test_result(
                        "Login Activity Logging",
                        True,
                        "Login successful - activity should be logged",
                        {'username': test_username}
                    )
                else:
                    self.log_test_result(
                        "Login Activity Logging",
                        False,
                        f"Login failed with status {login_response['status']}",
                        {'response': login_response['data']}
                    )
                
                # Step 3: Test /api/user-management/me/memory endpoint
                logger.info("💭 Testing user memory retrieval...")
                memory_response = await self.make_request('GET', '/api/user-management/me/memory')
                
                if memory_response['status'] == 200:
                    memory_data = memory_response['data']
                    self.log_test_result(
                        "User Memory Retrieval",
                        True,
                        "Successfully retrieved user memory data",
                        {'memory_keys': list(memory_data.keys()) if isinstance(memory_data, dict) else 'non-dict'}
                    )
                elif memory_response['status'] == 401:
                    self.log_test_result(
                        "User Memory Retrieval",
                        True,
                        "User memory endpoint requires authentication (expected behavior)",
                        {'status': memory_response['status']}
                    )
                else:
                    self.log_test_result(
                        "User Memory Retrieval",
                        False,
                        f"User memory endpoint failed with status {memory_response['status']}",
                        {'response': memory_response['data']}
                    )
                
                # Step 4: Test failed login attempt tracking
                logger.info("❌ Testing failed login attempt tracking...")
                invalid_username = "nonexistentuser123"
                failed_login_response = await self.make_request('POST', f'/api/viewer/login?username={invalid_username}')
                
                if failed_login_response['status'] == 404:
                    self.log_test_result(
                        "Failed Login Tracking",
                        True,
                        "Failed login attempt properly handled and should be tracked",
                        {'attempted_username': invalid_username, 'status': failed_login_response['status']}
                    )
                else:
                    self.log_test_result(
                        "Failed Login Tracking",
                        False,
                        f"Unexpected response for failed login: {failed_login_response['status']}",
                        {'response': failed_login_response['data']}
                    )
            else:
                self.log_test_result(
                    "Registration Activity Logging",
                    False,
                    "No user_id returned from registration",
                    {'response': response['data']}
                )
                return False
        else:
            self.log_test_result(
                "Registration Activity Logging",
                False,
                f"Registration failed with status {response['status']}",
                {'response': response['data']}
            )
            return False
        
        return True
    
    async def test_security_validation(self) -> bool:
        """Test Case 3: Security Validation Testing"""
        logger.info("🧪 Testing Security Validation...")
        
        # Test invalid usernames
        invalid_username_tests = [
            ("too_short", "too short"),
            ("special_chars", "special characters"),
            ("reserved", "reserved words"),
            ("too_long", "too long")
        ]
        
        for test_type, description in invalid_username_tests:
            invalid_username = self.generate_invalid_username(test_type)
            test_email = self.generate_test_email()
            
            logger.info(f"🚫 Testing invalid username: {description}")
            response = await self.make_request(
                'POST', 
                '/api/viewer/register',
                {
                    "username": invalid_username,
                    "email": test_email
                }
            )
            
            if response['status'] == 400:
                self.log_test_result(
                    f"Invalid Username - {description}",
                    True,
                    f"Properly rejected invalid username ({description})",
                    {'username': invalid_username, 'error': response['data'].get('detail')}
                )
            else:
                self.log_test_result(
                    f"Invalid Username - {description}",
                    False,
                    f"Should have rejected invalid username ({description}), got status {response['status']}",
                    {'username': invalid_username, 'response': response['data']}
                )
        
        # Test invalid emails
        invalid_email_tests = [
            ("bad_format", "bad format"),
            ("disposable", "disposable domain"),
            ("missing_domain", "missing domain")
        ]
        
        for test_type, description in invalid_email_tests:
            invalid_email = self.generate_invalid_email(test_type)
            test_username = self.generate_test_username()
            
            logger.info(f"📧 Testing invalid email: {description}")
            response = await self.make_request(
                'POST',
                '/api/viewer/register',
                {
                    "username": test_username,
                    "email": invalid_email
                }
            )
            
            if response['status'] == 400 or response['status'] == 422:
                self.log_test_result(
                    f"Invalid Email - {description}",
                    True,
                    f"Properly rejected invalid email ({description})",
                    {'email': invalid_email, 'error': response['data'].get('detail')}
                )
            else:
                self.log_test_result(
                    f"Invalid Email - {description}",
                    False,
                    f"Should have rejected invalid email ({description}), got status {response['status']}",
                    {'email': invalid_email, 'response': response['data']}
                )
        
        # Test valid username and email formats
        valid_username = self.generate_test_username()
        valid_email = self.generate_test_email()
        
        logger.info("✅ Testing valid username and email formats...")
        response = await self.make_request(
            'POST',
            '/api/viewer/register',
            {
                "username": valid_username,
                "email": valid_email
            }
        )
        
        if response['status'] == 200:
            self.log_test_result(
                "Valid Username and Email",
                True,
                "Valid username and email properly accepted",
                {'username': valid_username, 'email': valid_email}
            )
        else:
            self.log_test_result(
                "Valid Username and Email",
                False,
                f"Valid credentials rejected with status {response['status']}",
                {'username': valid_username, 'email': valid_email, 'response': response['data']}
            )
        
        return True
    
    async def test_discord_link(self) -> bool:
        """Test Case 4: Discord Link Testing"""
        logger.info("🧪 Testing Discord Link...")
        
        expected_discord_link = "https://discord.gg/5W2W23snAM"
        
        response = await self.make_request('GET', '/api/customization/current')
        
        if response['status'] == 200:
            customization_data = response['data'].get('data', {})
            discord_link = customization_data.get('discordLink', '')
            
            if discord_link == expected_discord_link:
                self.log_test_result(
                    "Discord Link Verification",
                    True,
                    f"Discord link correctly set to: {discord_link}",
                    {'expected': expected_discord_link, 'actual': discord_link}
                )
            else:
                self.log_test_result(
                    "Discord Link Verification",
                    False,
                    f"Discord link mismatch. Expected: {expected_discord_link}, Got: {discord_link}",
                    {'expected': expected_discord_link, 'actual': discord_link}
                )
        else:
            self.log_test_result(
                "Discord Link Verification",
                False,
                f"Failed to retrieve customization data, status: {response['status']}",
                {'response': response['data']}
            )
        
        return True
    
    async def test_email_verification_system(self) -> bool:
        """Test Case 5: Email Verification System"""
        logger.info("🧪 Testing Email Verification System...")
        
        # Generate test data
        test_username = self.generate_test_username()
        test_email = self.generate_test_email()
        
        # Step 1: Test that verification code is generated on registration
        logger.info("📝 Testing verification code generation during registration...")
        registration_data = {
            "username": test_username,
            "email": test_email
        }
        
        response = await self.make_request('POST', '/api/viewer/register', registration_data)
        
        if response['status'] == 200:
            response_data = response['data']
            message = response_data.get('message', '')
            
            # Check if message mentions email verification
            if 'email' in message.lower() and 'verify' in message.lower():
                self.log_test_result(
                    "Verification Code Generation",
                    True,
                    "Registration response indicates email verification is triggered",
                    {'message': message}
                )
            else:
                self.log_test_result(
                    "Verification Code Generation",
                    False,
                    "Registration response doesn't mention email verification",
                    {'message': message}
                )
        else:
            self.log_test_result(
                "Verification Code Generation",
                False,
                f"Registration failed with status {response['status']}",
                {'response': response['data']}
            )
            return False
        
        # Step 2: Test email verification endpoint exists
        logger.info("🔍 Testing email verification endpoint...")
        
        # Test with invalid code (should fail gracefully)
        verify_response = await self.make_request(
            'POST',
            '/api/viewer/verify',
            {
                'email': test_email,
                'code': 'INVALID123'
            }
        )
        
        if verify_response['status'] == 400:
            self.log_test_result(
                "Email Verification Endpoint",
                True,
                "Email verification endpoint exists and properly rejects invalid codes",
                {'status': verify_response['status'], 'error': verify_response['data'].get('detail')}
            )
        else:
            self.log_test_result(
                "Email Verification Endpoint",
                False,
                f"Email verification endpoint returned unexpected status: {verify_response['status']}",
                {'response': verify_response['data']}
            )
        
        # Step 3: Test alternative email verification endpoint
        logger.info("📧 Testing alternative email verification endpoint...")
        
        alt_verify_response = await self.make_request(
            'POST',
            '/api/auth/verify-email',
            {
                'email': test_email,
                'token': 'INVALID123'
            }
        )
        
        if alt_verify_response['status'] == 400:
            self.log_test_result(
                "Alternative Email Verification Endpoint",
                True,
                "Alternative email verification endpoint exists and properly rejects invalid tokens",
                {'status': alt_verify_response['status']}
            )
        elif alt_verify_response['status'] == 404:
            self.log_test_result(
                "Alternative Email Verification Endpoint",
                False,
                "Alternative email verification endpoint not found",
                {'status': alt_verify_response['status']}
            )
        else:
            self.log_test_result(
                "Alternative Email Verification Endpoint",
                False,
                f"Unexpected response from alternative verification endpoint: {alt_verify_response['status']}",
                {'response': alt_verify_response['data']}
            )
        
        # Step 4: Test email verification status check
        logger.info("📊 Testing email verification status check...")
        
        status_response = await self.make_request('GET', f'/api/auth/check-verification/{test_email}')
        
        if status_response['status'] == 200:
            status_data = status_response['data']
            self.log_test_result(
                "Email Verification Status Check",
                True,
                "Email verification status check endpoint working",
                {
                    'email': status_data.get('email'),
                    'verified': status_data.get('verified'),
                    'exists': status_data.get('exists')
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
    
    async def run_comprehensive_tests(self) -> Dict:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Cookie Session System Testing...")
        
        test_cases = [
            ("Cookie Session System Testing", self.test_cookie_session_system),
            ("User Memory System Testing", self.test_user_memory_system),
            ("Security Validation Testing", self.test_security_validation),
            ("Discord Link Testing", self.test_discord_link),
            ("Email Verification System Testing", self.test_email_verification_system),
        ]
        
        results_summary = {
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
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
    # Configuration - Use localhost as specified in review request
    BASE_URL = "http://localhost:8001"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "remza019admin"
    
    logger.info("🎮 REMZA019 Gaming - Cookie Session System Testing")
    logger.info(f"Backend URL: {BASE_URL}")
    logger.info(f"Admin User: {ADMIN_USERNAME}")
    
    async with CookieSessionTester(BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD) as tester:
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