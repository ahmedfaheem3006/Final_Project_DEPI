# 🚀 Quick Setup Guide

## Complete Interior Design API - Installation & Usage

---

## 📦 What You'll Get

This project combines your two notebooks into one powerful API:

1. **Image Generation** - Generate interior design images from text (Stable Diffusion)
2. **Video Generation** - Convert images to cinematic videos (Stable Video Diffusion)
3. **Complete Pipeline** - Text → Image → Video in one click

---

## 📁 File Structure

After setup, you'll have:

```
interior-design-api/
├── main.py                    # ← Main API server
├── requirements.txt           # ← Dependencies
├── test_complete_api.py       # ← Testing script
├── index.html                 # ← Web interface
├── run_server.sh              # ← Startup script
├── README.md                  # ← Full documentation
├── SETUP_GUIDE.md            # ← This file
│
├── uploads/                   # Auto-created
├── outputs/                   # Videos saved here
├── generated_images/          # Images saved here
└── temp/                      # Temporary files
```

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
# Install requirements
pip install -r requirements.txt
```

**What gets installed:**
- FastAPI (web framework)
- PyTorch (ML framework)
- Diffusers (Stable Diffusion + Video Diffusion)
- Image processing libraries

### Step 2: Start the Server

```bash
# Option A: Direct
python main.py

# Option B: Using script (Linux/Mac)
chmod +x run_server.sh
./run_server.sh

# Option C: Using uvicorn
uvicorn main:app --reload
```

### Step 3: Use It!

**Web Interface:**
```
Open browser → http://localhost:8000/index.html
```

**API Documentation:**
```
http://localhost:8000/docs
```

---

## 🎯 Usage Examples

### 🌐 Using Web Interface (Easiest)

1. Open `http://localhost:8000/index.html`
2. Choose a tab:
   - **Complete Pipeline** - Full workflow
   - **Image Only** - Just generate image
   - **Video Only** - Upload image, get video
3. Enter description or upload file
4. Click generate
5. Wait for progress
6. Download results!

---

### 💻 Using Python

#### Example 1: Complete Pipeline (Text → Image → Video)

```python
import requests
import time

# 1. Start generation
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

# 2. Wait for completion
while True:
    status = requests.get(f"http://localhost:8000/api/v1/status/{job_id}").json()
    print(f"{status['progress']}% - {status['message']}")
    
    if status['status'] == 'completed':
        break
    
    time.sleep(5)

# 3. Download results
# Image
image = requests.get(f"http://localhost:8000{status['image_url']}")
with open("result_image.png", "wb") as f:
    f.write(image.content)

# Video
video = requests.get(f"http://localhost:8000{status['video_url']}")
with open("result_video.mp4", "wb") as f:
    f.write(video.content)

print("✅ Done! Files saved.")
```

#### Example 2: Image Only

```python
import requests

# Generate image
response = requests.post(
    "http://localhost:8000/api/v1/generate/image",
    json={
        "prompt": "modern bedroom, king size bed, warm lighting"
    }
)

job_id = response.json()["job_id"]

# Check status and download (same as above)
```

#### Example 3: Video from Your Image

```python
import requests

# Upload image and generate video
with open("my_room.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/generate/video",
        files={"file": f},
        data={
            "room_type": "living_room",
            "motion_style": "showcase"
        }
    )

job_id = response.json()["job_id"]
# Then check status and download
```

---

### 🧪 Using Test Script

```bash
# Run all tests
python test_complete_api.py --mode all

# Test image generation
python test_complete_api.py --mode image --prompt "luxury bedroom"

# Test video from image
python test_complete_api.py --mode video --image room.jpg

# Test complete pipeline
python test_complete_api.py --mode pipeline --prompt "modern kitchen"
```

---

## 📝 Example Prompts That Work Well

### Living Rooms
```
luxury living room, beige sofa, wooden coffee table, large windows, plants, warm sunlight
modern minimalist living room, white walls, grey couch, abstract art
cozy living room, fireplace, leather armchair, bookshelves
```

### Bedrooms
```
modern bedroom, king size bed, wooden furniture, warm lighting
minimalist bedroom, platform bed, white bedding, natural light
cozy bedroom, tufted headboard, nightstands, soft lighting
```

### Kitchens
```
modern kitchen, white cabinets, marble countertop, stainless steel appliances
rustic kitchen, wooden cabinets, farmhouse sink, pendant lights
luxury kitchen, island with bar stools, professional range
```

