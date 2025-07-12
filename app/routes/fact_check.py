from fastapi import APIRouter, HTTPException, Request
from app.services.news_analyzer import NewsAnalyzer
from app.services.multi_agent_orchestrator import multi_agent_orchestrator
from app.models.request_models import FactCheckRequest
from app.services.supabase_chat import save_chat_message, get_chat_history, SUPABASE_URL, SUPABASE_KEY  # ✅ NEW
import logging, re, uuid, os
from dotenv import load_dotenv
from datetime import datetime

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
news_analyzer = NewsAnalyzer()

# ------------------------- Utility Functions -------------------------
def sanitize_input(text: str) -> str:
    if not text:
        return text
    text = re.sub(r'[<>"]', '', text)
    return text[:2000]

# ------------------------- Constants -------------------------
IDENTITY_RESPONSE = (
    "I am TruthFinder — your friendly AI assistant! 🤖✨ "
    "I specialize in news analysis, fact-checking, and misinformation detection, but I'm also here for general conversations and to help with personal information. "
    "I can remember details you share with me and help you with news, current events, or just chat about anything you'd like. "
    "Think of me as your knowledgeable friend who's great at analyzing information and having engaging conversations!"
)

# ------------------------- Chat Endpoint -------------------------
@router.post("/agent/chat")
async def chat_agent(request: Request):
    try:
        data = await request.json()
        message = sanitize_input(data.get('message', ''))
        session_id = data.get('session_id') or str(uuid.uuid4())
        user_id = data.get('user_id') or session_id  # Fallback

        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # Save user message to Supabase
        await save_chat_message(user_id=user_id, role="user", message=message)

        # Get full chat history
        history = await get_chat_history(user_id=user_id)

        # Prepare context from history (optional truncation)
        history_context = ""
        for msg in history[-15:]:  # Limit to last 15 messages
            role = msg['role']
            text = msg['message']
            history_context += f"{role.title()}: {text}\n"

        # Compose message with history context
        full_message = (
            f"Conversation so far:\n{history_context}\n"
            f"User: {message}\nAssistant:"
        )

        # Generate agent reply
        if "who are you" in message.lower():
            agent_reply = IDENTITY_RESPONSE
        else:
            # Pass the full message with history context to the orchestrator
            agent_reply = await multi_agent_orchestrator(full_message, user_id=user_id)

        # Save agent reply to Supabase
        await save_chat_message(user_id=user_id, role="agent", message=agent_reply)

        # Get updated history
        updated_history = await get_chat_history(user_id=user_id)

        return {
            "response": agent_reply,
            "session_id": session_id,
            "history": updated_history,
            "debug": {
                "user_id": user_id,
                "history_count": len(updated_history),
                "supabase_working": True
            }
        }

    except Exception as e:
        logger.error(f"Error in /agent/chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again.")

# Debug endpoint to test Supabase
@router.get("/debug/supabase/{user_id}")
async def debug_supabase(user_id: str):
    try:
        history = await get_chat_history(user_id)
        return {
            "user_id": user_id,
            "history": history,
            "count": len(history),
            "supabase_url": SUPABASE_URL,
            "supabase_key_set": bool(SUPABASE_KEY)
        }
    except Exception as e:
        return {
            "error": str(e),
            "user_id": user_id,
            "supabase_url": SUPABASE_URL,
            "supabase_key_set": bool(SUPABASE_KEY)
        }




















# from fastapi import APIRouter, HTTPException, Request
# from app.services.news_analyzer import NewsAnalyzer
# from app.services.multi_agent_orchestrator import multi_agent_orchestrator
# from app.models.request_models import FactCheckRequest
# from app.supabase_memory import save_memory, get_memory  # ✅ NEW

# import logging, re, uuid, os, httpx
# from dotenv import load_dotenv

# # Setup
# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter()
# news_analyzer = NewsAnalyzer()

