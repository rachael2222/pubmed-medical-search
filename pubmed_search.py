import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from config import config
import re
import time

class PubMedSearcher:
    def __init__(self):
        self.email = config.PUBMED_EMAIL
        self.tool = config.PUBMED_TOOL_NAME
        
    def search_papers(self, query: str, max_results: int = None) -> List[str]:
        """PubMed에서 논문 검색"""
        if max_results is None:
            max_results = config.MAX_PAPERS
            
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'sort': 'relevance',
            'email': self.email,
            'tool': self.tool
        }
        
        try:
            response = requests.get(config.PUBMED_SEARCH_URL, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            id_list = []
            
            for id_elem in root.findall('.//Id'):
                id_list.append(id_elem.text)
                
            return id_list
            
        except Exception as e:
            print(f"검색 오류: {e}")
            return []
    
    def fetch_paper_details(self, pmids: List[str]) -> List[Dict]:
        """논문 상세 정보 가져오기"""
        if not pmids:
            return []
            
        # API 호출 제한을 위한 지연
        time.sleep(0.1)
        
        pmid_str = ','.join(pmids)
        params = {
            'db': 'pubmed',
            'id': pmid_str,
            'retmode': 'xml',
            'rettype': 'abstract',
            'email': self.email,
            'tool': self.tool
        }
        
        try:
            response = requests.get(config.PUBMED_FETCH_URL, params=params)
            response.raise_for_status()
            
            return self._parse_paper_xml(response.content)
            
        except Exception as e:
            print(f"상세 정보 가져오기 오류: {e}")
            return []
    
    def _parse_paper_xml(self, xml_content: bytes) -> List[Dict]:
        """XML 응답을 파싱하여 논문 정보 추출"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                paper = {}
                
                # PMID
                pmid_elem = article.find('.//PMID')
                paper['pmid'] = pmid_elem.text if pmid_elem is not None else ''
                
                # 제목
                title_elem = article.find('.//ArticleTitle')
                paper['title'] = title_elem.text if title_elem is not None else ''
                
                # 초록
                abstract_elems = article.findall('.//AbstractText')
                abstract_parts = []
                for abs_elem in abstract_elems:
                    if abs_elem.text:
                        # 라벨이 있는 경우 (예: BACKGROUND:, METHODS: 등)
                        label = abs_elem.get('Label', '')
                        text = abs_elem.text
                        if label:
                            abstract_parts.append(f"{label}: {text}")
                        else:
                            abstract_parts.append(text)
                
                paper['abstract'] = ' '.join(abstract_parts)
                
                # 저자
                authors = []
                for author in article.findall('.//Author'):
                    lastname = author.find('LastName')
                    firstname = author.find('ForeName')
                    if lastname is not None and firstname is not None:
                        authors.append(f"{firstname.text} {lastname.text}")
                        
                paper['authors'] = authors
                
                # 저널
                journal_elem = article.find('.//Journal/Title')
                paper['journal'] = journal_elem.text if journal_elem is not None else ''
                
                # 발행일
                pub_date = article.find('.//PubDate')
                if pub_date is not None:
                    year = pub_date.find('Year')
                    month = pub_date.find('Month')
                    day = pub_date.find('Day')
                    
                    date_parts = []
                    if year is not None:
                        date_parts.append(year.text)
                    if month is not None:
                        date_parts.append(month.text)
                    if day is not None:
                        date_parts.append(day.text)
                    
                    paper['publication_date'] = '-'.join(date_parts)
                else:
                    paper['publication_date'] = ''
                
                # DOI
                doi_elem = article.find('.//ELocationID[@EIdType="doi"]')
                paper['doi'] = doi_elem.text if doi_elem is not None else ''
                
                # PubMed URL
                paper['pubmed_url'] = f"https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/"
                
                papers.append(paper)
                
        except Exception as e:
            print(f"XML 파싱 오류: {e}")
            
        return papers
    
    def search_and_fetch(self, query: str, max_results: int = None) -> List[Dict]:
        """검색과 상세 정보 가져오기를 한번에 수행"""
        pmids = self.search_papers(query, max_results)
        if pmids:
            return self.fetch_paper_details(pmids)
        return [] 