import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# [Streamlit 설정] 브라우저 상단 탭의 제목, 아이콘 및 전체 레이아웃을 설정합니다.
st.set_page_config(
    page_title="My AI Teacher",
    page_icon="🎙️",
    layout="centered"
)

# [프리미엄 UI/UX 스타일링] 커스텀 CSS를 주입하여 세련된 디자인을 적용합니다.
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
    /* 기본 배경 및 폰트 설정 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8f9ff 0%, #f1f3f9 100%);
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600 !important;
        color: #1e293b;
    }

    /* 사이드바 스타일링 (Glassmorphism) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* 채팅 버블 공통 스타일 */
    .stChatMessage {
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        background-color: white;
        transition: transform 0.2s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
    }

    /* 버튼 스타일링 */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        border: none;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
        transform: scale(1.02);
    }

    /* 오디오 플레이어 스타일링 */
    audio {
        width: 100%;
        height: 35px;
        border-radius: 10px;
        margin-top: 10px;
    }

    /* 텍스트 입력창 스타일링 */
    .stChatInputContainer {
        border-radius: 25px !important;
        padding: 5px !important;
        background-color: white !important;
        box-shadow: 0 -5px 25px rgba(0,0,0,0.05) !important;
    }
    
    /* 강조 섹션 (Correction, Suggested Answers) */
    .stMarkdown div[data-testid="stMarkdownContainer"] blockquote {
        border-left: 4px solid #6366f1;
        background-color: #f5f3ff;
        padding: 10px 15px;
        border-radius: 0 10px 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# [세션 상태 관리] 사용자의 대화 기록, 채팅 세션 객체, 현재 설정을 페이지 새로고침 시에도 유지합니다.
if "messages" not in st.session_state:
    st.session_state.messages = []  # 전체 대화 이력을 담는 리스트
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None  # Gemini API와의 연결 세션
if "current_config" not in st.session_state:
    st.session_state.current_config = {"level": None, "topic": None}  # 현재 선택된 레벨과 주제 정보

# [사이드바 UI 구성] 왼쪽 설정 창을 정의합니다.
with st.sidebar:
    st.title("⚙️ 설정")
    
    # API 키 입력 (입력 시 비밀번호처럼 마스킹 처리됨)
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        help="[여기서 API 키를 발급받으세요](https://aistudio.google.com/app/apikey)"
    )
    
    # 학습 레벨 및 대화 주제 선택
    level = st.selectbox("나의 영어 레벨", ["초급", "중급", "고급"])
    topic = st.selectbox("회화 주제", ["자기소개", "여행", "쇼핑", "음식점", "직장생활", "자유대화"])
    
    st.markdown("---")
    # AI 답변 시 자동으로 음성을 재생할지 여부 결정
    auto_speak = st.checkbox("AI 답변 자동 읽어주기", value=True)
    
    # 새 대화 시작 버튼: 기존 데이터를 모두 초기화하고 페이지를 다시 로드합니다.
    if st.button("🔄 새 대화 시작"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.current_config = {"level": level, "topic": topic}
        st.rerun()

    st.markdown("---")
    st.markdown("""
    ### 🎙️ 음성 버전 사용법
    1. **마이크 버튼**을 누르고 영어로 말해보세요.
    2. 녹음이 끝나면 자동으로 텍스트로 변환됩니다.
    3. AI 선생님의 답변은 **스피커 아이콘**을 눌러 다시 들을 수 있습니다.
    """)

# [텍스트 음성 변환 함수 (TTS)] 텍스트를 오디오 파일로 변환합니다.
def text_to_speech(text):
    # 💡 교정 이나 🗣️ 다음 질문 섹션을 제외한 순수한 영어 답변 부분만 추출 (첫 번째 단락)
    main_text = text.split('\n')[0]
    try:
        # Google TTS 라이브러리를 사용해 영어(en) 음성 생성
        tts = gTTS(text=main_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception as e:
        st.error(f"음성 생성 중 오류: {e}")
        return None

# 메인 화면 타이틀
st.title("🎙️ 나만의 영어 선생님 (음성 버전)")

# API 키 입력 여부 확인 및 안내
if not api_key:
    st.info("사이드바에 Gemini API Key를 입력하고 시작해주세요! 🔑")
    st.stop()

# [Gemini 설정] API 키 적용
genai.configure(api_key=api_key)

# [시스템 프롬프트 생성 함수] AI가 선생님으로서 가져야 할 역할과 규칙을 정의합니다.
def get_system_prompt(level, topic):
    level_instruction = {
        "초급": "Use very short and simple sentences. Focus on high-frequency basic words.",
        "중급": "Use natural, everyday expressions and some common idioms.",
        "고급": "Use sophisticated vocabulary, complex grammar, and native-level idioms."
    }
    
    prompt = f"""
    You are a friendly and encouraging English teacher. 
    Student Level: {level}
    Style: {level_instruction[level]}
    Topic: {topic}

    Rules:
    1. Respond naturally and keep the conversation moving forward.
    2. **FLEXIBILITY**: Even if the user's answer is slightly off-topic or doesn't perfectly answer your question, acknowledge what they said, provide a brief comment, and then **move to the next logical question**. 
    3. Do not get stuck on the same question for more than one turn. 
    4. **CORRECTION**: If the user makes a grammatical mistake, provide a '💡 Correction' section. 
    5. **KOREAN NAMES**: If a name is unclear, just use what you heard or ask once, but don't let it stop the flow.
    6. End every response with a **new, engaging follow-up question**.
    7. Provide 2-3 '🎯 Suggested Answers' for the NEW question.

    Format:
    [English Response]
    
    💡 Correction: (Optional)
    
    🗣️ Next question: [New follow-up question]

    🎯 Suggested Answers:
    - [Answer Option 1]
    - [Answer Option 2]
    """
    return prompt

# [오디오 중복 처리 방지용 상태]
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# [채팅 세션 초기화] 세션이 없거나 설정이 바뀌면 새 세션을 시작합니다.
if st.session_state.chat_session is None or st.session_state.current_config["level"] != level or st.session_state.current_config["topic"] != topic:
    try:
        # 최신 고효율 모델 gemini-2.0-flash 사용
        model = genai.GenerativeModel('gemini-2.0-flash')
        system_prompt = get_system_prompt(level, topic)
        st.session_state.chat_session = model.start_chat(history=[])
        
        # 첫 인사 유도
        initial_instruction = f"System Instruction: {system_prompt}\n\nPlease start the conversation warmly."
        response = st.session_state.chat_session.send_message(initial_instruction)
        
        st.session_state.messages = [{"role": "assistant", "content": response.text}]
        st.session_state.current_config = {"level": level, "topic": topic}
    except Exception as e:
        st.error(f"오류: {e}")
        st.stop()

# [대화 이력 로드] 기존에 나눈 대화들을 화면에 표시합니다.
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # AI 답변 아래에는 항상 음성 재생 바를 추가합니다.
        if message["role"] == "assistant":
            audio_fp = text_to_speech(message["content"])
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

# [입력 UI 영역]
st.markdown("---")
col1, col2 = st.columns([1, 4])

# 1. 마이크 입력 섹션 (STT용)
with col1:
    audio = mic_recorder(
        start_prompt="🎤 말하기",
        stop_prompt="🛑 중지",
        key="mic_recorder"
    )

# 2. 텍스트 입력창 섹션
with col2:
    text_input = st.chat_input("메시지를 입력하거나 마이크를 사용하세요")

# [입력 데이터 처리]
user_input = None

# 음성 입력을 텍스트로 변환 (기존에 처리된 오디오가 아닐 때만 실행)
if audio:
    audio_id = audio['id'] if 'id' in audio else hash(audio['bytes'])
    if st.session_state.last_processed_audio != audio_id:
        with st.spinner("음성을 분석 중입니다..."):
            try:
                audio_data = audio['bytes']
                # Gemini 모델을 이용해 오디오 내용을 영어 텍스트로 전사(Transcription)
                model = genai.GenerativeModel('gemini-2.0-flash')
                transcription_response = model.generate_content([
                    {"mime_type": "audio/wav", "data": audio_data},
                    "Please transcribe this audio into English text accurately. If it's Korean, translate it to English. Just give the text."
                ])
                user_input = transcription_response.text.strip()
                st.session_state.last_processed_audio = audio_id # 처리된 오디오 ID 저장
            except Exception as e:
                st.error(f"음성 인식 오류: {e}")

# 텍스트 입력을 최종 입력값으로 설정
if not user_input and text_input:
    user_input = text_input

# [AI 답변 생성 및 렌더링]
if user_input:
    # 유저 메시지 기록
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        with st.spinner("선생님이 생각 중입니다..."):
            # Gemini에게 메시지를 보내고 답변 수신
            response = st.session_state.chat_session.send_message(user_input)
            ai_response = response.text
            
            # 최종 답변 출력
            st.markdown(ai_response)
            # 답변 음성 파일 생성 및 오디오 재생 바 출력
            audio_fp = text_to_speech(ai_response)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
            
            # 대화 이력에 AI 답변 저장
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            # 화면 레이아웃 유지를 위해 페이지 새로고침
            st.rerun()
