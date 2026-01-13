import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("❌ API Key is missing in Streamlit Secrets!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= FULL CSS CUSTOMIZATION =================
st.markdown("""
    <style>
    /* Clean UI: Hide default Streamlit elements */
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    
    /* Remove empty spaces */
    div[data-testid="stVerticalBlock"] > div:empty {display: none !important;}
    
    /* Fix Chat Input and make space for Mic */
    div[data-testid="stChatInput"] { 
        margin-left: 65px !important; 
        z-index: 1000;
    }

    /* PERMANENT MIC BUTTON: Exactly 3cm (approx 15-20px) from bottom */
    .mic-container { 
        position: fixed; 
        bottom: 18px; /* Lowered as per 3cm request */
        left: 18px; 
        z-index: 9999 !important; 
    }

    /* Circular Mic Styling like the Plus Icon */
    .mic-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        border: 2px solid white !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Menu Card Styling */
    .menu-card { 
        background-color: #121212; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #FF4B4B; 
        margin-bottom: 20px; 
    }
    
    /* Audio player styling */
    .stAudio {
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state: 
    st.session_state.messages = []
if "last_audio_id" not in st.session_state: 
    st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: 
    st.session_state.last_audio_content = None
if "show_menu" not in st.session_state: 
    st.session_state.show_menu = False

st.title("🚀 Pro AI")

# ================= MENU LOGIC =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 About Pro AI")
    st.write("Professional Multimodal AI Assistant using Llama 3.3 and Whisper.")
    st.subheader("🔒 Privacy Policy")
    st.write("No data storage. Your conversations are private and session-based.")
    st.subheader("⚖️ Terms & Conditions")
    st.write("Use ethically. Verified AI responses for critical tasks.")
    st.divider()
    
    # Feedback System
    st.subheader("📬 GitHub Feedback")
    feedback_text = st.text_area("App kaisa laga? Sujhav likhein:")
    if st.button("Submit Feedback"):
        try:
            token = st.secrets["GITHUB_TOKEN"]
            repo = st.secrets["GITHUB_REPO"]
            res = requests.post(
                f"https://api.github.com/repos/{repo}/issues",
                json={"title": "User Feedback", "body": feedback_text},
                headers={"Authorization": f"token {token}"}
            )
            if res.status_code == 201: st.success("Feedback sent!")
        except: st.error("Feedback link error.")

    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio_content = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= DISPLAY CHAT =================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ================= PERMANENT MIC BUTTON =================
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
# Fixed key for permanent presence
audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='pro_mic_recorder')
st.markdown('</div>', unsafe_allow_html=True)

user_query = st.chat_input("Ask me anything...")

# ================= VOICE PROCESSING (BUG FIXED) =================
if audio:
    # Strict ID check: Sirf tab reply dega jab NAYA audio milega
    if st.session_state.last_audio_id != audio['id']:
        st.session_state.last_audio_id = audio['id']
        
        with st.spinner("🎙️ Listening..."):
            try:
                # Transcription using Whisper Large V3
                transcription = client.audio.transcriptions.create(
                    file=("voice.wav", audio['bytes']),
                    model="whisper-large-v3",
                    response_format="text"
                )
                
                # Filter: Agar aawaz 3 shabd se kam hai toh reply mat do (Prevents ghost replies)
                if transcription and len(transcription.strip().split()) >= 1:
                    user_query = transcription
                else:
                    user_query = None # Khali aawaz pe AI trigger nahi hoga
            except Exception as e:
                st.error(f"Whisper Error: {e}")
                user_query = None

# ================= RESPONSE GENERATION =================
if user_query:
    # Internal Time/Date for AI Context (Not for showing every time)
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    current_ts = now.strftime("%I:%M %p, %d %b %Y")

    # Add User Message to State
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    try:
        with st.chat_message("assistant"):
            full_response = ""
            response_box = st.empty()
            
            # System Instructions: No unwanted time/date mentions
            system_prompt = (
                "You are Pro AI, a helpful assistant. "
                "Respond in a natural Hindi-English mix (Hinglish). "
                "CRITICAL: Do not mention the current time or date in your response unless specifically asked. "
                f"Context (for internal use only): {current_ts}"
            )

            # Llama 3.3 70B Stream
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_box.markdown(full_response + "▌")
            
            response_box.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # TEXT TO SPEECH (gTTS)
            with st.spinner("🔊 Generating audio..."):
                tts = gTTS(text=full_response, lang='hi', tld='com.au')
                tts.save("response.mp3")
                with open("response.mp3", "rb") as f:
                    st.session_state.last_audio_content = f.read()
            
            st.rerun() # Refresh to show Hear Jawab button

    except Exception as e:
        st.error(f"AI Error: {e}")

# ================= AUDIO OUTPUT =================
if st.session_state.last_audio_content:
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
        
