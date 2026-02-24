import streamlit as st
from groq import Groq
import requests
import time
import urllib.parse
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
HF_TOKEN = "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" 

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq API Connection Failed!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= UI CSS (GEMINI DARK THEME) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }

    /* Yellow Plus Icon */
    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 40px !important; height: 40px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important; width: 40px !important; height: 40px !important;
    }
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 24px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }

    /* Mic Button */
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= SMART MEDIA ENGINE =================
def generate_media(prompt, mode="image"):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Using the most stable Models available today
    if mode == "video":
        API_URL = "https://api-inference.huggingface.co/models/guoyww/AnimateDiff"
        msg = "🎬 Searching Video Servers..."
    else:
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        msg = "🖼️ Creating Magic Image..."

    try:
        with st.status(msg, expanded=True) as s:
            resp = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            if resp.status_code == 200:
                s.update(label="✅ Success!", state="complete")
                return resp.content
            elif resp.status_code == 503:
                s.write("⏳ AI is waking up... wait 10s")
                time.sleep(10)
                resp = requests.post(API_URL, headers=headers, json={"inputs": prompt})
                if resp.status_code == 200: return resp.content
            
            return f"busy_{resp.status_code}"
    except:
        return "error"

# ================= APP FLOW =================
if "messages" not in st.session_state: st.session_state.messages = []
st.title("🚀 Pro AI")

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="ultimate_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='ultimate_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me, or say 'Generate image of...'")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    low_input = u_input.lower()
    
    # --- VIDEO LOGIC (WITH FALLBACK) ---
    if "video" in low_input:
        res = generate_media(u_input, mode="video")
        if isinstance(res, bytes):
            st.video(res)
        else:
            st.warning("⚠️ Video servers are overloaded right now. Try an Image instead?")
            search_query = urllib.parse.quote(u_input)
            st.markdown(f"🔍 [Click here to see real videos of '{u_input}' on YouTube](https://www.youtube.com/results?search_query={search_query})")

    # --- IMAGE LOGIC (HIGH STABILITY) ---
    elif any(x in low_input for x in ["image", "photo", "picture", "banao"]):
        res = generate_media(u_input, mode="image")
        if isinstance(res, bytes):
            st.image(res)
        else:
            st.error("❌ Even image servers are tired. Please try again in a few minutes.")

    # --- SMART CHAT ---
    else:
        with st.chat_message("assistant"):
            full_res = ""
            box = st.empty()
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": u_input}],
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    box.markdown(full_res + "▌")
            box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
                      
