#!/usr/bin/env python3
"""
YouTube Video Links Testing Suite for REMZA019 Gaming Website
Focused testing for YouTube API endpoints and watch_url field validation
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
    BACKEND_URL = "http://localhost:8001"

API_BASE_URL = f"{BACKEND_URL}/api"

class YouTubeLinksTest:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_logs': []
        }
        self.session = None

    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up YouTube links test environment...")
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
        except Exception as e:
            return False, str(e)

    async def test_youtube_latest_videos_watch_url(self):
        """Test GET /api/youtube/latest-videos returns videos with watch_url field"""
        print("\n🎬 Testing YouTube Latest Videos - watch_url Field Validation...")
        
        success, result = await self.test_api_endpoint("/youtube/latest-videos")
        self.log_test_result("YouTube latest videos endpoint accessible", success, "" if success else str(result))
        
        if success and isinstance(result, list):
            # Test that all videos have watch_url field
            videos_with_watch_url = 0
            videos_with_correct_format = 0
            videos_with_video_id = 0
            
            for video in result:
                # Check if watch_url field exists
                if 'watch_url' in video:
                    videos_with_watch_url += 1
                    
                    # Check if watch_url format is correct
                    watch_url = video['watch_url']
                    if watch_url.startswith('https://www.youtube.com/watch?v='):
                        videos_with_correct_format += 1
                    
                # Check if video_id field exists for compatibility
                if 'video_id' in video:
                    videos_with_video_id += 1
            
            total_videos = len(result)
            
            self.log_test_result(f"All videos have watch_url field ({videos_with_watch_url}/{total_videos})", 
                               videos_with_watch_url == total_videos,
                               f"Missing watch_url in {total_videos - videos_with_watch_url} videos")
            
            self.log_test_result(f"All watch_url fields have correct format ({videos_with_correct_format}/{total_videos})", 
                               videos_with_correct_format == total_videos,
                               f"Incorrect format in {total_videos - videos_with_correct_format} videos")
            
            self.log_test_result(f"All videos have video_id field ({videos_with_video_id}/{total_videos})", 
                               videos_with_video_id == total_videos,
                               f"Missing video_id in {total_videos - videos_with_video_id} videos")
            
            # Test specific video IDs mentioned in review
            expected_video_ids = ['GUhc9NBBxBM', 'h1HGztOJgHo', 'XnEtSLaI5Vo', '7782cWbt4yw', '7m3-c4_Yqlg']
            found_video_ids = [video.get('video_id', '') for video in result]
            
            for expected_id in expected_video_ids:
                found = expected_id in found_video_ids
                self.log_test_result(f"Video ID {expected_id} present in latest videos", found)
            
            # Validate specific watch URLs for expected video IDs
            for video in result:
                if video.get('video_id') in expected_video_ids:
                    expected_watch_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                    actual_watch_url = video.get('watch_url', '')
                    self.log_test_result(f"Video {video['video_id']} has correct watch_url format", 
                                       actual_watch_url == expected_watch_url,
                                       f"Expected: {expected_watch_url}, Got: {actual_watch_url}")
        else:
            self.log_test_result("Latest videos returns valid array", False, "Endpoint did not return array")

    async def test_youtube_featured_video_watch_url(self):
        """Test GET /api/youtube/featured-video returns video with watch_url field"""
        print("\n🎯 Testing YouTube Featured Video - watch_url Field Validation...")
        
        success, result = await self.test_api_endpoint("/youtube/featured-video")
        self.log_test_result("YouTube featured video endpoint accessible", success, "" if success else str(result))
        
        if success and isinstance(result, dict):
            # Check if watch_url field exists
            has_watch_url = 'watch_url' in result
            self.log_test_result("Featured video has watch_url field", has_watch_url)
            
            if has_watch_url:
                watch_url = result['watch_url']
                
                # Check if watch_url format is correct
                correct_format = watch_url.startswith('https://www.youtube.com/watch?v=')
                self.log_test_result("Featured video watch_url has correct format", correct_format,
                                   f"Got: {watch_url}")
                
                # Check if video_id field exists for compatibility
                has_video_id = 'video_id' in result
                self.log_test_result("Featured video has video_id field", has_video_id)
                
                if has_video_id:
                    video_id = result['video_id']
                    expected_watch_url = f"https://www.youtube.com/watch?v={video_id}"
                    self.log_test_result("Featured video watch_url matches video_id", 
                                       watch_url == expected_watch_url,
                                       f"Expected: {expected_watch_url}, Got: {watch_url}")
                    
                    # Check if this is one of the expected video IDs
                    expected_video_ids = ['GUhc9NBBxBM', 'h1HGztOJgHo', 'XnEtSLaI5Vo', '7782cWbt4yw', '7m3-c4_Yqlg']
                    is_expected_video = video_id in expected_video_ids
                    self.log_test_result(f"Featured video is one of expected videos ({video_id})", is_expected_video)
            
            # Check for other required fields
            required_fields = ['video_id', 'title', 'description', 'thumbnail_url', 'embed_url', 'watch_url']
            missing_fields = [field for field in required_fields if field not in result]
            
            self.log_test_result("Featured video has all required fields", len(missing_fields) == 0,
                               f"Missing fields: {missing_fields}")
        else:
            self.log_test_result("Featured video returns valid object", False, "Endpoint did not return object")

    async def test_no_dummy_or_placeholder_urls(self):
        """Test that no dummy or placeholder URLs exist in video data"""
        print("\n🚫 Testing for Dummy/Placeholder URLs...")
        
        # Test latest videos
        success, latest_videos = await self.test_api_endpoint("/youtube/latest-videos")
        if success and isinstance(latest_videos, list):
            dummy_patterns = ['dummy', 'placeholder', 'test', 'example.com', 'localhost']
            
            for video in latest_videos:
                watch_url = video.get('watch_url', '').lower()
                has_dummy = any(pattern in watch_url for pattern in dummy_patterns)
                self.log_test_result(f"Video {video.get('video_id', 'unknown')} has no dummy URL", not has_dummy,
                                   f"Found dummy pattern in: {video.get('watch_url', '')}")
        
        # Test featured video
        success, featured_video = await self.test_api_endpoint("/youtube/featured-video")
        if success and isinstance(featured_video, dict):
            watch_url = featured_video.get('watch_url', '').lower()
            dummy_patterns = ['dummy', 'placeholder', 'test', 'example.com', 'localhost']
            has_dummy = any(pattern in watch_url for pattern in dummy_patterns)
            self.log_test_result("Featured video has no dummy URL", not has_dummy,
                               f"Found dummy pattern in: {featured_video.get('watch_url', '')}")

    async def test_video_data_structure_validation(self):
        """Test that all video entries have both id and video_id fields"""
        print("\n📋 Testing Video Data Structure Validation...")
        
        # Test latest videos structure
        success, latest_videos = await self.test_api_endpoint("/youtube/latest-videos")
        if success and isinstance(latest_videos, list):
            for video in latest_videos:
                has_id = 'id' in video
                has_video_id = 'video_id' in video
                
                self.log_test_result(f"Video has 'id' field", has_id)
                self.log_test_result(f"Video has 'video_id' field", has_video_id)
                
                # Check if id and video_id match (for compatibility)
                if has_id and has_video_id:
                    id_match = video['id'] == video['video_id']
                    self.log_test_result(f"Video id and video_id match", id_match,
                                       f"id: {video.get('id')}, video_id: {video.get('video_id')}")
        
        # Test featured video structure
        success, featured_video = await self.test_api_endpoint("/youtube/featured-video")
        if success and isinstance(featured_video, dict):
            has_video_id = 'video_id' in featured_video
            self.log_test_result("Featured video has 'video_id' field", has_video_id)

    async def test_specific_video_ids_validation(self):
        """Test specific video IDs that should be in system"""
        print("\n🎯 Testing Specific Video IDs Validation...")
        
        expected_videos = {
            'GUhc9NBBxBM': 'main featured video',
            'h1HGztOJgHo': 'UNLUCKY 2',
            'XnEtSLaI5Vo': 'ROCKET RACING',
            '7782cWbt4yw': 'Gaming Tips',
            '7m3-c4_Yqlg': 'Weekend Highlights'
        }
        
        # Get all videos from latest videos endpoint
        success, latest_videos = await self.test_api_endpoint("/youtube/latest-videos")
        found_video_ids = []
        
        if success and isinstance(latest_videos, list):
            found_video_ids = [video.get('video_id', '') for video in latest_videos]
        
        # Check featured video
        success, featured_video = await self.test_api_endpoint("/youtube/featured-video")
        if success and isinstance(featured_video, dict):
            featured_id = featured_video.get('video_id', '')
            if featured_id and featured_id not in found_video_ids:
                found_video_ids.append(featured_id)
        
        # Validate each expected video ID
        for video_id, description in expected_videos.items():
            found = video_id in found_video_ids
            self.log_test_result(f"Video ID {video_id} ({description}) found in system", found)
            
            if found:
                # Validate the watch URL for this video ID
                expected_watch_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Find the video in latest videos
                for video in latest_videos:
                    if video.get('video_id') == video_id:
                        actual_watch_url = video.get('watch_url', '')
                        self.log_test_result(f"Video {video_id} has correct watch_url", 
                                           actual_watch_url == expected_watch_url,
                                           f"Expected: {expected_watch_url}, Got: {actual_watch_url}")
                        break

    async def test_youtube_url_format_validation(self):
        """Test that all YouTube URLs are in the correct format"""
        print("\n🔗 Testing YouTube URL Format Validation...")
        
        # Test latest videos
        success, latest_videos = await self.test_api_endpoint("/youtube/latest-videos")
        if success and isinstance(latest_videos, list):
            for video in latest_videos:
                watch_url = video.get('watch_url', '')
                video_id = video.get('video_id', '')
                
                # Check URL format
                expected_format = f"https://www.youtube.com/watch?v={video_id}"
                correct_format = watch_url == expected_format
                
                self.log_test_result(f"Video {video_id} URL format correct", correct_format,
                                   f"Expected: {expected_format}, Got: {watch_url}")
                
                # Check that URL is clickable (starts with https)
                is_clickable = watch_url.startswith('https://')
                self.log_test_result(f"Video {video_id} URL is clickable (https)", is_clickable)
        
        # Test featured video
        success, featured_video = await self.test_api_endpoint("/youtube/featured-video")
        if success and isinstance(featured_video, dict):
            watch_url = featured_video.get('watch_url', '')
            video_id = featured_video.get('video_id', '')
            
            expected_format = f"https://www.youtube.com/watch?v={video_id}"
            correct_format = watch_url == expected_format
            
            self.log_test_result("Featured video URL format correct", correct_format,
                               f"Expected: {expected_format}, Got: {watch_url}")
            
            is_clickable = watch_url.startswith('https://')
            self.log_test_result("Featured video URL is clickable (https)", is_clickable)

    async def run_all_tests(self):
        """Run all YouTube links tests"""
        print("🎮 Starting YouTube Video Links Testing Suite for REMZA019 Gaming Website")
        print("=" * 80)
        print("🎯 TESTING FOCUS:")
        print("   1. YouTube API endpoints return watch_url field")
        print("   2. All video data includes proper YouTube URLs")
        print("   3. Specific video IDs are present in system")
        print("   4. No dummy or placeholder URLs exist")
        print("=" * 80)
        
        await self.setup()
        
        try:
            await self.test_youtube_latest_videos_watch_url()
            await self.test_youtube_featured_video_watch_url()
            await self.test_no_dummy_or_placeholder_urls()
            await self.test_video_data_structure_validation()
            await self.test_specific_video_ids_validation()
            await self.test_youtube_url_format_validation()
            
        finally:
            await self.cleanup()
        
        # Print summary
        self.print_summary()
        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 YOUTUBE LINKS TESTING SUMMARY")
        print("=" * 60)
        
        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        
        success_rate = (self.results['passed_tests'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['error_logs']:
            print(f"\n🚨 Issues Found:")
            for error in self.results['error_logs']:
                print(f"   • {error}")
        else:
            print(f"\n🎉 All YouTube video links functionality tests passed!")
        
        print("\n" + "=" * 60)

async def main():
    """Main test runner"""
    tester = YouTubeLinksTest()
    results = await tester.run_all_tests()
    
    # Return exit code based on results
    if results['failed_tests'] == 0:
        print("🎉 All YouTube video links tests passed!")
        return 0
    else:
        print(f"⚠️  {results['failed_tests']} YouTube video links tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)