from typing import List, Dict, Optional
from pubmed_search import PubMedSearcher
from medical_analyzer import MedicalAnalyzer
from paper_summarizer import PaperSummarizer
import time

class MedicalSearchService:
    def __init__(self):
        self.pubmed_searcher = PubMedSearcher()
        self.medical_analyzer = MedicalAnalyzer()
        self.paper_summarizer = PaperSummarizer()
    
    def search_medical_papers(self, user_input: str, max_results: int = 10) -> Dict:
        """사용자 입력을 분석하여 관련 논문을 검색하고 요약"""
        
        # 시작 시간 기록
        start_time = time.time()
        
        # 1. 의료 개체 분석
        entities = self.medical_analyzer.analyze_input(user_input)
        
        # 2. 검색 쿼리 생성
        search_query = self.medical_analyzer.generate_search_query(entities, user_input)
        
        # 3. 수치 해석
        interpretations = self.medical_analyzer.interpret_values(entities)
        
        # 4. PubMed 검색 (더 많은 결과를 가져와서 필터링)
        papers = self.pubmed_searcher.search_and_fetch(search_query, max_results * 2)
        
        # 5. 논문 요약 및 관련성 평가
        summarized_papers = []
        if papers:
            summarized_papers = self.paper_summarizer.summarize_papers(papers, user_input)
            
            # 6. 논문 필터링 및 관련성 점수 계산 (최적화)
            filtered_papers = []
            min_relevance_threshold = 0.10  # 기본 10%
            
            # Spinal Cord Stimulation 특별 처리
            is_scs_search = any(term in user_input.lower() for term in ['spinal cord stimulation', 'scs', '척수자극술'])
            
            if is_scs_search:
                print(f"🎯 SCS 전용 필터링 적용")
                # SCS 검색의 경우 매우 관대한 필터링
                for paper in papers:
                    title = paper.get('title', '').lower()
                    abstract = paper.get('abstract', '').lower()
                    content = title + ' ' + abstract
                    
                    # SCS 관련성 점수 계산 (특별 로직)
                    scs_score = 0
                    
                    # 직접적인 SCS 언급
                    if 'spinal cord stimulation' in content:
                        scs_score += 0.7
                    elif 'scs' in content and ('pain' in content or 'stimulation' in content):
                        scs_score += 0.5
                    elif 'neurostimulation' in content and 'spinal' in content:
                        scs_score += 0.4
                    
                    # 관련 의료 용어
                    if any(term in content for term in ['chronic pain', 'neuropathic pain', 'back pain']):
                        scs_score += 0.2
                    if any(term in content for term in ['implantable', 'device', 'electrode']):
                        scs_score += 0.1
                    if any(term in content for term in ['efficacy', 'effectiveness', 'outcome']):
                        scs_score += 0.1
                    
                    # 명백히 관련 없는 내용 제외
                    exclude_terms = ['veterinary', 'animal model only', 'plant', 'agriculture', 'in vitro only']
                    has_exclude = any(term in content for term in exclude_terms)
                    
                    if scs_score >= 0.05 and not has_exclude:  # 매우 낮은 임계값
                        paper['relevance_score'] = scs_score
                        filtered_papers.append(paper)
            else:
                # 일반적인 필터링 로직
                for paper in papers:
                    title = paper.get('title', '').lower()
                    abstract = paper.get('abstract', '').lower()
                    content = title + ' ' + abstract
                    
                    # 관련성 점수 계산
                    relevance_score = self._calculate_relevance_score(paper, entities, user_input)
                    paper['relevance_score'] = relevance_score
                    
                    # 기본 제외 패턴 (매우 제한적)
                    exclude_patterns = [
                        'veterinary medicine', 'animal study only', 'plant biology', 
                        'agricultural research', 'environmental policy only'
                    ]
                    
                    has_exclude_pattern = any(pattern in content for pattern in exclude_patterns)
                    is_low_relevance = relevance_score < min_relevance_threshold
                    
                    # 특별 케이스: 고지혈증 관련 검색의 경우 더 관대한 기준 적용
                    is_hyperlipidemia_search = any(term in user_input.lower() for term in ['고지혈', '콜레스테롤', 'cholesterol', 'lipid', 'hyperlipidemia'])
                    if is_hyperlipidemia_search:
                        hyperlipidemia_keywords = ['hyperlipidemia', 'dyslipidemia', 'cholesterol', 'lipid', 'triglyceride', 'statin', 'atherosclerosis']
                        has_hyperlipidemia_content = any(keyword in content for keyword in hyperlipidemia_keywords)
                        if has_hyperlipidemia_content:
                            is_low_relevance = relevance_score < 0.08
                    
                    # 최종 필터링 조건
                    should_include = not is_low_relevance and not has_exclude_pattern
                    
                    if should_include:
                        filtered_papers.append(paper)
            
            # 관련성 점수로 재정렬하고 요청된 수만큼만 반환
            filtered_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            summarized_papers = filtered_papers[:max_results]
        
        # 7. 전체 요약 생성
        overall_summary = self.paper_summarizer.generate_overall_summary(summarized_papers, user_input)
        
        # 처리 시간 계산
        processing_time = round(time.time() - start_time, 2)
        
        return {
            'user_input': user_input,
            'search_query': search_query,
            'detected_entities': [
                {
                    'text': entity.text,
                    'type': entity.entity_type,
                    'value': entity.value,
                    'unit': entity.unit,
                    'normal_range': entity.normal_range
                } for entity in entities
            ],
            'interpretations': interpretations,
            'papers': summarized_papers,
            'total_papers_found': len(papers),  # 원본 검색 결과 수
            'filtered_papers_count': len(summarized_papers),  # 필터링 후 수
            'overall_summary': overall_summary,
            'processing_time': processing_time,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_paper_detail(self, pmid: str) -> Optional[Dict]:
        """특정 논문의 상세 정보 조회"""
        papers = self.pubmed_searcher.fetch_paper_details([pmid])
        if papers:
            return papers[0]
        return None
    
    def search_similar_papers(self, pmid: str, max_results: int = 5) -> List[Dict]:
        """특정 논문과 유사한 논문 검색"""
        # 원본 논문 정보 가져오기
        original_paper = self.get_paper_detail(pmid)
        if not original_paper:
            return []
        
        # 제목과 초록에서 키워드 추출하여 검색
        title = original_paper.get('title', '')
        abstract = original_paper.get('abstract', '')
        
        # 간단한 키워드 추출 (실제로는 더 정교한 방법 사용 가능)
        keywords = self._extract_keywords_from_text(title + ' ' + abstract)
        search_query = ' AND '.join([f'"{kw}"' for kw in keywords[:3]])
        
        # 검색 및 원본 논문 제외
        papers = self.pubmed_searcher.search_and_fetch(search_query, max_results + 1)
        similar_papers = [p for p in papers if p.get('pmid') != pmid][:max_results]
        
        return similar_papers
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """텍스트에서 주요 키워드 추출 (간단한 버전)"""
        import re
        
        # 기본적인 전처리
        text = text.lower()
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)  # 4글자 이상 영어 단어
        
        # 의학 용어로 보이는 단어들 우선선별
        medical_keywords = []
        common_words = {'with', 'from', 'they', 'this', 'that', 'were', 'been', 'have', 'more', 'such', 'also', 'than', 'only', 'these', 'may', 'can', 'between', 'after', 'before', 'during', 'study', 'studies', 'analysis', 'results', 'methods', 'patients', 'data', 'using', 'used', 'show', 'showed', 'found', 'observed'}
        
        for word in words:
            if word not in common_words and len(word) >= 4:
                medical_keywords.append(word)
                if len(medical_keywords) >= 5:  # 최대 5개 키워드
                    break
        
        return medical_keywords
    
    def _calculate_relevance_score(self, paper: Dict, entities: List, user_input: str) -> float:
        """논문의 관련성 점수 계산"""
        score = 0.0
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        content = title + ' ' + abstract
        user_lower = user_input.lower()
        
        # 1. 사용자 입력과의 직접적인 매칭
        user_words = user_lower.split()
        for word in user_words:
            if len(word) > 2:  # 2글자 이상의 단어만
                if word in title:
                    score += 0.05  # 제목에 있으면 5%
                elif word in abstract:
                    score += 0.02  # 초록에 있으면 2%
        
        # 2. 감지된 엔티티와의 매칭
        for entity in entities:
            entity_text = entity.text.lower()
            if entity_text in content:
                if entity.entity_type == 'disease':
                    score += 0.04  # 질병명 매칭
                elif entity.entity_type == 'test':
                    score += 0.03  # 검사명 매칭
                elif entity.entity_type == 'treatment':
                    score += 0.04  # 치료법 매칭
        
        # 3. 한국어 의료 용어 인식
        korean_medical_terms = {
            '당뇨병': 'diabetes', '고혈압': 'hypertension', '파킨슨': 'parkinson',
            '암': 'cancer', '종양': 'tumor', '심장': 'heart', '뇌': 'brain',
            '치료': 'treatment', '진단': 'diagnosis', '수술': 'surgery',
            '효능': 'efficacy', '효과': 'effectiveness'
        }
        
        for korean, english in korean_medical_terms.items():
            if korean in user_lower and english in content:
                score += 0.03
        
        # 4. 기본 의료 키워드 보너스
        medical_keywords = [
            'patient', 'clinical', 'treatment', 'therapy', 'diagnosis', 'disease',
            'medical', 'health', 'study', 'trial', 'efficacy', 'outcome', 'hospital'
        ]
        
        for keyword in medical_keywords:
            if keyword in content:
                score += 0.01
        
        # 5. CA-125 특별 처리
        if any(term in user_lower for term in ['ca 125', 'ca-125', 'ca125']):
            if any(term in content for term in ['ca-125', 'ca 125', 'tumor marker', 'ovarian cancer']):
                score += 0.1  # 높은 보너스
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    def get_health_tips(self, entities: List) -> List[str]:
        """감지된 의료 개체를 기반으로 건강 팁 제공"""
        tips = []
        
        for entity_data in entities:
            entity_type = entity_data.get('type')
            entity_text = entity_data.get('text', '').lower()
            
            if entity_type == 'test':
                if 'crp' in entity_text:
                    tips.append("💡 CRP 수치가 높다면 염증을 줄이기 위해 금연, 규칙적인 운동, 건강한 식단을 유지하세요.")
                elif 'hba1c' in entity_text or 'glucose' in entity_text:
                    tips.append("💡 혈당 관리를 위해 탄수화물 섭취를 조절하고 정기적인 운동을 하세요.")
                elif 'cholesterol' in entity_text:
                    tips.append("💡 콜레스테롤 관리를 위해 포화지방 섭취를 줄이고 오메가-3가 풍부한 음식을 섭취하세요.")
                elif 'bp' in entity_text:
                    tips.append("💡 혈압 관리를 위해 나트륨 섭취를 줄이고 스트레스를 관리하세요.")
            
            elif entity_type == 'disease':
                if '당뇨병' in entity_text or 'diabetes' in entity_text:
                    tips.append("💡 당뇨병 관리: 정기적인 혈당 측정, 균형잡힌 식단, 규칙적인 운동이 중요합니다.")
                elif '고혈압' in entity_text or 'hypertension' in entity_text:
                    tips.append("💡 고혈압 관리: 염분 섭취 제한, 정기적인 혈압 측정, 금연이 필요합니다.")
        
        # 일반적인 건강 팁
        if not tips:
            tips.append("💡 정기적인 건강검진과 의사와의 상담을 통해 건강을 관리하세요.")
        
        return tips
    
    def format_search_results(self, results: Dict) -> str:
        """검색 결과를 읽기 쉬운 형태로 포맷팅"""
        output = []
        
        # 헤더
        output.append("🔍 PubMed 의료 논문 검색 결과")
        output.append("=" * 50)
        output.append(f"검색어: {results['user_input']}")
        output.append(f"검색 시간: {results['timestamp']}")
        output.append(f"처리 시간: {results['processing_time']}초")
        output.append("")
        
        # 감지된 의료 개체
        if results['detected_entities']:
            output.append("📊 감지된 의료 정보:")
            for entity in results['detected_entities']:
                if entity['value']:
                    output.append(f"  • {entity['text']} ({entity['type']})")
                else:
                    output.append(f"  • {entity['text']} ({entity['type']})")
            output.append("")
        
        # 수치 해석
        if results['interpretations']:
            output.append("📈 수치 해석:")
            for interpretation in results['interpretations']:
                output.append(f"  • {interpretation}")
            output.append("")
        
        # 전체 요약
        if results['overall_summary']:
            output.append("📋 종합 요약:")
            output.append(f"  {results['overall_summary']}")
            output.append("")
        
        # 논문 목록
        output.append(f"📚 관련 논문 ({results['total_papers_found']}개 발견):")
        output.append("")
        
        for i, paper in enumerate(results['papers'][:5], 1):  # 상위 5개만 표시
            output.append(f"{i}. {paper['title']}")
            
            if paper['authors']:
                authors = ', '.join(paper['authors'][:3])  # 처음 3명만
                if len(paper['authors']) > 3:
                    authors += " 외"
                output.append(f"   저자: {authors}")
            
            if paper['journal']:
                output.append(f"   저널: {paper['journal']}")
            
            if paper['publication_date']:
                output.append(f"   발행일: {paper['publication_date']}")
            
            output.append(f"   PMID: {paper['pmid']}")
            output.append(f"   링크: {paper['pubmed_url']}")
            
            if paper['ai_summary']:
                output.append(f"   요약: {paper['ai_summary'][:200]}...")
            
            output.append("")
        
        return "\n".join(output) 