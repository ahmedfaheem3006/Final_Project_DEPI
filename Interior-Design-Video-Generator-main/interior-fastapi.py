"""
FastAPI Server for Interior Design Video Generation
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import torch
from diffusers import StableVideoDiffusionPipeline
from PIL import Image, ImageEnhance
import imageio
import numpy as np
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
import asyncio

# ============================================================================
# Configuration
# ============================================================================

class Config:
    UPLOAD_DIR = "uploads"
    OUTPUT_DIR = "outputs"
    TEMP_DIR = "temp"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
    MODEL_ID = "stabilityai/stable-video-diffusion-img2vid"
    HUGGINGFACE_TOKEN = None  # Set this if needed

# ============================================================================
# Models
# ============================================================================

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
    enhance_lighting: bool = Field(default=True, description="Enhance image lighting")
    adjust_contrast: bool = Field(default=True, description="Adjust image contrast")

class VideoGenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    video_url: Optional[str] = None
    duration: Optional[float] = None
    frames: Optional[int] = None
    file_size_mb: Optional[float] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    video_url: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

# ============================================================================
# Video Generator Class
# ============================================================================

class InteriorVideoGenerator:
    def __init__(self, huggingface_token=None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self.huggingface_token = huggingface_token
        
        # Room settings
        self.room_settings = {
            "living_room": {"motion": 85, "frames": 16, "fps": 7},
            "bedroom": {"motion": 70, "frames": 14, "fps": 6},
            "kitchen": {"motion": 95, "frames": 18, "fps": 8},
            "bathroom": {"motion": 75, "frames": 14, "fps": 6},
            "office": {"motion": 80, "frames": 16, "fps": 7},
            "dining_room": {"motion": 90, "frames": 16, "fps": 7},
            "exterior": {"motion": 100, "frames": 20, "fps": 8}
        }
        
        self.motion_styles = {
            "subtle": -15,
            "moderate": 0,
            "dynamic": +20,
            "showcase": +35
        }
    
    def load_model(self):
        """Load the model (lazy loading)"""
        if self.pipe is None:
            print(f"Loading model on {self.device}...")
            
            if self.huggingface_token:
                from huggingface_hub import login
                login(self.huggingface_token)
            
            self.pipe = StableVideoDiffusionPipeline.from_pretrained(
                Config.MODEL_ID,
                torch_dtype=torch.float16,
                variant="fp16"
            )
            self.pipe.to(self.device)
            print("Model loaded successfully!")
    
    def preprocess_image(self, image_path: str, enhance_lighting: bool = True,
                        adjust_contrast: bool = True, target_size: int = 384):
        """Preprocess interior image"""
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
        
        # Ensure model is loaded
        self.load_model()
        
        # Get settings
        settings = self.room_settings.get(room_type, self.room_settings["living_room"])
        motion_adjust = self.motion_styles.get(motion_style, 0)
        motion_bucket = min(255, max(0, settings["motion"] + motion_adjust))
        num_frames = settings["frames"]
        fps = settings["fps"]
        
        # Preprocess image
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
            motion_bucket_id=motion_bucket,
            fps=fps,
            decode_chunk_size=2,
            generator=torch.manual_seed(42)
        ).frames[0]
        
        # Convert to numpy
        video_frames_np = [np.array(frame) for frame in video_frames]
        
        # Save video
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
    title="Interior Design Video Generator API",
    description="Generate cinematic videos from interior design images",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global generator instance
generator = InteriorVideoGenerator(huggingface_token=Config.HUGGINGFACE_TOKEN)

# Job tracking
jobs = {}

# Create directories
for directory in [Config.UPLOAD_DIR, Config.OUTPUT_DIR, Config.TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============================================================================
# Helper Functions
# ============================================================================

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    import time
    current_time = time.time()
    
    for directory in [Config.UPLOAD_DIR, Config.OUTPUT_DIR]:
        for file in Path(directory).glob("*"):
            if current_time - file.stat().st_mtime > 3600:  # 1 hour
                file.unlink()

async def process_video_generation(job_id: str, image_path: str,
                                   request: VideoGenerationRequest):
    """Background task for video generation"""
    try:
        # Update job status
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Starting video generation..."
        
        # Generate output path
        output_filename = f"{job_id}.mp4"
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        
        # Update progress
        jobs[job_id]["progress"] = 30
        jobs[job_id]["message"] = "Generating video frames..."
        
        # Generate video
        result = generator.generate_video(
            image_path=image_path,
            output_path=output_path,
            room_type=request.room_type,
            motion_style=request.motion_style,
            enhance_lighting=request.enhance_lighting,
            adjust_contrast=request.adjust_contrast
        )
        
        # Update job as completed
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Video generated successfully!"
        jobs[job_id]["video_url"] = f"/api/v1/download/{job_id}"
        jobs[job_id]["duration"] = result["duration"]
        jobs[job_id]["frames"] = result["frames"]
        jobs[job_id]["file_size_mb"] = result["file_size_mb"]
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Interior Design Video Generator API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "generate": "/api/v1/generate",
            "status": "/api/v1/status/{job_id}",
            "download": "/api/v1/download/{job_id}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "device": generator.device,
        "model_loaded": generator.pipe is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/generate", response_model=VideoGenerationResponse)
async def generate_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    room_type: str = "living_room",
    motion_style: str = "moderate",
    enhance_lighting: bool = True,
    adjust_contrast: bool = True
):
    """
    Generate video from interior design image
    
    - **file**: Interior design image (JPG, JPEG, PNG)
    - **room_type**: Type of room (living_room, bedroom, kitchen, etc.)
    - **motion_style**: Animation style (subtle, moderate, dynamic, showcase)
    - **enhance_lighting**: Enhance image lighting
    - **adjust_contrast**: Adjust image contrast
    """
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {Config.ALLOWED_EXTENSIONS}"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_path = os.path.join(Config.UPLOAD_DIR, f"{job_id}{file_ext}")
    
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create job entry
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Job queued for processing",
        "created_at": datetime.now().isoformat(),
        "video_url": None,
        "completed_at": None
    }
    
    # Create request object
    request = VideoGenerationRequest(
        room_type=room_type,
        motion_style=motion_style,
        enhance_lighting=enhance_lighting,
        adjust_contrast=adjust_contrast
    )
    
    # Add background task
    background_tasks.add_task(
        process_video_generation,
        job_id,
        upload_path,
        request
    )
    
    return VideoGenerationResponse(
        job_id=job_id,
        status="queued",
        message="Video generation started. Use job_id to check status."
    )

@app.get("/api/v1/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status by ID"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**jobs[job_id])

@app.get("/api/v1/download/{job_id}")
async def download_video(job_id: str):
    """Download generated video"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Video not ready. Status: {job['status']}"
        )
    
    video_path = os.path.join(Config.OUTPUT_DIR, f"{job_id}.mp4")
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"interior_design_{job_id}.mp4"
    )

@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete job and associated files"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files
    for directory in [Config.UPLOAD_DIR, Config.OUTPUT_DIR]:
        for file in Path(directory).glob(f"{job_id}.*"):
            file.unlink()
    
    # Remove from jobs
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}

@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs"""
    return {"jobs": list(jobs.values())}

# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    print("Starting Interior Design Video API...")
    print("Preloading model...")
    generator.load_model()
    print("API ready!")

# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
