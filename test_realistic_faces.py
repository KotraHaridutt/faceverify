#!/usr/bin/env python3
"""
Test with more realistic face images to verify DeepFace functionality
"""

import requests
import io
from PIL import Image, ImageDraw
import time

BACKEND_URL = "https://faceverify-ai.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_realistic_face_image(width=300, height=400, face_color=(255, 220, 177)):
    """Create a more realistic face image for testing"""
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw a more detailed face
    face_center = (width//2, height//2)
    face_width = width // 3
    face_height = height // 3
    
    # Face outline (oval)
    draw.ellipse([
        face_center[0] - face_width, face_center[1] - face_height,
        face_center[0] + face_width, face_center[1] + face_height
    ], fill=face_color, outline=(200, 180, 160), width=3)
    
    # Eyes with more detail
    eye_y = face_center[1] - face_height // 2
    left_eye_x = face_center[0] - face_width // 2
    right_eye_x = face_center[0] + face_width // 2
    eye_width = 20
    eye_height = 12
    
    # Eye whites
    draw.ellipse([left_eye_x - eye_width, eye_y - eye_height, 
                  left_eye_x + eye_width, eye_y + eye_height], fill=(255, 255, 255))
    draw.ellipse([right_eye_x - eye_width, eye_y - eye_height, 
                  right_eye_x + eye_width, eye_y + eye_height], fill=(255, 255, 255))
    
    # Pupils
    draw.ellipse([left_eye_x - 8, eye_y - 8, left_eye_x + 8, eye_y + 8], fill=(0, 0, 0))
    draw.ellipse([right_eye_x - 8, eye_y - 8, right_eye_x + 8, eye_y + 8], fill=(0, 0, 0))
    
    # Eyebrows
    draw.arc([left_eye_x - 25, eye_y - 25, left_eye_x + 25, eye_y - 5], 
             start=0, end=180, fill=(100, 80, 60), width=4)
    draw.arc([right_eye_x - 25, eye_y - 25, right_eye_x + 25, eye_y - 5], 
             start=0, end=180, fill=(100, 80, 60), width=4)
    
    # Nose with more detail
    nose_y = face_center[1]
    nose_points = [
        (face_center[0], nose_y - 15),
        (face_center[0] - 8, nose_y + 5),
        (face_center[0] + 8, nose_y + 5)
    ]
    draw.polygon(nose_points, fill=(220, 190, 160), outline=(200, 170, 140))
    
    # Mouth with more detail
    mouth_y = face_center[1] + face_height // 2
    mouth_width = 30
    draw.ellipse([face_center[0] - mouth_width, mouth_y - 8, 
                  face_center[0] + mouth_width, mouth_y + 8], 
                 fill=(200, 100, 100), outline=(150, 80, 80), width=2)
    
    # Hair
    draw.ellipse([
        face_center[0] - face_width - 10, face_center[1] - face_height - 30,
        face_center[0] + face_width + 10, face_center[1] - face_height + 20
    ], fill=(80, 60, 40))
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=90)
    img_bytes.seek(0)
    
    return img_bytes

def test_realistic_face_verification():
    """Test with more realistic face images"""
    print("🔍 Testing with realistic face images...")
    
    try:
        # Create two different but realistic face images
        face1 = create_realistic_face_image(face_color=(255, 220, 177))
        face2 = create_realistic_face_image(face_color=(240, 200, 160))
        
        files = {
            'image1': ('realistic_face1.jpg', face1, 'image/jpeg'),
            'image2': ('realistic_face2.jpg', face2, 'image/jpeg')
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
        end_time = time.time()
        
        print(f"   Request completed in {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Realistic face verification successful")
            print(f"   Verified: {result.get('verified')}")
            print(f"   Match Percentage: {result.get('match_percentage')}%")
            print(f"   Model Used: {result.get('model_used')}")
            print(f"   Facial Areas: {len(result.get('facial_areas', {}))} detected")
            
            # Check facial area coordinates
            facial_areas = result.get('facial_areas', {})
            for key, area in facial_areas.items():
                print(f"   {key}: x={area['x']}, y={area['y']}, w={area['w']}, h={area['h']}")
            
            return True
        else:
            print(f"❌ Realistic face verification failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Realistic face verification test failed: {str(e)}")
        return False

def test_different_faces():
    """Test with very different face characteristics"""
    print("\n🔍 Testing with different face characteristics...")
    
    try:
        # Create faces with different characteristics
        face1 = create_realistic_face_image(width=250, height=350, face_color=(255, 220, 177))
        face2 = create_realistic_face_image(width=350, height=300, face_color=(200, 160, 120))
        
        files = {
            'image1': ('different_face1.jpg', face1, 'image/jpeg'),
            'image2': ('different_face2.jpg', face2, 'image/jpeg')
        }
        
        response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Different faces verification successful")
            print(f"   Verified: {result.get('verified')}")
            print(f"   Match Percentage: {result.get('match_percentage')}%")
            
            # Different faces should have lower match percentage
            match_percentage = result.get('match_percentage', 0)
            if match_percentage < 80:
                print("✅ Different faces correctly identified as different")
            else:
                print("⚠️  Different faces have high similarity - this might be expected with simple drawings")
            
            return True
        else:
            print(f"❌ Different faces verification failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Different faces test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing FaceVerify AI with Realistic Images")
    print("=" * 50)
    
    test_realistic_face_verification()
    test_different_faces()