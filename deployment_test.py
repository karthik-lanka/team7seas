#!/usr/bin/env python3
"""
Deployment test script to verify all components work correctly
"""

import os
import sys
import requests
import json

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI: {e}")
        return False
    
    try:
        import pinecone
        print(f"✓ Pinecone {pinecone.__version__}")
    except ImportError as e:
        print(f"✗ Pinecone: {e}")
        return False
    
    try:
        import pymupdf
        print(f"✓ PyMuPDF {pymupdf.__version__}")
    except ImportError as e:
        print(f"✗ PyMuPDF: {e}")
        return False
    
    try:
        from google import genai
        print("✓ Google GenAI")
    except ImportError as e:
        print(f"✗ Google GenAI: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\nTesting environment...")
    
    required_vars = ["GEMINI_API_KEY", "PINECONE_API_KEY"]
    all_set = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✓ {var} is set")
        else:
            print(f"✗ {var} is not set")
            all_set = False
    
    return all_set

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health endpoint error: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✓ Root endpoint working")
        else:
            print(f"✗ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Root endpoint error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 HackRx API Deployment Test\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("API Endpoints Test", test_api_endpoints)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if not test_func():
            all_passed = False
            print(f"❌ {test_name} FAILED\n")
        else:
            print(f"✅ {test_name} PASSED\n")
    
    if all_passed:
        print("🎉 All tests passed! Ready for deployment.")
        return 0
    else:
        print("💥 Some tests failed. Fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())