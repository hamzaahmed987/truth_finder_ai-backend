from fastapi import APIRouter, HTTPException, Request
from app.services.news_analyzer import NewsAnalyzer
from app.services.multi_agent_orchestrator import multi_agent_orchestrator
from app.models.request_models import FactCheckRequest
from app.services.supabase_chat import save_chat_message, get_chat_history, SUPABASE_URL, SUPABASE_KEY
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
        logger.info(f"🔵 SAVING: user_id={user_id}, message={message[:50]}...")
        save_result = await save_chat_message(user_id=user_id, role="user", message=message)
        logger.info(f"🔵 SAVE RESULT: {save_result}")

        # Generate agent reply - pass only the original message, not the full history
        if "who are you" in message.lower():
            agent_reply = IDENTITY_RESPONSE
        else:
            agent_reply = await multi_agent_orchestrator(message, user_id=user_id)

        # ✅ Agent reply is now saved inside multi_agent_orchestrator()

        # Get updated history
        logger.info(f"🔵 FETCHING UPDATED HISTORY")
        updated_history = await get_chat_history(user_id=user_id)
        logger.info(f"🔵 UPDATED HISTORY COUNT: {len(updated_history)}")

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

# ------------------------- Supabase Debug Endpoint -------------------------
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



















