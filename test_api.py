"""
Example test script for the CS 1.6 Sprite Generator API
"""

import requests
import json
from pathlib import Path

# API base URL (change to your deployed URL)
API_URL = "https://cs16-sprite-api.onrender.com"


def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_convert_image(image_path: str):
    """Test converting a single image"""
    print(f"Testing image conversion: {image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {
            'sprite_type': 'vp_parallel',
            'texture_format': 'additive',
            'max_width': 128,
            'max_height': 128,
        }
        
        response = requests.post(
            f"{API_URL}/api/v1/convert/image",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success!")
        print(json.dumps(result, indent=2))
        
        # Download the sprite
        sprite_id = result['sprite_id']
        download_sprite(sprite_id, f"output_{Path(image_path).stem}.spr")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    print()


def test_convert_video(video_path: str):
    """Test converting a video"""
    print(f"Testing video conversion: {video_path}")
    
    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {
            'sprite_type': 'vp_parallel',
            'texture_format': 'additive',
            'fps': 15,
            'max_frames': 30,
            'max_width': 128,
            'max_height': 128,
        }
        
        response = requests.post(
            f"{API_URL}/api/v1/convert/video",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success!")
        print(json.dumps(result, indent=2))
        
        # Download the sprite
        sprite_id = result['sprite_id']
        download_sprite(sprite_id, f"output_{Path(video_path).stem}.spr")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    print()


def test_convert_images_animated(image_paths: list):
    """Test converting multiple images to animated sprite"""
    print(f"Testing animated sprite from {len(image_paths)} images")
    
    files = [('files', open(path, 'rb')) for path in image_paths]
    data = {
        'sprite_type': 'vp_parallel',
        'texture_format': 'additive',
        'frame_interval': 0.1,
        'max_width': 128,
        'max_height': 128,
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/convert/images/animated",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success!")
            print(json.dumps(result, indent=2))
            
            # Download the sprite
            sprite_id = result['sprite_id']
            download_sprite(sprite_id, "output_animated.spr")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    finally:
        # Close all file handles
        for _, file_obj in files:
            file_obj.close()
    print()


def download_sprite(sprite_id: str, output_filename: str):
    """Download a sprite file"""
    print(f"Downloading sprite {sprite_id}...")
    
    response = requests.get(
        f"{API_URL}/api/v1/download/{sprite_id}",
        stream=True
    )
    
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved to: {output_filename}")
    else:
        print(f"Download failed: {response.status_code}")
    print()


def test_delete_sprite(sprite_id: str):
    """Test deleting a sprite"""
    print(f"Testing sprite deletion: {sprite_id}")
    
    response = requests.delete(f"{API_URL}/api/v1/delete/{sprite_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success!")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("CS 1.6 Sprite Generator API - Test Script")
    print("=" * 50)
    print()
    
    # Test health check
    test_health_check()
    
    # Example usage (uncomment and modify paths as needed):
    
    # Test image conversion
    # test_convert_image("path/to/your/image.png")
    
    # Test video conversion
    # test_convert_video("path/to/your/video.mp4")
    
    # Test animated sprite from multiple images
    # test_convert_images_animated([
    #     "path/to/frame1.png",
    #     "path/to/frame2.png",
    #     "path/to/frame3.png",
    # ])
    
    # Test deletion
    # test_delete_sprite("sprite-id-here")
    
    print("Tests completed!")
