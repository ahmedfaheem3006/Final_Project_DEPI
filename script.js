// DOM Elements
const micButton = document.getElementById('mic-button');
const statusEl = document.getElementById('status');
const chatContainer = document.getElementById('chat-history');
const avatarContainer = document.getElementById('avatar-container');
const textPromptInput = document.getElementById('text-prompt-input');
const sendTextButton = document.getElementById('send-text-button');
const chatForm = document.getElementById('chat-form');
const allInputs = [micButton, sendTextButton, textPromptInput];

// --- عناصر تبديل الوضع (جديد) ---
const themeToggleButton = document.getElementById('theme-toggle-button');
const themeIconSun = document.getElementById('theme-icon-sun');
const themeIconMoon = document.getElementById('theme-icon-moon');


// --- 3D AVATAR SETUP (Professional Orb) ---
let scene, camera, renderer, orbGroup, core, wireframeShell, ring1, ring2;
let isSpeaking3D = false;
// 'isListening' موجودة بالفعل في الكود الأصلي، سنستخدمها للأنيميشن

// --- ألوان الوضع الداكن والفاتح للـ 3D (جديد) ---
const darkThemeColors = {
    core: 0x4D94FF,
    wireframe: 0xFFFFFF,
    rings: 0xFFFFFF,
    light: 0x4D94FF
};
const lightThemeColors = {
    core: 0x0056B3, // أزرق أغمق
    wireframe: 0x333333, // رمادي غامق
    rings: 0x333333, // رمادي غامق
    light: 0x0056B3
};


function initThreeJS() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, avatarContainer.clientWidth / avatarContainer.clientHeight, 0.1, 1000);
    camera.position.z = 10;

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(avatarContainer.clientWidth, avatarContainer.clientHeight);
    avatarContainer.appendChild(renderer.domElement);

    // --- إضاءة احترافية (خافتة وأكثر عمقاً) ---
    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    scene.add(new THREE.HemisphereLight(0x6060ff, 0x101030, 0.5)); // إضاءة علوية زرقاء وسفلية داكنة
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.7);
    dirLight.position.set(5, 5, 5);
    scene.add(dirLight);
    
    orbGroup = new THREE.Group();
    scene.add(orbGroup);

    // --- 1. الكرة المركزية (Core) ---
    const coreMaterial = new THREE.MeshBasicMaterial({ 
        color: darkThemeColors.core, // استخدام اللون الافتراضي (الداكن)
        blending: THREE.AdditiveBlending,
        transparent: true,
        opacity: 0.8
    });
    const coreGeometry = new THREE.SphereGeometry(1.5, 32, 32);
    core = new THREE.Mesh(coreGeometry, coreMaterial);
    orbGroup.add(core);

    // --- 2. الغلاف الشبكي (Wireframe Shell) ---
    const shellMaterial = new THREE.MeshBasicMaterial({ 
        color: darkThemeColors.wireframe, 
        wireframe: true, 
        transparent: true, 
        opacity: 0.15 
    });
    const shellGeometry = new THREE.IcosahedronGeometry(2.8, 2); 
    wireframeShell = new THREE.Mesh(shellGeometry, shellMaterial);
    orbGroup.add(wireframeShell);

    // --- 3. الحلقات (Rings) ---
    const ringMaterial = new THREE.MeshStandardMaterial({ 
        color: darkThemeColors.rings, 
        side: THREE.DoubleSide, 
        transparent: true, 
        opacity: 0.7,
        roughness: 0.8,
        metalness: 0.1
    });

    // الحلقة 1 (أفقية)
    const ring1Geometry = new THREE.TorusGeometry(3.5, 0.03, 16, 100); 
    ring1 = new THREE.Mesh(ring1Geometry, ringMaterial.clone()); // استنساخ المادة لتغيير اللون بشكل مستقل
    ring1.rotation.x = Math.PI / 2;
    orbGroup.add(ring1);

    // الحلقة 2 (مائلة)
    const ring2Geometry = new THREE.TorusGeometry(3.2, 0.03, 16, 100); 
    ring2 = new THREE.Mesh(ring2Geometry, ringMaterial.clone()); // استنساخ المادة
    ring2.rotation.x = Math.PI / 2;
    ring2.rotation.y = Math.PI / 3;
    orbGroup.add(ring2);

    // --- ضوء يصدر من الكرة ---
    const orbLight = new THREE.PointLight(darkThemeColors.light, 1.0, 20);
    core.add(orbLight); // جعل الضوء يتبع الكرة

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

    // --- حركة أساسية (دائماً تعمل) ---
    orbGroup.position.y = Math.sin(time * 0.0005) * 0.1; // طفو بطيء
    orbGroup.rotation.y += 0.0005; // دوران بطيء للمجموعة كلها
    wireframeShell.rotation.y += 0.002; // دوران أسرع للغلاف
    wireframeShell.rotation.x += 0.001;
    ring1.rotation.z += 0.004;
    ring2.rotation.z -= 0.002;

    // --- متغيرات الأنيميشن حسب الحالة ---
    let corePulse = 1.0;
    let shellOpacity = 0.15;
    let ringOpacity = 0.7;

    if (isSpeaking3D) {
        // --- حالة التحدث (نبض قوي) ---
        corePulse = 1.0 + Math.abs(Math.sin(time * 0.03) * 0.3);
        shellOpacity = 0.3; // أوضح
        ringOpacity = 1.0;  // أوضح
    } else if (isListening) {
        // --- حالة الاستماع (نبض خافت وبطيء) ---
        corePulse = 1.0 + Math.abs(Math.sin(time * 0.01) * 0.1);
        shellOpacity = 0.25;
    }

    // --- تطبيق التغييرات بسلاسة (Lerp) ---
    core.scale.x += (corePulse - core.scale.x) * 0.1;
    core.scale.y += (corePulse - core.scale.y) * 0.1;
    core.scale.z += (corePulse - core.scale.z) * 0.1;
    
    wireframeShell.material.opacity += (shellOpacity - wireframeShell.material.opacity) * 0.1;
    ring1.material.opacity += (ringOpacity - ring1.material.opacity) * 0.1;
    ring2.material.opacity += (ringOpacity - ring2.material.opacity) * 0.1;

    renderer.render(scene, camera);
}

