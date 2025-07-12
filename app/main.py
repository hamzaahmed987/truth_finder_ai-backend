<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TruthFinder API",
    description="AI-powered news analysis and fact-checking service",
    version="1.0.0"
)

# CORS config – adjust origins when you go live
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with allowed frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Health Check Endpoints -------------------

@app.get("/")
async def root():
    return {"message": "TruthFinder API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TruthFinder API"}

# ------------------- Routes -------------------

from app.routes.fact_check import router as fact_check_router
app.include_router(fact_check_router, prefix="/api/v1", tags=["fact-check"])

# ------------------- Error Handlers -------------------

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url.path)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)}
    )

# ------------------- Run Server -------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
=======
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import AnalysisRequest, AnalysisResponse, AgentAnalysisRequest, AgentAnalysisResponse
from .utils import analyze_news
from .agents import news_agent, multi_agent_system

app = FastAPI()

# ✅ CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://truthfinder-df2ca88ig-hamzaahmed987s-projects.vercel.app",             
        "https://truthfinder-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],       # Allow all headers including Content-Type
)

# ✅ News analysis endpoint
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_news_endpoint(request: AnalysisRequest):
    try:
        result = analyze_news(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ AI Agent: single agent analysis
@app.post("/agent/analyze", response_model=AgentAnalysisResponse)
async def agent_analyze_endpoint(request: AgentAnalysisRequest):
    try:
        result = await news_agent.analyze_news_advanced(
            content=request.content,
            language=request.language or "english"
        )
        return AgentAnalysisResponse(**result.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ AI Agent: multi-agent system
@app.post("/agent/multi-analyze")
async def multi_agent_analyze_endpoint(request: AgentAnalysisRequest):
    try:
        results = await multi_agent_system.analyze_with_multiple_agents(
            content=request.content,
            language=request.language or "english"
        )

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

# ✅ Check status of the agent system
@app.get("/agent/status")
async def agent_status():
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

# ✅ Root endpoint
@app.get("/")
def home():
    return {
        "status": "API is working!",
        "docs": "/docs",
        "agent_endpoints": "/agent/analyze"
    }























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


>>>>>>> a4e33e179d3b70acd84f84b3ab035167bb14adb7
