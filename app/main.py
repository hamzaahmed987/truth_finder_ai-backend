from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AnalysisRequest, AnalysisResponse, AgentAnalysisRequest, AgentAnalysisResponse
from .utils import analyze_news
from .agents import news_agent, multi_agent_system

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    # Add your production domains here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_news_endpoint(request: AnalysisRequest):
    try:
        result = analyze_news(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New AI Agent endpoints
@app.post("/agent/analyze", response_model=AgentAnalysisResponse)
async def agent_analyze_endpoint(request: AgentAnalysisRequest):
    """Advanced analysis using AI Agent"""
    try:
        result = await news_agent.analyze_news_advanced(
            content=request.content,
            language=request.language or "english"
        )
        return AgentAnalysisResponse(**result.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/multi-analyze")
async def multi_agent_analyze_endpoint(request: AgentAnalysisRequest):
    """Multi-agent analysis system"""
    try:
        results = await multi_agent_system.analyze_with_multiple_agents(
            content=request.content,
            language=request.language or "english"
        )
        # If results contains any custom objects, convert them to dicts
        def convert(obj):
            if hasattr(obj, "dict"):
                return obj.dict()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            return obj
        if isinstance(results, dict):
            results = {k: convert(v) for k, v in results.items()}
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/status")
async def agent_status():
    """Check agent system status"""
    return {
        "status": "active",
        "agents": ["news_analysis"],
        "version": "1.0",
        "capabilities": [
            "web_search",
            "sentiment_analysis", 
            "fact_checking",
            "source_credibility",
            "twitter_sentiment"
        ]
    }

@app.get("/")
def home():
    return {"status": "API is working!", "docs": "/docs", "agent_endpoints": "/agent/analyze"}
























# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional
# from .schemas import AnalysisRequest, AnalysisResponse
# from .utils import analyze_news

# app = FastAPI()

# # CORS Settings
# origins = [
#     "http://localhost:3000",
#     "http://localhost:8000",
#     # Add your production domains here
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.post("/analyze", response_model=AnalysisResponse)
# async def analyze_news_endpoint(request: AnalysisRequest):
#     try:
#         result = analyze_news(request.content)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# def home():
#     return {"status": "API is working!", "docs": "/docs"}














# ---------------









# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware  # <-- Add this
# from app.routes import router  # Assuming your route handlers are in app/routes.py

# app = FastAPI()

# # 🔐 CORS Settings — Add this block
# origins = [
#     "http://localhost:3000",  # Your Next.js frontend during development
#     # You can add other domains like:
#     # "https://yourdomain.com",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,         # Use ["*"] for dev if you want to allow everything
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include your API routes
# app.include_router(router)

# # Optional root endpoint for testing
# @app.get("/")
# def home():
#     return {"status": "API is working!"}






# -------------------