// --- API, Speech Rec, & Core Logic ---
const API_KEY = "AIzaSyAJL7VXQzmJzhA32kQBD7_RSA5qjGYC3Wo"; // الرجاء استخدام مفتاحك الخاص
const GENERATE_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${API_KEY}`;
const TTS_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=${API_KEY}`;
const systemPrompt = "أنتِ مساعدة صوتية مفيدة. أجيبي بإيجاز ووضوح باللغة العربية.";
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isListening = false; // هذا المتغير مستخدم الآن في 'animate'
let currentAudio = null;

/**
 * A robust fetch function with exponential backoff retry mechanism.
 */
async function fetchWithRetry(url, options, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (response.status === 429 || (response.status >= 500 && response.status < 600)) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response;
        } catch (error) {
            if (i === retries - 1) throw error;
            console.log(`Attempt ${i + 1} failed. Retrying in ${delay / 1000}s...`);
            await new Promise(res => setTimeout(res, delay));
            delay *= 2;
        }
    }
}

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'ar-SA';
    recognition.interimResults = false;
    // --- تحديث isListening بناءً على حالة الميكروفون ---
    recognition.onstart = () => { isListening = true; micButton.classList.add('is-listening'); updateStatus('... أستمع الآن'); };
    recognition.onend = () => { isListening = false; micButton.classList.remove('is-listening'); if (statusEl.innerHTML === '... أستمع الآن') updateStatus('&nbsp;'); };
    recognition.onerror = (e) => console.error('Speech recognition error:', e);
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        addMessageToChat(transcript, 'user');
        getAIResponse(transcript);
    };
} else {
    updateStatus('عذراً، متصفحك لا يدعم التعرف على الصوت.');
    micButton.disabled = true;
}

function setInputsDisabled(disabled) {
    allInputs.forEach(input => input.disabled = disabled);
}

micButton.addEventListener('click', () => {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }
    isSpeaking3D = false;
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleTextInput();
});

function handleTextInput() {
    const prompt = textPromptInput.value.trim();
    if (prompt) {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
        }
        isSpeaking3D = false;
        addMessageToChat(prompt, 'user');
        getAIResponse(prompt);
        textPromptInput.value = '';
    }
}

