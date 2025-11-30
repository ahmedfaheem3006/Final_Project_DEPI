"""
Complete Interior Design API - Image Generation + Video Generation
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import torch
from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
from PIL import Image, ImageEnhance
import imageio
import numpy as np
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

class Config:
    UPLOAD_DIR = "uploads"
    OUTPUT_DIR = "outputs"
    GENERATED_IMAGES_DIR = "generated_images"
    TEMP_DIR = "temp"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
    
    # Model IDs
    IMAGE_MODEL_ID = "SG161222/Realistic_Vision_V6.0_B1_noVAE"
    VIDEO_MODEL_ID = "stabilityai/stable-video-diffusion-img2vid"
    
    HUGGINGFACE_TOKEN = None  # Set if needed

# ============================================================================
# Models
# ============================================================================

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Description of the interior design")
    room_type: str = Field(
        default="living_room",
        description="Type of room for optimization"
    )
    num_inference_steps: int = Field(default=20, ge=10, le=50)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    width: int = Field(default=512, ge=256, le=1024)
    height: int = Field(default=512, ge=256, le=1024)

class VideoGenerationRequest(BaseModel):
    room_type: str = Field(
        default="living_room",
        description="Type of room",
        enum=["living_room", "bedroom", "kitchen", "bathroom", 
              "office", "dining_room", "exterior"]
    )
    motion_style: str = Field(
        default="moderate",
        description="Animation style",
        enum=["subtle", "moderate", "dynamic", "showcase"]
    )
    enhance_lighting: bool = Field(default=True)
    adjust_contrast: bool = Field(default=True)

class ImageToVideoRequest(BaseModel):
    prompt: str = Field(..., description="Description of the interior design")
    room_type: str = Field(default="living_room")
    motion_style: str = Field(default="moderate")
    num_inference_steps: int = Field(default=20, ge=10, le=50)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    job_type: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    duration: Optional[float] = None
    frames: Optional[int] = None

# ============================================================================
# Image Generator
# ============================================================================

class InteriorImageGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        
    def load_model(self):
        """Load Stable Diffusion model"""
        if self.pipe is None:
            print(f"Loading image generation model on {self.device}...")
            self.pipe = StableDiffusionPipeline.from_pretrained(
                Config.IMAGE_MODEL_ID
            )
            self.pipe = self.pipe.to(self.device)
            self.pipe = self.pipe.to(torch.float16)
            print("Image model loaded!")
    
    def generate_image(self, prompt: str, output_path: str,
                      num_inference_steps: int = 20,
                      guidance_scale: float = 7.5,
                      width: int = 512,
                      height: int = 512):
        """Generate interior design image"""
        self.load_model()
        
        # Enhance prompt
        enhanced_prompt = f"interior design, {prompt}, professional photography, 8k, detailed, high quality"
        
        # Generate image
        image = self.pipe(
            prompt=enhanced_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            height=height,
            width=width
        ).images[0]
        
        # Save image
        image.save(output_path)
        
        return {
            "width": width,
            "height": height,
            "file_size_mb": os.path.getsize(output_path) / (1024 * 1024)
        }

# ============================================================================
# Video Generator
# ============================================================================

class InteriorVideoGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        
        self.room_settings = {
            "living_room": {"motion": 85, "frames": 14, "fps": 7},
            "bedroom": {"motion": 70, "frames": 14, "fps": 6},
            "kitchen": {"motion": 95, "frames": 14, "fps": 8},
            "bathroom": {"motion": 75, "frames": 14, "fps": 6},
            "office": {"motion": 80, "frames": 14, "fps": 7},
            "dining_room": {"motion": 90, "frames": 14, "fps": 7},
            "exterior": {"motion": 100, "frames": 14, "fps": 8}
        }
        
        self.motion_styles = {
            "subtle": -15,
            "moderate": 0,
            "dynamic": +20,
            "showcase": +35
        }
    
    def load_model(self):
        """Load Video Diffusion model"""
        if self.pipe is None:
            print(f"Loading video generation model on {self.device}...")
            self.pipe = StableVideoDiffusionPipeline.from_pretrained(
                Config.VIDEO_MODEL_ID,
                torch_dtype=torch.float16,
                variant="fp16"
            )
            self.pipe.to(self.device)
            print("Video model loaded!")
    
    def preprocess_image(self, image_path: str, enhance_lighting: bool = True,
                        adjust_contrast: bool = True, target_size: int = 384):
        """Preprocess image for video generation"""
        image = Image.open(image_path).convert("RGB")
        
        if enhance_lighting:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
        
        if adjust_contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.15)
        
        image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)
        return image
    
    def generate_video(self, image_path: str, output_path: str,
                      room_type: str = "living_room",
                      motion_style: str = "moderate",
                      enhance_lighting: bool = True,
                      adjust_contrast: bool = True):
        """Generate video from image"""
        self.load_model()
        
        # Get settings
        settings = self.room_settings.get(room_type, self.room_settings["living_room"])
        motion_adjust = self.motion_styles.get(motion_style, 0)
        motion_bucket = min(255, max(0, settings["motion"] + motion_adjust))
        num_frames = settings["frames"]
        fps = settings["fps"]
        
        # Preprocess
        image = self.preprocess_image(
            image_path,
            enhance_lighting=enhance_lighting,
            adjust_contrast=adjust_contrast
        )
        
        # Clear cache
        torch.cuda.empty_cache()
        
        # Generate video
        video_frames = self.pipe(
            image,
            num_frames=num_frames,
            num_inference_steps=10, # Reduced for speed
            motion_bucket_id=motion_bucket,
            fps=fps,
            decode_chunk_size=2,
            generator=torch.manual_seed(42)
        ).frames[0]
        
        # Save video
        video_frames_np = [np.array(frame) for frame in video_frames]
        imageio.mimsave(
            output_path,
            video_frames_np,
            fps=fps,
            codec='libx264',
            quality=9,
            pixelformat='yuv420p'
        )
        
        return {
            "frames": len(video_frames),
            "fps": fps,
            "duration": len(video_frames) / fps,
            "file_size_mb": os.path.getsize(output_path) / (1024 * 1024)
        }

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Complete Interior Design API",
    description="Generate images and videos from text descriptions",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize generators
image_generator = InteriorImageGenerator()
video_generator = InteriorVideoGenerator()

# Job tracking
jobs = {}

# Create directories
for directory in [Config.UPLOAD_DIR, Config.OUTPUT_DIR, 
                  Config.GENERATED_IMAGES_DIR, Config.TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============================================================================
# Background Tasks
# ============================================================================

async def process_image_generation(job_id: str, request: ImageGenerationRequest):
    """Generate image in background"""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 20
        jobs[job_id]["message"] = "Generating image..."
        
        output_filename = f"{job_id}.png"
        output_path = os.path.join(Config.GENERATED_IMAGES_DIR, output_filename)
        
        result = image_generator.generate_image(
            prompt=request.prompt,
            output_path=output_path,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            width=request.width,
            height=request.height
        )
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Image generated successfully!"
        jobs[job_id]["image_url"] = f"/api/v1/download/image/{job_id}"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

async def process_video_generation(job_id: str, image_path: str, 
                                   request: VideoGenerationRequest):
    """Generate video in background"""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 20
        jobs[job_id]["message"] = "Generating video..."
        
        output_filename = f"{job_id}.mp4"
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        
        result = video_generator.generate_video(
            image_path=image_path,
            output_path=output_path,
            room_type=request.room_type,
            motion_style=request.motion_style,
            enhance_lighting=request.enhance_lighting,
            adjust_contrast=request.adjust_contrast
        )
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Video generated successfully!"
        jobs[job_id]["video_url"] = f"/api/v1/download/video/{job_id}"
        jobs[job_id]["duration"] = result["duration"]
        jobs[job_id]["frames"] = result["frames"]
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

async def process_image_to_video(job_id: str, request: ImageToVideoRequest):
    """Generate image then video in background"""
    try:
        # Step 1: Generate Image
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Step 1/2: Generating image..."
        
        image_filename = f"{job_id}_image.png"
        image_path = os.path.join(Config.GENERATED_IMAGES_DIR, image_filename)
        
        image_generator.generate_image(
            prompt=request.prompt,
            output_path=image_path,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            width=512,
            height=512
        )
        
        jobs[job_id]["image_url"] = f"/api/v1/download/image/{job_id}_image"
        
        # Step 2: Generate Video
        jobs[job_id]["progress"] = 50
        jobs[job_id]["message"] = "Step 2/2: Generating video..."
        
        video_filename = f"{job_id}.mp4"
        video_path = os.path.join(Config.OUTPUT_DIR, video_filename)
        
        result = video_generator.generate_video(
            image_path=image_path,
            output_path=video_path,
            room_type=request.room_type,
            motion_style=request.motion_style
        )
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Image and video generated successfully!"
        jobs[job_id]["video_url"] = f"/api/v1/download/video/{job_id}"
        jobs[job_id]["duration"] = result["duration"]
        jobs[job_id]["frames"] = result["frames"]
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Complete Interior Design API",
        "version": "2.0.0",
        "features": ["Image Generation", "Video Generation", "Image-to-Video"],
        "endpoints": {
            "generate_image": "/api/v1/generate/image",
            "generate_video": "/api/v1/generate/video",
            "image_to_video": "/api/v1/generate/image-to-video",
            "status": "/api/v1/status/{job_id}",
            "download_image": "/api/v1/download/image/{job_id}",
            "download_video": "/api/v1/download/video/{job_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU",
        "image_model_loaded": image_generator.pipe is not None,
        "video_model_loaded": video_generator.pipe is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/generate/image", response_model=JobResponse)
async def generate_image(
    background_tasks: BackgroundTasks,
    request: ImageGenerationRequest
):
    """Generate interior design image from text prompt"""
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "job_id": job_id,
        "job_type": "image",
        "status": "queued",
        "progress": 0,
        "message": "Job queued",
        "created_at": datetime.now().isoformat()
    }
    
    background_tasks.add_task(process_image_generation, job_id, request)
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Image generation started"
    )

@app.post("/api/v1/generate/video", response_model=JobResponse)
async def generate_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    room_type: str = "living_room",
    motion_style: str = "moderate",
    enhance_lighting: bool = True,
    adjust_contrast: bool = True
):
    """Generate video from uploaded image"""
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")
    
    upload_path = os.path.join(Config.UPLOAD_DIR, f"{job_id}{file_ext}")
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    jobs[job_id] = {
        "job_id": job_id,
        "job_type": "video",
        "status": "queued",
        "progress": 0,
        "message": "Job queued",
        "created_at": datetime.now().isoformat()
    }
    
    # Video Generation Settings
    VIDEO_NUM_FRAMES = 14  # Reduced from 25 for faster CPU generation
    VIDEO_DECODE_CHUNK_SIZE = 2 # Reduced for memory efficiency
    VIDEO_STEPS = 10 # Reduced from 25 for speed
    
    request = VideoGenerationRequest(
        room_type=room_type,
        motion_style=motion_style,
        enhance_lighting=enhance_lighting,
        adjust_contrast=adjust_contrast
    )
    
    background_tasks.add_task(process_video_generation, job_id, upload_path, request)
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Video generation started"
    )

@app.post("/api/v1/generate/image-to-video", response_model=JobResponse)
async def generate_image_to_video(
    background_tasks: BackgroundTasks,
    request: ImageToVideoRequest
):
    """Generate image from text, then create video (complete pipeline)"""
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "job_id": job_id,
        "job_type": "image-to-video",
        "status": "queued",
        "progress": 0,
        "message": "Job queued",
        "created_at": datetime.now().isoformat()
    }
    
    background_tasks.add_task(process_image_to_video, job_id, request)
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Image-to-video generation started"
    )

@app.get("/api/v1/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return JobStatus(**jobs[job_id])

@app.get("/api/v1/download/image/{job_id}")
async def download_image(job_id: str):
    """Download generated image"""
    # Handle both direct job_id and job_id_image patterns
    image_id = job_id.replace("_image", "")
    
    if image_id not in jobs and job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    # Try both filename patterns
    image_path1 = os.path.join(Config.GENERATED_IMAGES_DIR, f"{job_id}.png")
    image_path2 = os.path.join(Config.GENERATED_IMAGES_DIR, f"{image_id}.png")
    
    image_path = image_path1 if os.path.exists(image_path1) else image_path2
    
    if not os.path.exists(image_path):
        raise HTTPException(404, "Image not found")
    
    return FileResponse(
        image_path,
        media_type="image/png",
        filename=f"interior_design_{job_id}.png"
    )

@app.get("/api/v1/download/video/{job_id}")
async def download_video(job_id: str):
    """Download generated video"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    video_path = os.path.join(Config.OUTPUT_DIR, f"{job_id}.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(404, "Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"interior_design_{job_id}.mp4"
    )

@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs"""
    return {"jobs": list(jobs.values())}

@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete job and files"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    
    # Delete files
    for directory in [Config.UPLOAD_DIR, Config.OUTPUT_DIR, Config.GENERATED_IMAGES_DIR]:
        for file in Path(directory).glob(f"{job_id}*"):
            file.unlink()
    
    del jobs[job_id]
    return {"message": "Job deleted"}

@app.on_event("startup")
async def startup():
    """Preload models on startup"""
    print("Starting Complete Interior Design API...")
    print("Preloading models (this may take a few minutes)...")
    image_generator.load_model()
    video_generator.load_model()
    print("✅ API Ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
