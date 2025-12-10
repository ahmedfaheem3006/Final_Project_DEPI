import { CONFIG } from './config.js';

// ==========================================
// 1. SETUP: SOCKET.IO CONNECTION (FIXED)
// ==========================================
// استخدام WebSocket مباشرة لتجنب خطأ 400 Bad Request
const socket = io("http://localhost:3000", {
    transports: ["websocket"],
    upgrade: false
});

socket.on("connect", () => {
    console.log("Connected to Unity Bridge Server!");
    updateStatus(TRANSLATIONS[currentLanguage].connected);
    setTimeout(() => updateStatus('&nbsp;'), 3000);
});

socket.on("connect_error", (err) => {
    console.error("Socket Connection Error:", err);
});

socket.on("disconnect", () => {
    console.log("Disconnected from Server");
    updateStatus(TRANSLATIONS[currentLanguage].disconnected);
});

// ==========================================
// 2. DOM ELEMENTS
// ==========================================
const micButton = document.getElementById('mic-button');
const statusEl = document.getElementById('status');
const chatContainer = document.getElementById('chat-history');
const avatarContainer = document.getElementById('avatar-container');
const textPromptInput = document.getElementById('text-prompt-input');
const sendTextButton = document.getElementById('send-text-button');
const chatForm = document.getElementById('chat-form');
const allInputs = [micButton, sendTextButton, textPromptInput];
const themeToggleButton = document.getElementById('theme-toggle-button');
const themeIconSun = document.getElementById('theme-icon-sun');
const themeIconMoon = document.getElementById('theme-icon-moon');
const langToggleButton = document.getElementById('lang-toggle-button');
const welcomeMessage = document.getElementById('welcome-message');
const toggleHistoryBtn = document.getElementById('toggle-history');
const historySidebar = document.getElementById('history-sidebar');
const closeSidebarBtn = document.getElementById('close-sidebar');
const newChatBtn = document.getElementById('new-chat-btn');
const chatListEl = document.getElementById('chat-list');

// ==========================================
// 2.1 CHAT HISTORY SYSTEM
// ==========================================
let currentChatId = null;
let chatSessions = {};

function generateChatId() {
    return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function saveChatSessions() {
    localStorage.setItem('chatSessions', JSON.stringify(chatSessions));
}

function loadChatSessions() {
    const saved = localStorage.getItem('chatSessions');
    if (saved) {
        chatSessions = JSON.parse(saved);
    }
}

function getCurrentChat() {
    if (!currentChatId || !chatSessions[currentChatId]) {
        createNewChat();
    }
    return chatSessions[currentChatId];
}

function createNewChat() {
    currentChatId = generateChatId();
    chatSessions[currentChatId] = {
        id: currentChatId,
        title: TRANSLATIONS[currentLanguage].welcome.substring(0, 30) + '...',
        messages: [],
        createdAt: new Date().toISOString()
    };
    saveChatSessions();
    updateChatList();
    clearChatUI();
}

function switchToChat(chatId) {
    if (chatSessions[chatId]) {
        currentChatId = chatId;
        loadChatMessages(chatId);
        updateChatList();
    }
}

function deleteChat(chatId) {
    if (confirm(currentLanguage === 'ar' ? 'هل تريد حذف هذه المحادثة؟' : 'Delete this chat?')) {
        delete chatSessions[chatId];
        saveChatSessions();

        // Always update the list first
        updateChatList();

        // If we deleted the current chat, create a new one
        if (currentChatId === chatId) {
            createNewChat();
        }
    }
}

function clearChatUI() {
    const chatHistoryContent = chatContainer.querySelector('.flex.flex-col.space-y-4');
    chatHistoryContent.innerHTML = `
        <div class="flex justify-start">
            <div id="welcome-message" class="chat-bubble assistant">${TRANSLATIONS[currentLanguage].welcome}</div>
        </div>
    `;
}

function loadChatMessages(chatId) {
    const chat = chatSessions[chatId];
    if (!chat) return;

    clearChatUI();
    const chatHistoryContent = chatContainer.querySelector('.flex.flex-col.space-y-4');

    chat.messages.forEach(msg => {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `flex justify-${msg.sender === 'user' ? 'end' : 'start'}`;
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${msg.sender}`;
        if (msg.text.includes('<img')) {
            bubble.innerHTML = msg.text;
        } else {
            bubble.textContent = msg.text;
        }
        messageWrapper.appendChild(bubble);
        chatHistoryContent.appendChild(messageWrapper);
    });

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function updateChatList() {
    chatListEl.innerHTML = '';
    const sortedChats = Object.values(chatSessions).sort((a, b) =>
        new Date(b.createdAt) - new Date(a.createdAt)
    );

    sortedChats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = `group relative p-3 rounded-lg cursor-pointer transition-colors ${chat.id === currentChatId ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
            }`;

        chatItem.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex-1 truncate text-sm text-white">${chat.title}</div>
                <button class="delete-chat-btn opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-600 rounded" data-chat-id="${chat.id}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
            <div class="text-xs text-gray-400 mt-1">${new Date(chat.createdAt).toLocaleDateString(currentLanguage === 'ar' ? 'ar-EG' : 'en-US')}</div>
        `;

        chatItem.addEventListener('click', (e) => {
            if (!e.target.closest('.delete-chat-btn')) {
                switchToChat(chat.id);
                if (window.innerWidth < 768) {
                    historySidebar.classList.remove('translate-x-0');
                    historySidebar.classList.add('-translate-x-full');
                }
            }
        });

        const deleteBtn = chatItem.querySelector('.delete-chat-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChat(chat.id);
        });

        chatListEl.appendChild(chatItem);
    });
}

// ==========================================
// 2.2 LANGUAGE SETUP
// ==========================================
let currentLanguage = 'ar'; // Default to Arabic

