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
async def news_event_agent(user_message: str, memory=None) -> str:
    keywords = user_message
    tweets = await search_twitter(keywords, max_results=10)
    twitter_context = "\n\n".join([f"Tweet by @{t.author_username}: {t.text}" for t in tweets]) if tweets else "No relevant tweets found."
    user_memory = ""
    if memory:
        user_msgs = [m['content'] for m in memory if m.get('role') == 'user']
        if user_msgs:
            user_memory = '\n'.join(user_msgs[-5:])
    prompt = (
        "You are TruthFinder, an AI assistant that analyzes news events using both news and social media data. "
        "Below is a user question, some of their previous messages, and recent tweets about the topic. "
        "Use all sources to provide a comprehensive, up-to-date answer. If the user asks about themselves, use their previous messages to answer.\n\n"
        f"User's previous messages:\n{user_memory}\n\n"
        f"User question: {user_message}\n\n"
        f"Recent tweets:\n{twitter_context}\n\n"
        "Answer:"
    )
    gemini_response = await call_gemini_api(prompt)
    # Fallback: If Gemini fails to answer and the question is about news, return tweets
    if not gemini_response or "not available" in gemini_response.lower() or "couldn't process" in gemini_response.lower():
        if any(word in user_message.lower() for word in ["news", "headline", "update", "event", "breaking"]):
            if tweets:
                tweets_text = "\n\n".join([f"@{t.author_username}: {t.text}" for t in tweets])
                return f"Gemini could not answer. Here are some recent tweets about '{user_message}':\n\n{tweets_text}"
            else:
                return "Gemini could not answer and no recent tweets were found about this topic."
    return gemini_response

# ------------------------ 🔁 Utility: Gemini API Caller ------------------------
async def call_gemini_api(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    import time
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(GEMINI_URL, json=payload)
            print(f"Gemini API status: {res.status_code}")
            print(f"Gemini API response: {res.text}")
            try:
                data = res.json()
            except Exception as e:
                print(f"Failed to parse Gemini response as JSON: {e}")
                return "I'm having trouble processing that right now. Could you try again?"
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        elapsed = time.time() - start
        print(f"🔵 Gemini API call took {elapsed:.2f}s")
        return text or "I couldn't process that request. Could you try rephrasing?"
    except httpx.TimeoutException:
        print("🔵 Gemini API call timed out")
        return "Sorry, the AI is taking too long to respond. Please try again later."
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

    # Always use news_event_agent so Twitter news is included
    agent_reply = await news_event_agent(original_message, memory=memory)

    # ✅ Save agent reply directly here
    if user_id and agent_reply:
        print(f"🔵 Saving agent reply inside orchestrator for user_id={user_id}")
        await save_chat_message(user_id=user_id, role="agent", message=agent_reply)

    return agent_reply
