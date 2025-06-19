from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from medical_search_service import MedicalSearchService
import uvicorn

# FastAPI 앱 초기화
app = FastAPI(
    title="PubMed 의료 검색 API",
    description="질병명이나 검사 수치를 기반으로 PubMed 논문을 검색하고 요약하는 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
service = MedicalSearchService()

# 요청 모델
class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10

class PaperDetailRequest(BaseModel):
    pmid: str

# 응답 모델
class EntityResponse(BaseModel):
    text: str
    type: str
    value: Optional[float] = None
    unit: Optional[str] = None
    normal_range: Optional[str] = None

class PaperResponse(BaseModel):
    title: str
    authors: List[str]
    journal: str
    publication_date: str
    pmid: str
    pubmed_url: str
    doi: str
    ai_summary: str
    original_abstract: str
    relevance_score: float

class SearchResponse(BaseModel):
    user_input: str
    search_query: str
    detected_entities: List[EntityResponse]
    interpretations: List[str]
    papers: List[PaperResponse]
    total_papers_found: int
    overall_summary: str
    processing_time: float
    timestamp: str

# API 엔드포인트
@app.get("/", response_class=HTMLResponse)
async def root():
    """API 메인 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PubMed 의료 검색 API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #27ae60; font-weight: bold; }
            code { background: #34495e; color: white; padding: 2px 6px; border-radius: 3px; }
            .example { background: #e8f4fd; padding: 10px; border-left: 4px solid #3498db; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 PubMed 의료 검색 API</h1>
            <p>질병명이나 검사 수치를 기반으로 관련 PubMed 논문을 검색하고 요약하는 API입니다.</p>
            
            <h2>📚 API 엔드포인트</h2>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/search</code> - 의료 논문 검색
                <div class="example">
                    <strong>예시 요청:</strong><br>
                    <code>{"query": "CRP 수치 12.5", "max_results": 10}</code>
                </div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/search</code> - 간단한 검색 (쿼리 파라미터)
                <div class="example">
                    <strong>예시:</strong><br>
                    <code>/search?q=HbA1c 7.8 당뇨병&max_results=5</code>
                </div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/paper-detail</code> - 특정 논문 상세 정보
                <div class="example">
                    <strong>예시 요청:</strong><br>
                    <code>{"pmid": "12345678"}</code>
                </div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/similar/{pmid}</code> - 유사 논문 검색
                <div class="example">
                    <strong>예시:</strong><br>
                    <code>/similar/12345678?max_results=5</code>
                </div>
            </div>
            
            <h2>📖 문서</h2>
            <p>
                <a href="/docs" target="_blank">🔗 Swagger UI 문서</a><br>
                <a href="/redoc" target="_blank">🔗 ReDoc 문서</a>
            </p>
            
            <h2>💡 사용 예시</h2>
            <div class="example">
                <strong>검색 예시:</strong><br>
                • "CRP 수치 12.5"<br>
                • "HbA1c 7.8 당뇨병"<br>
                • "혈압 180/120 고혈압"<br>
                • "파킨슨병 levodopa 반응"<br>
                • "콜레스테롤 250 심혈관질환"
            </div>
            
            <h2>⚠️ 주의사항</h2>
            <p>
                • 이 API는 의학적 조언을 제공하지 않습니다.<br>
                • 건강 관련 결정은 반드시 의료 전문가와 상담하세요.<br>
                • 검색 결과는 참고용으로만 활용하세요.
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """의료 논문 검색 (POST)"""
    try:
        results = service.search_medical_papers(request.query, request.max_results)
        return SearchResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@app.get("/search")
async def search_papers_get(
    q: str = Query(..., description="검색 쿼리"),
    max_results: int = Query(10, description="최대 결과 수", ge=1, le=50)
):
    """의료 논문 검색 (GET - 간단한 검색용)"""
    try:
        results = service.search_medical_papers(q, max_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@app.post("/paper-detail")
async def get_paper_detail(request: PaperDetailRequest):
    """특정 논문의 상세 정보 조회"""
    try:
        paper = service.get_paper_detail(request.pmid)
        if not paper:
            raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다.")
        return paper
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"논문 조회 중 오류가 발생했습니다: {str(e)}")

@app.get("/similar/{pmid}")
async def get_similar_papers(
    pmid: str,
    max_results: int = Query(5, description="최대 결과 수", ge=1, le=20)
):
    """특정 논문과 유사한 논문 검색"""
    try:
        similar_papers = service.search_similar_papers(pmid, max_results)
        return {
            "pmid": pmid,
            "similar_papers": similar_papers,
            "count": len(similar_papers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사 논문 검색 중 오류가 발생했습니다: {str(e)}")

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "PubMed Medical Search API",
        "version": "1.0.0"
    }

@app.get("/stats")
async def get_stats():
    """API 통계 정보"""
    return {
        "api_name": "PubMed 의료 검색 API",
        "version": "1.0.0",
        "supported_entities": [
            "검사 수치 (CRP, HbA1c, 혈압 등)",
            "질병명 (당뇨병, 고혈압, 파킨슨병 등)",
            "의료 용어"
        ],
        "features": [
            "PubMed 논문 검색",
            "의료 개체 인식",
            "AI 기반 논문 요약",
            "수치 해석",
            "건강 팁 제공"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 