const TRANSLATIONS = {
    ar: {
        title: "مساعد صوتي احترافي",
        welcome: "مرحباً بك! معك شركة RG، كيف يمكنني مساعدتك اليوم؟",
        placeholder: "اسألني أي شيء...",
        listening_web: "... أستمع الآن (Web Speech)",
        listening_whisper: "... أستمع (Whisper)",
        processing: "... معالجة الصوت",
        thinking: "... أفكر",
        speaking: "... يتحدث",
        connected: "تم الاتصال بـ Unity بنجاح",
        disconnected: "انقطع الاتصال بـ Unity",
        whisper_loading: "... جاري تحميل Whisper (أونلاين)",
        whisper_ready: "Whisper جاهز!",
        whisper_fail: "فشل تحميل Whisper. جرب Web Speech.",
        no_speech: "لم اسمع شيئاً واضحاً",
        error: "خطأ",
        lang_btn: "EN",
        dir: "rtl",
        sidebar_title: "المحادثات",
        new_chat: "➕ محادثة جديدة",
        btn_show_furniture: "🪑 عرض الأثاث",
        btn_my_items: "📋 اللى ضفت",
        btn_colors: "🎨 الألوان",
        btn_materials: "🛠️ المواد",
        btn_help: "🛟 المساعدة",
        btn_send: "📤 ارسال",
        btn_clear: "🗑️ مسح الكل",
        design_btn_title: "تصميم ديكور / تحويل صورة لفيديو",
        sent_success: "تم الإرسال بنجاح"
    },
    en: {
        title: "Professional Voice Assistant",
        welcome: "Welcome! RG Company here, how can I help you today?",
        placeholder: "Ask me anything...",
        listening_web: "... Listening (Web Speech)",
        listening_whisper: "... Listening (Whisper)",
        processing: "... Processing Audio",
        thinking: "... Thinking",
        speaking: "... Speaking",
        connected: "Connected to Unity successfully",
        disconnected: "Disconnected from Unity",
        whisper_loading: "... Loading Whisper (Online)",
        whisper_ready: "Whisper Ready!",
        whisper_fail: "Whisper failed to load. Try Web Speech.",
        no_speech: "Heard nothing clearly",
        error: "Error",
        lang_btn: "AR",
        dir: "ltr",
        sidebar_title: "Chats",
        new_chat: "➕ New Chat",
        btn_show_furniture: "🪑 Show Furniture",
        btn_my_items: "📋 My Items",
        btn_colors: "🎨 Colors",
        btn_materials: "🛠️ Materials",
        btn_help: "🛟 Help",
        btn_send: "📤 Send",
        btn_clear: "🗑️ Clear All",
        design_btn_title: "Generate Design / Image to Video",
        sent_success: "Successful send"
    }
};

function toggleLanguage() {
    currentLanguage = currentLanguage === 'ar' ? 'en' : 'ar';
    updateLanguageUI();
}

function updateLanguageUI() {
    const t = TRANSLATIONS[currentLanguage];

    // Update Document Direction & Lang
    document.documentElement.lang = currentLanguage;
    document.documentElement.dir = t.dir;

    // Update Text Elements
    document.title = t.title;
    if (welcomeMessage) welcomeMessage.textContent = t.welcome;
    if (textPromptInput) textPromptInput.placeholder = t.placeholder;
    if (langToggleButton) langToggleButton.textContent = t.lang_btn;

    // Update Sidebar Elements
    const sidebarTitle = document.querySelector('#history-sidebar h2');
    if (sidebarTitle) sidebarTitle.textContent = t.sidebar_title;
    if (newChatBtn) newChatBtn.textContent = t.new_chat;

    // Update Welcome Message in Chat
    const welcomeMsgBubble = document.getElementById('welcome-message');
    if (welcomeMsgBubble) welcomeMsgBubble.textContent = t.welcome;

    // Update Quick Action Buttons
    if (document.getElementById('btn-show-furniture')) document.getElementById('btn-show-furniture').textContent = t.btn_show_furniture;
    if (document.getElementById('btn-my-items')) document.getElementById('btn-my-items').textContent = t.btn_my_items;
    if (document.getElementById('btn-colors')) document.getElementById('btn-colors').textContent = t.btn_colors;
    if (document.getElementById('btn-materials')) document.getElementById('btn-materials').textContent = t.btn_materials;
    if (document.getElementById('btn-help')) document.getElementById('btn-help').textContent = t.btn_help;
    if (document.getElementById('btn-send')) document.getElementById('btn-send').textContent = t.btn_send;
    if (document.getElementById('btn-clear')) document.getElementById('btn-clear').textContent = t.btn_clear;

    // Update Design Button Title
    if (designButton) designButton.title = t.design_btn_title;

    // Update Speech Recognition Language
    if (recognition) recognition.lang = currentLanguage === 'ar' ? 'ar-SA' : 'en-US';

    // Update System Prompt (Dynamic)
    updateSystemPrompt();
}

function updateSystemPrompt() {
    // This function will be called to get the correct prompt before sending to AI
    // We can also update the global systemPrompt variable if needed, but it's better to generate it on the fly or update a global one.
    // For now, let's update the global variable if it's used, or just rely on the getAIResponse to pick the right one.
}


// ==========================================
// 3. 3D AVATAR SETUP (THREE.JS)
// ==========================================
let scene, camera, renderer, orbGroup, core, wireframeShell, ring1, ring2;
let isSpeaking3D = false;

const darkThemeColors = { core: 0x4D94FF, wireframe: 0xFFFFFF, rings: 0xFFFFFF, light: 0x4D94FF };
const lightThemeColors = { core: 0x0056B3, wireframe: 0x333333, rings: 0x333333, light: 0x0056B3 };

