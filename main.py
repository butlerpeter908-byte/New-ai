import streamlit as st
from groq import Groq
import requests
import random

# ================= SETUP =================
GROQ_KEY = "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"
PIXABAY_KEY = "48943715-64d84f88e7f1d448404a11c81"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="AI Video Pro Max", layout="wide")

# Session State for History
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= SIDEBAR MENU =================
with st.sidebar:
    st.title("⚙️ Menu Options")
    
    # 1. Clear History Button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # 2. Privacy & Terms (Expander)
    with st.expander("📄 Privacy Policy"):
        st.write("Aapka data safe hai. Hum koi bhi personal info save nahi karte.")
        
    with st.expander("⚖️ Terms & Conditions"):
        st.write("Ye AI educational purpose ke liye hai. Inappropriate content generate na karein.")
        
    st.markdown("---")
    
    # 3. Creator Info
    st.info("👤 **Created By:** [Aapka Naam]") # Yahan apna naam likh lena bhai
    st.write("Version: 2.0 (Stable)")

# ================= UI CSS =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 2rem; background-color: #0E1117;}
    .stVideo {border: 3px solid #FFD700; border-radius:15px;}
</style>
""", unsafe_allow_html=True)

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

# ================= MAIN APP =================
st.title("🎬 Pro AI Video Engine")

# Display History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

u_input = st.chat_input("Prompt: 'Rainy Mumbai', 'Fast Car'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        # System instructions to prevent code output
        try:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "system", "content": "Never output code. Speak naturally in Hindi/English."},
                          {"role": "user", "content": u_input}]
            )
            reply = res.choices[0].message.content
        except:
            reply = "Bhai, main process kar raha hoon..."
        
        st.write(reply)
        
        # Video Search
        v_url = get_video(u_input)
        if v_url:
            st.video(v_url)
            st.session_state.messages.append({"role": "assistant", "content": reply, "v_url": v_url})
        else:
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
    st.rerun()
    
