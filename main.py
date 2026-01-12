import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import requests # GitHub API ke liye

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

# --- GITHUB CONFIG (Secrets mein daalein) ---
# Streamlit secrets mein ye 3 cheezein zaroor add karein:
# GITHUB_TOKEN = "aapka_personal_access_token"
# GITHUB_REPO = "aapka_username/repo_naam"

st.set_page_config(page_title="Pro AI", layout="wide")

st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 100px;}
    
    /* Menu Button 1cm Up */
    div.stButton > button:first-child { margin-top: -40px !important; }

    div[data-testid="stChatInput"] { margin-left: 50px !important; }
    
    .plus-icon-container {
        position: fixed; bottom: 32px; left: 15px;
        background-color: #FF4B4B; color: white;
        border-radius: 50%; width: 40px; height: 40px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; font-weight: bold; z-index: 1000;
    }

    div[data-testid="stFileUploader"] {
        position: fixed; bottom: 32px; left: 15px;
        width: 40px; height: 40px; opacity: 0; z-index: 1001;
    }

    .menu-card {
        background-color: #121212; padding: 20px;
        border-radius: 15px; border: 1px solid #FF4B4B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

st.title("🚀 Pro AI")
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    
    # --- GITHUB FEEDBACK SECTION ---
    st.subheader("📬 Send Feedback to GitHub")
    feedback_msg = st.text_area("App ke baare mein likhein:", placeholder="Issue ya suggestion...")
    
    if st.button("Submit Feedback"):
        if feedback_msg:
            try:
                # GitHub API Details
                token = st.secrets["GITHUB_TOKEN"]
                repo = st.secrets["GITHUB_REPO"]
                url = f"https://api.github.com/repos/{repo}/issues"
                
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                data = {
                    "title": "New User Feedback",
                    "body": feedback_msg
                }
                
                res = requests.post(url, json=data, headers=headers)
                if res.status_code == 201:
                    st.success("✅ Shukriya! Feedback GitHub Issues mein add ho gaya hai.")
                else:
                    st.error(f"❌ Error: {res.json().get('message')}")
            except Exception as e:
                st.error("Secrets mein GitHub Token setup karein!")
        else:
            st.warning("Kuch toh likhiye!")

    st.divider()
    st.markdown("🔒 **Privacy:** No data saved. | ⚖️ **Terms:** Legal use only.")
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- PLUS ICON & CHAT INPUT ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    # ... (Baaki AI logic same rahega) ...
    try:
        content = [{"type": "text", "text": f"System: Use full words. User: {prompt}"}]
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            st.image(uploaded_file, width=150)

        with st.chat_message("assistant"):
            full_res = ""
            res_box = st.empty()
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": content}], stream=True)
            for chunk in comp:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 listen"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