function initThreeJS() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, avatarContainer.clientWidth / avatarContainer.clientHeight, 0.1, 1000);
    camera.position.z = 10;

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(avatarContainer.clientWidth, avatarContainer.clientHeight);
    avatarContainer.appendChild(renderer.domElement);

    // Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    scene.add(new THREE.HemisphereLight(0x6060ff, 0x101030, 0.5));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.7);
    dirLight.position.set(5, 5, 5);
    scene.add(dirLight);

    orbGroup = new THREE.Group();
    scene.add(orbGroup);

    // Orb Parts
    core = new THREE.Mesh(new THREE.SphereGeometry(1.5, 32, 32), new THREE.MeshBasicMaterial({ color: darkThemeColors.core, blending: THREE.AdditiveBlending, transparent: true, opacity: 0.8 }));
    orbGroup.add(core);

    wireframeShell = new THREE.Mesh(new THREE.IcosahedronGeometry(2.8, 2), new THREE.MeshBasicMaterial({ color: darkThemeColors.wireframe, wireframe: true, transparent: true, opacity: 0.15 }));
    orbGroup.add(wireframeShell);

    const ringMat = new THREE.MeshStandardMaterial({ color: darkThemeColors.rings, side: THREE.DoubleSide, transparent: true, opacity: 0.7, roughness: 0.8, metalness: 0.1 });
    ring1 = new THREE.Mesh(new THREE.TorusGeometry(3.5, 0.03, 16, 100), ringMat.clone());
    ring1.rotation.x = Math.PI / 2;
    orbGroup.add(ring1);

    ring2 = new THREE.Mesh(new THREE.TorusGeometry(3.2, 0.03, 16, 100), ringMat.clone());
    ring2.rotation.x = Math.PI / 2; ring2.rotation.y = Math.PI / 3;
    orbGroup.add(ring2);

    core.add(new THREE.PointLight(darkThemeColors.light, 1.0, 20));
    window.addEventListener('resize', onWindowResize);
}

function onWindowResize() {
    if (!renderer || !camera) return;
    camera.aspect = avatarContainer.clientWidth / avatarContainer.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(avatarContainer.clientWidth, avatarContainer.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    const time = Date.now();

    // Idle Animation
    orbGroup.position.y = Math.sin(time * 0.0005) * 0.1;
    orbGroup.rotation.y += 0.0005;
    wireframeShell.rotation.y += 0.002; wireframeShell.rotation.x += 0.001;
    ring1.rotation.z += 0.004; ring2.rotation.z -= 0.002;

    // Reactive Animation
    let corePulse = isSpeaking3D ? 1.0 + Math.abs(Math.sin(time * 0.03) * 0.3) : (isListening ? 1.0 + Math.abs(Math.sin(time * 0.01) * 0.1) : 1.0);
    let shellOpacity = isSpeaking3D ? 0.3 : (isListening ? 0.25 : 0.15);
    let ringOpacity = isSpeaking3D ? 1.0 : 0.7;

    core.scale.setScalar(core.scale.x + (corePulse - core.scale.x) * 0.1);
    wireframeShell.material.opacity += (shellOpacity - wireframeShell.material.opacity) * 0.1;
    ring1.material.opacity += (ringOpacity - ring1.material.opacity) * 0.1;
    ring2.material.opacity += (ringOpacity - ring2.material.opacity) * 0.1;

    renderer.render(scene, camera);
}

// ==========================================
// 4. API CONFIGURATION (OPENROUTER)
// ==========================================
const API_KEY = CONFIG.openRouterApiKey;
// Force the working model to avoid 429/400/404 errors
// Force the working model to avoid 429/400/404 errors
const MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-exp-1206:free",
    "microsoft/phi-3-medium-128k-instruct:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free"
];

// OpenRouter API URL
const GENERATE_API_URL = "https://openrouter.ai/api/v1/chat/completions";

// console.log("✅ API URL:", GENERATE_API_URL); 

function getSystemPrompt() {
    // Smart Polyglot Prompt
    return `
You are a smart, helpful assistant from RG Company.

**CORE RULE: LANGUAGE MIRRORING**
- IF the user speaks **ARABIC**, you MUST reply in **ARABIC** (Egyptian Dialect).
- IF the user speaks **ENGLISH**, you MUST reply in **ENGLISH** (Standard).
- NEVER switch languages unless asked. Match the user's language exactly.

**PERSONA (ARABIC / EGYPTIAN):**
- Tone: Friendly, natural, and smart.
- Style: Fluent Egyptian Dialect (Ammiya). Keep it clear.
- Keywords: "يا صاحبي", "تمام".
- BEHAVIOR: Act like a helpful Egyptian friend.

**PERSONA (ENGLISH):**
- Tone: Professional, concise, and helpful.
- Style: ChatGPT-like standard assistant.

**GLOBAL CAPABILITIES:**
1. **Unity**: Control 3D objects ONLY if explicitly asked.
2. **JSON**: Append commands at the end if needed:
   |UNITY_CMD|{"action": "create", "object": "cube", "color": "red"}|END_CMD|
`;
}

// Speech Variables
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isListening = false;
let currentAudio = null;
const whisperSettings = CONFIG.whisperOptions || {};
// Use base model for better balance (configured in worker)
const whisperModelId = "Xenova/whisper-base";
let whisperWorker = null;
let mediaStream = null;
let mediaRecorder = null;
let audioChunks = [];
let isWhisperActive = false;

// Utility: Fetch with Retry
async function fetchWithRetry(url, options, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
            return response;
        } catch (error) {
            if (i === retries - 1) throw error;
            await new Promise(res => setTimeout(res, delay));
            delay *= 2;
        }
    }
}

// ==========================================
// 5. SPEECH RECOGNITION (WEB SPEECH + WHISPER)
// ==========================================

// A. Web Speech API (Built-in)
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'ar-SA';
    recognition.interimResults = false;

    recognition.onstart = () => {
        isListening = true;
        micButton.classList.add('is-listening');
        updateStatus(TRANSLATIONS[currentLanguage].listening_web);
    };
    recognition.onend = () => {
        isListening = false;
        micButton.classList.remove('is-listening');
        if (!isWhisperActive) updateStatus('&nbsp;');
    };
    recognition.onerror = (e) => console.error('WebSpeech Error:', e);
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        addMessageToChat(transcript, 'user');
        getAIResponse(transcript);
    };
}

