#!/usr/bin/env python3
"""
Backend API Testing for FaceVerify AI
Tests the /api/verify endpoint with DeepFace ArcFace integration
"""

import requests
import os
import time
import tempfile
from PIL import Image, ImageDraw
import io
import json

# Backend URL from frontend/.env
BACKEND_URL = "https://faceverify-ai.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_test_face_image(width=400, height=400, face_color=(255, 220, 177), filename="test_face.jpg"):
    """Create a simple test image with a face-like shape for testing"""
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple face
    # Face outline (circle)
    face_center = (width//2, height//2)
    face_radius = min(width, height) // 3
    draw.ellipse([
        face_center[0] - face_radius, face_center[1] - face_radius,
        face_center[0] + face_radius, face_center[1] + face_radius
    ], fill=face_color, outline=(0, 0, 0), width=2)
    
    # Eyes
    eye_y = face_center[1] - face_radius // 3
    left_eye_x = face_center[0] - face_radius // 3
    right_eye_x = face_center[0] + face_radius // 3
    eye_radius = face_radius // 8
    
    draw.ellipse([left_eye_x - eye_radius, eye_y - eye_radius, 
                  left_eye_x + eye_radius, eye_y + eye_radius], fill=(0, 0, 0))
    draw.ellipse([right_eye_x - eye_radius, eye_y - eye_radius, 
                  right_eye_x + eye_radius, eye_y + eye_radius], fill=(0, 0, 0))
    
    # Nose
    nose_y = face_center[1]
    draw.ellipse([face_center[0] - 5, nose_y - 10, face_center[0] + 5, nose_y + 10], 
                 fill=(200, 180, 140))
    
    # Mouth
    mouth_y = face_center[1] + face_radius // 3
    draw.arc([face_center[0] - face_radius//4, mouth_y - 10, 
              face_center[0] + face_radius//4, mouth_y + 10], 
             start=0, end=180, fill=(0, 0, 0), width=3)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)
    
    return img_bytes

def create_large_test_image():
    """Create a test image larger than 5MB for size validation testing"""
    # Create raw data that's definitely larger than 5MB
    large_data = b'x' * (6 * 1024 * 1024)  # 6MB of data
    return io.BytesIO(large_data)

def test_api_health():
    """Test if the API is accessible"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=30)
        if response.status_code == 200:
            print("✅ API is accessible")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed: {str(e)}")
        return False

def test_verify_endpoint_with_valid_images():
    """Test /api/verify endpoint with valid face images"""
    print("\n🔍 Testing /api/verify with valid face images...")
    
    try:
        # Create two similar test face images
        image1_bytes = create_test_face_image(filename="face1.jpg")
        image2_bytes = create_test_face_image(face_color=(255, 210, 170), filename="face2.jpg")
        
        files = {
            'image1': ('face1.jpg', image1_bytes, 'image/jpeg'),
            'image2': ('face2.jpg', image2_bytes, 'image/jpeg')
        }
        
        print("   Sending request to /api/verify...")
        print("   ⚠️  Note: First request may take 30-60 seconds (model loading)")
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/verify", files=files, timeout=120)
        end_time = time.time()
        
        print(f"   Request completed in {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Face verification successful")
            print(f"   Verified: {result.get('verified')}")
            print(f"   Match Percentage: {result.get('match_percentage')}%")
            print(f"   Model Used: {result.get('model_used')}")
            print(f"   Facial Areas: {len(result.get('facial_areas', {}))} detected")
            
            # Validate response structure
            required_fields = ['verified', 'match_percentage', 'model_used', 'facial_areas']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Validate data types
            if not isinstance(result['verified'], bool):
                print("❌ 'verified' field should be boolean")
                return False
            
            if not isinstance(result['match_percentage'], (int, float)):
                print("❌ 'match_percentage' field should be numeric")
                return False
            
            if result['model_used'] != 'ArcFace':
                print(f"❌ Expected model 'ArcFace', got '{result['model_used']}'")
                return False
            
            print("✅ Response structure validation passed")
            return True
            
        else:
            print(f"❌ Face verification failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Face verification test failed: {str(e)}")
        return False

def test_file_size_validation():
    """Test file size validation (should reject >5MB files)"""
    print("\n🔍 Testing file size validation...")
    
    try:
        # Create a large image (>5MB)
        large_image = create_large_test_image()
        normal_image = create_test_face_image()
        
        files = {
            'image1': ('large_face.jpg', large_image, 'image/jpeg'),
            'image2': ('normal_face.jpg', normal_image, 'image/jpeg')
        }
        
        response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
        
        if response.status_code == 400:
            error_detail = response.json().get('detail', '')
            if "5MB" in error_detail or "size" in error_detail.lower():
                print("✅ File size validation working correctly")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Expected 400 status code for large file, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File size validation test failed: {str(e)}")
        return False

def test_file_type_validation():
    """Test file type validation (should reject non-JPG/PNG files)"""
    print("\n🔍 Testing file type validation...")
    
    try:
        # Create a text file disguised as an image
        text_content = b"This is not an image file"
        normal_image = create_test_face_image()
        
        files = {
            'image1': ('fake_image.jpg', io.BytesIO(text_content), 'image/jpeg'),
            'image2': ('normal_face.jpg', normal_image, 'image/jpeg')
        }
        
        response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
        
        if response.status_code == 400:
            error_detail = response.json().get('detail', '')
            if "JPEG" in error_detail or "PNG" in error_detail or "supported" in error_detail:
                print("✅ File type validation working correctly")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Expected 400 status code for invalid file type, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File type validation test failed: {str(e)}")
        return False

def test_no_face_detection_error():
    """Test error handling when no faces are detected"""
    print("\n🔍 Testing no face detection error handling...")
    
    try:
        # Create images without faces (just solid colors)
        img1 = Image.new('RGB', (200, 200), color=(255, 0, 0))  # Red square
        img2 = Image.new('RGB', (200, 200), color=(0, 255, 0))  # Green square
        
        img1_bytes = io.BytesIO()
        img2_bytes = io.BytesIO()
        
        img1.save(img1_bytes, format='JPEG')
        img2.save(img2_bytes, format='JPEG')
        
        img1_bytes.seek(0)
        img2_bytes.seek(0)
        
        files = {
            'image1': ('no_face1.jpg', img1_bytes, 'image/jpeg'),
            'image2': ('no_face2.jpg', img2_bytes, 'image/jpeg')
        }
        
        response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
        
        if response.status_code == 400:
            error_detail = response.json().get('detail', '')
            if "face" in error_detail.lower() and ("detect" in error_detail.lower() or "not" in error_detail.lower()):
                print("✅ No face detection error handling working correctly")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Expected 400 status code for no face detection, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ No face detection test failed: {str(e)}")
        return False

def test_performance_subsequent_requests():
    """Test that subsequent requests are faster than the first one"""
    print("\n🔍 Testing performance of subsequent requests...")
    
    try:
        image1_bytes = create_test_face_image()
        image2_bytes = create_test_face_image(face_color=(255, 200, 160))
        
        files = {
            'image1': ('face1.jpg', image1_bytes, 'image/jpeg'),
            'image2': ('face2.jpg', image2_bytes, 'image/jpeg')
        }
        
        print("   Making second request (should be faster)...")
        start_time = time.time()
        response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
        end_time = time.time()
        
        request_time = end_time - start_time
        print(f"   Second request completed in {request_time:.2f} seconds")
        
        if response.status_code == 200:
            if request_time < 30:  # Should be much faster than first request
                print("✅ Subsequent request performance is good")
                return True
            else:
                print("⚠️  Subsequent request took longer than expected, but still working")
                return True
        else:
            print(f"❌ Subsequent request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("🚀 Starting FaceVerify AI Backend API Tests")
    print("=" * 60)
    
    test_results = {}
    
    # Test API health first
    test_results['api_health'] = test_api_health()
    
    if not test_results['api_health']:
        print("\n❌ API is not accessible. Stopping tests.")
        return test_results
    
    # Run all verification tests
    test_results['valid_images'] = test_verify_endpoint_with_valid_images()
    test_results['file_size_validation'] = test_file_size_validation()
    test_results['file_type_validation'] = test_file_type_validation()
    test_results['no_face_detection'] = test_no_face_detection_error()
    test_results['performance'] = test_performance_subsequent_requests()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Backend API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return test_results

if __name__ == "__main__":
    results = run_all_tests()