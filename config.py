import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # PubMed API 설정
    PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "your_email@example.com")
    PUBMED_TOOL_NAME = os.getenv("PUBMED_TOOL_NAME", "PubMedSearchApp")
    
    # 앱 설정
    MAX_PAPERS = int(os.getenv("MAX_PAPERS", "10"))
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ko")
    
    # PubMed API URL
    PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

config = Config() 