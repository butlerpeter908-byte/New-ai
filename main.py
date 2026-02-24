import streamlit as st
from groq import Groq
import requests
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP (KEYS INTEGRATED) =================
GROQ_KEY = "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"
# Bhai, aapki Hugging Face key yahan paste kar di hai
HF_TOKEN = "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" 

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq API Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= PROFESSIONAL UI CSS =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem;}

    /* Input Box Alignment */
    div[data-testid="stChatInput"] { padding-left: 95px !important; }

    /* Yellow Plus Button */
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
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= FREE VIDEO ENGINE (Hugging Face) =================
def generate_free_video(prompt):
    # Zeroscope Model - High Quality Free Text-to-Video
    API_URL = "https://api-inference.huggingface.co/models/cerspense/zeroscope_v2_576w"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        with st.status("🎬 AI is rendering your video (Free)...", expanded=True) as s:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            
            # Model loading (503 error check)
            if response.status_code == 503:
                s.write("⏳ AI Model is warming up... please wait 20 seconds.")
                time.sleep(20)
                response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

            if response.status_code == 200:
                s.update(label="✅ Video Generated!", state="complete")
                return response.content 
            else:
                return f"❌ Error: {response.status_code}. Make sure your token has 'Inference' permission."
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []
st.title("🚀 Pro AI")

# Icons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="pro_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='pro_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Say 'Generate video of a sunset'...")

# ================= PROCESS INPUT =================
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    # Check for Video Request
    if any(word in u_input.lower() for word in ["video", "generate", "banao"]):
        result = generate_free_video(u_input)
        if isinstance(result, bytes):
            st.video(result)
            st.session_state.messages.append({"role": "assistant", "content": "Here is your free video!"})
        else:
            st.error(result)
    else:
        # Normal Smart Chat
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
            