# # Store chat history per session in RAM (frontend should also store this if needed)
# CHAT_SESSIONS = {}

# # ------------------------- Utility Functions -------------------------

# def sanitize_input(text: str) -> str:
#     if not text:
#         return text
#     text = re.sub(r'[<>"]', '', text)
#     return text[:2000]

# # ------------------------- Constants -------------------------

# IDENTITY_RESPONSE = (
#     "I am TruthFinder — your AI-powered news assistant. "
#     "I specialize in summarizing, fact-checking, bias detection, investigation, and generating reports "
#     "on news articles or claims. I aim to help people spot misinformation and make informed decisions."
# )

# # ------------------------- Routes -------------------------

# @router.post("/fact-check")
# async def fact_check_endpoint(request: FactCheckRequest):
#     try:
#         content = sanitize_input(request.content)
#         if not content:
#             raise HTTPException(status_code=400, detail="Content cannot be empty.")
#         result = await news_analyzer.analyze_news_advanced(content, request.language or "english")
#         return result
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error in /fact-check: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error.")


# @router.post("/agent/chat")
# async def chat_agent(request: Request):
#     try:
#         data = await request.json()
#         message = sanitize_input(data.get('message', ''))
#         session_id = data.get('session_id') or str(uuid.uuid4())
#         user_id = data.get('user_id') or session_id  # fallback if no auth

#         if not message:
#             raise HTTPException(status_code=400, detail="Message cannot be empty.")

#         CHAT_SESSIONS.setdefault(session_id, []).append({"role": "user", "content": message})
#         lower_msg = message.lower()
#         reply_found = False

#         # ✅ Supabase Memory Handling
#         if match := re.match(r"my ([\w ]+) is ([\w ]+)", lower_msg):
#             key, value = match.group(1).strip().replace(' ', '_'), match.group(2).strip()
#             save_memory(user_id, key, value)
#             agent_reply = f"Got it! I'll remember your {key.replace('_', ' ')} is {value}."
#             reply_found = True

#         elif lower_msg.startswith("i am "):
#             name = message[5:].strip()
#             save_memory(user_id, "identity", name)
#             agent_reply = f"Nice to meet you, {name}!"
#             reply_found = True

#         elif lower_msg.startswith("my name is"):
#             name = message.split("my name is", 1)[-1].strip().split()[0]
#             save_memory(user_id, "user_name", name)
#             agent_reply = f"Nice to meet you, {name}!"
#             reply_found = True

#         elif "what is my name" in lower_msg or "what's my name" in lower_msg:
#             name = get_memory(user_id, "user_name")
#             agent_reply = f"Your name is {name}!" if name else "You haven't told me your name yet."
#             reply_found = True

#         elif lower_msg.startswith("i live in") or "i am from" in lower_msg:
#             location = message.split()[-1]
#             save_memory(user_id, "location", location)
#             agent_reply = f"Got it! I'll remember you're from {location}."
#             reply_found = True

#         elif "where do i live" in lower_msg or "where am i from" in lower_msg:
#             location = get_memory(user_id, "location")
#             agent_reply = f"You live in {location}." if location else "You haven't told me where you live yet."
#             reply_found = True

#         elif lower_msg.startswith("what is my "):
#             key = lower_msg[11:].strip().replace(' ', '_')
#             value = get_memory(user_id, key)
#             agent_reply = f"Your {key.replace('_', ' ')} is {value}." if value else f"You haven't told me your {key.replace('_', ' ')} yet."
#             reply_found = True

#         # 🔁 Otherwise, route to multi-agent orchestrator
#         if not reply_found:
#             try:
#                 if "who are you" in lower_msg or "what is your name" in lower_msg:
#                     agent_reply = IDENTITY_RESPONSE
#                 else:
#                     agent_reply = await multi_agent_orchestrator(message)
#             except Exception as e:
#                 logger.error(f"Agent orchestration error: {e}")
#                 agent_reply = "Sorry, something went wrong while processing your request. Please try again."

