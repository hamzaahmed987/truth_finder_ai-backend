"""
Advanced AI Agents for News Analysis and Fact-Checking

This module provides comprehensive news analysis capabilities using multiple AI agents
and external APIs for fact-checking, sentiment analysis, and credibility assessment.
"""

import os
import asyncio
import re
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

# Third-party imports with proper error handling
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available. Install with: pip install google-generativeai")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Requests library not available. Install with: pip install requests")

try:
    import tweepy
    from textblob import TextBlob
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    logging.warning("Twitter libraries not available. Install with: pip install tweepy textblob")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerdictType(Enum):
    """Enumeration for news verification verdicts"""
    REAL = "REAL"
    FAKE = "FAKE"
    PROPAGANDA = "PROPAGANDA"
    SUSPICIOUS = "SUSPICIOUS"
    ERROR = "ERROR"


class SentimentType(Enum):
    """Enumeration for sentiment analysis results"""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


@dataclass
class AnalysisResult:
    """Data class for structured analysis results"""
    analysis: str
    confidence: int
    verdict: VerdictType
    language: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_version: str = "2.0"
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebSearchResult:
    """Data class for web search results"""
    title: str
    url: str
    snippet: str
    relevance_score: float = 0.0


@dataclass
class TwitterSentimentResult:
    """Data class for Twitter sentiment analysis results"""
    sentiment: SentimentType
    average_polarity: float
    tweet_count: int
    sample_tweets: List[str]
    summary: Optional[str] = None


class ConfigurationManager:
    """Manages configuration and API keys"""
    
    def __init__(self):
        self.config = {
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "google_search_api_key": os.getenv("GOOGLE_SEARCH_API_KEY"),
            "google_search_engine_id": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
            "twitter_api_key": os.getenv("TWITTER_API_KEY"),
            "twitter_api_secret": os.getenv("TWITTER_API_SECRET"),
            "twitter_access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
            "twitter_access_secret": os.getenv("TWITTER_ACCESS_SECRET"),
            "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
        }
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration and log warnings for missing keys"""
        missing_keys = []
        
        if not self.config["google_api_key"]:
            missing_keys.append("GOOGLE_API_KEY")
        
        if not self.config["google_search_api_key"]:
            missing_keys.append("GOOGLE_SEARCH_API_KEY")
        
        if not self.config["google_search_engine_id"]:
            missing_keys.append("GOOGLE_SEARCH_ENGINE_ID")
        
        if missing_keys:
            logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
            logger.info("Some features may not work without proper API configuration")
    
    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value"""
        return self.config.get(key)
    
    def is_configured(self, service: str) -> bool:
        """Check if a service is properly configured"""
        config_map = {
            "gemini": bool(self.config["google_api_key"]),
            "web_search": bool(self.config["google_search_api_key"] and self.config["google_search_engine_id"]),
            "twitter": bool(self.config["twitter_bearer_token"] or 
                          (self.config["twitter_api_key"] and self.config["twitter_api_secret"]))
        }
        return config_map.get(service, False)


