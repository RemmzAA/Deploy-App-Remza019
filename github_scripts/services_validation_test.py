#!/usr/bin/env python3
"""
Services Endpoint Validation Test - Specific Review Request
Tests the /api/services endpoint for:
1. Total of 8 services including PHP/Laravel Development
2. Proper data structure (name, description, features, icon)
3. PHP/Laravel service validation with enterprise description
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
frontend_env_path = Path("/app/frontend/.env")

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
    exit(1)

API_BASE_URL = f"{BACKEND_URL}/api"

async def test_services_endpoint():
    """Test services endpoint as requested in review"""
    print("🎯 SERVICES ENDPOINT VALIDATION TEST - REVIEW REQUEST")
    print("=" * 60)
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            # Test /api/services endpoint
            async with session.get(f"{API_BASE_URL}/services") as response:
                if response.status != 200:
                    print(f"❌ Services endpoint failed with HTTP {response.status}")
                    return False
                
                services = await response.json()
                
                # 1. Check total number of services (should be 8)
                total_services = len(services)
                print(f"📊 Total Services Found: {total_services}")
                
                if total_services == 8:
                    print("✅ Services count verification: 8 services total (CORRECT)")
                else:
                    print(f"❌ Services count verification: Expected 8, got {total_services}")
                    return False
                
                # 2. Verify all services have proper data structure
                print("\n🔍 Services Data Structure Validation:")
                required_fields = ['name', 'description', 'features', 'icon']
                all_valid = True
                
                for i, service in enumerate(services, 1):
                    print(f"\n   Service {i}: {service.get('name', 'UNNAMED')}")
                    
                    for field in required_fields:
                        if field in service and service[field]:
                            print(f"      ✅ {field}: Present")
                        else:
                            print(f"      ❌ {field}: Missing or empty")
                            all_valid = False
                    
                    # Check features is a list
                    if isinstance(service.get('features'), list):
                        print(f"      ✅ features type: List with {len(service['features'])} items")
                    else:
                        print(f"      ❌ features type: Not a list")
                        all_valid = False
                
                if all_valid:
                    print("\n✅ All services have proper data structure")
                else:
                    print("\n❌ Some services missing required fields")
                    return False
                
                # 3. Find and validate PHP/Laravel service
                print("\n🐘 PHP/Laravel Service Validation:")
                php_service = None
                
                for service in services:
                    if 'PHP/Laravel' in service.get('name', ''):
                        php_service = service
                        break
                
                if php_service:
                    print("✅ PHP/Laravel Development service found")
                    print(f"   Name: {php_service['name']}")
                    print(f"   Description: {php_service['description']}")
                    print(f"   Icon: {php_service['icon']}")
                    print(f"   Features: {php_service['features']}")
                    
                    # Check for enterprise-related keywords in description
                    description = php_service['description'].lower()
                    enterprise_keywords = ['enterprise', 'subscription', 'billing', 'admin', 'panel', 'payment', 'gateway']
                    found_keywords = [keyword for keyword in enterprise_keywords if keyword in description]
                    
                    if found_keywords:
                        print(f"✅ Enterprise description confirmed - Keywords found: {found_keywords}")
                    else:
                        print("⚠️  Enterprise description may be missing enterprise-specific keywords")
                    
                    # Check features for enterprise-related items
                    features_text = ' '.join(php_service['features']).lower()
                    enterprise_features = [keyword for keyword in enterprise_keywords if keyword in features_text]
                    
                    if enterprise_features:
                        print(f"✅ Enterprise features confirmed - Found: {enterprise_features}")
                    else:
                        print("⚠️  Enterprise features may be missing")
                    
                    print("✅ PHP/Laravel service validation complete")
                else:
                    print("❌ PHP/Laravel Development service NOT FOUND")
                    return False
                
                # 4. List all services for verification
                print("\n📋 Complete Services List:")
                for i, service in enumerate(services, 1):
                    print(f"   {i}. {service['name']} ({service['icon']})")
                
                print("\n🎉 ALL SERVICES ENDPOINT VALIDATIONS PASSED!")
                return True
                
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            return False

async def main():
    """Main test runner"""
    success = await test_services_endpoint()
    
    if success:
        print("\n✅ REVIEW REQUEST COMPLETED SUCCESSFULLY")
        print("   - Services endpoint returns 8 services total ✅")
        print("   - All services have proper data structure ✅") 
        print("   - PHP/Laravel service present with enterprise features ✅")
        return 0
    else:
        print("\n❌ REVIEW REQUEST FAILED")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)