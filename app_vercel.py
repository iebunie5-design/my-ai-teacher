import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# [stlite 전용 설정] 브라우저 웹 앱용 설정
st.set_page_config(
    page_title="My AI Teacher - Vercel",
    page_icon="🎓",
    layout="centered"
)

# [UI 디자인] 모던 메신저 스타일 적용
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
    [data-testid="stAppViewContainer"] { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    .app-header { text-align: center; padding: 2rem 0; border-bottom: 1px solid #f1f5f9; margin-bottom: 2rem; }
    .app-header h1 { font-family: 'Outfit', sans-serif; font-size: 1.8rem; color: #0f172a; margin: 0; }
    [data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    .stChatInputContainer { border-radius: 16px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; }
    </style>
    <div class="app-header">
        <h1>🎓 My AI Teacher</h1>
        <p>Vercel / stlite Edition</p>
    </div>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_session" not in st.session_state: st.session_state.chat_session = None

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    level = st.selectbox("Your Level", ["초급", "중급", "고급"])
    topic = st.selectbox("Topic", ["자기소개", "여행", "쇼핑", "음식점", "직장생활"])
    if st.button("🔄 Start New Session"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

# TTS 함수
def text_to_speech(text):
    main_text = text.split('\n')[0]
    try:
        tts = gTTS(text=main_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except: return None

if not api_key:
    st.info("사이드바에 Gemini API Key를 입력해주세요.")
    st.stop()

genai.configure(api_key=api_key)

# 페르소나 설정
def get_system_prompt(level, topic):
    return f"You are a friendly English teacher. Student: {level}, Topic: {topic}. Provide grammar corrections using '💡 Correction' and end with a question."

# 메시지 엔진 시작
if st.session_state.chat_session is None:
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        st.session_state.chat_session = model.start_chat(history=[])
        init_res = st.session_state.chat_session.send_message(f"System: {get_system_prompt(level, topic)}")
        st.session_state.messages = [{"role": "assistant", "content": init_res.text}]
    except Exception as e:
        st.error(f"Error: {e}")

# 대화 내용 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            audio_fp = text_to_speech(msg["content"])
            if audio_fp: st.audio(audio_fp, format="audio/mp3")

# 사용자 입력 처리
text_input = st.chat_input("Say something to your AI Teacher...")
if text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    with st.chat_message("assistant"):
        res = st.session_state.chat_session.send_message(text_input)
        st.markdown(res.text)
        audio_fp = text_to_speech(res.text)
        if audio_fp: st.audio(audio_fp, format="audio/mp3")
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()
