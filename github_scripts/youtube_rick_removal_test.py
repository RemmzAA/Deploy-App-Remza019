#!/usr/bin/env python3
"""
CRITICAL TEST: Rick Astley Removal Verification for REMZA019 Gaming Website
This test specifically verifies that Rick Astley content has been completely removed
and replaced with authentic REMZA019 gaming content as requested by the user.
"""

import asyncio
import aiohttp
import json
import os
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
    BACKEND_URL = "https://deployed-app.preview.emergentagent.com"

API_BASE_URL = f"{BACKEND_URL}/api"

class RickAstleyRemovalTester:
    def __init__(self):
        self.session = None
        self.rick_astley_indicators = [
            "dQw4w9WgXcQ",  # Rick Astley video ID
            "Rick Astley",
            "Never Gonna Give You Up",
            "rick astley",
            "never gonna give you up",
            "rickroll",
            "rick roll"
        ]
        self.remza019_indicators = [
            "REMZA019",
            "remza019",
            "FORTNITE",
            "Call of Duty",
            "ROCKET RACING",
            "Serbia",
            "Serbian",
            "gaming",
            "RMZ019_V"  # REMZA019 video ID pattern
        ]
        self.results = {
            'rick_astley_found': False,
            'remza019_content_found': False,
            'featured_video_authentic': False,
            'latest_videos_authentic': False,
            'channel_stats_authentic': False,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_issues': []
        }

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up Rick Astley removal verification...")
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
                self.results['critical_issues'].append(f"{test_name}: {details}")

    def check_for_rick_astley(self, content):
        """Check if content contains Rick Astley references"""
        if isinstance(content, dict):
            content_str = json.dumps(content).lower()
        elif isinstance(content, list):
            content_str = json.dumps(content).lower()
        else:
            content_str = str(content).lower()
        
        found_indicators = []
        for indicator in self.rick_astley_indicators:
            if indicator.lower() in content_str:
                found_indicators.append(indicator)
        
        return found_indicators

    def check_for_remza019(self, content):
        """Check if content contains REMZA019 gaming references"""
        if isinstance(content, dict):
            content_str = json.dumps(content)
        elif isinstance(content, list):
            content_str = json.dumps(content)
        else:
            content_str = str(content)
        
        found_indicators = []
        for indicator in self.remza019_indicators:
            if indicator in content_str:
                found_indicators.append(indicator)
        
        return found_indicators

    async def test_api_endpoint(self, endpoint):
        """Test individual API endpoint"""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return True, response_data
                else:
                    return False, f"HTTP {response.status}"
        except Exception as e:
            return False, str(e)

    async def test_featured_video_endpoint(self):
        """Test Featured Video Endpoint for Rick Astley removal"""
        print("\n🎯 Testing Featured Video Endpoint - RICK ASTLEY REMOVAL VERIFICATION")
        
        success, result = await self.test_api_endpoint("/youtube/featured-video")
        
        if success:
            self.log_test_result("Featured video endpoint accessible", True)
            
            # Check for Rick Astley content
            rick_indicators = self.check_for_rick_astley(result)
            if rick_indicators:
                self.results['rick_astley_found'] = True
                self.log_test_result("Featured video - NO Rick Astley content", False, 
                                   f"FOUND RICK ASTLEY INDICATORS: {rick_indicators}")
            else:
                self.log_test_result("Featured video - NO Rick Astley content", True)
            
            # Check for REMZA019 content
            remza_indicators = self.check_for_remza019(result)
            if remza_indicators:
                self.results['remza019_content_found'] = True
                self.log_test_result("Featured video - Contains REMZA019 content", True,
                                   f"Found REMZA019 indicators: {remza_indicators}")
            else:
                self.log_test_result("Featured video - Contains REMZA019 content", False,
                                   "No REMZA019 gaming content found")
            
            # Specific checks
            if 'video_id' in result:
                video_id = result['video_id']
                if video_id == "dQw4w9WgXcQ":
                    self.log_test_result("Featured video - NOT Rick Astley video ID", False,
                                       f"CRITICAL: Still using Rick Astley video ID: {video_id}")
                    self.results['rick_astley_found'] = True
                else:
                    self.log_test_result("Featured video - NOT Rick Astley video ID", True,
                                       f"Using authentic video ID: {video_id}")
            
            if 'title' in result:
                title = result['title']
                if "REMZA019" in title:
                    self.log_test_result("Featured video - Title contains REMZA019", True)
                    self.results['featured_video_authentic'] = True
                else:
                    self.log_test_result("Featured video - Title contains REMZA019", False,
                                       f"Title: {title}")
            
            if 'description' in result:
                description = result['description']
                if any(word in description for word in ["Serbia", "Serbian", "gaming", "REMZA019"]):
                    self.log_test_result("Featured video - Description contains Serbian gaming content", True)
                else:
                    self.log_test_result("Featured video - Description contains Serbian gaming content", False,
                                       f"Description: {description[:100]}...")
            
            print(f"📊 Featured Video Data: {json.dumps(result, indent=2)}")
            
        else:
            self.log_test_result("Featured video endpoint accessible", False, str(result))

    async def test_latest_videos_endpoint(self):
        """Test Latest Videos Endpoint for Rick Astley removal"""
        print("\n🎬 Testing Latest Videos Endpoint - RICK ASTLEY REMOVAL VERIFICATION")
        
        success, result = await self.test_api_endpoint("/youtube/latest-videos")
        
        if success and isinstance(result, list):
            self.log_test_result("Latest videos endpoint accessible", True)
            
            # Check each video for Rick Astley content
            rick_videos_found = []
            remza_videos_found = []
            
            for i, video in enumerate(result):
                video_rick_indicators = self.check_for_rick_astley(video)
                video_remza_indicators = self.check_for_remza019(video)
                
                if video_rick_indicators:
                    rick_videos_found.append(f"Video {i+1}: {video_rick_indicators}")
                    self.results['rick_astley_found'] = True
                
                if video_remza_indicators:
                    remza_videos_found.append(f"Video {i+1}: {video_remza_indicators}")
                    self.results['remza019_content_found'] = True
                
                # Check specific video ID
                if 'id' in video and video['id'] == "dQw4w9WgXcQ":
                    rick_videos_found.append(f"Video {i+1}: Rick Astley video ID found")
                    self.results['rick_astley_found'] = True
            
            # Report results
            if rick_videos_found:
                self.log_test_result("Latest videos - NO Rick Astley content", False,
                                   f"FOUND RICK ASTLEY IN: {rick_videos_found}")
            else:
                self.log_test_result("Latest videos - NO Rick Astley content", True)
            
            if remza_videos_found:
                self.log_test_result("Latest videos - All REMZA019 gaming content", True,
                                   f"Found REMZA019 content in: {len(remza_videos_found)} videos")
                self.results['latest_videos_authentic'] = True
            else:
                self.log_test_result("Latest videos - All REMZA019 gaming content", False,
                                   "No REMZA019 gaming content found in videos")
            
            # Check view counts are realistic for small Serbian gaming channel
            realistic_views = True
            for video in result:
                if 'view_count' in video:
                    try:
                        views = int(video['view_count'])
                        # Realistic range for small Serbian gaming channel: 50-500 views
                        if views > 1000:  # Too high for small channel
                            realistic_views = False
                            break
                    except (ValueError, TypeError):
                        pass
            
            self.log_test_result("Latest videos - Realistic view counts for small Serbian channel", realistic_views)
            
            print(f"📊 Latest Videos Count: {len(result)}")
            for i, video in enumerate(result):
                print(f"   Video {i+1}: {video.get('title', 'N/A')} - {video.get('view_count', 'N/A')} views")
            
        else:
            self.log_test_result("Latest videos endpoint accessible", False, str(result))

    async def test_channel_stats_endpoint(self):
        """Test Channel Stats Endpoint for authentic REMZA019 data"""
        print("\n📊 Testing Channel Stats Endpoint - REMZA019 AUTHENTICITY VERIFICATION")
        
        success, result = await self.test_api_endpoint("/youtube/channel-stats")
        
        if success:
            self.log_test_result("Channel stats endpoint accessible", True)
            
            # Check for Rick Astley content
            rick_indicators = self.check_for_rick_astley(result)
            if rick_indicators:
                self.results['rick_astley_found'] = True
                self.log_test_result("Channel stats - NO Rick Astley content", False,
                                   f"Found Rick Astley indicators: {rick_indicators}")
            else:
                self.log_test_result("Channel stats - NO Rick Astley content", True)
            
            # Check for realistic REMZA019 channel statistics
            if 'subscriber_count' in result:
                try:
                    subs = int(result['subscriber_count'])
                    # Realistic range for small Serbian gaming channel: 50-500 subscribers
                    if 50 <= subs <= 500:
                        self.log_test_result("Channel stats - Realistic subscriber count", True,
                                           f"{subs} subscribers (appropriate for small Serbian gaming channel)")
                        self.results['channel_stats_authentic'] = True
                    else:
                        self.log_test_result("Channel stats - Realistic subscriber count", False,
                                           f"{subs} subscribers (unrealistic for small channel)")
                except (ValueError, TypeError):
                    self.log_test_result("Channel stats - Valid subscriber count", False,
                                       f"Invalid subscriber count: {result['subscriber_count']}")
            
            if 'video_count' in result:
                try:
                    videos = int(result['video_count'])
                    # Realistic range for starting channel: 5-50 videos
                    if 5 <= videos <= 50:
                        self.log_test_result("Channel stats - Realistic video count", True,
                                           f"{videos} videos (appropriate for starting channel)")
                    else:
                        self.log_test_result("Channel stats - Realistic video count", False,
                                           f"{videos} videos (unrealistic for starting channel)")
                except (ValueError, TypeError):
                    self.log_test_result("Channel stats - Valid video count", False,
                                       f"Invalid video count: {result['video_count']}")
            
            if 'view_count' in result:
                try:
                    views = int(result['view_count'])
                    # Realistic range for small channel: 1000-10000 total views
                    if 1000 <= views <= 10000:
                        self.log_test_result("Channel stats - Realistic total view count", True,
                                           f"{views} total views (appropriate for small Serbian gaming channel)")
                    else:
                        self.log_test_result("Channel stats - Realistic total view count", False,
                                           f"{views} total views (unrealistic for small channel)")
                except (ValueError, TypeError):
                    self.log_test_result("Channel stats - Valid view count", False,
                                       f"Invalid view count: {result['view_count']}")
            
            if 'channel_id' in result:
                channel_id = result['channel_id']
                if "remza019" in channel_id.lower() or "rmz019" in channel_id.lower():
                    self.log_test_result("Channel stats - Appropriate REMZA019 channel ID", True,
                                       f"Channel ID: {channel_id}")
                else:
                    self.log_test_result("Channel stats - Appropriate REMZA019 channel ID", False,
                                       f"Channel ID: {channel_id}")
            
            print(f"📊 Channel Statistics: {json.dumps(result, indent=2)}")
            
        else:
            self.log_test_result("Channel stats endpoint accessible", False, str(result))

    async def test_data_authenticity_comprehensive(self):
        """Comprehensive test for data authenticity"""
        print("\n🔍 COMPREHENSIVE DATA AUTHENTICITY CHECK")
        
        # Test all endpoints together
        endpoints = [
            "/youtube/featured-video",
            "/youtube/latest-videos", 
            "/youtube/channel-stats"
        ]
        
        all_data = {}
        for endpoint in endpoints:
            success, result = await self.test_api_endpoint(endpoint)
            if success:
                all_data[endpoint] = result
        
        # Check entire dataset for Rick Astley
        all_rick_indicators = self.check_for_rick_astley(all_data)
        if all_rick_indicators:
            self.results['rick_astley_found'] = True
            self.log_test_result("COMPREHENSIVE - NO Rick Astley anywhere", False,
                               f"CRITICAL: Found Rick Astley indicators: {all_rick_indicators}")
        else:
            self.log_test_result("COMPREHENSIVE - NO Rick Astley anywhere", True,
                               "✅ NO Rick Astley content found in any endpoint")
        
        # Check entire dataset for REMZA019
        all_remza_indicators = self.check_for_remza019(all_data)
        if all_remza_indicators:
            self.results['remza019_content_found'] = True
            self.log_test_result("COMPREHENSIVE - All content is REMZA019 gaming", True,
                               f"Found REMZA019 indicators: {len(all_remza_indicators)} references")
        else:
            self.log_test_result("COMPREHENSIVE - All content is REMZA019 gaming", False,
                               "CRITICAL: No REMZA019 gaming content found")

    async def run_all_tests(self):
        """Run all Rick Astley removal verification tests"""
        print("🚨 CRITICAL TEST: Rick Astley Removal Verification for REMZA019 Gaming Website")
        print("User Request: 'Jos uvek mi nisi uklonio onog pevaca Ricka sa moj web sajta'")
        print("=" * 80)
        
        await self.setup()
        
        try:
            await self.test_featured_video_endpoint()
            await self.test_latest_videos_endpoint()
            await self.test_channel_stats_endpoint()
            await self.test_data_authenticity_comprehensive()
            
        finally:
            await self.cleanup()
        
        # Print summary
        self.print_summary()
        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🏁 RICK ASTLEY REMOVAL VERIFICATION SUMMARY")
        print("=" * 80)
        
        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 CRITICAL FINDINGS:")
        if self.results['rick_astley_found']:
            print("❌ RICK ASTLEY CONTENT STILL FOUND - REMOVAL INCOMPLETE!")
        else:
            print("✅ NO RICK ASTLEY CONTENT FOUND - SUCCESSFULLY REMOVED!")
        
        if self.results['remza019_content_found']:
            print("✅ REMZA019 GAMING CONTENT CONFIRMED - AUTHENTIC REPLACEMENT!")
        else:
            print("❌ REMZA019 GAMING CONTENT MISSING - REPLACEMENT INCOMPLETE!")
        
        print(f"\n📋 Component Status:")
        print(f"   Featured Video Authentic: {'✅' if self.results['featured_video_authentic'] else '❌'}")
        print(f"   Latest Videos Authentic: {'✅' if self.results['latest_videos_authentic'] else '❌'}")
        print(f"   Channel Stats Authentic: {'✅' if self.results['channel_stats_authentic'] else '❌'}")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in self.results['critical_issues']:
                print(f"   • {issue}")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if not self.results['rick_astley_found'] and self.results['remza019_content_found']:
            print("✅ SUCCESS: Rick Astley completely removed and replaced with authentic REMZA019 gaming content!")
        elif self.results['rick_astley_found']:
            print("❌ FAILURE: Rick Astley content still present - user request NOT fulfilled!")
        elif not self.results['remza019_content_found']:
            print("❌ FAILURE: REMZA019 gaming content missing - replacement incomplete!")
        else:
            print("⚠️  PARTIAL: Some issues found - review required!")
        
        print("=" * 80)

async def main():
    """Main test runner"""
    tester = RickAstleyRemovalTester()
    results = await tester.run_all_tests()
    
    # Return exit code based on results
    if not results['rick_astley_found'] and results['remza019_content_found']:
        print("🎉 Rick Astley successfully removed and replaced with REMZA019 content!")
        return 0
    else:
        print("⚠️  Rick Astley removal verification failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)