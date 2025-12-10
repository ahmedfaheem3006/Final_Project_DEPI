
import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2';

// 1. Suppress ONNX Warnings & Logs
// Override console.warn to capture C++ runtime warnings that bypass env.logLevel
const originalWarn = console.warn;
console.warn = function (...args) {
    if (args[0] && typeof args[0] === 'string' && args[0].includes('CleanUnusedInitializersAndNodeArgs')) return;
    originalWarn.apply(console, args);
};

env.backends.onnx.logLevel = 'fatal';
env.allowLocalModels = false;
env.useBrowserCache = true;

let transcriber = null;

// 2. Initialize Pipeline
async function loadTranscriber() {
    try {
        // Quantized + WebGPU = FAST & SMART (Small Model)
        // 'small' is the sweet spot. 'tiny' is dumb, 'base' is heavy.
        transcriber = await pipeline('automatic-speech-recognition', 'Xenova/whisper-small', {
            device: 'webgpu'
        });
        self.postMessage({ status: 'ready' });
    } catch (error) {
        // Fallback to WASM if WebGPU fails
        try {
            console.log("WebGPU Quantized failed, falling back to WASM");
            transcriber = await pipeline('automatic-speech-recognition', 'Xenova/whisper-small');
            self.postMessage({ status: 'ready' });
        } catch (e) {
            self.postMessage({ status: 'error', message: e.message });
        }
    }
}

// 3. Handle Messages
self.addEventListener('message', async (event) => {
    const { type, audio } = event.data;

    if (type === 'init') {
        await loadTranscriber();
    } else if (type === 'transcribe') {
        if (!transcriber) {
            self.postMessage({ status: 'error', message: 'Transcriber not initialized' });
            return;
        }

        try {
            const output = await transcriber(audio, {
                // Auto-detect language
                task: 'transcribe',
                return_timestamps: false
            });

            self.postMessage({ status: 'complete', text: output.text });
        } catch (error) {
            self.postMessage({ status: 'error', message: error.message });
        }
    }
});
