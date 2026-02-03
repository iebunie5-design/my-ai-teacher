# 🎓 나만의 영어회화 선생님 (My Own English Teacher)

Streamlit과 Google Gemini API를 이용한 맞춤형 영어 회화 챗봇입니다.

## 주요 기능
- **라이브러리**: `streamlit`, `google-generativeai`
- **모델**: `gemini-pro`
- **맞춤형 설정**: 초급/중급/고급 레벨 및 6가지 회화 주제 선택 가능
- **실시간 피드백**: 문법 교정 및 자연스러운 영어 표현 안내
- **한국어 대응**: 한국어로 질문 시 영어 표현 방법 설명

## 실행 방법
1. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```
2. 앱 실행:
   ```bash
   streamlit run app.py
   ```
3. 웹 브라우저에서 열리는 페이지의 사이드바에 **Gemini API Key**를 입력합니다.
