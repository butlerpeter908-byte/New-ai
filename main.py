import streamlit as st
from groq import Groq
import random
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq Connection Failed!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= UI CSS (DARKEST THEME) =================
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

# ================= HYBRID VIDEO ENGINE (No Token Required) =================
def generate_fail_safe_video(prompt):
    seed = random.randint(1, 1000000)
    clean_prompt = prompt.replace(" ", "%20")
    
    # Ye URL direct cloud server se video render karta hai bina kisi token ke
    video_url = f"https://pollinations.ai/p/{clean_prompt}?width=576&height=320&seed={seed}&model=video"
    
    return video_url

# ================= MAIN APP FLOW =================
if "messages" not in st.session_state: 
    st.session_state.messages = []

st.title("🚀 Pro AI")

# Sidebar and Mic Logic
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="ultra_v1")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='ultra_mic_v1')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me or say 'Create video of...'")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    low_input = u_input.lower()

    if "video" in low_input or "banao" in low_input:
        with st.chat_message("assistant"):
            with st.spinner("⚡ Connecting to High-Speed Video Server..."):
                v_url = generate_fail_safe_video(u_input)
                # Video ko direct render karne ke liye thoda buffer
                time.sleep(2) 
                st.video(v_url)
                st.success("✅ Video Streamed Successfully!")
                st.session_state.messages.append({"role": "assistant", "content": "Video generated using Pro-Speed Server."})
                
    elif any(x in low_input for x in ["image", "photo", "picture"]):
        with st.chat_message("assistant"):
            with st.spinner("🎨 Painting your imagination..."):
                img_url = f"https://image.pollinations.ai/prompt/{u_input.replace(' ','%20')}?nologo=true&seed={random.randint(1,999)}"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": "Image ready!"})
    
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
            
