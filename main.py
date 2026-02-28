import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from PIL import Image

# ================= CREDENTIALS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"

client = Groq(api_key=GROQ_KEY)
st.set_page_config(page_title="New AI 🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UTILITY FUNCTIONS =================
def send_feedback_email(user_msg):
    try:
        msg = MIMEText(f"New Feedback Received:\n\n{user_msg}")
        msg['Subject'] = 'New AI - User Feedback'
        msg['From'] = MY_GMAIL
        msg['To'] = MY_GMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_GMAIL, APP_PASS)
            server.send_message(msg)
        return True
    except: return False

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# ================= UI CUSTOMIZATION =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    .user-bubble { background-color: #005c4b; color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px; margin: 10px 0; max-width: 80%; float: right; clear: both; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); }
    .ai-bubble { background-color: #202c33; color: white; padding: 12px 18px; border-radius: 18px 18px 18px 0; margin: 10px 0; max-width: 80%; float: left; clear: both; border-left: 5px solid #FFD700; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); }
    .stButton>button { border-radius: 20px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR MENU (ALL FEATURES) =================
with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.selectbox("Navigate", ["Chat", "About Creator", "Feedback", "Privacy & Terms"])
    
    if menu == "About Creator":
        st.info("👤 **Creator:** Butler Peter\n\nVision: Smart, Visual & Fast AI.")
    elif menu == "Feedback":
        f_msg = st.text_area("Humein batayein:")
        if st.button("Submit to Gmail"):
            if send_feedback_email(f_msg): st.success(f"Sent to {MY_GMAIL}!")
            else: st.error("Email setup error.")
    elif menu == "Privacy & Terms":
        st.write("🔒 **Privacy:** Data encrypted.\n⚖️ **Terms:** Powered by Groq Llama 3.2 Vision.")
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ================= MAIN CHAT AREA =================
st.title("🤖 New AI")
curr_info = f"Date: {datetime.now().strftime('%A, %b %d, %Y')} | Time: {datetime.now().strftime('%I:%M %p')}"

# Display Chat History
for i, m in enumerate(st.session_state.messages):
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)
    if m["role"] == "assistant":
        if st.button(f"🔊 Listen", key=f"voice_{i}"):
            tts = gTTS(text=m["content"], lang='hi', tld='co.in')
            fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)

# ================= PHOTO UPLOAD (VISION) =================
st.markdown("---")
uploaded_file = st.file_uploader("📸 Upload Photo for Solution", type=["jpg", "png", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, width=250)
    if st.button("🔍 Analyze Photo"):
        try:
            base64_img = encode_image(uploaded_file)
            # Latest vision model added
            response = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[{"role": "user", "content": [{"type": "text", "text": "Solve or describe this image."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
            )
            st.session_state.messages.append({"role": "user", "content": "Analyzing photo..."})
            st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
            st.rerun()
        except Exception as e: st.error(f"Vision Error: {e}")

# ================= TEXT INPUT (INSTANT) =================
u_input = st.chat_input("Ask New AI anything...")
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    st.rerun() # Refresh for instant visibility

# AI Logic
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Processing..."):
        try:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"New AI 🤖. {curr_info}. No code replies."}, {"role": "user", "content": st.session_state.messages[-1]["content"]}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")
    
