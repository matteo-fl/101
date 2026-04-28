#!/usr/bin/env python
"""
Simple backend test suite - checks main API endpoints
Run: python test_simple.py
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_config():
    """Test config endpoint"""
    print("\n=== Testing Config ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/config", timeout=5)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Styles: {data.get('styles', [])}")
        print(f"Tones: {data.get('tones', [])}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_generate_simple():
    """Test simple presentation generation without images"""
    print("\n=== Testing Generate Simple Presentation ===")
    try:
        data = {
            "prompt": "Введение в искусственный интеллект",
            "num_slides": 3,
            "style": "corporate",
            "tone": "professional",
            "include_images": False
        }
        
        print(f"Sending: {json.dumps(data, ensure_ascii=False)}")
        resp = requests.post(
            f"{BASE_URL}/api/generate",
            data=data,
            timeout=120
        )
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            session_id = result.get('session_id')
            slides_count = len(result.get('slides', []))
            print(f"✅ Session ID: {session_id}")
            print(f"✅ Slides: {slides_count}")
            return session_id
        else:
            print(f"❌ Error: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_session_info(session_id):
    """Test getting session info"""
    print(f"\n=== Testing Get Session Info ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/session/{session_id}", timeout=5)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Session: {data.get('session_id')}")
            print(f"✅ Slides count: {data.get('slides_count')}")
            print(f"✅ Created at: {data.get('created_at')}")
            return True
        else:
            print(f"❌ Error: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_edit_slide(session_id):
    """Test editing a slide"""
    print(f"\n=== Testing Edit Slide ===")
    try:
        data = {
            "title": "Обновленный заголовок",
            "content": "• Новый пункт 1\n• Новый пункт 2"
        }
        
        resp = requests.put(
            f"{BASE_URL}/api/session/{session_id}/slides/0",
            data=data,
            timeout=5
        )
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ {result.get('message')}")
            print(f"✅ New title: {result.get('slide', {}).get('title')}")
            return True
        else:
            print(f"❌ Error: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_download(session_id):
    """Test downloading presentation"""
    print(f"\n=== Testing Download ===")
    try:
        resp = requests.get(f"{BASE_URL}/api/download/{session_id}", timeout=30)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            # Save file
            filename = f"test_presentation_{session_id[:8]}.pptx"
            with open(filename, "wb") as f:
                f.write(resp.content)
            
            file_size = len(resp.content) / 1024
            print(f"✅ Downloaded: {filename} ({file_size:.1f} KB)")
            return True
        else:
            print(f"❌ Error: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("BACKEND API TEST SUITE")
    print("=" * 60)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"❌ Server not running at {BASE_URL}")
        print("Start server: python -m uvicorn app.main:app --reload")
        return
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Config", test_config()))
    
    session_id = test_generate_simple()
    results.append(("Generate Presentation", session_id is not None))
    
    if session_id:
        results.append(("Get Session Info", test_session_info(session_id)))
        results.append(("Edit Slide", test_edit_slide(session_id)))
        results.append(("Download", test_download(session_id)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")

if __name__ == "__main__":
    main()
