from openai import OpenAI
from typing import List, Dict, Optional
from config import config
import json

class PaperSummarizer:
    def __init__(self):
        if config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
    
    def summarize_paper(self, paper: Dict, user_query: str) -> Dict:
        """단일 논문 요약"""
        if not self.enabled:
            return self._create_basic_summary(paper, user_query)
        
        try:
            # 논문 제목과 초록을 결합
            paper_content = f"Title: {paper.get('title', '')}\n\nAbstract: {paper.get('abstract', '')}"
            
            prompt = f"""
다음 의학 논문을 사용자의 질문 "{user_query}"와 관련하여 한국어로 요약해주세요:

{paper_content}

다음 형식으로 응답해주세요:
1. 핵심 내용 (2-3문장)
2. 사용자 질문과의 관련성
3. 주요 결과나 결론
4. 임상적 의미 (있다면)

간결하고 이해하기 쉽게 작성해주세요.
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 의학 논문을 요약하는 전문가입니다. 일반인도 이해할 수 있도록 명확하고 간결하게 설명해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            
            return {
                'title': paper.get('title', ''),
                'authors': paper.get('authors', []),
                'journal': paper.get('journal', ''),
                'publication_date': paper.get('publication_date', ''),
                'pmid': paper.get('pmid', ''),
                'pubmed_url': paper.get('pubmed_url', ''),
                'doi': paper.get('doi', ''),
                'ai_summary': summary,
                'original_abstract': paper.get('abstract', ''),
                'relevance_score': self._calculate_relevance_score(paper, user_query)
            }
            
        except Exception as e:
            print(f"요약 생성 오류: {e}")
            return self._create_basic_summary(paper, user_query)
    
    def summarize_papers(self, papers: List[Dict], user_query: str) -> List[Dict]:
        """여러 논문 요약"""
        summarized_papers = []
        
        for paper in papers:
            summarized_paper = self.summarize_paper(paper, user_query)
            summarized_papers.append(summarized_paper)
        
        # 관련성 점수로 정렬
        summarized_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return summarized_papers
    
    def _create_basic_summary(self, paper: Dict, user_query: str) -> Dict:
        """OpenAI API가 없을 때 기본 요약 생성"""
        # 기본적인 논문 정보 정리
        abstract = paper.get('abstract', '')
        
        # 초록을 문장 단위로 나누고 처음 2-3문장만 사용
        sentences = abstract.split('. ')[:3]
        basic_summary = '. '.join(sentences)
        
        if basic_summary and not basic_summary.endswith('.'):
            basic_summary += '.'
        
        return {
            'title': paper.get('title', ''),
            'authors': paper.get('authors', []),
            'journal': paper.get('journal', ''),
            'publication_date': paper.get('publication_date', ''),
            'pmid': paper.get('pmid', ''),
            'pubmed_url': paper.get('pubmed_url', ''),
            'doi': paper.get('doi', ''),
            'ai_summary': basic_summary or "요약을 생성할 수 없습니다.",
            'original_abstract': abstract,
            'relevance_score': self._calculate_relevance_score(paper, user_query)
        }
    
    def _calculate_relevance_score(self, paper: Dict, user_query: str) -> float:
        """논문과 사용자 질문의 관련성 점수 계산 (개선된 버전)"""
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        journal = paper.get('journal', '').lower()
        
        # 즉시 제외 패턴들 (명백히 비의료적인 것만)
        immediate_exclusion_patterns = [
            'autophagy in plants', 'plant autophagy', 'vegetable growth models',
            'health system review', 'luxembourg health', 'north macedonia health',
            'research advance on vegetable', 'agricultural research', 'plant biology',
            'veterinary medicine', 'animal disease', 'livestock health'
        ]
        
        # 점수 계산
        score = 0
        content = (title + ' ' + abstract).lower()
        
        # 1. 즉시 제외 패턴 확인 (최우선)
        for pattern in immediate_exclusion_patterns:
            if pattern in content:
                return 0.0  # 즉시 제외
        
        # 2. 사용자 쿼리와의 직접 매칭 (높은 점수)
        query_words = [word.lower().strip() for word in user_query.split() if len(word.strip()) > 2]
        for word in query_words:
            if word in title:
                score += 5  # 제목에서 매칭되면 높은 점수
            elif word in abstract:
                score += 2  # 초록에서 매칭되면 중간 점수
        
        # 3. 의료 키워드 점수 (기본 점수)
        medical_keywords = [
            'patient', 'clinical', 'treatment', 'therapy', 'diagnosis', 'therapeutic',
            'medical', 'hospital', 'surgery', 'drug', 'medication', 'medicine',
            'disease', 'disorder', 'syndrome', 'infection', 'cancer', 'tumor',
            'cardiovascular', 'diabetes', 'hypertension', 'inflammation',
            'pharmacological', 'pathology', 'symptoms', 'prognosis', 'mortality',
            'intervention', 'randomized', 'trial', 'efficacy', 'safety', 'outcome',
            'healthcare', 'health care', 'medical care', 'patient care', 'nursing',
            'physician', 'doctor', 'nurse', 'clinic', 'emergency', 'intensive care',
            'blood', 'serum', 'plasma', 'laboratory', 'biomarker', 'screening',
            'hemoglobin', 'anemia', 'dizziness', 'fatigue', 'weakness'  # 헤모글로빈 관련 추가
        ]
        
        for keyword in medical_keywords:
            if keyword in content:
                score += 1
        
        # 4. 한국어 의료 용어 (추가 점수)
        korean_medical_terms = [
            '치료', '진단', '환자', '질병', '질환', '증상', '검사', '수치',
            '헤모글로빈', '빈혈', '어지러움', '피로', '무력감'
        ]
        
        for term in korean_medical_terms:
            if term in user_query:
                score += 3  # 한국어 의료 용어 매칭시 높은 점수
        
        # 5. 비의료 키워드 감점 (핵심만)
        non_medical_keywords = [
            'autophagy in plants', 'plant biology', 'agricultural research',
            'health system review', 'veterinary medicine', 'livestock',
            'narcissism', 'political', 'social media', 'artificial intelligence'
        ]
        
        for keyword in non_medical_keywords:
            if keyword in content:
                score -= 3
        
        # 6. 최종 점수 정규화 (0~1 범위로)
        max_possible_score = 30  # 예상 최대 점수
        normalized_score = max(0.0, min(1.0, score / max_possible_score))
        
        return normalized_score
    
    def generate_overall_summary(self, papers: List[Dict], user_query: str) -> str:
        """전체 검색 결과에 대한 종합 요약"""
        if not self.enabled or not papers:
            return self._create_basic_overall_summary(papers, user_query)
        
        try:
            # 상위 3개 논문의 제목과 요약 정보 수집
            top_papers = papers[:3]
            papers_info = ""
            
            for i, paper in enumerate(top_papers, 1):
                papers_info += f"{i}. {paper.get('title', '')}\n"
                papers_info += f"   요약: {paper.get('ai_summary', '')[:200]}...\n\n"
            
            prompt = f"""
