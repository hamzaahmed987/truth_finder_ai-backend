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
