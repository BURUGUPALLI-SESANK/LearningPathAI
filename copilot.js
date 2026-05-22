// AI Tutor Chatbot - Floating Assistant
(function() {
    'use strict';

    // Create chatbot HTML
    const chatbotHTML = `
        <div id="ai-tutor-container" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
            <!-- Chat Button -->
            <button id="ai-tutor-btn" style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #6366f1, #a855f7);
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <i class="bi bi-chat-dots-fill"></i>
            </button>

            <!-- Chat Window -->
            <div id="ai-tutor-window" style="
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 380px;
                height: 500px;
                background: rgba(9, 13, 22, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                display: none;
                flex-direction: column;
                overflow: hidden;
            ">
                <!-- Header -->
                <div style="
                    background: linear-gradient(135deg, #6366f1, #a855f7);
                    padding: 1rem 1.5rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div>
                        <div style="font-weight: 700; font-size: 1.1rem; color: white;">
                            <i class="bi bi-robot"></i> AI Learning Tutor
                        </div>
                        <div style="font-size: 0.85rem; color: rgba(255,255,255,0.8);">
                            Ask me anything about your learning
                        </div>
                    </div>
                    <button id="ai-tutor-close" style="
                        background: none;
                        border: none;
                        color: white;
                        font-size: 1.5rem;
                        cursor: pointer;
                        padding: 0;
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <i class="bi bi-x"></i>
                    </button>
                </div>

                <!-- Messages Container -->
                <div id="ai-tutor-messages" style="
                    flex: 1;
                    overflow-y: auto;
                    padding: 1.5rem;
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                ">
                    <div class="ai-message" style="
                        background: rgba(99, 102, 241, 0.15);
                        border: 1px solid rgba(99, 102, 241, 0.3);
                        border-radius: 16px;
                        padding: 1rem;
                        color: #e2e8f0;
                        font-size: 0.95rem;
                        line-height: 1.6;
                    ">
                        <strong style="color: #818cf8;">AI Tutor:</strong><br>
                        Hi! I'm your AI learning assistant. I can help you with:
                        <ul style="margin: 0.5rem 0 0 1.5rem; padding: 0;">
                            <li>Explaining concepts</li>
                            <li>Recommending resources</li>
                            <li>Creating study plans</li>
                            <li>Answering questions</li>
                        </ul>
                        What would you like to learn today?
                    </div>
                </div>

                <!-- Input Area -->
                <div style="
                    padding: 1rem 1.5rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    background: rgba(0, 0, 0, 0.3);
                ">
                    <div style="display: flex; gap: 0.75rem;">
                        <input 
                            type="text" 
                            id="ai-tutor-input" 
                            placeholder="Ask me anything..."
                            style="
                                flex: 1;
                                background: rgba(255, 255, 255, 0.05);
                                border: 1px solid rgba(255, 255, 255, 0.1);
                                border-radius: 12px;
                                padding: 0.75rem 1rem;
                                color: #e2e8f0;
                                font-size: 0.95rem;
                                outline: none;
                            "
                        />
                        <button id="ai-tutor-send" style="
                            background: linear-gradient(135deg, #6366f1, #a855f7);
                            border: none;
                            border-radius: 12px;
                            padding: 0.75rem 1.25rem;
                            color: white;
                            font-weight: 600;
                            cursor: pointer;
                            transition: all 0.3s ease;
                        ">
                            <i class="bi bi-send-fill"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Inject chatbot into page
    document.addEventListener('DOMContentLoaded', function() {
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);

        const btn = document.getElementById('ai-tutor-btn');
        const window = document.getElementById('ai-tutor-window');
        const closeBtn = document.getElementById('ai-tutor-close');
        const input = document.getElementById('ai-tutor-input');
        const sendBtn = document.getElementById('ai-tutor-send');
        const messagesContainer = document.getElementById('ai-tutor-messages');

        // Toggle chat window
        btn.addEventListener('click', () => {
            if (window.style.display === 'none' || window.style.display === '') {
                window.style.display = 'flex';
                btn.style.transform = 'scale(0.9)';
                input.focus();
            } else {
                window.style.display = 'none';
                btn.style.transform = 'scale(1)';
            }
        });

        closeBtn.addEventListener('click', () => {
            window.style.display = 'none';
            btn.style.transform = 'scale(1)';
        });

        // Send message
        async function sendMessage() {
            const message = input.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, 'user');
            input.value = '';

            // Show typing indicator
            const typingId = addTypingIndicator();

            try {
                // Get AI response
                const response = await getAIResponse(message);
                removeTypingIndicator(typingId);
                addMessage(response, 'ai');
            } catch (error) {
                removeTypingIndicator(typingId);
                addMessage('Sorry, I encountered an error. Please try again.', 'ai');
            }
        }

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Add message to chat
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = sender === 'user' ? 'user-message' : 'ai-message';
            
            if (sender === 'user') {
                messageDiv.style.cssText = `
                    background: linear-gradient(135deg, #6366f1, #a855f7);
                    border-radius: 16px;
                    padding: 1rem;
                    color: white;
                    font-size: 0.95rem;
                    line-height: 1.6;
                    margin-left: auto;
                    max-width: 80%;
                `;
                messageDiv.innerHTML = `<strong>You:</strong><br>${text}`;
            } else {
                messageDiv.style.cssText = `
                    background: rgba(99, 102, 241, 0.15);
                    border: 1px solid rgba(99, 102, 241, 0.3);
                    border-radius: 16px;
                    padding: 1rem;
                    color: #e2e8f0;
                    font-size: 0.95rem;
                    line-height: 1.6;
                    max-width: 85%;
                `;
                messageDiv.innerHTML = `<strong style="color: #818cf8;">AI Tutor:</strong><br>${text}`;
            }

            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Add typing indicator
        function addTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.style.cssText = `
                background: rgba(99, 102, 241, 0.15);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 16px;
                padding: 1rem;
                color: #818cf8;
                font-size: 0.95rem;
                max-width: 85%;
            `;
            typingDiv.innerHTML = '<i class="bi bi-three-dots"></i> AI is thinking...';
            messagesContainer.appendChild(typingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            return 'typing-indicator';
        }

        // Remove typing indicator
        function removeTypingIndicator(id) {
            const indicator = document.getElementById(id);
            if (indicator) indicator.remove();
        }

        // Get AI response (using OpenRouter API)
        async function getAIResponse(userMessage) {
            try {
                const API_BASE = window.location.hostname === 'localhost' 
                    ? 'http://localhost:5000' 
                    : window.location.origin + '/api';

                const userId = localStorage.getItem('userId');

                const response = await fetch(`${API_BASE}/ai-chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: userMessage,
                        userId: userId
                    })
                });

                const data = await response.json();

                if (data.success) {
                    return data.response;
                } else {
                    throw new Error(data.error || 'Failed to get response');
                }
            } catch (error) {
                console.error('AI Chat error:', error);
                // Fallback responses
                return getFallbackResponse(userMessage);
            }
        }

        // Fallback responses when API is unavailable
        function getFallbackResponse(message) {
            const lowerMessage = message.toLowerCase();

            if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
                return "I'm here to help! You can ask me about:\n• Explaining concepts\n• Recommending courses\n• Creating study plans\n• Tips for learning\n\nWhat specific topic would you like help with?";
            }

            if (lowerMessage.includes('course') || lowerMessage.includes('learn')) {
                return "To find the best courses for you, check out your Learning Path page. I've personalized recommendations based on your skills and goals!";
            }

            if (lowerMessage.includes('progress') || lowerMessage.includes('track')) {
                return "You can track your progress on the Dashboard page. It shows your completed courses, skill levels, and overall progress!";
            }

            if (lowerMessage.includes('quiz') || lowerMessage.includes('test')) {
                return "Great idea! You can take AI-generated quizzes on any course detail page. Just click on a course and go to the Quiz tab!";
            }

            if (lowerMessage.includes('daily') || lowerMessage.includes('task')) {
                return "Check out the Daily Tasks page to break your learning goals into manageable daily tasks. It helps you stay consistent!";
            }

            return "That's an interesting question! While I'm still learning, I recommend checking your Learning Path for personalized recommendations, or visit the Dashboard to track your progress.";
        }
    });
})();