사용자가 "{user_query}"에 대해 질문했고, 다음과 같은 관련 논문들을 찾았습니다:

{papers_info}

이 논문들을 바탕으로 사용자의 질문에 대한 종합적인 답변을 한국어로 작성해주세요:

1. 현재 연구 동향
2. 주요 발견사항
3. 임상적 시사점 (있다면)
4. 추가 고려사항

300자 이내로 간결하게 작성해주세요.
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 의학 연구 동향을 분석하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"종합 요약 생성 오류: {e}")
            return self._create_basic_overall_summary(papers, user_query)
    
    def _create_basic_overall_summary(self, papers: List[Dict], user_query: str) -> str:
        """기본 종합 요약"""
        if not papers:
            return f"'{user_query}'에 대한 관련 논문을 찾을 수 없습니다."
        
        paper_count = len(papers)
        recent_papers = [p for p in papers if '2023' in p.get('publication_date', '') or '2024' in p.get('publication_date', '')]
        
        summary = f"'{user_query}'에 대해 총 {paper_count}개의 관련 논문을 찾았습니다."
        
        if recent_papers:
            summary += f" 이 중 {len(recent_papers)}개는 최근(2023-2024년) 연구입니다."
        
        summary += " 각 논문의 상세 내용을 확인하여 더 자세한 정보를 얻으실 수 있습니다."
        
        return summary 