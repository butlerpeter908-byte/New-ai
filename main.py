import streamlit as st
from groq import Groq
import requests
import random
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
PIXABAY_KEY = "48943715-64d84f88e7f1d448404a11c81" # Fresh High-Speed Key
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Ultimate AI Video", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI (FIXED TINY YELLOW) =================
st.markdown("""
<style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; background-color: #0E1117;}
    
    /* Smallest Plus Button */
    .stFileUploader {
        position: fixed; bottom: 35px; left: 10px;
        width: 32px !important; height: 32px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 32px !important;
        background-color: #FFD700 !important; border-radius: 50% !important; border: none !important;
    }
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 18px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 32px;
    }
</style>
""", unsafe_allow_html=True)

# ================= NEW VIDEO LOGIC =================
def fetch_ai_video(query):
    # Engine: Pixabay Global API (Super Fast)
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={query.replace(' ', '+')}&per_page=3"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['hits']:
            # Sabse best quality medium size video lena
            return data['hits'][0]['videos']['medium']['url']
    except:
        return None
    return None

# ================= MAIN APP =================
st.title("🎥 Next-Gen AI Video")

# History Loop
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m:
            st.video(m["v_url"])

# Input Controls
st.file_uploader("", type=["png", "jpg", "mp4"], key="ultra_fix")
u_input = st.chat_input("Prompt: 'Cyberpunk Mumbai', 'Nature', 'Space'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"):
        st.markdown(u_input)
    
    with st.chat_message("assistant"):
        if any(x in u_input.lower() for x in ["video", "generate", "banao"]):
            with st.spinner("🚀 Searching Global AI Nodes..."):
                v_url = fetch_ai_video(u_input)
                if v_url:
                    st.video(v_url)
                    st.session_state.messages.append({"role": "assistant", "content": "Bhai, ye video 100% chalegi!", "v_url": v_url})
                else:
                    st.error("Bhai, koi video nahi mili. Thoda simple prompt try karo!")
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            reply = res.choices[0].message.content
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
    
