import os
import httpx
import json
from dotenv import load_dotenv
from app.services.tools import TRUTHFINDER_TOOLS
from app.services.supabase_chat import get_chat_history  # NEW IMPORT

load_dotenv()
GEMINI_API_KEY = os.getenv("gemini_api_key")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

GREETING_KEYWORDS = ["hello", "hi", "hey", "salaam", "assalam", "greetings"]
NEWS_EVENT_KEYWORDS = [
    "news", "breaking", "happened", "event", "incident", "attack", "war", "earthquake", "election",
    "trending", "protest", "riot", "conflict", "explosion", "disaster", "crisis", "shooting", "flood",
    "storm", "fire", "accident", "strike", "emergency"
]
PERSONAL_DATA_KEYWORDS = [
    "my name", "i am", "i'm", "my age", "my birthday", "my location", "i live", "i work", 
    "my job", "my hobby", "my favorite", "i like", "i love", "remember", "what did i tell you",
    "what's my", "what is my", "do you remember", "recall", "my information"
]

from app.services.tools import search_twitter

# ------------------------ 🔧 Sub-Agent: Fact-Checker ------------------------
async def factcheck_agent(news_text: str) -> str:
    prompt = f"""
You are a fact-checking AI agent. Analyze the following news and respond if it's real, fake, biased, or misleading. 
Also give a short reasoning for your conclusion.

News:
'''{news_text}'''

Give final verdict and explain why.
"""
    return await call_gemini_api(prompt)

# ------------------------ ✂️ Sub-Agent: Summarizer ------------------------
async def summarizer_agent(text: str) -> str:
    prompt = f"""
You are a summarizer agent. Your task is to summarize the following article or news text into a short and clear summary.

Text:
'''{text}'''

Return a 3-5 sentence summary.
"""
    return await call_gemini_api(prompt)

# ------------------------ 📰 Sub-Agent: News Event Analyzer ------------------------
async def news_event_agent(user_message: str) -> str:
    keywords = user_message
    tweets = await search_twitter(keywords, max_results=10)
    twitter_context = "\n\n".join([
        f"Tweet by @{t.author_username}: {t.text}" for t in tweets
    ]) if tweets else "No relevant tweets found."
    prompt = (
        "You are TruthFinder, an AI assistant that analyzes news events using both news and social media data. "
        "Below is a user question about a recent event, and some recent tweets about the topic. "
        "Use both sources to provide a comprehensive, up-to-date answer.\n\n"
        f"User question: {user_message}\n\n"
        f"Recent tweets:\n{twitter_context}\n\n"
        "Answer:"
    )
    return await call_gemini_api(prompt)

