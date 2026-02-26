import streamlit as st
from groq import Groq
import requests
import random

# ================= API SETUP =================
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="AI Video Pro", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI CSS (TINY YELLOW) =================
st.markdown("""
<style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 60px !important; }
    .stVideo { border: 2px solid #FFD700; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIC =================
def get_universal_video(query):
    # Pixabay Global Node (Sabse Reliable)
    PIXABAY_KEY = "48943715-64d84f88e7f1d448404a11c81"
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={query.replace(' ', '+')}&per_page=3&safesearch=true"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['hits']:
            return data['hits'][0]['videos']['medium']['url']
    except: return None
    return None

# ================= APP =================
st.title("🎥 Direct AI Video Engine")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

u_input = st.chat_input("Prompt: 'Car', 'Nature', 'City'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        if any(x in u_input.lower() for x in ["video", "generate", "banao"]):
            with st.spinner("Connecting to global nodes..."):
                v_url = get_universal_video(u_input)
                if v_url:
                    st.video(v_url)
                    st.session_state.messages.append({"role": "assistant", "content": "Bhai, ye video load ho gayi!", "v_url": v_url})
                else:
                    st.error("Bhai, server busy hai. Ek baar 'Nature' ya 'Car' jaise simple prompt se test karo!")
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            reply = res.choices[0].message.content
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
    
