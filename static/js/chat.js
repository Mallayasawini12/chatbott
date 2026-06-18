document.addEventListener('DOMContentLoaded', () => {
    // --- STATE VARIABLES ---
    let ttsEnabled = localStorage.getItem('tts_enabled') === 'true';
    let recognition = null;
    let isRecording = false;

    // --- DOM ELEMENTS ---
    const menuItems = document.querySelectorAll('.menu-item');
    const panels = document.querySelectorAll('.workspace-panel');
    
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-message-input');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const ttsToggleBtn = document.getElementById('tts-toggle-btn');
    const voiceInputBtn = document.getElementById('voice-input-btn');
    
    const dropZone = document.getElementById('drop-zone');
    const resumeFileInput = document.getElementById('resume-file-input');
    const browseFilesBtn = document.getElementById('browse-files-btn');
    const fileNameDisplay = document.getElementById('file-name-display');
    const analyzerLoading = document.getElementById('analyzer-loading');
    const analyzerResult = document.getElementById('analyzer-result');

    // --- TAB SYSTEM INITIALIZATION ---
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetId = item.getAttribute('data-target');
            
            // Toggle active menu item
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            // Toggle active panel
            panels.forEach(p => p.classList.remove('active-panel'));
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active-panel');
            }
            
            // Auto scroll chat if chat is clicked
            if (targetId === 'chat-panel') {
                scrollToBottom();
            }
        });
    });

    // --- TEXT FORMATTER (MARKDOWN-TO-HTML) ---
    function formatMessageText(text) {
        let html = text;
        
        // 1. Headers (### Title)
        html = html.replace(/^### (.*?)$/gm, '<h4 class="msg-header">$1</h4>');
        
        // 2. Bold (**text**)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // 3. Bullet points (* item or - item)
        // Group lists together
        html = html.replace(/^\s*[-*]\s+(.*?)$/gm, '<li>$1</li>');
        // Wrap contiguous list items in <ul>
        html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
        
        // 4. Links ([text](url))
        html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1 <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 0.75rem;"></i></a>');
        
        // 5. Linebreaks
        html = html.replace(/\n/g, '<br>');
        // Fix duplicate linebreaks around list structures
        html = html.replace(/<\/ul><br>/g, '</ul>');
        html = html.replace(/<br><ul>/g, '<ul>');
        
        return html;
    }

    // --- SPEECH SYNTHESIS (TTS) ---
    function speakText(text) {
        if ('speechSynthesis' in window) {
            // Cancel active speech
            window.speechSynthesis.cancel();
            
            // Strip markdown notations and HTML before speaking
            const cleanText = text.replace(/[*#_\-\[\]\(\)]/g, '')
                                  .replace(/<[^>]*>/g, '');
                                  
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            
            window.speechSynthesis.speak(utterance);
        }
    }

    // Toggle TTS
    function updateTTSButton() {
        if (ttsEnabled) {
            ttsToggleBtn.classList.add('btn-primary');
            ttsToggleBtn.querySelector('span').innerText = "TTS: On";
        } else {
            ttsToggleBtn.classList.remove('btn-primary');
            ttsToggleBtn.querySelector('span').innerText = "TTS: Off";
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        }
    }

    ttsToggleBtn.addEventListener('click', () => {
        ttsEnabled = !ttsEnabled;
        localStorage.setItem('tts_enabled', ttsEnabled);
        updateTTSButton();
    });
    updateTTSButton();

    // Add Speak button dynamically to message bubbles
    function addListenButton(bubbleElement, rawText) {
        const listenBtn = document.createElement('button');
        listenBtn.className = 'audio-btn';
        listenBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Listen';
        listenBtn.addEventListener('click', () => speakText(rawText));
        bubbleElement.appendChild(listenBtn);
    }

    // --- CHAT MODULE ---
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendMessage(sender, text, skipFormat = false) {
        const msgWrapper = document.createElement('div');
        msgWrapper.className = sender === 'user' ? 'user-msg-wrapper msg-animate' : 'bot-msg-wrapper msg-animate';
        
        const avatar = document.createElement('div');
        avatar.className = sender === 'user' ? 'user-avatar' : 'bot-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        
        const bubble = document.createElement('div');
        bubble.className = sender === 'user' ? 'message-bubble user-bubble' : 'message-bubble bot-bubble';
        
        if (sender === 'bot' && !skipFormat) {
            bubble.innerHTML = formatMessageText(text);
            addListenButton(bubble, text);
        } else {
            bubble.innerText = text;
        }
        
        msgWrapper.appendChild(avatar);
        msgWrapper.appendChild(bubble);
        chatMessages.appendChild(msgWrapper);
        scrollToBottom();
        
        return msgWrapper;
    }

    // Load Chat History
    async function loadChatHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            if (data.status === 'success' && data.history.length > 0) {
                // Clear initial placeholder greeting
                chatMessages.innerHTML = '';
                data.history.forEach(chat => {
                    appendMessage(chat.sender, chat.message);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    loadChatHistory();

    // Send Message
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Append user message
        appendMessage('user', message);
        chatInput.value = '';
        
        // Create typing placeholder
        const typingWrapper = document.createElement('div');
        typingWrapper.className = 'bot-msg-wrapper msg-animate';
        typingWrapper.innerHTML = `
            <div class="bot-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-bubble bot-bubble">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingWrapper);
        scrollToBottom();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            
            // Remove typing bubble
            typingWrapper.remove();
            
            if (data.status === 'success') {
                appendMessage('bot', data.response);
                if (ttsEnabled) {
                    speakText(data.response);
                }
            } else {
                appendMessage('bot', "Sorry, I encountered an error processing your query. Please try again.");
            }
        } catch (error) {
            typingWrapper.remove();
            appendMessage('bot', "Network error. Please make sure your server is running.");
            console.error('Chat error:', error);
        }
    });

    // Clear Chat
    clearChatBtn.addEventListener('click', async () => {
        if (!confirm("Are you sure you want to clear your conversation history?")) return;
        
        try {
            const response = await fetch('/api/clear_history', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                chatMessages.innerHTML = '';
                // Append default greeting
                appendMessage('bot', "Chat history cleared. How can I help you today?");
            }
        } catch (error) {
            console.error("Error clearing history:", error);
        }
    });

    // --- SPEECH INPUT (STT) ---
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecObj = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecObj();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isRecording = true;
            voiceInputBtn.classList.add('recording-active');
            chatInput.placeholder = "Listening... Speak now...";
        };

        recognition.onend = () => {
            isRecording = false;
            voiceInputBtn.classList.remove('recording-active');
            chatInput.placeholder = "Type your career question here...";
        };

        recognition.onerror = (e) => {
            console.error('Speech recognition error:', e.error);
            isRecording = false;
            voiceInputBtn.classList.remove('recording-active');
        };

        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            chatInput.value = transcript;
            // Submit form automatically
            chatForm.dispatchEvent(new Event('submit'));
        };

        voiceInputBtn.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        voiceInputBtn.style.display = 'none';
        console.warn('Speech recognition not supported in this browser.');
    }

    // --- RESUME UPLOADER MODULE ---
    browseFilesBtn.addEventListener('click', () => resumeFileInput.click());
    
    resumeFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            processFile(e.target.files[0]);
        }
    });

    // Drag-and-drop
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    });

    function processFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext !== 'txt' && ext !== 'pdf') {
            alert('Unsupported file format! Please upload a .txt or .pdf resume.');
            return;
        }
        
        fileNameDisplay.innerText = `Selected File: ${file.name}`;
        uploadResume(file);
    }

    async function uploadResume(file) {
        const formData = new FormData();
        formData.append('resume', file);

        // UI state transitions
        dropZone.classList.add('hidden');
        analyzerResult.classList.add('hidden');
        analyzerLoading.classList.remove('hidden');

        try {
            const response = await fetch('/api/upload_resume', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            analyzerLoading.classList.add('hidden');

            if (data.status === 'success') {
                renderResumeAnalysis(data.analysis);
            } else {
                alert(data.message || 'Error processing resume.');
                dropZone.classList.remove('hidden');
            }
        } catch (error) {
            analyzerLoading.classList.add('hidden');
            dropZone.classList.remove('hidden');
            alert('Network error uploading resume.');
            console.error('Resume upload error:', error);
        }
    }

    function renderResumeAnalysis(analysis) {
        analyzerResult.classList.remove('hidden');
        
        // Update radial progress bar using conic gradient
        const score = analysis.match_score;
        const progressContainer = document.querySelector('.radial-progress-container');
        progressContainer.style.background = `conic-gradient(var(--accent-color) ${score}%, var(--border-glass) ${score}%)`;
        document.getElementById('match-score-val').innerText = `${score}%`;
        
        // Recommended role details
        document.getElementById('recommended-role-title').innerText = analysis.primary_career_title;
        
        // Clean badge containers
        const matchedContainer = document.getElementById('matched-skills-badges');
        const missingContainer = document.getElementById('missing-skills-badges');
        matchedContainer.innerHTML = '';
        missingContainer.innerHTML = '';
        
        // Inject found skills
        if (analysis.matched_skills.length > 0) {
            analysis.matched_skills.forEach(skill => {
                matchedContainer.innerHTML += `<span class="skill-badge skill-matched"><i class="fa-solid fa-square-check"></i> ${skill}</span>`;
            });
        } else {
            matchedContainer.innerHTML = '<span class="text-muted" style="font-size: 0.9rem;">No matching keywords found.</span>';
        }
        
        // Inject missing skills
        if (analysis.missing_skills.length > 0) {
            analysis.missing_skills.forEach(skill => {
                missingContainer.innerHTML += `<span class="skill-badge skill-missing"><i class="fa-solid fa-triangle-exclamation"></i> ${skill}</span>`;
            });
        } else {
            missingContainer.innerHTML = '<span class="text-success" style="font-size: 0.9rem;"><i class="fa-solid fa-check"></i> You have all core keywords!</span>';
        }

        // Render recommended courses
        const coursesList = document.getElementById('recommended-courses-list');
        coursesList.innerHTML = '';
        analysis.recommendations.courses.forEach(course => {
            coursesList.innerHTML += `
                <li><a href="${course.link}" target="_blank">${course.name}</a> (${course.platform})</li>
            `;
        });

        // Render recommended prep tips
        const tipsList = document.getElementById('recommended-tips-list');
        tipsList.innerHTML = '';
        analysis.recommendations.prep_tips.forEach(tip => {
            tipsList.innerHTML += `<li>${tip}</li>`;
        });
    }
});
