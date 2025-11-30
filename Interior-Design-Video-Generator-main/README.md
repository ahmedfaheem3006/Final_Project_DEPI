# 🏠 Complete Interior Design API

**Text-to-Image-to-Video Pipeline for Interior Design**

Generate photorealistic interior design images from text descriptions, then automatically create cinematic videos with camera movement.

---

## 🌟 Features

### 🖼️ Image Generation
- Generate high-quality interior design images from text descriptions
- Professional photography quality (8K, detailed)
- Customizable inference steps and guidance
- Room-type specific optimization

### 🎬 Video Generation
- Convert static images to cinematic videos
- Multiple motion styles (subtle, moderate, dynamic, showcase)
- Room-specific camera movement presets
- Automatic image enhancement (lighting, contrast)

### 🚀 Complete Pipeline
- **One-click workflow**: Text → Image → Video
- Background processing with progress tracking
- Download both image and video outputs
- Optimized for interior design visualization

---

## 📋 Requirements

- **Python**: 3.10+
- **GPU**: CUDA-compatible (8GB+ VRAM recommended)
- **CUDA**: 11.8+
- **Disk Space**: ~10GB for models

---

## 🔧 Installation

### Quick Start

```bash
# 1. Clone/create project directory
mkdir interior-design-api
cd interior-design-api

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
python main.py

# Server will start on http://localhost:8000
```

### Docker Installation

```bash
# Build
docker build -t interior-api .

# Run with GPU
docker run --gpus all -p 8000:8000 interior-api
```

---

## 📁 Project Structure

```
interior-design-api/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── test_complete_api.py       # Testing script
├── README.md                  # This file
├── Dockerfile                 # Docker configuration
│
├── uploads/                   # Uploaded images
├── outputs/                   # Generated videos
├── generated_images/          # Generated images
└── temp/                      # Temporary files
```

---

## 🎯 API Endpoints

### Base URL
```
http://localhost:8000
```

### 📖 Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 Endpoint Details

### 1️⃣ Generate Image from Text

**Endpoint:** `POST /api/v1/generate/image`

**Description:** Generate interior design image from text description

**Request Body:**
```json
{
  "prompt": "luxury living room, modern sofa, wooden table, large windows",
  "room_type": "living_room",
  "num_inference_steps": 20,
  "guidance_scale": 7.5,
  "width": 512,
  "height": 512
}
```

**Example (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate/image",
    json={
        "prompt": "modern bedroom, king size bed, warm lighting",
        "room_type": "bedroom",
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "width": 512,
        "height": 512
    }
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/generate/image" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "luxury living room with modern furniture",
    "room_type": "living_room"
  }'
```

---

### 2️⃣ Generate Video from Image

**Endpoint:** `POST /api/v1/generate/video`

**Description:** Convert an image to a cinematic video

**Parameters:**
- `file`: Image file (multipart/form-data)
- `room_type`: living_room, bedroom, kitchen, bathroom, office, dining_room, exterior
- `motion_style`: subtle, moderate, dynamic, showcase
- `enhance_lighting`: true/false
- `adjust_contrast`: true/false

**Example (Python):**
```python
with open("room.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/generate/video",
        files={"file": f},
        data={
            "room_type": "living_room",
            "motion_style": "showcase",
            "enhance_lighting": True,
            "adjust_contrast": True
        }
    )

job_id = response.json()["job_id"]
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/generate/video" \
  -F "file=@interior.jpg" \
  -F "room_type=living_room" \
  -F "motion_style=moderate"
```

---

### 3️⃣ Complete Pipeline (Text → Image → Video)

**Endpoint:** `POST /api/v1/generate/image-to-video`

**Description:** Generate both image and video in one request

**Request Body:**
```json
{
  "prompt": "cozy bedroom, warm lighting, modern furniture",
  "room_type": "bedroom",
  "motion_style": "subtle",
  "num_inference_steps": 20,
  "guidance_scale": 7.5
}
```

**Example (Python):**
```python
response = requests.post(
    "http://localhost:8000/api/v1/generate/image-to-video",
    json={
        "prompt": "luxury living room, beige sofa, wooden coffee table",
        "room_type": "living_room",
        "motion_style": "showcase"
    }
)

