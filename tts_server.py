"""
Coqui TTS Server - Free, High-Quality Text-to-Speech
Runs on port 5001
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from pathlib import Path

app = FastAPI(title="Coqui TTS Server", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory
OUTPUT_DIR = "tts_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global TTS model (loaded once)
tts_model = None

class TTSRequest(BaseModel):
    text: str
    language: str = "ar"  # ar for Arabic, en for English

def load_tts_model():
    """Load Coqui TTS model (lazy loading)"""
    global tts_model
    if tts_model is None:
        try:
            from TTS.api import TTS
            print("🎤 Loading Coqui TTS model...")
            # Using multilingual model that supports Arabic
            tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
            print("✅ TTS Model loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load TTS model: {e}")
            print("💡 Trying fallback model...")
            try:
                # Fallback to a simpler model
                tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
                print("✅ Fallback model loaded!")
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                raise
    return tts_model

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "service": "Coqui TTS Server",
        "version": "1.0.0"
    }

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        # Load model if not loaded
        model = load_tts_model()
        
        # Generate unique filename
        audio_id = str(uuid.uuid4())
        output_path = os.path.join(OUTPUT_DIR, f"{audio_id}.wav")
        
        # Generate speech
        print(f"🎙️ Generating speech for: {request.text[:50]}...")
        
        # Check if model supports language parameter
        try:
            model.tts_to_file(
                text=request.text,
                file_path=output_path,
                language=request.language
            )
        except TypeError:
            # Model doesn't support language parameter
            model.tts_to_file(
                text=request.text,
                file_path=output_path
            )
        
        print(f"✅ Audio generated: {output_path}")
        
        # Return audio file
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename=f"speech_{audio_id}.wav"
        )
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

@app.get("/models")
async def list_models():
    """List available TTS models"""
    try:
        from TTS.api import TTS
        models = TTS.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Preload TTS model on startup"""
    print("🚀 Starting Coqui TTS Server...")
    print("📦 Preloading TTS model (this may take a minute)...")
    try:
        load_tts_model()
        print("✅ Server ready!")
    except Exception as e:
        print(f"⚠️ Warning: Could not preload model: {e}")
        print("Model will be loaded on first request.")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🎤 Coqui TTS Server")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=5001)