// B. Whisper (Transformers.js) - Running in Web Worker
async function initWhisper() {
    if (whisperWorker) return true;

    updateStatus(TRANSLATIONS[currentLanguage].whisper_loading);

    return new Promise((resolve) => {
        whisperWorker = new Worker('whisper.worker.js', { type: 'module' });

        whisperWorker.onmessage = (e) => {
            const { status, text, message } = e.data;
            if (status === 'ready') {
                updateStatus(TRANSLATIONS[currentLanguage].whisper_ready);
                setTimeout(() => updateStatus('&nbsp;'), 2000);
                resolve(true);
            } else if (status === 'error') {
                console.error('Whisper Worker Error:', message);
                updateStatus(TRANSLATIONS[currentLanguage].whisper_fail);
                resolve(false);
            }
        };

        // CRASH RECOVERY: Handle unexpected worker termination
        whisperWorker.onerror = (e) => {
            console.error("⚠️ Whisper Worker Crashed (Likely OOM). Restarting...", e);
            whisperWorker.terminate();
            whisperWorker = null;
            // Auto-restart
            initWhisper().then(() => {
                console.log("♻️ Whisper Worker recovered.");
            });
        };

        whisperWorker.postMessage({ type: 'init' });
    });
}

async function startWhisperRecording() {
    try {
        // Ensure worker is ready BEFORE asking for mic
        const isReady = await initWhisper();
        if (!isReady) {
            console.error("Whisper failed to initialize.");
            return false;
        }

        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: { channelCount: 1, sampleRate: 16000, echoCancellation: true }
        });

        audioChunks = [];
        mediaRecorder = new MediaRecorder(mediaStream, { mimeType: 'audio/webm' });

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            isListening = false;
            micButton.classList.remove('is-listening');
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await processAudioWithWhisper(audioBlob);
            cleanupMediaStream();
            isWhisperActive = false;
        };

        mediaRecorder.start();
        isListening = true;
        isWhisperActive = true;
        micButton.classList.add('is-listening');
        updateStatus(TRANSLATIONS[currentLanguage].listening_whisper);
        return true;
    } catch (error) {
        console.error(error);
        cleanupMediaStream();
        isWhisperActive = false;
        return false;
    }
}

async function stopWhisperRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        updateStatus(TRANSLATIONS[currentLanguage].processing);
        mediaRecorder.stop();
    } else {
        cleanupMediaStream();
    }
}

async function processAudioWithWhisper(audioBlob) {
    try {
        const buffer = await audioBlob.arrayBuffer();
        const audioCtx = new AudioContext({ sampleRate: 16000 });
        const audioBuffer = await audioCtx.decodeAudioData(buffer);
        const audioData = audioBuffer.getChannelData(0);

        // Send to Worker - No language forced, enabling auto-detect
        whisperWorker.postMessage({
            type: 'transcribe',
            audio: audioData
        });

        // Handle Response via onmessage (simple implementation)
        // Note: For concurrent requests, use a request ID mapping, but here we process one at a time.
        const originalOnMessage = whisperWorker.onmessage; // Backup init listener

        whisperWorker.onmessage = (e) => {
            const { status, text, message } = e.data;

            if (status === 'complete') {
                const cleanText = text?.trim();
                if (cleanText && cleanText.length > 1) {
                    addMessageToChat(cleanText, 'user');

                    // Check LocalBot
                    const localResponse = LocalBot.process(cleanText);
                    if (localResponse) {
                        updateStatus(TRANSLATIONS[currentLanguage].thinking);
                        setTimeout(async () => {
                            addMessageToChat(localResponse, 'assistant');
                            await speakWithGeminiTTS(localResponse);
                            updateStatus('&nbsp;');
                        }, 500);
                    } else {
                        getAIResponse(cleanText);
                    }
                } else {
                    updateStatus(TRANSLATIONS[currentLanguage].no_speech);
                    setTimeout(() => updateStatus('&nbsp;'), 2000);
                }
                // Restore listener or keep it? Checking 'ready' again isn't needed but safest is to just keep this one.
            } else if (status === 'error') {
                console.error("Whisper Process Error:", message);
                updateStatus(TRANSLATIONS[currentLanguage].error);
            }
        };

    } catch (error) {
        console.error("Whisper Setup Error:", error);
        updateStatus(TRANSLATIONS[currentLanguage].error);
    }
}

function cleanupMediaStream() {
    if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
    mediaStream = null;
    mediaRecorder = null;
    audioChunks = [];
}

// ==========================================
// 6. MAIN INTERACTION LOGIC
// ==========================================

function setInputsDisabled(disabled) { allInputs.forEach(input => input.disabled = disabled); }

micButton.addEventListener('click', async () => {
    // Stop current audio
    if (currentAudio) { currentAudio.pause(); currentAudio.currentTime = 0; }
    isSpeaking3D = false;

    if (isListening) {
        if (isWhisperActive) await stopWhisperRecording();
        else if (recognition) recognition.stop();
        return;
    }

    // Try Whisper first
    const started = await startWhisperRecording();
    // If Whisper fails, use Web Speech
    if (!started && recognition) recognition.start();
});

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleTextInput();
});

function handleTextInput() {
    const prompt = textPromptInput.value.trim();
    if (!prompt) return;

    if (currentAudio) { currentAudio.pause(); currentAudio.currentTime = 0; }
    isSpeaking3D = false;

    addMessageToChat(prompt, 'user');
    textPromptInput.value = '';

    // Check LocalBot first
    const localResponse = LocalBot.process(prompt);
    if (localResponse) {
        updateStatus(TRANSLATIONS[currentLanguage].thinking);
        setTimeout(async () => {
            addMessageToChat(localResponse, 'assistant');
            await speakWithGeminiTTS(localResponse);
            updateStatus('&nbsp;');
        }, 500);
    } else {
        getAIResponse(prompt);
    }
}