#         CHAT_SESSIONS[session_id].append({"role": "agent", "content": agent_reply})
#         return {
#             "response": agent_reply,
#             "session_id": session_id,
#             "history": CHAT_SESSIONS[session_id]
#         }

#     except Exception as e:
#         logger.error(f"Unexpected error in /agent/chat: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error. Please try again.")


# @router.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "fact-check"}


# @router.get("/sessions/{session_id}")
# async def get_chat_session(session_id: str):
#     try:
#         return {"session_id": session_id, "history": CHAT_SESSIONS.get(session_id, [])}
#     except Exception as e:
#         logger.error(f"Error getting session: {e}")
#         raise HTTPException(status_code=500, detail="Error retrieving session history.")


























































# from fastapi import APIRouter, HTTPException, Request
# from app.services.news_analyzer import NewsAnalyzer
# from app.services.multi_agent_orchestrator import main_agent, multi_agent_orchestrator
# from app.models.request_models import FactCheckRequest
# import logging, re, uuid, os, httpx
# from dotenv import load_dotenv
# from datetime import datetime, timedelta

# # Setup
# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter()
# news_analyzer = NewsAnalyzer()

# # Session management
# CHAT_SESSIONS = {}
# SESSION_DATA = {}
# SESSION_TIMEOUT_MINUTES = 10

# # ------------------------- Utility Functions -------------------------

# def sanitize_input(text: str) -> str:
#     if not text:
#         return text
#     text = re.sub(r'[<>"]', '', text)
#     return text[:2000]

# def update_session(session_id: str, key: str, value: str):
#     SESSION_DATA.setdefault(session_id, {})
#     SESSION_DATA[session_id][key] = value
#     SESSION_DATA[session_id]['__last_active'] = datetime.utcnow()

# def get_session(session_id: str):
#     session = SESSION_DATA.get(session_id)
#     if session:
#         last_active = session.get('__last_active')
#         if last_active and datetime.utcnow() - last_active > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
#             del SESSION_DATA[session_id]
#             return None
#         return session
#     return None

# # ------------------------- Intent & Keyword Sets -------------------------

# IDENTITY_RESPONSE = (
#     "I am TruthFinder — your AI-powered news assistant. "
#     "I specialize in summarizing, fact-checking, bias detection, investigation, and generating reports "
#     "on news articles or claims. I aim to help people spot misinformation and make informed decisions."
# )

# IDENT_KEYWORDS = ["who are you", "what's your name", "tell me about yourself", "who is truthfinder", "what is your work"]
# SUMMARY_KEYWORDS = ["summarize", "summary"]
# FACTCHECK_KEYWORDS = ["fact check", "is it true", "verify", "real or fake"]
# BIAS_KEYWORDS = ["bias", "political bias", "tone", "sentiment"]
# INVESTIGATE_KEYWORDS = ["investigate", "investigation", "deep check"]
# REPORT_KEYWORDS = ["report", "generate report", "final report"]
# NEWS_KEYWORDS = ["news", "article", "headline", "report", "fake", "misinformation"]

# # ------------------------- Endpoints -------------------------

# @router.post("/fact-check")
# async def fact_check_endpoint(request: FactCheckRequest):
#     try:
#         content = sanitize_input(request.content)
#         if not content:
#             raise HTTPException(status_code=400, detail="Content cannot be empty.")
#         result = await news_analyzer.analyze_news_advanced(content, request.language or "english")
#         return result
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error in /fact-check: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error.")

# @router.post("/agent/chat")
# async def chat_agent(request: Request):
#     try:
#         data = await request.json()
#         message = sanitize_input(data.get('message', ''))
#         session_id = data.get('session_id') or str(uuid.uuid4())

#         if not message:
#             raise HTTPException(status_code=400, detail="Message cannot be empty.")

