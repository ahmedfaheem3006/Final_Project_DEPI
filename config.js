export const CONFIG = {
    geminiApiKey: "AIzaSyDiqzbdBQNJbzlty0sX-4Yc2lplmVOPcns",
    
    // ✅ استخدم الموديل الذي يشتغل
    geminiModel: "gemini-2.0-flash-lite",
    
    whisperModel: "Xenova/whisper-small", 
    whisperLocalModelPath: null,
    whisperAllowRemote: true,
    transformersScriptPath: "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/dist/transformers.min.js",
    whisperOptions: {
        dtype: "float32",
        device: "wasm",
        language: "arabic",
        chunkLength: 30,
        strideLength: 5
    }
};