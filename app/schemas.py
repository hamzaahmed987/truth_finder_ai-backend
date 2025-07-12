from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AnalysisRequest(BaseModel):
    content: str

class AnalysisResponse(BaseModel):
    is_fake: bool
    confidence: float
    analysis: str
    sources: List[str] = []
    public_sentiment: Optional[str] = None
    detected_language: Optional[str] = None
    sample_tweets: Optional[List[str]] = None

# New schemas for AI Agent
class AgentAnalysisRequest(BaseModel):
    content: str
    language: Optional[str] = "english"

class AgentAnalysisResponse(BaseModel):
    analysis: str
    confidence: float
    verdict: str
    language: str
    timestamp: str
    agent_version: str
    error: Optional[str] = None

class MultiAgentResponse(BaseModel):
    news_analysis: Dict[str, Any]
    # Add more agent results as needed