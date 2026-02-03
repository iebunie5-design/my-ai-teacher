import google.generativeai as genai
import sys

# 실행 시 API 키를 인자로 받거나 직접 입력할 수 있게 구성했습니다.
if len(sys.argv) > 1:
    api_key = sys.argv[1]
else:
    api_key = input("Gemini API Key를 입력하세요: ")

try:
    genai.configure(api_key=api_key)
    print("\n--- 사용 가능한 Gemini 모델 목록 ---")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"Model: {model.name}")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")
