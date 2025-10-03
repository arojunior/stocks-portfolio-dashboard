#!/usr/bin/env python3
"""
Quick test script to verify your Meta Threads access token
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_token():
    """Test your Meta Threads access token"""
    print("🧪 Testing Meta Threads Access Token...")
    print("=" * 50)
    
    # Get token from environment
    token = os.getenv("META_ACCESS_TOKEN")
    
    if not token:
        print("❌ No META_ACCESS_TOKEN found in .env file")
        print("   Please add your token to the .env file")
        return False
    
    print(f"✅ Found token: {token[:20]}...")
    
    # Test 1: Basic API call
    print("\n1. Testing basic API call...")
    try:
        url = "https://graph.threads.net/v1.0/me"
        params = {"access_token": token}
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! API call worked")
            print(f"   User ID: {data.get('id', 'Unknown')}")
            print(f"   Username: {data.get('username', 'Unknown')}")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_threads_endpoint():
    """Test the threads endpoint specifically"""
    print("\n2. Testing threads endpoint...")
    
    token = os.getenv("META_ACCESS_TOKEN")
    if not token:
        return False
    
    try:
        url = "https://graph.threads.net/v1.0/me/threads"
        params = {
            "access_token": token,
            "fields": "id,text,created_time",
            "limit": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            threads = data.get("data", [])
            print(f"✅ SUCCESS! Found {len(threads)} threads")
            
            if threads:
                print("   Sample threads:")
                for i, thread in enumerate(threads[:2], 1):
                    text = thread.get("text", "No text")[:50]
                    print(f"   {i}. {text}...")
            else:
                print("   No threads found (this is normal if you haven't posted)")
            
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🔍 META THREADS TOKEN TESTER")
    print("=" * 50)
    
    # Test basic API
    basic_ok = test_token()
    
    if basic_ok:
        # Test threads endpoint
        threads_ok = test_threads_endpoint()
        
        print("\n" + "=" * 50)
        print("📊 RESULTS")
        print("=" * 50)
        print(f"Basic API: {'✅ PASS' if basic_ok else '❌ FAIL'}")
        print(f"Threads API: {'✅ PASS' if threads_ok else '❌ FAIL'}")
        
        if basic_ok and threads_ok:
            print("\n🎉 EXCELLENT! Your token is working perfectly!")
            print("   You can now use the Threads integration in your app.")
        elif basic_ok:
            print("\n⚠️  Basic API works but Threads API failed.")
            print("   This might be due to missing permissions or no threads.")
        else:
            print("\n❌ Token is not working. Please check:")
            print("   1. Token format (should start with 'EAABwzL...')")
            print("   2. Token permissions (threads_basic, etc.)")
            print("   3. App status (should be in Development mode)")
    else:
        print("\n❌ Basic API failed. Please check:")
        print("   1. Token is correct and not expired")
        print("   2. App is in Development mode")
        print("   3. You have the right permissions")

if __name__ == "__main__":
    main()
