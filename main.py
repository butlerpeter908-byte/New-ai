import streamlit as st
from groq import Groq
import requests
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
# Bhai, maine token yahan ekdam fresh paste kiya hai
REPLICATE_TOKEN = "r8_IAbdjeQkoGq2XmgP9VBN11OpmC1qfAw1IVij9"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq API Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= UI CSS (EXACT GEMINI STYLE) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem;}

    div[data-testid="stChatInput"] { padding-left: 95px !important; }

    /* Yellow Plus Button - Fixed inside Input area */
    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 40px !important; height: 40px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important; width: 40px !important; height: 40px !important;
        min-height: 40px !important;
    }
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 24px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }

    /* Mic Button Aligned */
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI")

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="final_fix_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='final_fix_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me or say 'Generate video of...'")

# ================= ENGINE WITH TOKEN CLEANING =================
def generate_video_fixed(prompt):
    # Token ko clean karna zaroori hai (No spaces, exact format)
    clean_token = REPLICATE_TOKEN.strip()
    headers = {
        "Authorization": f"Token {clean_token}",
        "Content-Type": "application/json"
    }
    
    # Text-to-Video Model (Stable Video Diffusion)
    payload = {
        "version": "3f0c272252c416187766b1e6b52c3c662e0868f00d235c249495c2e9b980e03e",
        "input": {"prompt": prompt}
    }
    
    try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions", 
            json=payload, 
            headers=headers
        )
        
        data = response.json()
        if response.status_code == 201 and "urls" in data:
            poll_url = data["urls"]["get"]
            with st.status("🎬 Processing Video...", expanded=True) as s:
                while True:
                    res = requests.get(poll_url, headers=headers).json()
                    if res["status"] == "succeeded":
                        s.update(label="✅ Ready!", state="complete")
                        return res["output"]
                    elif res["status"] == "failed":
                        return f"❌ Failed: {res.get('error', 'Limit reached')}"
                    time.sleep(5)
        else:
            # Yahan detailed error dikhayega agar token abhi bhi reject hua
            detail = data.get('detail', 'Unauthorized')
            return f"❌ API Error: {detail}. Please check if you have added a payment method on Replicate."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ================= PROCESS =================
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    if any(x in u_input.lower() for x in ["video", "banao", "generate"]):
        video_url = generate_video_fixed(u_input)
        if video_url and "http" in str(video_url):
            st.video(video_url)
        else:
            st.error(video_url)
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
            
