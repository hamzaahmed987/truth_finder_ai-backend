import os
import httpx
import json
from dotenv import load_dotenv
from app.services.tools import TRUTHFINDER_TOOLS
from app.services.supabase_chat import get_chat_history, save_chat_message
from app.services.tools import search_twitter

load_dotenv()
GEMINI_API_KEY = os.getenv("gemini_api_key")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

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
    twitter_context = "\n\n".join([f"Tweet by @{t.author_username}: {t.text}" for t in tweets]) if tweets else "No relevant tweets found."
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
            return text or "I couldn't process that request. Could you try rephrasing?"
    except Exception as e:
        print(f"🔵 GEMINI API ERROR: {e}")
        return "I'm having trouble processing that right now. Could you try again?"

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
    original_message = user_message

    memory = []
    if user_id:
        print(f"🔵 ORCHESTRATOR: Getting chat history for user_id={user_id}")
        memory = await get_chat_history(user_id)
        print(f"🔵 ORCHESTRATOR: Memory count={len(memory)}")

    if memory:
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in memory[-20:]])
        prompt = (
            "You are TruthFinder, a friendly and helpful AI assistant. You can discuss news, current events, personal topics, "
            "and general questions. You have access to the user's complete chat history and personal information they've shared. "
            "If they ask about their personal data, provide it naturally from the conversation history. "
            "Be conversational, helpful, and engaging. You can analyze news, fact-check information, and have general conversations. "
            "Never say you don't have access to personal data if it's in the conversation history. "
            "Remember everything the user has told you and use that information when relevant.\n\n"
            f"Complete conversation history:\n{history_text}\n\n"
            f"User: {original_message}\nAssistant:"
        )
    else:
        prompt = (
            "You are TruthFinder, a friendly and helpful AI assistant. You can discuss news, current events, personal topics, "
            "and general questions. Be conversational, helpful, and engaging. You can analyze news, fact-check information, and have general conversations.\n"
            f"User: {original_message}\nAssistant:"
        )

    agent_reply = await call_gemini_api(prompt)

    # ✅ Save agent reply directly here
    if user_id and agent_reply:
        print(f"🔵 Saving agent reply inside orchestrator for user_id={user_id}")
        await save_chat_message(user_id=user_id, role="agent", message=agent_reply)

    return agent_reply
