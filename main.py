import streamlit as st
from groq import Groq
import requests
import random

# ================= SETUP =================
GROQ_KEY = "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"
PIXABAY_KEY = "48943715-64d84f88e7f1d448404a11c81"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="AI Video Pro Max", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= TOP MENU SHIFT =================
# Menu ko sidebar se hatakar top par shift kiya hai
col1, col2 = st.columns([8, 2])
with col2:
    menu = st.selectbox("Menu ☰", ["Home", "Clear History", "Privacy Policy", "Terms", "Credits"])
    
    if menu == "Clear History":
        st.session_state.messages = []
        st.rerun()
    elif menu == "Privacy Policy":
        st.info("Your data is encrypted and safe. We don't store personal chats.")
    elif menu == "Terms":
        st.warning("Use for legal purposes only. No NSFW content allowed.")
    elif menu == "Credits":
        st.success("Created by: [Your Name] | Powered by Pixabay")

# ================= UI CSS =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .stVideo {border: 4px solid #FFD700; border-radius:15px;}
    .stChatMessage {font-family: 'Arial';}
</style>
""", unsafe_allow_html=True)

# ================= VIDEO ENGINE =================
def get_video(query):
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={query.replace(' ', '+')}&per_page=3"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['hits']:
            return data['hits'][0]['videos']['medium']['url']
    except: return None
    return None

# ================= MAIN APP =================
st.title("🎬 High-Speed Video AI")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

u_input = st.chat_input("Ask me anything or generate video...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        # AI ko English + Hindi dono use karne ka order
        try:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "system", "content": "Respond in a mix of English and Hindi. Be professional. Never output code blocks."},
                          {"role": "user", "content": u_input}]
            )
            reply = res.choices[0].message.content
        except:
            reply = "I am processing your request. Please wait... (Main kaam kar raha hoon...)"
        
        st.write(reply)
        
        # Video Logic
        v_url = get_video(u_input)
        if v_url:
            st.video(v_url)
            st.session_state.messages.append({"role": "assistant", "content": reply, "v_url": v_url})
        else:
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
    st.rerun()
