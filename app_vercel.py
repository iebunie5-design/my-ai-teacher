import streamlit as st
import requests
import json
from gtts import gTTS
import io

# [stlite 전용 설정]
st.set_page_config(
    page_title="My AI Teacher - Vercel",
    page_icon="🎓",
    layout="centered"
)

# [UI 디자인]
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
        <p>Vercel Serverless Edition</p>
    </div>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state: st.session_state.messages = []
if "history" not in st.session_state: st.session_state.history = []

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    level = st.selectbox("Your Level", ["초급", "중급", "고급"])
    topic = st.selectbox("Topic", ["자기소개", "여행", "쇼핑", "음식점", "직장생활"])
    if st.button("🔄 Start New Session"):
        st.session_state.messages = []; st.session_state.history = []; st.rerun()

# [중요] Gemini REST API 호출 함수 (라이브러리 없이 직접 통신)
def call_gemini_api(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # 대화 맥락 유지를 위한 히스토리 구성
    contents = st.session_state.history + [{"role": "user", "parts": [{"text": prompt}]}]
    
    data = {"contents": contents}
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        # 히스토리 업데이트
        st.session_state.history.append({"role": "user", "parts": [{"text": prompt}]})
        st.session_state.history.append({"role": "model", "parts": [{"text": ai_text}]})
        return ai_text
    else:
        return f"Error: {response.text}"

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

# 첫 인사 시작 로직
if not st.session_state.messages:
    system_instruction = f"You are a friendly English teacher. Student: {level}, Topic: {topic}. Provide corrections and end with a question. Start the conversation warmly."
    ai_greeting = call_gemini_api(system_instruction, api_key)
    st.session_state.messages.append({"role": "assistant", "content": ai_greeting})

# 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            audio_fp = text_to_speech(msg["content"])
            if audio_fp: st.audio(audio_fp, format="audio/mp3")

# 입력 처리
text_input = st.chat_input("Say something to your AI Teacher...")
if text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    with st.chat_message("assistant"):
        ai_res = call_gemini_api(text_input, api_key)
        st.markdown(ai_res)
        audio_fp = text_to_speech(ai_res)
        if audio_fp: st.audio(audio_fp, format="audio/mp3")
        st.session_state.messages.append({"role": "assistant", "content": ai_res})
        st.rerun()
