import streamlit as st
from groq import Groq
import requests
import datetime
import pytz 
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
# Token ko exact format mein rakha hai
REPLICATE_TOKEN = "r8_IAbdjeQkoGq2XmgP9VBN11OpmC1qfAw1IVij9"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq API Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= UI CSS (FIXED POSITIONS) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem;}

    div[data-testid="stChatInput"] { padding-left: 95px !important; }

    /* Yellow Plus Button */
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

    /* Mic Button */
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI")

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="v7_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='v7_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me or say 'Generate video of...'")

# ================= ROBUST VIDEO ENGINE =================
def generate_video_final(prompt):
    # Token ko clean karke bhej rahe hain
    token = REPLICATE_TOKEN.strip()
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
        "User-Agent": "StreamlitApp/1.0"
    }
    
    # Stable Video Model ID
    payload = {
        "version": "a71f032252c416187766b1e6b52c3c662e0868f00d235c249495c2e9b980e03e",
        "input": {"prompt": prompt}
    }
    
    try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions", 
            json=payload, 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 401:
            return "❌ Token Invalid! Replicate dashboard par check karein ki token 'r8_' se start ho raha hai na?"
        
        data = response.json()
        if "urls" in data:
            poll_url = data["urls"]["get"]
            with st.status("🎬 AI Rendering... wait 60s", expanded=True) as s:
                while True:
                    res = requests.get(poll_url, headers=headers).json()
                    if res["status"] == "succeeded":
                        s.update(label="✅ Video Ready!", state="complete")
                        return res["output"]
                    elif res["status"] == "failed":
                        return f"❌ Error: {res.get('error')}"
                    time.sleep(5)
        else:
            return f"❌ API Error: {data.get('detail', 'Unknown error')}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# ================= PROCESS =================
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    if any(x in u_input.lower() for x in ["video", "banao", "generate"]):
        v_url = generate_video_final(u_input)
        if v_url and "http" in str(v_url):
            st.video(v_url)
            st.session_state.messages.append({"role": "assistant", "content": "Video generated!"})
        else:
            st.error(v_url)
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
            