#         CHAT_SESSIONS.setdefault(session_id, []).append({"role": "user", "content": message})
#         lower_msg = message.lower()
#         session = get_session(session_id) or {}
#         reply_found = False

#         # Memory Patterns
#         if match := re.match(r"my ([\w ]+) is ([\w ]+)", lower_msg):
#             key, value = match.group(1).strip().replace(' ', '_'), match.group(2).strip()
#             update_session(session_id, key, value)
#             agent_reply = f"Got it! I'll remember your {key.replace('_', ' ')} is {value}."
#             reply_found = True

#         elif lower_msg.startswith("i am "):
#             name = message[5:].strip()
#             update_session(session_id, "identity", name)
#             agent_reply = f"Nice to meet you, {name}!"
#             reply_found = True

#         elif lower_msg.startswith("my name is"):
#             name = message.split("my name is", 1)[-1].strip().split()[0]
#             update_session(session_id, "user_name", name)
#             agent_reply = f"Nice to meet you, {name}!"
#             reply_found = True

#         elif "what is my name" in lower_msg or "what's my name" in lower_msg:
#             name = session.get("user_name")
#             agent_reply = f"Your name is {name}!" if name else "You haven't told me your name yet in this session."
#             reply_found = True

#         elif lower_msg.startswith("i live in") or "i am from" in lower_msg:
#             location = message.split()[-1]
#             update_session(session_id, "location", location)
#             agent_reply = f"Got it! I'll remember you're from {location}."
#             reply_found = True

#         elif "where do i live" in lower_msg or "where am i from" in lower_msg:
#             location = session.get("location")
#             agent_reply = f"You live in {location}." if location else "You haven't told me where you live yet."
#             reply_found = True

#         elif lower_msg.startswith("what is my "):
#             key = lower_msg[11:].strip().replace(' ', '_')
#             value = session.get(key)
#             agent_reply = f"Your {key.replace('_', ' ')} is {value}." if value else f"You haven't told me your {key.replace('_', ' ')} yet."
#             reply_found = True

#         # Intent Routing to Multi-Agent Orchestrator
#         if not reply_found:
#             try:
#                 if any(k in lower_msg for k in IDENT_KEYWORDS):
#                     agent_reply = IDENTITY_RESPONSE
#                 elif any(k in lower_msg for k in SUMMARY_KEYWORDS + FACTCHECK_KEYWORDS + BIAS_KEYWORDS + INVESTIGATE_KEYWORDS + REPORT_KEYWORDS + NEWS_KEYWORDS):
#                     agent_reply = await multi_agent_orchestrator(message)
#                 else:
#                     agent_reply = await multi_agent_orchestrator(message)
#             except Exception as e:
#                 logger.error(f"Agent orchestration error: {e}")
#                 agent_reply = "Sorry, something went wrong while processing your request. Please try again shortly."

#         CHAT_SESSIONS[session_id].append({"role": "agent", "content": agent_reply})
#         return {"response": agent_reply, "session_id": session_id, "history": CHAT_SESSIONS[session_id]}

#     except Exception as e:
#         logger.error(f"Unexpected error in /agent/chat: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error. Please try again.")

# @router.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "fact-check"}

# @router.get("/sessions/{session_id}")
# async def get_chat_session(session_id: str):
#     try:
#         return {"session_id": session_id, "history": CHAT_SESSIONS.get(session_id, [])}
#     except Exception as e:
#         logger.error(f"Error getting session: {e}")
#         raise HTTPException(status_code=500, detail="Error retrieving session history.")


















# from fastapi import APIRouter, HTTPException, Request
# from app.services.news_analyzer import NewsAnalyzer
# from app.services.multi_agent_orchestrator import main_agent, multi_agent_orchestrator
# from app.models.request_models import FactCheckRequest
# from app.models.response_models import FactCheckResult
# import logging
# import re
# import uuid
# import os
# import httpx
# from dotenv import load_dotenv
# from datetime import datetime, timedelta

# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter()
# news_analyzer = NewsAnalyzer()

# SESSION_TIMEOUT_MINUTES = 10

# # In-memory chat sessions
# CHAT_SESSIONS = {}
# # In-memory session data for user info (like name, location, etc.)
# SESSION_DATA = {}

# # Identity response
# IDENTITY_RESPONSE = (
#     "I am TruthFinder — your AI-powered news assistant. "
#     "I specialize in summarizing, fact-checking, bias detection, investigation, and generating reports "
#     "on news articles or claims. My goal is to help people spot misinformation and make informed decisions using verified information."
# )

# # Intent keyword sets
# IDENT_KEYWORDS = ["who are you", "what's your name", "tell me about yourself", "what are you", "who is truthfinder", "what is your work", "what is your purpose", "what is your goal", "what is your mission", "what is your vision", "what is your goal", "what is your mission", "what is your vision", "what is your goal", "what is your mission", "what is your vision"]
# SUMMARY_KEYWORDS = ["summarize", "summary"]
# FACTCHECK_KEYWORDS = ["fact check", "is it true", "verify", "real or fake"]
# BIAS_KEYWORDS = ["bias", "political bias", "tone", "sentiment"]
# INVESTIGATE_KEYWORDS = ["investigate", "investigation", "deep check"]
# REPORT_KEYWORDS = ["report", "generate report", "final report"]
# NEWS_KEYWORDS = ["news", "article", "headline", "report", "fact", "fake", "misinformation", "bias"]

# def sanitize_input(text: str) -> str:
#     if not text:
#         return text
#     text = re.sub(r'[<>"]', '', text)
#     return text[:2000]

# def update_session(session_id: str, key: str, value: str):
#     now = datetime.utcnow()
#     SESSION_DATA[session_id] = SESSION_DATA.get(session_id, {})
#     SESSION_DATA[session_id][key] = value
#     SESSION_DATA[session_id]['__last_active'] = now

# def get_session(session_id: str):
#     session = SESSION_DATA.get(session_id)
#     if session:
#         last_active = session.get('__last_active')
#         if last_active and datetime.utcnow() - last_active > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
#             del SESSION_DATA[session_id]  # auto-delete expired session
#             return None
#         return session
#     return None

# @router.post("/fact-check")
# async def fact_check_endpoint(request: FactCheckRequest):
#     """Main fact-checking endpoint"""
#     try:
#         # Sanitize input
#         content = sanitize_input(request.content)
        
#         if not content:
#             raise HTTPException(status_code=400, detail="Content cannot be empty.")
        
#         # Use the news analyzer for comprehensive analysis
#         result = await news_analyzer.analyze_news_advanced(content, request.language or "english")
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error in fact-check endpoint: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error during fact-checking.")

# @router.post("/agent/chat")
# async def chat_agent(request: Request):
#     try:
#         data = await request.json()
#         message = sanitize_input(data.get('message', ''))
#         session_id = data.get('session_id') or str(uuid.uuid4())

#         if not message:
#             raise HTTPException(status_code=400, detail="Message cannot be empty.")

#         history = CHAT_SESSIONS.setdefault(session_id, [])
#         history.append({"role": "user", "content": message})
#         lower_msg = message.lower()