job_id = response.json()["job_id"]
```

---

### 4️⃣ Check Job Status

**Endpoint:** `GET /api/v1/status/{job_id}`

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "Image and video generated successfully!",
  "job_type": "image-to-video",
  "image_url": "/api/v1/download/image/550e8400...",
  "video_url": "/api/v1/download/video/550e8400...",
  "created_at": "2024-11-29T10:30:00",
  "completed_at": "2024-11-29T10:32:45",
  "duration": 2.3,
  "frames": 16
}
```

**Status Values:**
- `queued`: Waiting to be processed
- `processing`: Currently generating
- `completed`: Ready for download
- `failed`: Error occurred

---

### 5️⃣ Download Image

**Endpoint:** `GET /api/v1/download/image/{job_id}`

**Example:**
```python
# Get status first
status = requests.get(f"http://localhost:8000/api/v1/status/{job_id}").json()

# Download image
if status['status'] == 'completed':
    image = requests.get(f"http://localhost:8000/api/v1/download/image/{job_id}")
    with open("output.png", "wb") as f:
        f.write(image.content)
```

---

### 6️⃣ Download Video

**Endpoint:** `GET /api/v1/download/video/{job_id}`

**Example:**
```python
video = requests.get(f"http://localhost:8000/api/v1/download/video/{job_id}")
with open("output.mp4", "wb") as f:
    f.write(video.content)
```

---

### 7️⃣ List All Jobs

**Endpoint:** `GET /api/v1/jobs`

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400...",
      "job_type": "image-to-video",
      "status": "completed",
      "progress": 100,
      "created_at": "2024-11-29T10:30:00"
    }
  ]
}
```

---

### 8️⃣ Delete Job

**Endpoint:** `DELETE /api/v1/jobs/{job_id}`

**Response:**
```json
{
  "message": "Job deleted"
}
```

---

## 🧪 Testing

### Run All Tests
```bash
python test_complete_api.py --mode all
```

### Test Individual Features
```bash
# Health check
python test_complete_api.py --mode health

# Image generation
python test_complete_api.py --mode image --prompt "luxury bedroom"

# Video from image
python test_complete_api.py --mode video --image room.jpg --room living_room

# Complete pipeline
python test_complete_api.py --mode pipeline --prompt "modern kitchen"
```

---

## 📊 Room Types & Motion Settings

### Room Types

| Room Type | Motion | Frames | FPS | Use Case |
|-----------|--------|--------|-----|----------|
| living_room | 85 | 16 | 7 | General showcases |
| bedroom | 70 | 14 | 6 | Calm, peaceful |
| kitchen | 95 | 18 | 8 | Dynamic tours |
| bathroom | 75 | 14 | 6 | Elegant reveals |
| office | 80 | 16 | 7 | Professional |
| dining_room | 90 | 16 | 7 | Entertaining spaces |
| exterior | 100 | 20 | 8 | Wide outdoor shots |

### Motion Styles

| Style | Modifier | Best For |
|-------|----------|----------|
| subtle | -15 | Client presentations |
| moderate | 0 | General use |
| dynamic | +20 | Social media posts |
| showcase | +35 | Portfolio videos |

---

## 💡 Example Prompts

### Living Rooms
```
"luxury living room, beige sofa, wooden coffee table, large windows, plants, warm sunlight"
"modern minimalist living room, white walls, grey couch, abstract art, floor lamp"
"cozy living room, fireplace, leather armchair, bookshelves, warm lighting"
```

### Bedrooms
```
"modern bedroom, king size bed, wooden furniture, warm lighting, plants"
"minimalist bedroom, platform bed, white bedding, large window, natural light"
"cozy bedroom, tufted headboard, nightstands, soft lighting, neutral colors"
```

### Kitchens
```
"modern kitchen, white cabinets, marble countertop, stainless steel appliances"
"rustic kitchen, wooden cabinets, farmhouse sink, pendant lights, open shelving"
"luxury kitchen, island with bar stools, professional range, wine fridge"
```

---

## 🔄 Complete Workflow Example

```python
import requests
import time

