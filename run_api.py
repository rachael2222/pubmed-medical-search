#!/usr/bin/env python3
"""
FastAPI 서버 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    print("🏥 PubMed 의료 검색 API 서버 시작")
    print("=" * 50)
    
    # 환경 변수 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API 키가 설정되지 않았습니다.")
        print("   기본 기능은 사용 가능하지만 AI 요약은 제한됩니다.")
        print()
    
    print("🚀 API 서버가 시작됩니다...")
    print("🔗 서버 URL: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    print("📋 ReDoc 문서: http://localhost:8000/redoc")
    print()
    print("💡 API 사용 예시:")
    print("GET  /search?q=CRP 수치 12.5")
    print("POST /search")
    print("GET  /health")
    print()
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 50)
    
    try:
        # FastAPI 서버 실행
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 API 서버를 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 다음을 확인해보세요:")
        print("1. pip install -r requirements.txt")
        print("2. main.py 파일이 존재하는지 확인")

if __name__ == "__main__":
    main() 