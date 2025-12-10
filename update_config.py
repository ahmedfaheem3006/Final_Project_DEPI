
content = """export const CONFIG = {
    geminiApiKey: "AIzaSyBQPKF9ZH2oqA9Ns3GORCWXoE_WLOqdRjc",
    openRouterApiKey: "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",
    geminiModel: "gemini-2.0-flash-lite",
    openRouterModel: "google/gemini-2.0-flash-exp:free",
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
};"""

with open('config.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("config.js updated successfully")
