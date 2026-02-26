import streamlit as st
from groq import Groq
import requests
import random

# ================= SETUP =================
GROQ_KEY = "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"
PIXABAY_KEY = "48943715-64d84f88e7f1d448404a11c81"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="AI Video Ultimate", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI =================
st.markdown("<style>.stVideo {border: 2px solid #FFD700; border-radius:10px;}</style>", unsafe_allow_html=True)

# ================= ENGINE =================
def get_video(query):
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={query.replace(' ', '+')}&per_page=3"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data['hits']:
            return data['hits'][0]['videos']['medium']['url']
    except: return None
    return None

# ================= APP =================
st.title("🎥 Fast AI Video Engine")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

u_input = st.chat_input("Prompt likho (e.g. Red Car, Rain, Mumbai)...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        # Sabse pehle reply generate karo taaki blank na rahe
        try:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            reply = res.choices[0].message.content
        except:
            reply = "Bhai, main process kar raha hoon..."
        
        st.write(reply)
        
        # Ab video search karo (Har prompt par)
        v_url = get_video(u_input)
        if v_url:
            st.video(v_url)
            st.session_state.messages.append({"role": "assistant", "content": reply, "v_url": v_url})
        else:
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
    st.rerun()
    
