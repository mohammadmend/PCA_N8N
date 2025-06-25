import streamlit as st
import time
from datetime import datetime
import base64
import os
import requests
import uuid
#N8N_URL = "https://mohammadmend.app.n8n.cloud/webhook-test/pca-chat"
N8N_URL="https://mohammadmend.app.n8n.cloud/webhook/pca-chat"

# Page configuration
st.set_page_config(
    page_title="Ag Chat",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Force light theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #9b7bb8;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .logo-image {
        width: 60px;
        height: 60px;
        object-fit: contain;
    }
    
    .logo-text {
        font-size: 2.5rem;
        font-weight: bold;
        color: #9b7bb8;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    
    .user-message {
        margin-left: 0;
        margin-right: 2rem;
        max-width: 70%;
    }
    
    .bot-message {
        margin-right: 2rem;
        margin-left: 0;
        max-width: 70%;
    }
    
    .message-time {
        font-size: 0.7rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Hardcoded responses for the chatbot
BOT_RESPONSES = {
    "hello": "Hello! How can I help you?",
    "hi": "Hi there! What can I do for you?",
    "how are you": "I'm doing well, thanks for asking!",
    "what can you do": "I'm a simple chatbot. I can respond to basic greetings and questions.",
    "help": "I'm here to help! Just type your message and I'll respond.",
    "bye": "Goodbye! Have a great day!",
    "thanks": "You're welcome!",
    "thank you": "You're welcome!",
    "default": "I'm a simple chatbot. I can respond to basic greetings and questions."
}
def ask_n8n(session_id: str, text: str) -> str:
    payload = {"sessionId": session_id, "text": text}
    try:
        r = requests.post(N8N_URL, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return (
            data.get("answer")           # preferred
            or data.get("output")        # current n8n field
            or "No answer field in response."
        )
    except Exception as exc:
        return f"Error contacting the assistant: {exc}"


def get_logo_base64():
    """Load logo image and return as base64 string"""
    logo_path = "ag.png"
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string
    else:
        # Return a simple placeholder if logo doesn't exist
        return ""

def get_bot_response(user_input: str) -> str:
    """Get bot response based on user input"""
    """Forward the message to n8n and return its answer."""
    # ensure we keep a stable session ID per browser tab
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    return ask_n8n(st.session_state.session_id, user_input)

def main():
    # Header with logo
    try:
        st.markdown("""
        <div class="logo-container">
            <img src="data:image/png;base64,{}" class="logo-image" alt="Bonipak Logo">
            <div class="logo-text">Bonipak</div>
        </div>
        """.format(get_logo_base64()), unsafe_allow_html=True)
    except:
        # Fallback to text only if logo fails to load
        st.markdown('<h1 class="main-header">🌱 Bonipak</h1>', unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            # Get icon with default fallback for older messages
            icon = message.get("icon", "💬")  # Default icon if not present
            with st.chat_message(message["role"], avatar=icon):
                st.markdown(f"""
                <div class="chat-message {'user-message' if message['role'] == 'user' else 'bot-message'}">
                    <div>
                        <strong>{'You' if message['role'] == 'user' else 'ChatBot'}</strong>
                        <p>{message['content']}</p>
                        <div class="message-time">{message['timestamp']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt, 
            "timestamp": timestamp,
            "icon": "👤",
        })
        
        # Get bot response
        bot_response = get_bot_response(prompt)
        
        # Add bot response to chat history
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": bot_response, 
            "timestamp": timestamp,
            "icon": "🧑‍🌾",
        })
        
        # Rerun to display new messages
        st.rerun()
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("## 💡 Chat Tips")
        st.markdown("""
        Try asking me:
        - "Hello" or "Hi"
        - "How are you?"
        - "What can you do?"
        - "Help"
        - "Bye"
        """)
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main() 