async function getAIResponse(prompt) {
    updateStatus('... أفكر');
    setInputsDisabled(true);
    isListening = false; // توقف عن أنيميشن الاستماع
    try {
        const response = await fetchWithRetry(GENERATE_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                systemInstruction: { parts: [{ text: systemPrompt }] },
            })
        });
        if (!response.ok) throw new Error(`API error: ${response.status} ${response.statusText}`);
        const result = await response.json();
        const text = result.candidates?.[0]?.content?.parts?.[0]?.text;
        if (text) {
            addMessageToChat(text, 'assistant');
            await speakWithGeminiTTS(text);
        } else throw new Error('No content in API response');
    } catch (e) {
        console.error("Error calling Gemini API:", e);
        let errorMessage = `عذراً، حدث خطأ: ${e.message}.`;
        if (e.message.includes('429')) {
            errorMessage = "عذراً، لقد تجاوزت حد الطلبات. الرجاء الانتظار قليلاً ثم المحاولة مرة أخرى.";
        }
        addMessageToChat(errorMessage, 'assistant');
    } finally {
        updateStatus('الرجاء الانتظار قليلاً...');
        setTimeout(() => {
            setInputsDisabled(false);
            updateStatus('&nbsp;');
        }, 3000); // 3-second cooldown
    }
}

async function speakWithGeminiTTS(text) {
    return new Promise(async (resolve, reject) => {
        updateStatus('... أقوم بتركيب الصوت');
        try {
            const response = await fetchWithRetry(TTS_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "gemini-2.5-flash-preview-tts",
                    contents: [{ parts: [{ text: text }] }],
                    generationConfig: {
                        responseModalities: ["AUDIO"],
                        speechConfig: {
                            voiceConfig: {
                                prebuiltVoiceConfig: { voiceName: "Kore" }
                            }
                        }
                    },
                })
            });
            if (!response.ok) throw new Error(`TTS API error: ${response.statusText}`);
            const result = await response.json();
            const audioData = result.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
            const mimeType = result.candidates?.[0]?.content?.parts?.[0]?.inlineData?.mimeType;
            if (audioData && mimeType?.startsWith("audio/")) {
                const sampleRate = parseInt(mimeType.match(/rate=(\d+)/)[1], 10);
                const wavBlob = pcmToWav(new Int16Array(base64ToArrayBuffer(audioData)), sampleRate);
                
                currentAudio = new Audio(URL.createObjectURL(wavBlob));
                currentAudio.onplay = () => { updateStatus('... أتحدث'); isSpeaking3D = true; };
                currentAudio.onended = () => { 
                    isSpeaking3D = false;
                    resolve(); 
                };
                currentAudio.onerror = (e) => reject(e);
                currentAudio.play();
            } else { throw new Error('No audio data in TTS response.'); }
        } catch (error) {
            console.error("Error calling Gemini TTS API:", error);
            addMessageToChat("عذرًا، حدث خطأ في الصوت.", 'assistant');
            isSpeaking3D = false;
            reject(error);
        }
    });
}

function updateStatus(text) { statusEl.innerHTML = text; }

function addMessageToChat(text, sender) {
    const chatHistoryContent = chatContainer.querySelector('.flex.flex-col.space-y-4');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = `flex justify-${sender === 'user' ? 'end' : 'start'}`;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.textContent = text;
    
    messageWrapper.appendChild(bubble);
    
    chatHistoryContent.appendChild(messageWrapper);
    chatContainer.scrollTop = chatContainer.scrollHeight;
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

// --- تشغيل الكود الأساسي ---
initThreeJS();
animate();

// --- إضافة مستمع الحدث لزر تبديل الوضع (جديد) ---
themeToggleButton.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    
    const isLightMode = document.body.classList.contains('light-mode');
    
    // تحديد الألوان بناءً على الوضع
    const colors = isLightMode ? lightThemeColors : darkThemeColors;
    
    // تبديل الأيقونات
    themeIconSun.classList.toggle('hidden', isLightMode);
    themeIconMoon.classList.toggle('hidden', !isLightMode);
    
    // تحديث ألوان مجسم الـ 3D
    core.material.color.set(colors.core);
    wireframeShell.material.color.set(colors.wireframe);
    ring1.material.color.set(colors.rings);
    ring2.material.color.set(colors.rings);
    
    // تحديث لون الضوء (نبحث عنه داخل الكرة)
    core.children.find(child => child.isPointLight).color.set(colors.light);
});