# ------------------------ 🔁 Utility: Gemini API Caller ------------------------
async def call_gemini_api(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(GEMINI_URL, json=payload)
            res.raise_for_status()
            data = res.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            return text or "Sorry, I couldn't process this request."
    except:
        return "Sorry, this topic seems too sensitive for the AI to respond to. Please try rephrasing."

# ------------------------ 🤖 TruthFinder Agent & Orchestrator ------------------------
class TruthFinderAgent:
    def __init__(self, tools):
        self.tools = {getattr(tool, 'name', tool.__class__.__name__): tool for tool in tools}

    async def handle(self, user_input: str, tool_name: str = None, **kwargs):
        if tool_name and tool_name in self.tools:
            tool = self.tools[tool_name]
            return await tool(**kwargs)
        return await multi_agent_orchestrator(user_input)

class MultiAgentOrchestrator:
    def __init__(self):
        self.tools = TRUTHFINDER_TOOLS
        self.agent = TruthFinderAgent(self.tools)

    async def analyze_news(self, content: str, language: str = "english") -> dict:
        try:
            fact_check = await factcheck_agent(content)
            summary = await summarizer_agent(content)
            return {
                "fact_check": fact_check,
                "summary": summary,
                "language": language,
                "status": "completed"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

main_agent = TruthFinderAgent(TRUTHFINDER_TOOLS)

# ------------------------ 🧠 Final Orchestrator Function ------------------------
async def multi_agent_orchestrator(user_message: str, user_id: str = None) -> str:
    lower_msg = user_message.lower()

    if user_id:
        memory = await get_chat_history(user_id)
        if memory:
            memory_text = "\n".join([f"{m['role'].capitalize()}: {m['message']}" for m in memory])
            user_message = f"Here is chat history:\n{memory_text}\n\nNow respond to this:\n{user_message}"

    if any(k in lower_msg for k in GREETING_KEYWORDS):
        return "Hello! 👋 I'm TruthFinder, your friendly AI assistant! I can help you with news analysis, fact-checking, general questions, or just chat about anything you'd like. What's on your mind today?"
    if any(k in lower_msg for k in ["who are you", "about you", "yourself"]):
        return (
            "I'm TruthFinder, your friendly AI assistant created by Hamza Ahmed! 🤖✨ "
            "I specialize in news analysis, fact-checking, and misinformation detection, but I'm also here for general conversations and to help with personal information. "
            "I can remember details you share with me and help you with news, current events, or just chat about anything you'd like. "
            "Think of me as your knowledgeable friend who's great at analyzing information and having engaging conversations!"
        )
    elif any(k in lower_msg for k in NEWS_EVENT_KEYWORDS):
        return await news_event_agent(user_message)
    elif any(k in lower_msg for k in ["summarize", "summary", "short version", "tl;dr"]):
        return await main_agent.handle(user_message, tool_name="summarize_news", news_text=user_message)
    elif any(k in lower_msg for k in ["fact check", "is it true", "verify", "real or fake"]):
        return await main_agent.handle(user_message, tool_name="fact_checker", claim=user_message)
    elif any(k in lower_msg for k in ["bias", "political bias", "tone", "sentiment"]):
        return await main_agent.handle(user_message, tool_name="analyze_sentiment", text=user_message)
    elif any(k in lower_msg for k in ["keywords", "extract", "entities"]):
        return await main_agent.handle(user_message, tool_name="extract_keywords", text=user_message)
    elif any(k in lower_msg for k in ["statistic", "number", "verify stat"]):
        return await main_agent.handle(user_message, tool_name="verify_stat", stat=user_message)
    elif any(k in lower_msg for k in ["report", "generate report", "final report"]):
        summary = await main_agent.handle(user_message, tool_name="summarize_news", news_text=user_message)
        verdict = await main_agent.handle(user_message, tool_name="fact_checker", claim=user_message)
        keywords = await main_agent.handle(user_message, tool_name="extract_keywords", text=user_message)
        return await main_agent.handle(user_message, tool_name="generate_report", summary=summary, verdict=verdict, keywords=keywords)
    elif any(k in lower_msg for k in ["twitter", "tweet", "social media"]):
        return await main_agent.handle(user_message, tool_name="search_twitter", keyword=user_message)
    elif any(k in lower_msg for k in PERSONAL_DATA_KEYWORDS):
        # Handle personal data queries - let the AI use conversation history
        prompt = (
            "You are TruthFinder, a friendly AI assistant. The user is asking about personal information. "
            "Use the conversation history to provide accurate information about what they've shared with you. "
            "If they're sharing new personal information, acknowledge it warmly. "
            "If they're asking about their personal data, provide it naturally from the conversation history. "
            "Be conversational and helpful. Never say you don't have access to their information if it's in the conversation.\n"
            f"User: {user_message}\nAssistant:"
        )
        return await call_gemini_api(prompt)
    else:
        prompt = (
            "You are TruthFinder, a friendly and helpful AI assistant. You can discuss news, current events, personal topics, "
            "and general questions. You have access to the user's chat history and personal information they've shared. "
            "If they ask about their personal data, provide it naturally from the conversation history. "
            "Be conversational, helpful, and engaging. You can analyze news, fact-check information, and have general conversations. "
            "Never say you don't have access to personal data if it's in the conversation history.\n"
            f"User: {user_message}\nAssistant:"
        )
        return await call_gemini_api(prompt)


















































# import os
# import httpx
# import json
# from dotenv import load_dotenv
# from app.services.tools import TRUTHFINDER_TOOLS

# load_dotenv()
# GEMINI_API_KEY = os.getenv("gemini_api_key")

# GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# # Add greeting keywords
# GREETING_KEYWORDS = ["hello", "hi", "hey", "salaam", "assalam", "greetings"]

# # Add news event keywords for intent detection
# NEWS_EVENT_KEYWORDS = [
#     "news", "breaking", "happened", "event", "incident", "attack", "war", "earthquake", "election", "trending", "protest", "riot", "conflict", "explosion", "disaster", "crisis", "shooting", "flood", "storm", "fire", "accident", "strike", "emergency"
# ]

# from app.services.tools import search_twitter

# # ------------------------ 🔧 Sub-Agent: Fact-Checker ------------------------
# async def factcheck_agent(news_text: str) -> str:
#     prompt = f"""
# You are a fact-checking AI agent. Analyze the following news and respond if it's real, fake, biased, or misleading. 
# Also give a short reasoning for your conclusion.

# News:
# '''{news_text}'''

# Give final verdict and explain why.
# """
#     return await call_gemini_api(prompt)

# # ------------------------ ✂️ Sub-Agent: Summarizer ------------------------
# async def summarizer_agent(text: str) -> str:
#     prompt = f"""
# You are a summarizer agent. Your task is to summarize the following article or news text into a short and clear summary.

# Text:
# '''{text}'''

# Return a 3-5 sentence summary.
# """
#     return await call_gemini_api(prompt)

# # ------------------------ 📰 Sub-Agent: News Event Analyzer ------------------------
# async def news_event_agent(user_message: str) -> str:
#     """
#     Sub-agent for news event queries: fetches Twitter data and combines it with LLM analysis.
#     """
#     # Extract keywords (simple approach: use the user message directly)
#     keywords = user_message
#     # Fetch recent tweets
#     tweets = await search_twitter(keywords, max_results=10)
#     # Format tweets for LLM context
#     if tweets:
#         twitter_context = "\n\n".join([
#             f"Tweet by @{t.author_username}: {t.text}" for t in tweets
#         ])
#     else:
#         twitter_context = "No relevant tweets found."
#     # Compose prompt for LLM
#     prompt = (
#         "You are TruthFinder, an AI assistant that analyzes news events using both news and social media data. "
#         "Below is a user question about a recent event, and some recent tweets about the topic. "
#         "Use both sources to provide a comprehensive, up-to-date answer.\n\n"
#         f"User question: {user_message}\n\n"
#         f"Recent tweets:\n{twitter_context}\n\n"
#         "Answer:"
#     )
#     return await call_gemini_api(prompt)

# # ------------------------ 🔁 Utility: Gemini API Caller ------------------------
# async def call_gemini_api(prompt: str) -> str:
#     payload = {
#         "contents": [{"parts": [{"text": prompt}]}]
#     }
#     try:
#         async with httpx.AsyncClient() as client:
#             res = await client.post(GEMINI_URL, json=payload)
#             try:
#                 res.raise_for_status()
#             except httpx.HTTPStatusError as e:
#                 return "Sorry, this topic seems too sensitive for the AI to respond to. Please try rephrasing or ask about something else."
#             data = res.json()
#             text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
#             if not text:
#                 return "Sorry, this topic seems too sensitive for the AI to respond to. Please try rephrasing or ask about something else."
#             return text
#     except Exception as e:
#         return "Sorry, this topic seems too sensitive for the AI to respond to. Please try rephrasing or ask about something else."

# # Main TruthFinderAgent class
# class TruthFinderAgent:
#     def __init__(self, tools):
#         self.tools = {getattr(tool, 'name', tool.__class__.__name__): tool for tool in tools}

#     async def handle(self, user_input: str, tool_name: str = None, **kwargs):
#         if tool_name and tool_name in self.tools:
#             tool = self.tools[tool_name]
#             return await tool(**kwargs)
#         # Default: Use orchestrator logic to pick tool
#         return await multi_agent_orchestrator(user_input)

# # MultiAgentOrchestrator class for compatibility
# class MultiAgentOrchestrator:
#     def __init__(self):
#         self.tools = TRUTHFINDER_TOOLS
#         self.agent = TruthFinderAgent(self.tools)
    
#     async def analyze_news(self, content: str, language: str = "english") -> dict:
#         """Analyze news content using multiple agents"""
#         try:
#             # Get fact check
#             fact_check = await factcheck_agent(content)
            
#             # Get summary
#             summary = await summarizer_agent(content)
            
#             return {
#                 "fact_check": fact_check,
#                 "summary": summary,
#                 "language": language,
#                 "status": "completed"
#             }
#         except Exception as e:
#             return {
#                 "error": str(e),
#                 "status": "failed"
#             }

# # Instantiate the main agent with all tools
# main_agent = TruthFinderAgent(TRUTHFINDER_TOOLS)

# # Update orchestrator to use tools and allow handoff
# async def multi_agent_orchestrator(user_message: str) -> str:
#     # Example intent detection (expand as needed)
#     lower_msg = user_message.lower()
#     if any(k in lower_msg for k in GREETING_KEYWORDS):
#         return "Hello! 👋 I'm TruthFinder. How can I help you with news, fact-checking, or analysis today?"
#     if any(k in lower_msg for k in ["who are you", "about you", "yourself"]):
#         return (
#             "I'm Truth Finder Agent, made by Hamza Ahmed. "
#             "I help you fact-check news and analyze information using advanced AI and social media data. "
#             "Ask me about any news, and I'll help you verify its credibility!"
#         )
#     # News event intent detection and handoff
#     elif any(k in lower_msg for k in NEWS_EVENT_KEYWORDS):
#         return await news_event_agent(user_message)
#     elif any(k in lower_msg for k in ["summarize", "summary", "short version", "tl;dr"]):
#         return await main_agent.handle(user_message, tool_name="summarize_news", news_text=user_message)
#     elif any(k in lower_msg for k in ["fact check", "is it true", "verify", "real or fake"]):
#         return await main_agent.handle(user_message, tool_name="fact_checker", claim=user_message)
#     elif any(k in lower_msg for k in ["bias", "political bias", "tone", "sentiment"]):
#         return await main_agent.handle(user_message, tool_name="analyze_sentiment", text=user_message)
#     elif any(k in lower_msg for k in ["keywords", "extract", "entities"]):
#         return await main_agent.handle(user_message, tool_name="extract_keywords", text=user_message)
#     elif any(k in lower_msg for k in ["statistic", "number", "verify stat"]):
#         return await main_agent.handle(user_message, tool_name="verify_stat", stat=user_message)
#     elif any(k in lower_msg for k in ["report", "generate report", "final report"]):
#         summary = await main_agent.handle(user_message, tool_name="summarize_news", news_text=user_message)
#         verdict = await main_agent.handle(user_message, tool_name="fact_checker", claim=user_message)
#         keywords = await main_agent.handle(user_message, tool_name="extract_keywords", text=user_message)
#         return await main_agent.handle(user_message, tool_name="generate_report", summary=summary, verdict=verdict, keywords=keywords)
#     elif any(k in lower_msg for k in ["twitter", "tweet", "social media"]):
#         return await main_agent.handle(user_message, tool_name="search_twitter", keyword=user_message)
#     else:
#         # Fallback: Use Gemini LLM for general chat
#         prompt = (
#             "You are TruthFinder, an AI assistant that analyzes news, detects misinformation, summarizes content, "
#             "and explains findings. You never mention Google or Gemini. Stay in character as TruthFinder.\n"
#             f"User: {user_message}\nAssistant:"
#         )
#         return await call_gemini_api(prompt) 