---

## 🎛️ Configuration Options

### Room Types
- `living_room` - Balanced motion
- `bedroom` - Calm, gentle
- `kitchen` - Dynamic
- `bathroom` - Elegant
- `office` - Professional
- `dining_room` - Moderate
- `exterior` - Wide movements

### Motion Styles
- `subtle` - Minimal movement (client presentations)
- `moderate` - Balanced (general use)
- `dynamic` - Pronounced (social media)
- `showcase` - Virtual tour (portfolio)

---

## ⚙️ System Requirements

### Minimum
- GPU: NVIDIA GPU with 6GB+ VRAM
- RAM: 16GB
- Storage: 15GB free
- CUDA: 11.8+

### Recommended
- GPU: RTX 3060 or better
- RAM: 32GB
- Storage: 20GB free

---

## ⏱️ Expected Processing Times

### RTX 3060 (6GB VRAM)
- Image: 15-20 seconds
- Video: 30-40 seconds
- Complete: 45-60 seconds

### RTX 3080 (10GB VRAM)
- Image: 10-15 seconds
- Video: 20-30 seconds
- Complete: 30-45 seconds

### RTX 4090 (24GB VRAM)
- Image: 5-10 seconds
- Video: 15-20 seconds
- Complete: 20-30 seconds

---

## 🔧 Troubleshooting

### Problem: "CUDA out of memory"

**Solution:**
```python
# In main.py, reduce image size
width=384,  # instead of 512
height=384
```

### Problem: "Models not downloading"

**Solution:**
```bash
# Check internet connection
# Or download manually and set path
```

### Problem: "Server won't start on port 8000"

**Solution:**
```bash
# Use different port
python main.py --port 8001

# Or kill process on 8000
lsof -i :8000
kill -9 <PID>
```

### Problem: "Generation is slow"

**Check GPU is being used:**
```bash
# Open new terminal
nvidia-smi

# Should show Python using GPU
```

### Problem: "ModuleNotFoundError"

**Solution:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

---

## 🌐 API Endpoints Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Image
```bash
curl -X POST http://localhost:8000/api/v1/generate/image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "luxury bedroom"}'
```

### Generate Video
```bash
curl -X POST http://localhost:8000/api/v1/generate/video \
  -F "file=@room.jpg" \
  -F "room_type=living_room"
```

### Complete Pipeline
```bash
curl -X POST http://localhost:8000/api/v1/generate/image-to-video \
  -H "Content-Type: application/json" \
  -d '{"prompt": "modern kitchen", "room_type": "kitchen"}'
```

### Check Status
```bash
curl http://localhost:8000/api/v1/status/{job_id}
```

---

## 📊 Features Comparison

| Feature | Your Old Code | New API |
|---------|---------------|---------|
| Image Generation | ✅ Jupyter only | ✅ API + Web |
| Video Generation | ✅ Jupyter only | ✅ API + Web |
| Complete Pipeline | ❌ Manual | ✅ Automated |
| Multiple Users | ❌ | ✅ Job Queue |
| Web Interface | ❌ | ✅ HTML UI |
| Progress Tracking | ❌ | ✅ Real-time |
| Download Results | ❌ | ✅ Direct links |
| Remote Access | ❌ | ✅ REST API |

---

## 🎓 Next Steps

1. **Test the API**: Run `python test_complete_api.py --mode all`
2. **Try Web Interface**: Open `http://localhost:8000/index.html`
3. **Read Full Docs**: Check `README.md` for complete API reference
4. **Customize**: Edit room types, motion settings in `main.py`

---

## 📞 Need Help?

1. Check `/health` endpoint
2. Look at server logs in terminal
3. Run test script to diagnose
4. Check GPU with `nvidia-smi`

---

## ✨ Tips for Best Results

### For Images:
- Be specific in descriptions
- Mention lighting, materials, colors
- Include style keywords (modern, luxury, cozy)

### For Videos:
- Use images with depth and perspective
- Well-lit images work better
- Match room type to actual room
- Choose motion style based on use case

### For Performance:
- Close other GPU applications
- Start with smaller image sizes
- Use `moderate` motion style first
- Monitor GPU memory with `nvidia-smi`

---

## 🎉 You're All Set!

Your complete interior design generation system is ready!

Start the server and begin creating amazing visualizations! 🏠✨