#         # --- General personal/contextual data detection and recall logic ---
#         reply_found = False
#         session = get_session(session_id) or {}
#         # Pattern: "my X is Y"
#         match = re.match(r"my ([\w ]+) is ([\w ]+)", lower_msg)
#         if match:
#             key = match.group(1).strip().replace(' ', '_')
#             value = match.group(2).strip()
#             update_session(session_id, key, value)
#             agent_reply = f"Got it! I'll remember your {key.replace('_', ' ')} is {value}."
#             reply_found = True
#         # Pattern: "I am Y"
#         elif lower_msg.startswith("i am "):
#             value = message[5:].strip()
#             update_session(session_id, "identity", value)
#             agent_reply = f"Nice to meet you, {value}!"
#             reply_found = True
#         # Pattern: "i'm from X" or "i am from X" or "i live in X"
#         elif lower_msg.startswith("i'm from ") or lower_msg.startswith("i am from "):
#             value = message.split("from", 1)[-1].strip()
#             update_session(session_id, "location", value)
#             agent_reply = f"Got it! I'll remember you're from {value}."
#             reply_found = True
#         elif lower_msg.startswith("i live in "):
#             value = message.split("in", 1)[-1].strip()
#             update_session(session_id, "location", value)
#             agent_reply = f"Got it! I'll remember you live in {value}."
#             reply_found = True
#         # Pattern: "my location is X"
#         elif lower_msg.startswith("my location is "):
#             value = message.split("is", 1)[-1].strip()
#             update_session(session_id, "location", value)
#             agent_reply = f"Got it! I'll remember your location is {value}."
#             reply_found = True
#         # Pattern: "what is my X"
#         elif lower_msg.startswith("what is my "):
#             key = lower_msg[11:].strip().replace(' ', '_')
#             value = session.get(key)
#             if value:
#                 agent_reply = f"Your {key.replace('_', ' ')} is {value}."
#             else:
#                 agent_reply = f"You haven't told me your {key.replace('_', ' ')} yet in this session."
#             reply_found = True
#         # Pattern: "where do i live" or "from where am i" or "where am i from"
#         elif lower_msg.startswith("where do i live") or lower_msg.startswith("from where am i") or lower_msg.startswith("where am i from"):
#             value = session.get("location")
#             if value:
#                 agent_reply = f"You live in {value}."
#             else:
#                 agent_reply = "You haven't told me where you live yet in this session."
#             reply_found = True
#         # Pattern: "what's my name" or "what is my name"
#         elif "what's my name" in lower_msg or "what is my name" in lower_msg:
#             name = session.get("user_name")
#             if name:
#                 agent_reply = f"Your name is {name}!"
#             else:
#                 agent_reply = "You haven't told me your name yet in this session."
#             reply_found = True
#         # Pattern: "my name is X"
#         elif "my name is" in lower_msg:
#             name = message.split("my name is", 1)[-1].strip().split()[0]
#             update_session(session_id, "user_name", name)
#             agent_reply = f"Nice to meet you, {name}!"
#             reply_found = True
#         # Intent routing using the new main agent/orchestrator
#         if not reply_found:
#             try:
#                 if any(k in lower_msg for k in IDENT_KEYWORDS):
#                     agent_reply = IDENTITY_RESPONSE
#                 elif any(k in lower_msg for k in SUMMARY_KEYWORDS + FACTCHECK_KEYWORDS + BIAS_KEYWORDS + INVESTIGATE_KEYWORDS + REPORT_KEYWORDS + NEWS_KEYWORDS):
#                     agent_reply = await multi_agent_orchestrator(message)
#                 else:
#                     agent_reply = await multi_agent_orchestrator(message)
#             except Exception as e:
#                 logger.error(f"Error in agent orchestration: {e}")
#                 agent_reply = "I'm experiencing technical difficulties right now. Please try again in a moment."

#         history.append({"role": "agent", "content": agent_reply})
#         return {"response": agent_reply, "session_id": session_id, "history": history}
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error in chat_agent: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error. Please try again.")

# @router.get("/health")
# async def health_check():
#     """Health check endpoint for the fact-check service"""
#     return {"status": "healthy", "service": "fact-check"}

# @router.get("/sessions/{session_id}")
# async def get_chat_session(session_id: str):
#     """Get chat session history"""
#     try:
#         history = CHAT_SESSIONS.get(session_id, [])
#         return {"session_id": session_id, "history": history}
#     except Exception as e:
#         logger.error(f"Error getting session {session_id}: {e}")
#         raise HTTPException(status_code=500, detail="Error retrieving session")


