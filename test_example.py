#!/usr/bin/env python3
"""
PubMed 의료 검색 앱 테스트 예시

이 스크립트는 OpenAI API 키 없이도 기본 기능을 테스트할 수 있습니다.
"""

from medical_search_service import MedicalSearchService
import time

def test_medical_search():
    """의료 검색 기능 테스트"""
    print("🏥 PubMed 의료 검색 앱 테스트")
    print("=" * 50)
    
    # 서비스 초기화
    service = MedicalSearchService()
    
    # 테스트 쿼리들
    test_queries = [
        "CRP 수치 12.5",
        "HbA1c 7.8 당뇨병",
        "혈압 180/120",
        "파킨슨병 치료",
        "콜레스테롤 250"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 테스트 {i}: {query}")
        print("-" * 30)
        
        try:
            # 검색 실행
            results = service.search_medical_papers(query, max_results=3)
            
            # 결과 출력
            print(f"✅ 검색 완료 - {results['processing_time']}초")
            print(f"📊 발견된 논문: {results['total_papers_found']}개")
            
            # 감지된 의료 개체
            if results['detected_entities']:
                print("\n🔍 감지된 의료 정보:")
                for entity in results['detected_entities']:
                    print(f"  • {entity['text']} ({entity['type']})")
            
            # 수치 해석
            if results['interpretations']:
                print("\n📈 수치 해석:")
                for interpretation in results['interpretations']:
                    print(f"  • {interpretation}")
            
            # 종합 요약
            if results['overall_summary']:
                print(f"\n📋 종합 요약:")
                print(f"  {results['overall_summary']}")
            
            # 상위 논문 제목들
            if results['papers']:
                print(f"\n📚 주요 논문들:")
                for j, paper in enumerate(results['papers'][:2], 1):
                    print(f"  {j}. {paper['title'][:80]}...")
                    print(f"     PMID: {paper['pmid']}")
            
            print()
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        # API 호출 제한을 위한 대기
        time.sleep(1)

def test_medical_analyzer():
    """의료 텍스트 분석 기능만 테스트"""
    print("\n🔬 의료 텍스트 분석 테스트")
    print("=" * 50)
    
    from medical_analyzer import MedicalAnalyzer
    
    analyzer = MedicalAnalyzer()
    
    test_texts = [
        "CRP 수치가 15.2로 나왔어요",
        "당화혈색소 HbA1c 8.5% 당뇨병",
        "혈압이 190/100으로 측정되었습니다",
        "총 콜레스테롤 280, HDL 35",
        "파킨슨병 환자의 levodopa 반응성"
    ]
    
    for text in test_texts:
        print(f"\n📝 입력: {text}")
        
        # 의료 개체 분석
        entities = analyzer.analyze_input(text)
        
        if entities:
            print("🔍 감지된 의료 정보:")
            for entity in entities:
                info = f"  • {entity.text} ({entity.entity_type})"
                if entity.value:
                    info += f" - 값: {entity.value}"
                if entity.normal_range:
                    info += f" - 정상범위: {entity.normal_range}"
                print(info)
        
        # 검색 쿼리 생성
        search_query = analyzer.generate_search_query(entities, text)
        print(f"🔍 생성된 검색 쿼리: {search_query}")
        
        # 수치 해석
        interpretations = analyzer.interpret_values(entities)
        if interpretations:
            print("📈 수치 해석:")
            for interpretation in interpretations:
                print(f"  • {interpretation}")

def test_pubmed_search():
    """PubMed 검색 기능만 테스트"""
    print("\n🔍 PubMed 검색 테스트")
    print("=" * 50)
    
    from pubmed_search import PubMedSearcher
    
    searcher = PubMedSearcher()
    
    # 간단한 검색 테스트
    query = "diabetes mellitus"
    print(f"📝 검색어: {query}")
    
    try:
        # 논문 ID 검색
        pmids = searcher.search_papers(query, max_results=3)
        print(f"✅ 발견된 논문 ID: {len(pmids)}개")
        
        if pmids:
            # 상세 정보 가져오기
            papers = searcher.fetch_paper_details(pmids[:2])
            print(f"📚 상세 정보 가져온 논문: {len(papers)}개")
            
            for i, paper in enumerate(papers, 1):
                print(f"\n{i}. {paper['title'][:80]}...")
                print(f"   저자: {', '.join(paper['authors'][:2]) if paper['authors'] else 'N/A'}")
                print(f"   저널: {paper['journal']}")
                print(f"   PMID: {paper['pmid']}")
    
    except Exception as e:
        print(f"❌ 검색 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 PubMed 의료 검색 앱 종합 테스트 시작\n")
    
    # 1. 의료 텍스트 분석 테스트 (인터넷 연결 불필요)
    test_medical_analyzer()
    
    # 2. PubMed 검색 테스트 (인터넷 연결 필요)
    try:
        test_pubmed_search()
    except Exception as e:
        print(f"⚠️ PubMed 검색 테스트 건너뜀 (인터넷 연결 필요): {e}")
    
    # 3. 전체 서비스 테스트 (인터넷 연결 필요)
    try:
        test_medical_search()
    except Exception as e:
        print(f"⚠️ 전체 서비스 테스트 건너뜀 (인터넷 연결 필요): {e}")
    
    print("\n✅ 테스트 완료!")
    print("\n💡 실제 사용을 위해서는:")
    print("1. 인터넷 연결을 확인하세요")
    print("2. OpenAI API 키를 설정하면 더 나은 요약을 받을 수 있습니다")
    print("3. Streamlit 앱 실행: streamlit run app.py")
    print("4. FastAPI 서버 실행: uvicorn main:app --reload")

if __name__ == "__main__":
    main() 