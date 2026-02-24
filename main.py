import streamlit as st
from groq import Groq
import requests
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
# Hugging Face key yahan hai
HF_TOKEN = "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" 

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= UI CSS (DARK THEME) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }

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

    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= RE-ENGINEERED VIDEO ENGINE =================
def generate_stable_video(prompt):
    # Ab hum ek naya aur fast model try karenge
    API_URL = "https://api-inference.huggingface.co/models/vdo/zeroscope_v2_XL"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        with st.status("🎬 AI is rendering your video... (Hang tight!)", expanded=True) as s:
            # First attempt
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=120)
            
            # Agar model load ho raha ho
            if response.status_code == 503:
                s.write("⏳ Server is warming up... waiting 15s")
                time.sleep(15)
                response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

            if response.status_code == 200:
                s.update(label="✅ Video Generated Successfully!", state="complete")
                return response.content
            else:
                return f"⚠️ Server Busy (Error {response.status_code}). Sabhi log abhi generate kar rahe hain, 1 min baad try karein."
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# ================= MAIN FLOW =================
if "messages" not in st.session_state: st.session_state.messages = []
st.title("🚀 Pro AI")

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="fixed_v1")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='fixed_mic1')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me, or 'Generate video of...'")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    if "video" in u_input.lower():
        video_data = generate_stable_video(u_input)
        if isinstance(video_data, bytes):
            st.video(video_data)
        else:
            st.error(video_data)
    else:
        # Standard Smart Chat
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
            
