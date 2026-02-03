import streamlit as st
import google.generativeai as genai

# [Streamlit 설정] 브라우저 탭의 제목 및 아이콘, 레이아웃을 설정합니다.
st.set_page_config(
    page_title="나만의 영어회화 선생님",
    page_icon="🎓",
    layout="centered"
)

# [세션 상태 관리] 사용자의 대화 기록, 채팅 세션, 현재 설정을 브라우저 세션에 저장하여 유지합니다.
if "messages" not in st.session_state:
    st.session_state.messages = []  # 대화 이력 저장용 리스트
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None  # Gemini 채팅 세션 객체
if "current_config" not in st.session_state:
    st.session_state.current_config = {"level": None, "topic": None}  # 현재 선택된 레벨과 주제

# [사이드바 UI] 앱 왼쪽의 슬라이드바 영역을 정의합니다.
with st.sidebar:
    st.title("⚙️ 설정")
    
    # API 키 입력 (password 타입으로 키를 숨깁니다)
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        help="[여기서 API 키를 발급받으세요](https://aistudio.google.com/app/apikey)"
    )
    
    # 영어 레벨 및 대화 주제 선택 UI
    level = st.selectbox("나의 영어 레벨", ["초급", "중급", "고급"])
    topic = st.selectbox("회화 주제", ["자기소개", "여행", "쇼핑", "음식점", "직장생활", "자유대화"])
    
    # 버튼 클릭 시 세션 초기화 및 페이지 새로고침
    if st.button("🔄 새 대화 시작"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.current_config = {"level": level, "topic": topic}
        st.rerun()

    st.markdown("---")
    st.markdown("""
    ### 💡 사용 방법
    1. **Gemini API Key**를 입력하세요.
    2. 본인의 **레벨**과 **주제**를 선택하세요.
    3. 하단 입력창에 영어로 먼저 말을 걸거나, 대화를 시작해보세요!
    4. 한국어로 질문하면 영어 표현을 친절히 알려드립니다.
    """)

# [메인 영역] 메인 화면 타이틀 출력
st.title("🎓 나만의 영어회화 선생님")

# API 키가 입력되지 않았을 경우 안내 메시지 출력 및 실행 중단
if not api_key:
    st.info("사이드바에 Gemini API Key를 입력하고 시작해주세요! 🔑", icon="ℹ️")
    st.markdown("""
    ### 🔑 API 키가 없으신가요?
    1. [Google AI Studio](https://aistudio.google.com/app/apikey)에 접속합니다.
    2. 'Create API key' 버튼을 클릭하여 키를 생성합니다.
    3. 생성된 키를 복사하여 왼쪽 사이드바에 입력하세요.
    """)
    st.stop()

# [Gemini 설정] 입력받은 API 키로 라이브러리를 초기화합니다.
genai.configure(api_key=api_key)

# [시스템 프롬프트 생성] 선택된 레벨과 주제에 맞춰 AI의 페르소나와 규칙을 정의합니다.
def get_system_prompt(level, topic):
    level_instruction = {
        "초급": "Use very short and simple sentences. Focus on high-frequency basic words. Speak slowly (via text) and be very encouraging.",
        "중급": "Use natural, everyday expressions and some common idioms. Use moderate sentence complexity matching a B1-B2 learner.",
        "고급": "Use sophisticated vocabulary, complex grammar, and native-level idioms. Discuss deep concepts within the topic."
    }
    
    prompt = f"""
    You are a friendly, professional, and patient English conversation teacher.
    Student Level: {level}
    Teacher's Guiding Style: {level_instruction[level]}
    Current Topic: {topic}

    Follow these STRICT response rules:
    1. Respond naturally in English based on the conversation topic.
    2. If the user makes grammatical errors, spelling mistakes, or uses awkward phrasing, provide a '💡 Correction' section.
    3. If the user speaks in Korean, explain how to say it in English naturally.
    4. Always encourage the user and keep the mood positive.
    5. **CRITICAL**: Every response MUST end with a follow-up question related to the topic to continue the dialogue.
    6. Use relevant emojis to keep it friendly.
    
    Response Format:
    [English Response]
    
    💡 Correction: (Provide only if the user made a mistake in their previous message. Use the format: 'Instead of "...", you can say "..." because ...')
    
    🗣️ Next question: [Follow-up question to the user]
    """
    return prompt

# [채팅 세션 초기화] 세션이 없거나 설정(레벨/주제)이 변경된 경우 새로운 대화를 시작합니다.
if st.session_state.chat_session is None or st.session_state.current_config["level"] != level or st.session_state.current_config["topic"] != topic:
    try:
        # Gemini 모델 인스턴스 생성 (최신 gemini-2.5-flash 모델 적용)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config={"temperature": 0.7}
        )
        
        system_prompt = get_system_prompt(level, topic)
        st.session_state.chat_session = model.start_chat(history=[])
        
        # [첫 인사 유도] AI가 먼저 환영 인사를 건네도록 초기 명령을 보냅니다.
        initial_instruction = f"System Instruction: {system_prompt}\n\nPlease start the conversation by greeting me warmly in English as my teacher. Follow the response format."
        response = st.session_state.chat_session.send_message(initial_instruction)
        
        # 첫 인사 기록 저장 및 설정 업데이트
        st.session_state.messages = [{"role": "assistant", "content": response.text}]
        st.session_state.current_config = {"level": level, "topic": topic}
        
    except Exception as e:
        st.error(f"모델 초기화 중 오류 발생: {e}")
        st.stop()

# [채팅 히스토리 렌더링] 세션에 저장된 이전 대화 내용들을 화면에 표시합니다.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# [채팅 입력 및 처리] 사용자가 메시지를 입력했을 때 실행됩니다.
if prompt := st.chat_input("선생님께 말을 걸어보세요 (영어나 한국어 모두 가능)"):
    # 1. 유저 메시지를 히스토리에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 응답 생성 영역
    with st.chat_message("assistant"):
        try:
            # Gemini에 메시지 전송 및 응답 수신
            response = st.session_state.chat_session.send_message(prompt)
            ai_response = response.text
            
            # 응답 출력 및 히스토리에 저장
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            # 예외 발생 시 안내 메시지 표시
            st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
            if "api_key" in str(e).lower():
                st.warning("API 키가 유효하지 않거나 만료되었을 수 있습니다. 사이드바에서 다시 확인해주세요.")
