#!/usr/bin/env python3
"""
Advanced deployment readiness checker for HackRx API
Validates all components before and after deployment
"""

import os
import sys
import requests
import json
import time
from typing import Dict, List, Tuple, Optional

class DeploymentChecker:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "http://localhost:5000"
        self.api_token = "9953d967b81381295864fb71b20cd27085ee80c24512eeabce64f3f921bb009d"
        self.test_document = "https://www.orimi.com/pdf-test.pdf"
        
    def check_environment_variables(self) -> bool:
        """Check if required environment variables are set"""
        print("🔍 Checking Environment Variables...")
        
        required_vars = ["GEMINI_API_KEY", "PINECONE_API_KEY"]
        optional_vars = ["PINECONE_INDEX", "PINECONE_ENV"]
        
        all_good = True
        for var in required_vars:
            if os.getenv(var):
                print(f"  ✅ {var} is set")
            else:
                print(f"  ❌ {var} is NOT set (REQUIRED)")
                all_good = False
        
        for var in optional_vars:
            if os.getenv(var):
                print(f"  ✅ {var} is set")
            else:
                print(f"  ⚠️  {var} not set (using default)")
        
        return all_good
    
    def check_dependencies(self) -> bool:
        """Check if all required Python packages are importable"""
        print("\n📦 Checking Dependencies...")
        
        dependencies = [
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
            ("pydantic", "Pydantic"),
            ("requests", "Requests"),
            ("pymupdf", "PyMuPDF"),
            ("docx", "python-docx"),
            ("google.genai", "Google GenAI"),
            ("pinecone", "Pinecone")
        ]
        
        all_good = True
        for package, name in dependencies:
            try:
                __import__(package)
                print(f"  ✅ {name} imported successfully")
            except ImportError as e:
                print(f"  ❌ {name} import failed: {e}")
                all_good = False
        
        return all_good
    
    def check_files_exist(self) -> bool:
        """Check if all required files exist"""
        print("\n📁 Checking Required Files...")
        
        required_files = [
            "main.py",
            "models.py", 
            "gemini_client.py",
            "pinecone_client.py",
            "document_processor.py",
            "text_chunker.py",
            "question_answerer.py",
            "render-requirements.txt",
            "render.yaml",
            "Dockerfile"
        ]
        
        all_good = True
        for file in required_files:
            if os.path.exists(file):
                print(f"  ✅ {file} exists")
            else:
                print(f"  ❌ {file} is missing")
                all_good = False
        
        return all_good
    
    def check_api_health(self, timeout: int = 10) -> bool:
        """Check API health endpoint"""
        print(f"\n🏥 Checking API Health ({self.base_url})...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Health check passed: {data}")
                return True
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Health check error: {e}")
            return False
    
    def check_api_root(self, timeout: int = 10) -> bool:
        """Check API root endpoint"""
        print(f"\n🏠 Checking Root Endpoint ({self.base_url})...")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Root endpoint working: {data.get('service', 'Unknown')}")
                return True
            else:
                print(f"  ❌ Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Root endpoint error: {e}")
            return False
    
    def test_api_functionality(self, timeout: int = 60) -> Tuple[bool, Optional[float]]:
        """Test full API functionality with document processing"""
        print(f"\n🧪 Testing API Functionality ({self.base_url})...")
        
        test_payload = {
            "documents": self.test_document,
            "questions": [
                "What is this document about?",
                "What is the main purpose?"
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/hackrx/run",
                json=test_payload,
                headers=headers,
                timeout=timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answers = data.get("answers", [])
                print(f"  ✅ API test passed in {response_time:.2f}s")
                print(f"  📊 Processed {len(answers)} questions")
                for i, answer in enumerate(answers, 1):
                    preview = answer[:100] + "..." if len(answer) > 100 else answer
                    print(f"    Q{i}: {preview}")
                return True, response_time
            else:
                print(f"  ❌ API test failed: {response.status_code}")
                print(f"    Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"  ❌ API test error: {e}")
            return False, None
    
    def check_render_deployment_files(self) -> bool:
        """Check Render-specific deployment files"""
        print("\n☁️  Checking Render Deployment Files...")
        
        # Check render.yaml
        if os.path.exists("render.yaml"):
            print("  ✅ render.yaml exists")
            try:
                with open("render.yaml", "r") as f:
                    content = f.read()
                    if "hackrx-document-api" in content and "uvicorn main:app" in content:
                        print("  ✅ render.yaml has correct configuration")
                    else:
                        print("  ⚠️  render.yaml may have configuration issues")
            except Exception as e:
                print(f"  ❌ Error reading render.yaml: {e}")
                return False
        else:
            print("  ❌ render.yaml is missing")
            return False
        
        # Check render-requirements.txt
        if os.path.exists("render-requirements.txt"):
            print("  ✅ render-requirements.txt exists")
            try:
                with open("render-requirements.txt", "r") as f:
                    content = f.read()
                    required_packages = ["fastapi", "uvicorn", "google-genai", "pinecone-client"]
                    missing = [pkg for pkg in required_packages if pkg not in content]
                    if not missing:
                        print("  ✅ All required packages in render-requirements.txt")
                    else:
                        print(f"  ❌ Missing packages: {missing}")
                        return False
            except Exception as e:
                print(f"  ❌ Error reading render-requirements.txt: {e}")
                return False
        else:
            print("  ❌ render-requirements.txt is missing")
            return False
        
        return True
    
    def run_pre_deployment_checks(self) -> bool:
        """Run all pre-deployment checks"""
        print("🚀 PRE-DEPLOYMENT READINESS CHECK\n")
        
        checks = [
            ("Environment Variables", self.check_environment_variables),
            ("Dependencies", self.check_dependencies),
            ("Required Files", self.check_files_exist),
            ("Render Files", self.check_render_deployment_files)
        ]
        
        results = []
        for name, check_func in checks:
            try:
                result = check_func()
                results.append((name, result))
            except Exception as e:
                print(f"  ❌ {name} check failed with error: {e}")
                results.append((name, False))
        
        # Summary
        print("\n📋 PRE-DEPLOYMENT SUMMARY:")
        all_passed = True
        for name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} {name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 ALL PRE-DEPLOYMENT CHECKS PASSED!")
            print("✅ Ready for Render deployment")
        else:
            print("\n💥 SOME CHECKS FAILED!")
            print("❌ Fix issues before deploying")
        
        return all_passed
    
    def run_post_deployment_checks(self) -> bool:
        """Run all post-deployment checks"""
        print("🔍 POST-DEPLOYMENT VERIFICATION\n")
        
        # Basic connectivity
        health_ok = self.check_api_health()
        root_ok = self.check_api_root()
        
        if not (health_ok and root_ok):
            print("\n💥 BASIC CONNECTIVITY FAILED!")
            return False
        
        # Full functionality test
        api_ok, response_time = self.test_api_functionality()
        
        # Summary
        print("\n📋 POST-DEPLOYMENT SUMMARY:")
        print(f"  ✅ Health Check: {'PASS' if health_ok else 'FAIL'}")
        print(f"  ✅ Root Endpoint: {'PASS' if root_ok else 'FAIL'}")
        print(f"  ✅ API Functionality: {'PASS' if api_ok else 'FAIL'}")
        
        if response_time:
            print(f"  ⏱️  Response Time: {response_time:.2f}s")
            if response_time < 60:
                print(f"  🚀 Performance: EXCELLENT")
            elif response_time < 120:
                print(f"  ✅ Performance: GOOD") 
            else:
                print(f"  ⚠️  Performance: SLOW")
        
        if health_ok and root_ok and api_ok:
            print("\n🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!")
            print("✅ API is live and fully functional")
            return True
        else:
            print("\n💥 DEPLOYMENT VERIFICATION FAILED!")
            print("❌ Check logs and fix issues")
            return False

def main():
    """Main function to run deployment checks"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        base_url = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        print("Usage:")
        print("  python deployment_checker.py pre                    # Pre-deployment checks")
        print("  python deployment_checker.py post [url]             # Post-deployment checks")
        print("  python deployment_checker.py post https://your-app.onrender.com")
        sys.exit(1)
    
    checker = DeploymentChecker(base_url)
    
    if mode == "pre":
        success = checker.run_pre_deployment_checks()
    elif mode == "post":
        success = checker.run_post_deployment_checks()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()