// Main AI Handler (OpenRouter with Fallback)
async function getAIResponse(prompt) {
    updateStatus(TRANSLATIONS[currentLanguage].thinking);
    setInputsDisabled(true);
    isListening = false;

    // 0. CHECK INTERNET CONNECTION
    if (!navigator.onLine) {
        const errText = currentLanguage === 'ar' ? "⚠️ لا يوجد اتصال بالإنترنت." : "⚠️ No Internet Connection.";
        addMessageToChat(errText, 'assistant');
        setInputsDisabled(false);
        updateStatus('&nbsp;');
        return;
    }

    let lastError = null;

    // Try models in sequence
    for (const model of MODELS) {
        try {
            console.log(`🔄 Trying model: ${model}...`);

            const response = await fetch(GENERATE_API_URL, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${API_KEY}`,
                    'HTTP-Referer': window.location.href, // Site URL
                    'X-Title': 'RG Chatbot', // Site Title
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: model,
                    messages: [
                        {
                            role: "system",
                            content: getSystemPrompt()
                        },
                        {
                            role: "user",
                            content: prompt
                        }
                    ],
                    temperature: 0.6,
                    top_p: 0.9
                })
            });

            console.log(`📊 Status (${model}):`, response.status);

            if (!response.ok) {
                const errorData = await response.json();
                console.warn(`⚠️ Model ${model} failed:`, errorData);

                // If it's a rate limit (429) or invalid model (400 or 404), continue to next model
                if (response.status === 429 || response.status === 400 || response.status === 404) {
                    lastError = errorData;
                    continue;
                }

                throw new Error(`OpenRouter Error: ${errorData.error?.message || response.statusText}`);
            }

            const result = await response.json();
            console.log(`✅ Success with ${model}:`, result);

            const text = result.choices?.[0]?.message?.content;

            if (text) {
                addMessageToChat(text, 'assistant');

                // >>> Send Command to UNITY <<<
                console.log("Sending to Unity Bridge:", text);
                socket.emit("ai_response", text);

                await speakWithGeminiTTS(text);
                setInputsDisabled(false); // Fix: Re-enable inputs on success
                return; // Exit function on success
            } else {
                console.error("❌ API Response Missing Content. Full Result:", JSON.stringify(result, null, 2));
                throw new Error("No response content from API");
            }

        } catch (error) {
            console.error(`❌ Error with ${model}:`, error.message);
            lastError = error;

            // Check for network errors
            if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
                addMessageToChat(currentLanguage === 'ar' ? "⚠️ مشكلة في الاتصال بالشبكة (DNS/Internet)." : "⚠️ Network/DNS Error.", 'assistant');
                break; // Stop trying other models if internet is down
            }
            // Continue to next model
        }
    }

    // If loop finishes without success (checking lastError)
    if (lastError) {
        console.error("❌ All models failed.");
        addMessageToChat(`Error: All models failed. Last error: ${lastError?.message || 'Unknown'}`, 'assistant');
        setInputsDisabled(false);
        updateStatus('&nbsp;');
    }
}

// TTS Handler - Web Speech API with Dynamic Language Detection
async function speakWithGeminiTTS(text) {
    updateStatus(TRANSLATIONS[currentLanguage].speaking);

    try {
        let speechText = text;

        // Remove Unity Commands
        const hasUnityCmd = speechText.includes("|UNITY_CMD|");
        if (hasUnityCmd) {
            speechText = speechText.substring(0, text.indexOf("|UNITY_CMD|")).trim();
        }

        if (!speechText) {
            if (hasUnityCmd) {
                // Speak confirmation if it was a command
                speechText = TRANSLATIONS[currentLanguage].sent_success;
            } else {
                // Just empty??
                isSpeaking3D = false;
                updateStatus('&nbsp;');
                return;
            }
        }

        if ('speechSynthesis' in window) {
            speechSynthesis.cancel(); // Stop previous speech

            const utterance = new SpeechSynthesisUtterance(speechText);

            // DYNAMIC DEVICE SELECTION: Detect language from TEXT
            const isArabicText = /[\u0600-\u06FF]/.test(speechText);

            if (isArabicText) {
                // Force Arabic Voice
                utterance.lang = 'ar-SA';
                const arVoice = window.speechSynthesis.getVoices().find(v => v.lang.includes('ar'));
                if (arVoice) utterance.voice = arVoice;
            } else {
                // Force English Voice
                utterance.lang = 'en-US';
                const enVoice = window.speechSynthesis.getVoices().find(v => v.lang.includes('en') && !v.lang.includes('ar'));
                if (enVoice) utterance.voice = enVoice;
            }

            // Adjust properties
            utterance.pitch = 1.0;
            utterance.rate = 1.0;

            utterance.onstart = () => {
                updateStatus(TRANSLATIONS[currentLanguage].speaking);
                isSpeaking3D = true;
            };

            utterance.onend = () => {
                isSpeaking3D = false;
                updateStatus('&nbsp;');
            };

            utterance.onerror = (e) => {
                console.error("Speech Error:", e);
                isSpeaking3D = false;
                updateStatus('&nbsp;');
            };

            speechSynthesis.speak(utterance);
        } else {
            console.warn("Speech Synthesis not supported");
            isSpeaking3D = false;
        }
    } catch (error) {
        console.error("TTS Error:", error);
        isSpeaking3D = false;
        updateStatus('&nbsp;');
    }
}
// ==========================================
// 7. HELPERS
// ==========================================

function updateStatus(text) {
    if (statusEl) statusEl.innerHTML = text;
}

function addMessageToChat(text, sender) {
    const chatHistoryContent = chatContainer.querySelector('.flex.flex-col.space-y-4');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = `flex justify-${sender === 'user' ? 'end' : 'start'}`;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;

    // إخفاء الأوامر من الشات
    let displayText = text;
    const hasUnityCmd = text.includes("|UNITY_CMD|");

    if (sender === 'assistant' && hasUnityCmd) {
        displayText = text.substring(0, text.indexOf("|UNITY_CMD|"));
    }

    // If pure command, show confirmation
    if (sender === 'assistant' && hasUnityCmd && !displayText.trim()) {
        displayText = TRANSLATIONS[currentLanguage].sent_success;
    }

    // ✅ السماح بـ HTML للصور فقط
    if (displayText.includes('<img')) {
        bubble.innerHTML = displayText;
    } else {
        bubble.textContent = displayText;
    }

    messageWrapper.appendChild(bubble);
    chatHistoryContent.appendChild(messageWrapper);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Save to current chat session
    const currentChat = getCurrentChat();
    currentChat.messages.push({
        text: displayText,
        sender: sender,
        timestamp: new Date().toISOString()
    });

    // Auto-generate title from first user message
    if (sender === 'user' && currentChat.messages.filter(m => m.sender === 'user').length === 1) {
        currentChat.title = displayText.substring(0, 40) + (displayText.length > 40 ? '...' : '');
        updateChatList();
    }

    saveChatSessions();
}

function base64ToArrayBuffer(base64) {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = binaryString.charCodeAt(i);
    return bytes.buffer;
}

function pcmToWav(pcmData, sampleRate) {
    const buffer = new ArrayBuffer(44 + pcmData.length * 2);
    const view = new DataView(buffer);
    view.setUint32(0, 1380533830, false); view.setUint32(4, 36 + pcmData.length * 2, true); view.setUint32(8, 1463899717, false);
    view.setUint32(12, 1718449184, false); view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true); view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true); view.setUint16(34, 16, true);
    view.setUint32(36, 1684108385, false); view.setUint32(40, pcmData.length * 2, true);
    for (let i = 0; i < pcmData.length; i++) { view.setInt16(44 + i * 2, pcmData[i], true); }
    return new Blob([view], { type: 'audio/wav' });
}

// ==========================================
// 8. INITIALIZATION & THEME TOGGLE
// ==========================================

initThreeJS();
animate();
// تحميل Whisper مبكراً
initWhisper();

if (themeToggleButton) {
    themeToggleButton.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        const isLightMode = document.body.classList.contains('light-mode');
        const colors = isLightMode ? lightThemeColors : darkThemeColors;

        if (themeIconSun) themeIconSun.classList.toggle('hidden', isLightMode);
        if (themeIconMoon) themeIconMoon.classList.toggle('hidden', !isLightMode);

        if (core) core.material.color.set(colors.core);
        if (wireframeShell) wireframeShell.material.color.set(colors.wireframe);
        if (ring1) ring1.material.color.set(colors.rings);
        if (ring2) ring2.material.color.set(colors.rings);

        if (core && core.children) {
            const light = core.children.find(child => child.isPointLight);
            if (light) light.color.set(colors.light);
        }
    });
}

if (langToggleButton) {
    langToggleButton.addEventListener('click', toggleLanguage);
}

// ==========================================
// 8. LOCAL BOT LOGIC (Enhanced)
// ==========================================
const LOCAL_DATA = {
    furniture: {
        "كنبة": {
            "models": [
                { "name": "كنبة مودرن 3 أفراد", "available_colors": ["أحمر", "أزرق", "رمادي", "أسود"], "materials": ["قُماش", "جِلْد"] },
                { "name": "كنبة كلاسيك منجدة", "available_colors": ["بني", "ذهبي", "أخضر", "أبيض"], "materials": ["قُماش", "جِلْد"] }
            ]
        },
        "كرسي": {
            "models": [
                { "name": "كرسي مكتب دوار", "available_colors": ["أسود", "رمادي", "أزرق"], "materials": ["بلاستيك", "معدن"] },
                { "name": "كرسي سفرة خشب", "available_colors": ["بني", "أبيض", "أصفر"], "materials": ["خشب"] }
            ]
        },
        "ترابيزة": {
            "models": [
                { "name": "ترابيزة سفرة خشب", "available_colors": ["بني", "أبيض"], "materials": ["خشب"] },
                { "name": "ترابيزة قهوة مودرن", "available_colors": ["أسود", "أبيض", "ذهبي"], "materials": ["زجاج", "معدن"] }
            ]
        }
    },
    colors: {
        "أحمر": "أحمر", "أزرق": "أزرق", "أخضر": "أخضر", "أصفر": "أصفر",
        "أسود": "أسود", "أبيض": "أبيض", "رمادي": "رمادي", "بني": "بني",
        "ذهبي": "ذهبي", "فضي": "فضي"
    },
    materials: {
        "خشب": "خشب", "معدن": "معدن", "زجاج": "زجاج",
        "قُماش": "قُماش", "جِلْد": "جِلْد", "بلاستيك": "بلاستيك"
    }
};

const LocalBot = {
    memory: [],
    sessionState: {
        pendingAction: null, // 'awaiting_color'
        pendingItem: null
    },

    // NLP Helpers
    normalize: function (text) {
        if (!text) return "";
        let t = text.toLowerCase().trim();
        t = t.replace(/[أإآ]/g, 'ا').replace('ة', 'ه');
        return t;
    },

    detectFurniture: function (text) {
        const norm = this.normalize(text);
        for (const item of Object.keys(LOCAL_DATA.furniture)) {
            if (norm.includes(this.normalize(item))) return item;
        }
        // Synonyms
        if (norm.includes('كنبه') || norm.includes('اريكة')) return 'كنبة';
        if (norm.includes('طاوله') || norm.includes('منضدة')) return 'ترابيزة';
        if (norm.includes('مقعد')) return 'كرسي';
        return null;
    },

    detectColor: function (text) {
        const norm = this.normalize(text);
        for (const color of Object.keys(LOCAL_DATA.colors)) {
            if (norm.includes(this.normalize(color))) return color;
        }
        return null;
    },

    process: function (action) {
        const text = this.normalize(action);

        // 1. Check Pending State (Awaiting Color)
        if (this.sessionState.pendingAction === 'awaiting_color') {
            const color = this.detectColor(text);
            const item = this.sessionState.pendingItem;

            if (color) {
                this.addItem(item, color);
                this.sessionState.pendingAction = null;
                this.sessionState.pendingItem = null;
                return `✅ تم إضافة ${item} باللون ${color} إلى القائمة.`;
            } else {
                return `🤔 لم أفهم اللون. الألوان المتاحة لـ ${item}: ${LOCAL_DATA.furniture[item].models[0].available_colors.join(", ")}`;
            }
        }

        // 2. Show Furniture
        if (text.includes("عرض الاثاث") || text.includes("show furniture")) {
            let response = "🪑 الأثاث المتاح:\n";
            for (const [item, info] of Object.entries(LOCAL_DATA.furniture)) {
                const models = info.models.map(m => m.name).join(", ");
                response += `• ${item} - الموديلات: ${models}\n`;
            }
            return response;
        }

        // 3. Show My Items (Enhanced to show JSON)
        if (text.includes("عرض اللى ضفت") || text.includes("اللى ضفت") || text.includes("my items")) {
            if (this.memory.length === 0) {
                return "🪑 مفيش قطع أثاث مضيفة حالياً.";
            }
            let response = "🪑 القطع اللى ضفتها:\n";
            this.memory.forEach((entry, index) => {
                response += `${index + 1}. ${entry.item} (${entry.color || 'بدون لون'})\n`;
            });

            // Generate JSON for display
            response += "\n📋 كود JSON:\n";
            this.memory.forEach(entry => {
                let objName = "Cube";
                if (entry.item === "كنبة") objName = "Sofa";
                if (entry.item === "كرسي") objName = "Chair";
                if (entry.item === "ترابيزة") objName = "Table";

                let colorName = "White";
                if (entry.color === "أحمر") colorName = "Red";
                if (entry.color === "أزرق") colorName = "Blue";
                if (entry.color === "أخضر") colorName = "Green";

                const cmd = {
                    action: "create",
                    object: objName,
                    color: colorName
                };
                response += `|UNITY_CMD|${JSON.stringify(cmd)}|END_CMD|\n`;
            });

            return response;
        }

        // 4. Send to Unity
        if (text.includes("ارسال") || text.includes("send")) {
            if (this.memory.length === 0) {
                return "❌ القائمة فارغة. أضف أثاث أولاً.";
            }
            return this.sendToUnity();
        }

        // 5. Show Colors
        if (text.includes("الالوان") || text.includes("colors")) {
            return `🎨 الألوان المتاحة:\n${Object.keys(LOCAL_DATA.colors).join(", ")}`;
        }

        // 6. Show Materials
        if (text.includes("المواد") || text.includes("materials")) {
            return `🛠️ المواد المتاحة:\n${Object.keys(LOCAL_DATA.materials).join(", ")}`;
        }

        // 7. Help
        if (text.includes("المساعدة") || text.includes("help")) {
            return "🛟 كيف أساعدك؟\n\n" +
                "• إضافة: اكتب اسم الأثاث (مثلاً 'كنبة')\n" +
                "• عرض: 'عرض الأثاث' أو 'اللى ضفت'\n" +
                "• ارسال: 'ارسال' لبعث الأوامر لـ Unity\n" +
                "• مسح: 'مسح الكل'";
        }

        // 8. Add Item Intent (Enhanced to detect just item name)
        const detectedItem = this.detectFurniture(text);
        const detectedColor = this.detectColor(text);

        if (detectedItem) {
            if (detectedColor) {
                this.addItem(detectedItem, detectedColor);
                return `✅ تم إضافة ${detectedItem} باللون ${detectedColor} إلى القائمة.`;
            } else {
                this.sessionState.pendingAction = 'awaiting_color';
                this.sessionState.pendingItem = detectedItem;
                // Show available colors for this item
                const availableColors = LOCAL_DATA.furniture[detectedItem].models[0].available_colors.join(", ");
                return `🎨 ممتاز! عايز تضيف ${detectedItem} بإيه لون؟\nالألوان المتاحة: ${availableColors}`;
            }
        }

        return null; // Pass to AI
    },

    addItem: function (item, color) {
        this.memory.push({
            item: item,
            color: color,
            timestamp: new Date().toISOString()
        });
    },

    sendToUnity: function () {
        let response = "🚀 جاري إرسال الأوامر لـ Unity...\n";
        let commands = "";

        this.memory.forEach(entry => {
            // Construct Unity JSON Command
            // Assuming 'create' action for added items
            // Mapping Arabic names to English if needed, but keeping simple for now
            // You might need a mapping dictionary if Unity expects English names

            // Simple mapping for demo
            let objName = "Cube";
            if (entry.item === "كنبة") objName = "Sofa";
            if (entry.item === "كرسي") objName = "Chair";
            if (entry.item === "ترابيزة") objName = "Table";

            let colorName = "White";
            if (entry.color === "أحمر") colorName = "Red";
            if (entry.color === "أزرق") colorName = "Blue";
            if (entry.color === "أخضر") colorName = "Green";

            const cmd = {
                action: "create",
                object: objName,
                color: colorName
            };

            const jsonCmd = `|UNITY_CMD|${JSON.stringify(cmd)}|END_CMD|`;
            commands += jsonCmd + "\n";

            // Send to Socket
            if (socket && socket.connected) {
                socket.emit("ai_response", jsonCmd);
            }
        });

        return response + commands;
    },

    clear: function () {
        this.memory = [];
        this.sessionState.pendingAction = null;
        this.sessionState.pendingItem = null;
    }
};

// ==========================================
// 9. QUICK ACTIONS
// ==========================================
window.quickAction = async function (action) {
    addMessageToChat(action, 'user');

    // Try LocalBot first
    const localResponse = LocalBot.process(action);

    if (localResponse) {
        // Simulate thinking delay
        updateStatus(TRANSLATIONS[currentLanguage].thinking);
        await new Promise(resolve => setTimeout(resolve, 500));

        addMessageToChat(localResponse, 'assistant');
        await speakWithGeminiTTS(localResponse);
        updateStatus('&nbsp;');
    } else {
        // Fallback to Gemini for other requests
        await getAIResponse(action);
    }
}

window.clearChat = async function () {
    try {
        // Clear LocalBot memory
        LocalBot.clear();

        // Clear UI
        chatContainer.querySelector('.flex.flex-col.space-y-4').innerHTML = '';

        // Clear Chat History Session
        if (currentChatId && chatSessions[currentChatId]) {
            chatSessions[currentChatId].messages = [];
            saveChatSessions();
        }

        updateStatus("تم مسح المحادثة والذاكرة");
        setTimeout(() => updateStatus('&nbsp;'), 2000);

        // Reset Welcome Message
        clearChatUI();

    } catch (e) {
        console.error(e);
        updateStatus("خطأ في المسح");
    }
}

// ==========================================
// 10. INITIALIZE CHAT HISTORY
// ==========================================
// Initialize chat history after TRANSLATIONS is defined
loadChatSessions();
if (Object.keys(chatSessions).length === 0) {
    createNewChat();
} else {
    const latestChatId = Object.keys(chatSessions).sort((a, b) =>
        new Date(chatSessions[b].createdAt) - new Date(chatSessions[a].createdAt)
    )[0];
    currentChatId = latestChatId;
    loadChatMessages(currentChatId);
}
updateChatList();
// ==========================================
// 9. INTERIOR DESIGN GENERATOR LOGIC
// ==========================================

const DESIGN_API_URL = "http://localhost:8000/api/v1";
const designButton = document.getElementById('design-button');
const imageUpload = document.getElementById('image-upload');

if (designButton && imageUpload) {
    designButton.addEventListener('click', handleDesignAction);
    imageUpload.addEventListener('change', handleImageUpload);
}

async function handleDesignAction() {
    const prompt = textPromptInput.value.trim();

    if (prompt) {
        // 1. Text-to-Image Flow
        addMessageToChat(`🎨 Generating design for: "${prompt}"...`, 'assistant');
        textPromptInput.value = '';
        await generateImageFromText(prompt);
    } else {
        // 2. Image-to-Video Flow (Upload)
        imageUpload.click();
    }
}

async function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    addMessageToChat(`🎬 Uploading image for video generation...`, 'assistant');
    await generateVideoFromImage(file);
    imageUpload.value = ''; // Reset
}

async function generateImageFromText(prompt) {
    updateStatus("Generating Image...");
    try {
        // استخدام Pollinations AI (مجاني، سريع، بدون API Key، بدون Proxy)
        const encodedPrompt = encodeURIComponent(`interior design, ${prompt}, professional photography, 8k, detailed, high quality`);
        const imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=1024&height=1024&model=flux&nologo=true`;

        // تحميل الصورة للتأكد من أنها جاهزة
        const img = new Image();
        img.onload = async () => {
            addMessageToChat(
                `✅ Image Generated!<br><img src="${imageUrl}" class="mt-2 rounded-lg max-w-full h-auto shadow-md" alt="Generated Design">`,
                'assistant'
            );
            updateStatus('&nbsp;');

            // حفظ الصورة محلياً
            try {
                const saveResponse = await fetch('http://localhost:5000/save-image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_url: imageUrl })
                });
                const saveData = await saveResponse.json();
                if (saveData.status === 'success') {
                    console.log(`Image saved to: ${saveData.path}`);
                    addMessageToChat(`💾 Image saved to: <br><code>${saveData.path}</code>`, 'assistant');
                }
            } catch (e) {
                console.error("Failed to save image locally:", e);
            }
        };
        img.onerror = () => {
            throw new Error("Failed to load image");
        };
        img.src = imageUrl;

    } catch (error) {
        console.error(error);
        addMessageToChat("❌ Failed to generate image. Please try again.", 'assistant');
        updateStatus('&nbsp;');
    }
}

async function generateVideoFromImage(file) {
    updateStatus("Generating Video...");
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('room_type', 'living_room'); // Default
        formData.append('motion_style', 'moderate');

        const response = await fetch(`${DESIGN_API_URL}/generate/video`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("API Error");

        const data = await response.json();
        monitorJob(data.job_id, "video");

    } catch (error) {
        console.error(error);
        addMessageToChat("❌ Failed to start video generation. Is the server running?", 'assistant');
        updateStatus('&nbsp;');
    }
}

async function monitorJob(jobId, type) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${DESIGN_API_URL}/status/${jobId}`);
            const status = await response.json();

            if (status.status === 'completed') {
                clearInterval(interval);
                updateStatus('&nbsp;');

                if (type === 'image') {
                    const imageUrl = `${DESIGN_API_URL}/download/image/${jobId}`;
                    addMessageToChat(`✅ Image Generated!<br><img src="${imageUrl}" class="mt-2 rounded-lg max-w-full h-auto shadow-md" alt="Generated Design">`, 'assistant');
                } else {
                    const videoUrl = `${DESIGN_API_URL}/download/video/${jobId}`;
                    addMessageToChat(`✅ Video Generated!<br><video controls autoplay loop class="mt-2 rounded-lg max-w-full h-auto shadow-md"><source src="${videoUrl}" type="video/mp4"></video>`, 'assistant');
                }
            } else if (status.status === 'failed') {
                clearInterval(interval);
                updateStatus('&nbsp;');
                addMessageToChat(`❌ Generation Failed: ${status.message}`, 'assistant');
            } else {
                updateStatus(`Processing: ${status.progress}%`);
            }
        } catch (e) {
            clearInterval(interval);
        }
    }, 2000);
}
// Event listeners for history sidebar
if (toggleHistoryBtn) {
    toggleHistoryBtn.addEventListener('click', () => {
        historySidebar.classList.toggle('-translate-x-full');
        historySidebar.classList.toggle('translate-x-0');
    });
}

if (closeSidebarBtn) {
    closeSidebarBtn.addEventListener('click', () => {
        historySidebar.classList.remove('translate-x-0');
        historySidebar.classList.add('-translate-x-full');
    });
}

if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
        createNewChat();
        if (window.innerWidth < 768) {
            historySidebar.classList.remove('translate-x-0');
            historySidebar.classList.add('-translate-x-full');
        }
    });
}

// FORCE UI SYNC ON LOAD
updateLanguageUI();