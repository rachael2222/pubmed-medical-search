#!/usr/bin/env python3
"""
Streamlit 웹 앱 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    print("🏥 PubMed 의료 검색 앱 (Streamlit) 시작")
    print("=" * 50)
    
    # 환경 변수 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API 키가 설정되지 않았습니다.")
        print("   앱에서 직접 입력하거나 .env 파일에 설정하세요.")
        print()
    
    print("📱 웹 브라우저에서 앱이 열립니다...")
    print("🔗 URL: http://localhost:8501")
    print()
    print("💡 사용 팁:")
    print("- 'CRP 수치 12.5' 같은 검사 수치 입력")
    print("- '당뇨병 HbA1c' 같은 질병명과 검사명 조합")
    print("- '혈압 180/120 고혈압' 같은 복합 정보")
    print()
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 50)
    
    try:
        # Streamlit 앱 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 앱을 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 다음을 확인해보세요:")
        print("1. pip install -r requirements.txt")
        print("2. 필요한 패키지가 모두 설치되었는지 확인")

if __name__ == "__main__":
    main() 