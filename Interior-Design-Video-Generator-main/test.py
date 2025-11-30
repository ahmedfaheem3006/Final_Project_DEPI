"""
Test Client for Complete Interior Design API
"""

import requests
import time
import json
from pathlib import Path
import argparse

API_BASE = "http://localhost:8000"

def health_check():
    """Check API health"""
    print("\n" + "="*60)
    print("🏥 HEALTH CHECK")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"🖥️  Device: {data['device']}")
        print(f"🎮 GPU: {data['gpu_name']}")
        print(f"🖼️  Image Model: {'Loaded' if data['image_model_loaded'] else 'Not Loaded'}")
        print(f"🎬 Video Model: {'Loaded' if data['video_model_loaded'] else 'Not Loaded'}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_image_generation(prompt: str):
    """Test image generation from text"""
    print("\n" + "="*60)
    print("🖼️  IMAGE GENERATION TEST")
    print("="*60)
    print(f"Prompt: {prompt}\n")
    
    # Request image generation
    response = requests.post(
        f"{API_BASE}/api/v1/generate/image",
        json={
            "prompt": prompt,
            "room_type": "living_room",
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create job: {response.status_code}")
        return None
    
    job_id = response.json()["job_id"]
    print(f"✅ Job created: {job_id}")
    
    # Wait for completion
    print("\n⏳ Waiting for image generation...")
    while True:
        status_response = requests.get(f"{API_BASE}/api/v1/status/{job_id}")
        status = status_response.json()
        
        print(f"📊 {status['status']} - {status['progress']}% - {status['message']}")
        
        if status['status'] == 'completed':
            print("\n✅ Image generated successfully!")
            
            # Download image
            image_response = requests.get(f"{API_BASE}/api/v1/download/image/{job_id}")
            output_path = f"test_image_{job_id}.png"
            with open(output_path, "wb") as f:
                f.write(image_response.content)
            
            print(f"💾 Image saved: {output_path}")
            return output_path
            
        elif status['status'] == 'failed':
            print(f"\n❌ Generation failed: {status['message']}")
            return None
        
        time.sleep(5)

def test_video_from_image(image_path: str, room_type: str = "living_room", 
                         motion_style: str = "moderate"):
    """Test video generation from image file"""
    print("\n" + "="*60)
    print("🎬 VIDEO GENERATION TEST (From Image)")
    print("="*60)
    print(f"Image: {image_path}")
    print(f"Room: {room_type}")
    print(f"Motion: {motion_style}\n")
    
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{API_BASE}/api/v1/generate/video",
            files={"file": f},
            data={
                "room_type": room_type,
                "motion_style": motion_style,
                "enhance_lighting": True,
                "adjust_contrast": True
            }
        )
    
    if response.status_code != 200:
        print(f"❌ Failed to create job: {response.status_code}")
        return None
    
    job_id = response.json()["job_id"]
    print(f"✅ Job created: {job_id}")
    
    # Wait for completion
    print("\n⏳ Waiting for video generation...")
    while True:
        status_response = requests.get(f"{API_BASE}/api/v1/status/{job_id}")
        status = status_response.json()
        
        print(f"📊 {status['status']} - {status['progress']}% - {status['message']}")
        
        if status['status'] == 'completed':
            print("\n✅ Video generated successfully!")
            print(f"⏱️  Duration: {status.get('duration', 'N/A')} seconds")
            print(f"🎞️  Frames: {status.get('frames', 'N/A')}")
            
            # Download video
            video_response = requests.get(f"{API_BASE}/api/v1/download/video/{job_id}")
            output_path = f"test_video_{job_id}.mp4"
            with open(output_path, "wb") as f:
                f.write(video_response.content)
            
            print(f"💾 Video saved: {output_path}")
            return output_path
            
        elif status['status'] == 'failed':
            print(f"\n❌ Generation failed: {status['message']}")
            return None
        
        time.sleep(5)

def test_image_to_video_pipeline(prompt: str, room_type: str = "living_room",
                                motion_style: str = "moderate"):
    """Test complete pipeline: text -> image -> video"""
    print("\n" + "="*60)
    print("🚀 COMPLETE PIPELINE TEST (Text -> Image -> Video)")
    print("="*60)
    print(f"Prompt: {prompt}")
    print(f"Room: {room_type}")
    print(f"Motion: {motion_style}\n")
    
    # Request complete pipeline
    response = requests.post(
        f"{API_BASE}/api/v1/generate/image-to-video",
        json={
            "prompt": prompt,
            "room_type": room_type,
            "motion_style": motion_style,
            "num_inference_steps": 20,
            "guidance_scale": 7.5
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create job: {response.status_code}")
        return None
    
    job_id = response.json()["job_id"]
    print(f"✅ Job created: {job_id}")
    
    # Wait for completion
    print("\n⏳ Waiting for complete generation...")
    image_downloaded = False
    
    while True:
        status_response = requests.get(f"{API_BASE}/api/v1/status/{job_id}")
        status = status_response.json()
        
        print(f"📊 {status['status']} - {status['progress']}% - {status['message']}")
        
        # Download image when available
        if not image_downloaded and status.get('image_url'):
            try:
                image_response = requests.get(f"{API_BASE}{status['image_url']}")
                if image_response.status_code == 200:
                    image_path = f"test_pipeline_image_{job_id}.png"
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    print(f"✅ Image downloaded: {image_path}")
                    image_downloaded = True
            except:
                pass
        
        if status['status'] == 'completed':
            print("\n✅ Complete pipeline finished!")
            print(f"⏱️  Duration: {status.get('duration', 'N/A')} seconds")
            print(f"🎞️  Frames: {status.get('frames', 'N/A')}")
            
            # Download video
            video_response = requests.get(f"{API_BASE}/api/v1/download/video/{job_id}")
            video_path = f"test_pipeline_video_{job_id}.mp4"
            with open(video_path, "wb") as f:
                f.write(video_response.content)
            
            print(f"💾 Video saved: {video_path}")
            return video_path
            
        elif status['status'] == 'failed':
            print(f"\n❌ Generation failed: {status['message']}")
            return None
        
        time.sleep(5)

def list_all_jobs():
    """List all jobs"""
    print("\n" + "="*60)
    print("📋 ALL JOBS")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/api/v1/jobs")
    if response.status_code == 200:
        jobs = response.json()['jobs']
        print(f"Total jobs: {len(jobs)}\n")
        for job in jobs:
            print(f"🔹 {job['job_id'][:8]}... | {job['job_type']} | {job['status']} ({job['progress']}%)")
    else:
        print(f"❌ Failed to list jobs: {response.status_code}")

# ============================================================================
# Main Test Scenarios
# ============================================================================

def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "="*60)
    print("🧪 COMPLETE API TEST SUITE")
    print("="*60)
    
    # 1. Health check
    if not health_check():
        print("\n❌ Health check failed. Make sure the API is running.")
        return
    
    time.sleep(2)
    
    # 2. Test image generation
    print("\n" + "="*60)
    print("TEST 1: Image Generation")
    print("="*60)
    image_path = test_image_generation(
        "modern luxury living room, beige sofa, wooden coffee table, large windows, plants"
    )
    
    if not image_path:
        print("❌ Image generation test failed")
        return
    
    time.sleep(2)
    
    # 3. Test video from generated image
    print("\n" + "="*60)
    print("TEST 2: Video from Generated Image")
    print("="*60)
    video_path = test_video_from_image(
        image_path=image_path,
        room_type="living_room",
        motion_style="showcase"
    )
    
    if not video_path:
        print("❌ Video generation test failed")
        return
    
    time.sleep(2)
    
    # 4. Test complete pipeline
    print("\n" + "="*60)
    print("TEST 3: Complete Pipeline (Text -> Image -> Video)")
    print("="*60)
    pipeline_video = test_image_to_video_pipeline(
        prompt="cozy bedroom, king size bed, warm lighting, wooden furniture, modern design",
        room_type="bedroom",
        motion_style="subtle"
    )
    
    if not pipeline_video:
        print("❌ Pipeline test failed")
        return
    
    time.sleep(2)
    
    # 5. List all jobs
    list_all_jobs()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)

# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Complete Interior Design API")
    parser.add_argument("--mode", choices=["all", "image", "video", "pipeline", "health"],
                       default="all", help="Test mode")
    parser.add_argument("--prompt", type=str, 
                       default="luxury living room, modern furniture, large windows",
                       help="Text prompt for generation")
    parser.add_argument("--image", type=str, help="Image file path for video generation")
    parser.add_argument("--room", type=str, default="living_room",
                       help="Room type")
    parser.add_argument("--motion", type=str, default="moderate",
                       help="Motion style")
    
    args = parser.parse_args()
    
    if args.mode == "all":
        run_all_tests()
    elif args.mode == "health":
        health_check()
    elif args.mode == "image":
        test_image_generation(args.prompt)
    elif args.mode == "video":
        if not args.image:
            print("❌ --image required for video mode")
        else:
            test_video_from_image(args.image, args.room, args.motion)
    elif args.mode == "pipeline":
        test_image_to_video_pipeline(args.prompt, args.room, args.motion)
