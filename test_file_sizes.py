#!/usr/bin/env python3
"""
Test script to check actual file sizes being generated
"""

import io
from PIL import Image, ImageDraw
import requests

def create_large_test_image():
    """Create a test image larger than 5MB for size validation testing"""
    # Create a very large image (should exceed 5MB)
    img = Image.new('RGB', (4000, 4000), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Add some content to make it larger
    for i in range(0, 4000, 50):
        draw.line([(0, i), (4000, i)], fill=(i % 255, (i*2) % 255, (i*3) % 255), width=2)
        draw.line([(i, 0), (i, 4000)], fill=((i*3) % 255, i % 255, (i*2) % 255), width=2)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=100)  # High quality to increase size
    img_bytes.seek(0)
    
    return img_bytes

def create_test_face_image(width=400, height=400, face_color=(255, 220, 177)):
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

def test_file_sizes():
    print("Testing file sizes...")
    
    # Test normal image
    normal_image = create_test_face_image()
    normal_size = len(normal_image.getvalue())
    print(f"Normal image size: {normal_size / (1024*1024):.2f} MB")
    
    # Test large image
    large_image = create_large_test_image()
    large_size = len(large_image.getvalue())
    print(f"Large image size: {large_size / (1024*1024):.2f} MB")
    
    # Create a definitely large file (raw bytes)
    huge_data = b'x' * (6 * 1024 * 1024)  # 6MB of data
    print(f"Huge data size: {len(huge_data) / (1024*1024):.2f} MB")
    
    # Test with the API
    BACKEND_URL = "https://faceverify-ai.preview.emergentagent.com"
    API_BASE = f"{BACKEND_URL}/api"
    
    print("\nTesting with large image...")
    large_image.seek(0)
    normal_image.seek(0)
    
    files = {
        'image1': ('large_face.jpg', large_image, 'image/jpeg'),
        'image2': ('normal_face.jpg', normal_image, 'image/jpeg')
    }
    
    response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.text}")
    
    print("\nTesting with huge raw data...")
    files = {
        'image1': ('huge_file.jpg', io.BytesIO(huge_data), 'image/jpeg'),
        'image2': ('normal_face.jpg', create_test_face_image(), 'image/jpeg')
    }
    
    response = requests.post(f"{API_BASE}/verify", files=files, timeout=60)
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_file_sizes()