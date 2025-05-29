import streamlit as st
import pandas as pd
from medical_search_service import MedicalSearchService
import time
import os

# 페이지 설정
st.set_page_config(
    page_title="🏥 PubMed 의료 검색 앱",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.info-box {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.paper-card {
    border: 1px solid #e0e0e0;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0.5rem 0;
    background-color: #fafafa;
}
.entity-tag {
    background-color: #e3f2fd;
    color: #1565c0;
    padding: 0.2rem 0.5rem;
    border-radius: 1rem;
    font-size: 0.8rem;
    margin: 0.2rem;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown('<h1 class="main-header">🏥 PubMed 의료 검색 앱</h1>', unsafe_allow_html=True)

# 서비스 초기화
def init_service():
    return MedicalSearchService()

service = init_service()

# 세션 상태 초기화
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# show_abstracts 세션 상태 초기화 추가
if 'show_abstracts' not in st.session_state:
    st.session_state.show_abstracts = {}

if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # OpenAI API 키 입력
    api_key_input = st.text_input(
        "🔑 OpenAI API 키 (선택사항)",
        type="password",
        help="AI 요약 기능을 사용하려면 OpenAI API 키를 입력하세요"
    )
    
    if api_key_input:
        os.environ['OPENAI_API_KEY'] = api_key_input
        st.success("✅ API 키가 설정되었습니다")
    
    st.markdown("---")
    
    # 검색 옵션
    st.subheader("🔍 검색 설정")
    max_papers = st.slider("최대 논문 수", 5, 20, 10)
    
    # 캐시 클리어 버튼
    if st.button("🔄 캐시 클리어", help="검색 결과 초기화"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.search_results = None
        st.rerun()
    
    st.markdown("---")
    
    # 예시 질문들
    st.subheader("💡 검색 예시")
    example_queries = [
        "파킨슨병 치료법",
        "CRP 수치 12.5",
        "HbA1c 7.8 당뇨병",
        "혈압 180/120",
        "콜레스테롤 250"
    ]
    
    for query in example_queries:
        if st.button(f"📝 {query}", key=f"example_{query}", use_container_width=True):
            st.session_state.search_query = query

# 메인 콘텐츠
col1, col2 = st.columns([3, 1])

with col1:
    # 검색 입력
    search_query = st.text_input(
        "🔍 질병명, 증상, 검사 수치를 입력하세요:",
        value=st.session_state.get('search_query', ''),
        placeholder="예: CRP 수치 12.5, HbA1c 7.8 당뇨병, 혈압 180/120 등"
    )

with col2:
    search_button = st.button("🔍 검색", type="primary", use_container_width=True)

# 검색 실행
if search_button and search_query:
    with st.spinner('논문을 검색하고 분석 중입니다... ⏳'):
        try:
            # 검색 실행
            results = service.search_medical_papers(search_query, max_papers)
            
            # 결과 저장 (세션 상태)
            st.session_state.search_results = results
            
        except Exception as e:
            st.error(f"검색 중 오류가 발생했습니다: {str(e)}")

# 결과 표시
if st.session_state.search_results:
    results = st.session_state.search_results
    
    # 감지된 의료 개체 표시 (간단하게)
    if results['detected_entities']:
        st.subheader("🔍 감지된 의료 정보")
        entity_tags = []
        for entity in results['detected_entities']:
            if entity['value']:
                entity_tags.append(f"`{entity['text']}` ({entity['type']})")
            else:
                entity_tags.append(f"`{entity['text']}` ({entity['type']})")
        st.markdown(" • ".join(entity_tags))
        st.markdown("---")
    
    # 수치 해석 표시 (간단하게)
    if results['interpretations']:
        st.subheader("📊 수치 분석")
        for interpretation in results['interpretations']:
            st.info(interpretation)
        st.markdown("---")
    
    # 논문 목록 표시
    if results['papers']:
        st.subheader(f"📚 검색 결과 ({len(results['papers'])}개 논문)")
        
        for i, paper in enumerate(results['papers'], 1):
            # 깔끔한 논문 카드
            with st.container():
                # 제목과 기본 정보
                st.markdown(f"### {i}. {paper['title']}")
                
                # 메타 정보를 한 줄로
                meta_info = []
                if paper.get('authors'):
                    authors = ', '.join(paper['authors'][:2])
                    if len(paper['authors']) > 2:
                        authors += f" 외 {len(paper['authors'])-2}명"
                    meta_info.append(f"**저자:** {authors}")
                
                if paper.get('journal'):
                    meta_info.append(f"**저널:** {paper['journal']}")
                
                if paper.get('publication_date'):
                    meta_info.append(f"**발행:** {paper['publication_date']}")
                
                if paper.get('relevance_score'):
                    score = paper['relevance_score']
                    meta_info.append(f"**관련성:** {score:.2f}")
                
                st.markdown(" | ".join(meta_info))
                
                # AI 요약 (있는 경우)
                if paper.get('ai_summary'):
                    st.markdown("**🤖 AI 요약**")
                    st.markdown(f"> {paper['ai_summary']}")
                
                # 초록 보기 토글
                if paper.get('abstract'):
                    abstract_key = f"show_abstract_{i}"
                    if abstract_key not in st.session_state.show_abstracts:
                        st.session_state.show_abstracts[abstract_key] = False
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button(f"📖 초록 {'숨기기' if st.session_state.show_abstracts[abstract_key] else '보기'}", 
                                   key=f"abstract_btn_{i}"):
                            st.session_state.show_abstracts[abstract_key] = not st.session_state.show_abstracts[abstract_key]
                    
                    with col2:
                        if paper.get('pmid'):
                            pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}"
                            st.markdown(f"🔗 [PubMed에서 보기]({pubmed_url})")
                    
                    if st.session_state.show_abstracts[abstract_key]:
                        st.markdown("**원본 초록:**")
                        st.markdown(f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;'>{paper['abstract']}</div>", 
                                  unsafe_allow_html=True)
                
                st.markdown("---")
    
    else:
        st.warning("❌ 검색 조건에 맞는 논문을 찾을 수 없습니다.")
        st.info("다른 키워드로 검색해보세요.")

# 사용법 안내
with st.expander("📖 사용법 안내"):
    st.markdown("""
    ### 🔍 검색 방법
    - **질병명**: 파킨슨병, 당뇨병, 고혈압 등
    - **검사 수치**: CRP 12.5, HbA1c 8.2, 혈압 180/120 등
    - **복합 검색**: 당뇨병 HbA1c, 고혈압 치료 등
    
    ### 🧪 지원하는 검사 항목
    CRP, HbA1c, 혈압, 콜레스테롤, 혈당, 헤모글로빈, CA-125 등
    
    ### 🤖 AI 기능
    OpenAI API 키를 입력하면 논문의 한국어 요약을 제공합니다
    """)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
        🏥 PubMed 의료 검색 앱 | 의료 정보는 참고용이며, 정확한 진단은 의료진과 상담하세요
    </div>
    """, 
    unsafe_allow_html=True
)

# 사이드바 하단 (간소화)
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 결과 초기화", use_container_width=True):
        if 'search_results' in st.session_state:
            del st.session_state.search_results
        if 'search_query' in st.session_state:
            del st.session_state.search_query
        st.rerun() 