class GeminiClient:
    """Wrapper for Google Gemini API with error handling"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with proper error handling"""
        if not GEMINI_AVAILABLE:
            logger.error("Google Generative AI library not available")
            return
        
        api_key = self.config_manager.get_config("google_api_key")
        if not api_key:
            logger.error("Google API key not configured")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel("models/gemini-1.5-flash")
            logger.info("✅ Gemini API configured successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Gemini client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Gemini client is available"""
        return self.client is not None
    
    async def generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using Gemini API"""
        if not self.is_available():
            return None
        
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None


class WebSearchClient:
    """Client for Google Custom Search API"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
    
    def is_available(self) -> bool:
        """Check if web search is available"""
        return self.config_manager.is_configured("web_search")
    
    async def search(self, query: str, max_results: int = 5) -> List[WebSearchResult]:
        """Perform web search and return structured results"""
        if not self.is_available():
            logger.warning("Web search not configured")
            return []
        
        if not REQUESTS_AVAILABLE:
            logger.error("Requests library not available")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config_manager.get_config("google_search_api_key"),
                'cx': self.config_manager.get_config("google_search_engine_id"),
                'q': query,
                'num': max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'items' in data:
                for item in data['items']:
                    result = WebSearchResult(
                        title=item.get('title', ''),
                        url=item.get('link', ''),
                        snippet=item.get('snippet', '')
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []


class TwitterClient:
    """Client for Twitter API with sentiment analysis"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twitter client"""
        if not TWITTER_AVAILABLE:
            logger.warning("Twitter libraries not available")
            return
        
        bearer_token = self.config_manager.get_config("twitter_bearer_token")
        api_key = self.config_manager.get_config("twitter_api_key")
        api_secret = self.config_manager.get_config("twitter_api_secret")
        
        if not bearer_token and not (api_key and api_secret):
            logger.warning("Twitter API not configured")
            return
        
        try:
            if bearer_token:
                self.client = tweepy.Client(bearer_token=bearer_token)
            else:
                auth = tweepy.OAuthHandler(api_key, api_secret)
                auth.set_access_token(
                    self.config_manager.get_config("twitter_access_token"),
                    self.config_manager.get_config("twitter_access_secret")
                )
                self.client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=self.config_manager.get_config("twitter_access_token"),
                    access_token_secret=self.config_manager.get_config("twitter_access_secret")
                )
            logger.info("✅ Twitter API configured successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Twitter client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Twitter client is available"""
        return self.client is not None
    
    async def get_sentiment(self, topic: str, max_tweets: int = 20) -> Optional[TwitterSentimentResult]:
        """Get Twitter sentiment for a topic"""
        if not self.is_available():
            return None
        
        try:
            query = f"{topic} -is:retweet lang:en"
            tweets = self.client.search_recent_tweets(
                query=query, 
                max_results=max_tweets, 
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not tweets.data:
                return None
            
            tweet_texts = [tweet.text for tweet in tweets.data[:10]]
            
            # Sentiment analysis using TextBlob
            sentiments = [TextBlob(text).sentiment.polarity for text in tweet_texts]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            # Determine sentiment label
            if avg_sentiment > 0.1:
                sentiment_label = SentimentType.POSITIVE
            elif avg_sentiment < -0.1:
                sentiment_label = SentimentType.NEGATIVE
            else:
                sentiment_label = SentimentType.NEUTRAL
            
            return TwitterSentimentResult(
                sentiment=sentiment_label,
                average_polarity=avg_sentiment,
                tweet_count=len(tweet_texts),
                sample_tweets=tweet_texts
            )
            
        except Exception as e:
            logger.error(f"Twitter sentiment analysis failed: {e}")
            return None


class NewsAnalysisAgent:
    """Advanced AI Agent for comprehensive news analysis"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.gemini_client = GeminiClient(self.config_manager)
        self.web_search_client = WebSearchClient(self.config_manager)
        self.twitter_client = TwitterClient(self.config_manager)
        self.analysis_history: List[Dict[str, Any]] = []
    
    def _get_prompts(self, content: str, language: str = "english") -> tuple[str, str]:
        """Get system and user prompts based on language"""
        if language == "urdu_hindi":
            system_prompt = """
            You are an expert news verification AI agent. Your role is to:
            1. Analyze news content for accuracy and credibility
            2. Check facts against reliable sources
            3. Evaluate source credibility
            4. Analyze public sentiment
            5. Detect propaganda and misinformation patterns
            6. Provide detailed, evidence-based analysis
            
            Always be thorough, objective, and provide clear reasoning for your conclusions.
            Respond in Urdu/Hindi with emojis and friendly language.
            """
            
            user_prompt = f"""
            🔍 **ADVANCED NEWS VERIFICATION ANALYSIS** 🔍
            
            Ye news ko comprehensive analysis karo: "{content}"
            
            **REQUIRED ANALYSIS STEPS:**
            1. 📰 News content ko summarize karo
            2. 🔍 Web search karo related information ke liye
            3. ✅ Fact-checking karo reliable sources se
            4. 📊 Source credibility evaluate karo
            5. 💭 Public sentiment analyze karo Twitter se
            6. ⚠️ Propaganda/misinformation patterns detect karo
            7. 🎯 Final verdict with confidence level
            
            **RESPONSE FORMAT:**
            - Detailed analysis with evidence
            - Confidence score (0-100)
            - Risk factors identified
            - Recommendations
            
            Use all available tools for comprehensive analysis.
            """
        else:
            system_prompt = """
            You are an expert news verification AI agent. Your role is to:
            1. Analyze news content for accuracy and credibility
            2. Check facts against reliable sources
            3. Evaluate source credibility
            4. Analyze public sentiment
            5. Detect propaganda and misinformation patterns
            6. Provide detailed, evidence-based analysis
            
            Always be thorough, objective, and provide clear reasoning for your conclusions.
            """
            
            user_prompt = f"""
            🔍 **ADVANCED NEWS VERIFICATION ANALYSIS** 🔍
            
            Please perform comprehensive analysis of this news: "{content}"
            
            **REQUIRED ANALYSIS STEPS:**
            1. 📰 Summarize the news content
            2. 🔍 Search web for related information
            3. ✅ Fact-check against reliable sources
            4. 📊 Evaluate source credibility
            5. 💭 Analyze public sentiment from Twitter
            6. ⚠️ Detect propaganda/misinformation patterns
            7. 🎯 Provide final verdict with confidence level
            
            **RESPONSE FORMAT:**
            - Detailed analysis with evidence
            - Confidence score (0-100)
            - Risk factors identified
            - Recommendations
            
            Use all available tools for comprehensive analysis.
            """
        
        return system_prompt, user_prompt
    
    def _extract_confidence_score(self, response: str) -> int:
        """Extract confidence score from AI response"""
        try:
            confidence_match = re.search(r'confidence[:\s]*(\d+)', response.lower())
            if confidence_match:
                confidence = int(confidence_match.group(1))
                return max(0, min(100, confidence))  # Clamp between 0-100
        except (ValueError, AttributeError):
            pass
        return 50  # Default confidence
    
    def _determine_verdict(self, response: str) -> VerdictType:
        """Determine verdict based on response content"""
        response_lower = response.lower()
        
        # Keywords for different verdicts
        fake_keywords = ['fake', 'false', 'misinformation', 'untrue', 'jhoot', 'galat', 'incorrect']
        propaganda_keywords = ['propaganda', 'biased', 'agenda', 'misleading', 'partial', 'manipulated']
        real_keywords = ['real', 'true', 'verified', 'credible', 'sach', 'authentic', 'accurate']
        
        if any(word in response_lower for word in fake_keywords):
            return VerdictType.FAKE
        elif any(word in response_lower for word in propaganda_keywords):
            return VerdictType.PROPAGANDA
        elif any(word in response_lower for word in real_keywords):
            return VerdictType.REAL
        else:
            return VerdictType.SUSPICIOUS
    
    async def analyze_news_advanced(self, content: str, language: str = "english") -> AnalysisResult:
        """Advanced news analysis using AI agent"""
        try:
            if not self.gemini_client.is_available():
                return AnalysisResult(
                    analysis="Unable to perform analysis - Gemini API not configured",
                    confidence=0,
                    verdict=VerdictType.ERROR,
                    language=language,
                    error="Google API key not configured"
                )
            
            # Get prompts
            system_prompt, user_prompt = self._get_prompts(content, language)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate AI response
            ai_response = await self.gemini_client.generate_content(full_prompt)
            if not ai_response:
                return AnalysisResult(
                    analysis="Unable to generate AI response",
                    confidence=0,
                    verdict=VerdictType.ERROR,
                    language=language,
                    error="AI generation failed"
                )
            
            # Parse response
            confidence = self._extract_confidence_score(ai_response)
            verdict = self._determine_verdict(ai_response)
            
            # Create result
            result = AnalysisResult(
                analysis=ai_response,
                confidence=confidence,
                verdict=verdict,
                language=language
            )
            
            # Store in history
            self.analysis_history.append({
                "content": content,
                "analysis": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Agent analysis failed: {e}")
            return AnalysisResult(
                analysis="Unable to perform advanced analysis",
                confidence=0,
                verdict=VerdictType.ERROR,
                language=language,
                error=str(e)
            )
    
    async def search_web(self, query: str, max_results: int = 5) -> List[WebSearchResult]:
        """Search web for information"""
        return await self.web_search_client.search(query, max_results)
    
    async def analyze_sentiment(self, text: str) -> SentimentType:
        """Analyze sentiment of text using Gemini"""
        try:
            if not self.gemini_client.is_available():
                return SentimentType.NEUTRAL
            
            prompt = f"""
            Analyze the sentiment of the following text. Consider emotional language, tone, and overall message.
            Return only: POSITIVE, NEGATIVE, or NEUTRAL
            
            Text: {text}
            """
            
            response = await self.gemini_client.generate_content(prompt)
            if not response:
                return SentimentType.NEUTRAL
            
            response_clean = response.strip().upper()
            if "POSITIVE" in response_clean:
                return SentimentType.POSITIVE
            elif "NEGATIVE" in response_clean:
                return SentimentType.NEGATIVE
            else:
                return SentimentType.NEUTRAL
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return SentimentType.NEUTRAL
    
    async def fact_check(self, claim: str) -> Dict[str, Any]:
        """Fact-check a claim using web search and AI analysis"""
        try:
            if not self.gemini_client.is_available():
                return {
                    "error": "AI model not configured",
                    "claim": claim,
                    "verdict": VerdictType.ERROR
                }
            
            # Search for related information
            search_results = await self.search_web(claim, max_results=3)
            search_text = "\n\n".join([
                f"Title: {result.title}\nURL: {result.url}\nSnippet: {result.snippet}"
                for result in search_results
            ])
            
            # Use AI to analyze the claim against search results
            prompt = f"""
            Fact-check this claim: "{claim}"
            
            Here are the top web search results for this claim:
            {search_text}
            
            Please answer:
            1. Is this claim supported by reliable sources?
            2. Are there contradicting reports?
            3. What is the overall accuracy?
            4. Provide a confidence score (0-100).
            5. Give a short summary verdict (REAL/FAKE/PROPAGANDA/SUSPICIOUS).
            
            Be objective and evidence-based.
            """
            
            response = await self.gemini_client.generate_content(prompt)
            if not response:
                return {
                    "error": "AI analysis failed",
                    "claim": claim,
                    "verdict": VerdictType.ERROR
                }
            
            confidence = self._extract_confidence_score(response)
            verdict = self._determine_verdict(response)
            
            return {
                "claim": claim,
                "analysis": response,
                "confidence": confidence,
                "verdict": verdict,
                "sources": [result.url for result in search_results]
            }
            
        except Exception as e:
            logger.error(f"Fact-checking failed: {e}")
            return {
                "error": str(e),
                "claim": claim,
                "verdict": VerdictType.ERROR
            }
    
    async def evaluate_source_credibility(self, source: str) -> Dict[str, Any]:
        """Evaluate source credibility using AI analysis"""
        try:
            if not self.gemini_client.is_available():
                return {
                    "error": "AI model not configured",
                    "source": source,
                    "credibility_score": 0
                }
            
            prompt = f"""
            Evaluate the credibility of this news source: "{source}"
            
            Consider:
            1. Reputation and history
            2. Editorial standards
            3. Fact-checking practices
            4. Bias indicators
            5. Professional journalism standards
            
            Provide a credibility score (0-100) and detailed analysis.
            """
            
            response = await self.gemini_client.generate_content(prompt)
            if not response:
                return {
                    "error": "AI analysis failed",
                    "source": source,
                    "credibility_score": 0
                }
            
            credibility_score = self._extract_confidence_score(response)
            
            return {
                "source": source,
                "analysis": response,
                "credibility_score": credibility_score
            }
            
        except Exception as e:
            logger.error(f"Credibility analysis failed: {e}")
            return {
                "error": str(e),
                "source": source,
                "credibility_score": 0
            }
    
    async def get_twitter_sentiment(self, topic: str) -> Optional[TwitterSentimentResult]:
        """Get Twitter sentiment for a topic"""
        return await self.twitter_client.get_sentiment(topic)
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis history"""
        return self.analysis_history[-limit:] if self.analysis_history else []


class MultiAgentSystem:
    """System to coordinate multiple specialized agents"""
    
    def __init__(self):
        self.news_agent = NewsAnalysisAgent()
        self.agents = {
            "news_analysis": self.news_agent
        }
    
    async def analyze_with_multiple_agents(self, content: str, language: str = "english") -> Dict[str, Any]:
        """Run analysis with multiple specialized agents"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "language": language
        }
        
        try:
            # Run news analysis agent
            news_result = await self.news_agent.analyze_news_advanced(content, language)
            results["news_analysis"] = news_result
            
            # Run additional analysis tools concurrently
            tasks = [
                self.news_agent.fact_check(content),
                self.news_agent.analyze_sentiment(content),
                self.news_agent.search_web(content[:100], max_results=3),
                self.news_agent.get_twitter_sentiment(content[:50])
            ]
            
            fact_check_result, sentiment_result, search_results, twitter_result = await asyncio.gather(
                *tasks, return_exceptions=True
            )
            
            # Process results
            results["fact_checking"] = fact_check_result if not isinstance(fact_check_result, Exception) else {"error": str(fact_check_result)}
            results["sentiment_analysis"] = {"sentiment": sentiment_result} if not isinstance(sentiment_result, Exception) else {"error": str(sentiment_result)}
            results["web_search"] = {"results": search_results} if not isinstance(search_results, Exception) else {"error": str(search_results)}
            results["twitter_sentiment"] = twitter_result if not isinstance(twitter_result, Exception) else {"error": str(twitter_result)}
            
        except Exception as e:
            logger.error(f"Multi-agent analysis failed: {e}")
            results["error"] = str(e)
        
        return results


# Global instances
config_manager = ConfigurationManager()
news_agent = NewsAnalysisAgent()
multi_agent_system = MultiAgentSystem()


if __name__ == "__main__":
    async def test_agents():
        """Test the agents with a sample news article"""
        test_content = "Scientists discover a new species of deep-sea creatures in the Pacific Ocean"
        result = await news_agent.analyze_news_advanced(test_content, "english")
        print(f"Analysis Result: {result}")
    
    asyncio.run(test_agents())