# 1. Start complete pipeline
response = requests.post(
    "http://localhost:8000/api/v1/generate/image-to-video",
    json={
        "prompt": "luxury living room, modern furniture, large windows",
        "room_type": "living_room",
        "motion_style": "showcase"
    }
)

job_id = response.json()["job_id"]
print(f"Job started: {job_id}")

# 2. Monitor progress
while True:
    status = requests.get(
        f"http://localhost:8000/api/v1/status/{job_id}"
    ).json()
    
    print(f"{status['progress']}% - {status['message']}")
    
    if status['status'] == 'completed':
        break
    elif status['status'] == 'failed':
        print(f"Error: {status['message']}")
        exit(1)
    
    time.sleep(5)

# 3. Download image
image = requests.get(
    f"http://localhost:8000/api/v1/download/image/{job_id}_image"
)
with open("generated_image.png", "wb") as f:
    f.write(image.content)

# 4. Download video
video = requests.get(
    f"http://localhost:8000/api/v1/download/video/{job_id}"
)
with open("generated_video.mp4", "wb") as f:
    f.write(video.content)

print("✅ Complete! Image and video downloaded.")
```

---

## ⚡ Performance

### Processing Times (approximate)

| Task | RTX 3060 | RTX 3080 | RTX 4090 |
|------|----------|----------|----------|
| Image (512x512) | 15-20s | 10-15s | 5-10s |
| Video (16 frames) | 30-40s | 20-30s | 15-20s |
| Complete Pipeline | 45-60s | 30-45s | 20-30s |

### VRAM Usage

| Task | VRAM Required |
|------|---------------|
| Image Generation | ~4-5GB |
| Video Generation | ~6-7GB |
| Both Models Loaded | ~10-11GB |

---

## 🔒 Production Considerations

### Security
- [ ] Add API authentication (JWT, API keys)
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization
- [ ] Set up HTTPS/TLS
- [ ] Configure CORS properly

### Optimization
- [ ] Use Redis for job queue
- [ ] Implement caching
- [ ] Add CDN for downloads
- [ ] Set up load balancing
- [ ] Monitor GPU usage

### Monitoring
- [ ] Add logging (structured logs)
- [ ] Set up error tracking (Sentry)
- [ ] Monitor API metrics
- [ ] Track GPU utilization
- [ ] Set up alerts

---

## 🐛 Troubleshooting

### CUDA Out of Memory
```python
# Reduce batch size or image size
# Clear cache between generations
torch.cuda.empty_cache()
```

### Models Not Loading
- Check internet connection
- Verify HuggingFace token (if needed)
- Ensure sufficient disk space (~10GB)

### Slow Generation
- Confirm GPU is being used (`/health` endpoint)
- Close other GPU applications
- Reduce inference steps

### API Not Starting
```bash
# Check if port 8000 is available
lsof -i :8000

# Try different port
uvicorn main:app --port 8001
```

---

## 📝 License

This project uses:
- **Realistic Vision V6.0** (Stable Diffusion) - Check license
- **Stable Video Diffusion** (Stability AI) - Check license

Verify licenses before commercial use.

---

## 🤝 Support

Need help?
1. Check `/health` endpoint
2. Review API logs
3. Test with `test_complete_api.py`
4. Check GPU: `nvidia-smi`

---

## 🎉 Credits

Built with:
- FastAPI
- Stable Diffusion (Realistic Vision V6.0)
- Stable Video Diffusion (Stability AI)
- PyTorch
- Diffusers (Hugging Face)

---

**Happy Designing! 🏠✨**
