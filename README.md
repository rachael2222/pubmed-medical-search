# 🏥 PubMed 의료 검색 앱

한국어와 영어로 의료 정보를 입력하면 관련 PubMed 논문을 검색하고 AI로 요약해주는 의료 연구 도구입니다.

## ✨ 주요 기능

### 🔍 스마트 의료 검색
- **질병명 인식**: 당뇨병, 고혈압, 파킨슨병, 암 등 한국어/영어 질병명 자동 인식
- **검사 수치 분석**: CRP, HbA1c, 혈압, 콜레스테롤, CA-125 등 15개 이상 검사 항목 지원
- **증상 매핑**: 한국어 증상을 영어 의학 용어로 자동 변환
- **치료법 인식**: 척수자극술, 심부뇌자극술 등 고급 의료 시술 지원

### 🧬 종양 표지자 전문 지원
- **CA-125**: 난소암 진단, 정상 범위 (<35 U/mL)
- **CEA**: 대장암 진단, 정상 범위 (<3.0 ng/mL)
- **AFP**: 간암 진단, 정상 범위 (<10 ng/mL)
- **PSA**: 전립선암 진단, 정상 범위 (<4.0 ng/mL)
- **CA 19-9**: 췌장암 진단, 정상 범위 (<37 U/mL)
- **CA 15-3**: 유방암 진단, 정상 범위 (<30 U/mL)

### 🤖 AI 기반 논문 요약
- **OpenAI GPT 통합**: 최신 GPT 모델로 논문 요약
- **한국어 요약**: 영어 논문을 한국어로 번역 요약
- **관련성 평가**: AI가 검색어와 논문의 관련성 점수 계산
- **종합 분석**: 여러 논문을 종합한 전체 요약 제공

### 🎯 고급 필터링
- **관련성 기반 필터링**: 의료 관련성 점수로 논문 선별
- **최신 연구 우선**: 2014-2024년 최신 논문 우선 검색
- **인간 대상 연구**: 동물 실험이나 in vitro 연구 제외
- **의료 저널 우선**: 의학 전문 저널 논문 우선 표시

## 🚀 빠른 시작

### 설치
```bash
git clone https://github.com/YOUR_USERNAME/pubmed-medical-search.git
cd pubmed-medical-search
pip install -r requirements.txt
```

### 실행

#### 1. Streamlit 웹 앱 (추천)
```bash
python run_streamlit.py
```
브라우저에서 `http://localhost:8501` 접속

#### 2. FastAPI REST API
```bash
python run_api.py
```
API 문서: `http://localhost:8000/docs`

#### 3. 명령행 인터페이스
```bash
python test_example.py
```

### OpenAI API 키 설정
1. **웹 앱에서 직접 입력**: Streamlit 사이드바에서 API 키 입력
2. **환경 변수**: `OPENAI_API_KEY` 환경 변수 설정
3. **config.py**: `config.py` 파일에서 API 키 설정

## 📋 사용 예시

### 검사 수치 입력
```
CRP 수치 12.5
혈압 180/120 고혈압
당화혈색소 8.5% 당뇨병
CA-125가 50으로 높으면
```

### 질병 및 증상 검색
```
파킨슨병 진단 받았는데 치료법?
고지혈증 주의사항
헤모글로빈 어지러움
만성 요통 치료
```

### 고급 의료 시술
```
spinal cord stimulation 치료법 효능
척수자극술 만성통증
deep brain stimulation 파킨슨
심부뇌자극술 떨림
```

### 종양 표지자 검색
```
ca 125 정상범위
CEA 수치 상승
PSA 검사 결과
AFP 간암 진단
```

## 🏗️ 프로젝트 구조

```
pubmed-medical-search/
├── medical_analyzer.py      # 의료 개체 인식 및 분석
├── pubmed_search.py         # PubMed API 연동
├── paper_summarizer.py      # OpenAI 기반 논문 요약
├── medical_search_service.py # 메인 검색 서비스
├── app.py                   # Streamlit 웹 앱
├── main.py                  # FastAPI REST API
├── config.py                # 설정 파일
├── requirements.txt         # 의존성 패키지
├── run_streamlit.py         # Streamlit 실행 스크립트
├── run_api.py               # FastAPI 실행 스크립트
└── test_example.py          # 사용 예시 및 테스트
```

## 🔧 주요 컴포넌트

### MedicalAnalyzer
- 의료 개체 인식 (NER)
- 한국어-영어 의학 용어 매핑
- 검사 수치 정상 범위 판정
- PubMed 검색 쿼리 생성

### PubMedSearcher
- NCBI E-utilities API 연동
- XML 파싱 및 논문 메타데이터 추출
- 검색 결과 페이징 처리

### PaperSummarizer
- OpenAI GPT API 통합
- 논문 초록 한국어 요약
- 관련성 점수 계산
- 종합 분석 리포트 생성

### MedicalSearchService
- 전체 검색 파이프라인 조율
- 고급 필터링 및 순위 결정
- 결과 포맷팅 및 반환

## 🌟 특별 기능

### 1. 척수자극술(SCS) 전문 검색
```python
# 입력: "spinal cord stimulation 치료법 효능"
# 결과: 척수자극술 관련 최신 논문 10편 + AI 요약
```

### 2. CA-125 종양표지자 특화
```python
# 입력: "ca 125 정상범위"
# 결과: CA-125 기준값 및 난소암 진단 논문들
```

### 3. 파킨슨병 통합 검색
```python
# 입력: "파킨슨병 진단 받았는데 치료법?"
# 결과: 레보도파, 도파민 작용제, DBS 관련 논문들
```

### 4. 고지혈증 관리 정보
```python
# 입력: "고지혈 주의사항"
# 결과: 고지혈증 치료 및 예방 관련 논문들
```

## 📊 API 엔드포인트

### REST API (FastAPI)
- `POST /search`: 의료 논문 검색
- `GET /paper/{pmid}`: 특정 논문 상세 정보
- `GET /similar/{pmid}`: 유사 논문 검색
- `GET /health`: 서버 상태 확인

### Streamlit 웹 앱
- 직관적인 웹 인터페이스
- 실시간 검색 및 결과 표시
- 논문 상세 정보 모달
- OpenAI API 키 관리

## 🔬 기술 스택

- **Python 3.8+**
- **Streamlit**: 웹 인터페이스
- **FastAPI**: REST API 서버
- **OpenAI GPT**: AI 논문 요약
- **PubMed E-utilities**: 논문 검색 API
- **Pandas**: 데이터 처리
- **BioPython**: 생물의학 데이터 처리

## 📈 성능 최적화

### 검색 정확도
- **관련성 점수**: 제목(5점) + 초록(2점) + 키워드 매칭
- **의료 필터링**: 비의료 논문 자동 제외
- **최신성 가중치**: 최근 10년 논문 우선

### 응답 속도
- **병렬 처리**: 논문 요약 병렬 실행
- **캐싱**: 검색 결과 메모리 캐싱
- **API 제한**: PubMed API 호출 속도 제한 준수

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 GitHub Issues를 통해 연락해주세요.

## 🙏 감사의 말

- **NCBI PubMed**: 공개 의학 논문 데이터베이스 제공
- **OpenAI**: GPT API를 통한 AI 요약 기능
- **Streamlit**: 훌륭한 웹 앱 프레임워크
- **FastAPI**: 고성능 API 프레임워크

---

**⚠️ 주의사항**: 이 도구는 의학 연구 및 정보 수집 목적으로만 사용해야 하며, 실제 의학적 진단이나 치료 결정에는 반드시 의료 전문가와 상담하시기 바랍니다. 