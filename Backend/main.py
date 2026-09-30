from fastapi import FastAPI, UploadFile, File, HTTPException
import onnxruntime as ort
import os

app = FastAPI(title="EdgeScholar AI Backend", version="1.0.0")

# Dynamically resolve the absolute path to the models directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "whisper_base.onnx")

# Global session variable
ort_session = None

@app.on_event("startup")
async def load_model():
    global ort_session
    print("\n--- EDGESCHOLAR AI INITIALIZATION ---")
    print(f"Target model path: {MODEL_PATH}")
    
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 1000000:
        available_providers = ort.get_available_providers()
        print(f"System ONNX providers detected: {available_providers}")
        
        # Prioritize Hexagon NPU via QNN, fallback to CPU
        providers = ['QNNExecutionProvider', 'CPUExecutionProvider'] if 'QNNExecutionProvider' in available_providers else ['CPUExecutionProvider']
        
        try:
            ort_session = ort.InferenceSession(MODEL_PATH, providers=providers)
            print(f"✅ Model loaded successfully! Active provider: {ort_session.get_providers()[0]}")
        except Exception as e:
            print(f"❌ Error loading model into ONNX Session: {e}")
    else:
        print("❌ ERROR: Valid ONNX model file not found. Ensure the >100MB file is at models/whisper_base.onnx")
    print("-------------------------------------\n")

@app.get("/")
async def root():
    return {"message": "EdgeScholar AI Backend is live. NPU inference ready."}

@app.get("/health")
async def health_check():
    if ort_session:
        active_providers = ort_session.get_providers()
        return {
            "status": "online", 
            "npu_active": "QNNExecutionProvider" in active_providers,
            "active_providers": active_providers
        }
    return {
        "status": "degraded", 
        "npu_active": False, 
        "message": "Backend running, but ONNX model failed to load."
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not ort_session:
        raise HTTPException(status_code=503, detail="AI Model not loaded into memory.")
    
    # Next step: Add the audio preprocessing and ONNX run logic here
    return {
        "filename": file.filename, 
        "status": "received",
        "message": "Audio transcription logic pending implementation."
    }
