from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.services.news_analyzer import NewsAnalyzer
from app.services.multi_agent_orchestrator import multi_agent_orchestrator
from app.models.request_models import FactCheckRequest
from app.services.supabase_chat import save_chat_message, get_chat_history, SUPABASE_URL, SUPABASE_KEY
# Add async imports
# from app.qdrant_client import async_search_text, async_store_text
import logging, re, uuid, os
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment
load_dotenv()

# Setup
app = FastAPI(title="TruthFinder API")
router = APIRouter()
news_analyzer = NewsAnalyzer()
logging.basicConfig(level=logging.INFO)

# ---------------- Utility ----------------
def sanitize_input(text: str) -> str:
    if not text:
        return text
    text = re.sub(r'[<>"]', '', text)
    return text[:2000]

IDENTITY_RESPONSE = (
    "I am TruthFinder — your friendly AI assistant! 🤖✨ "
    "I specialize in news analysis, fact-checking, and misinformation detection..."
)

# --------------- Startup Event ----------------
@app.on_event("startup")
def startup_event():
    # create_collection() # Commented out as per edit hint
    pass

# ---------------- Chat Endpoint ----------------
@router.post("/agent/chat")
async def chat_agent(request: Request):
    try:
        data = await request.json()
        message = sanitize_input(data.get('message', ''))
        session_id = data.get('session_id') or str(uuid.uuid4())
        user_id = data.get('user_id') or session_id

        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # Save to Supabase
        logging.info(f"🔵 Saving message: {message[:50]}")
        await save_chat_message(user_id=user_id, role="user", message=message)

        # Identity response check
        if "who are you" in message.lower():
            agent_reply = IDENTITY_RESPONSE
        else:
            # Qdrant search (async, with timeout and timing)
            # qdrant_start = time.time()
            # try:
            #     qdrant_results = await async_search_text(message, timeout=10.0)
            #     logging.info(f"🧠 Qdrant Results: {qdrant_results}")
            # except TimeoutError:
            #     logging.error("Qdrant search timed out")
            #     raise HTTPException(status_code=504, detail="Knowledge search is taking too long. Please try again later.")
            # except Exception as e:
            #     logging.error(f"Qdrant search error: {e}")
            #     raise HTTPException(status_code=500, detail="Knowledge search failed. Please try again later.")
            # qdrant_elapsed = time.time() - qdrant_start
            # logging.info(f"Qdrant search took {qdrant_elapsed:.2f}s")

            # Orchestrator (AI agent)
            orchestrator_start = time.time()
            agent_reply = await multi_agent_orchestrator(message, user_id=user_id)
            orchestrator_elapsed = time.time() - orchestrator_start
            logging.info(f"Orchestrator took {orchestrator_elapsed:.2f}s")

            # Qdrant store (async, with timeout and timing)
            # store_start = time.time()
            # try:
            #     await async_store_text(id=uuid.uuid4().int >> 64, text=agent_reply, timeout=10.0)
            # except TimeoutError:
            #     logging.error("Qdrant store timed out")
            # except Exception as e:
            #     logging.error(f"Qdrant store error: {e}")
            # store_elapsed = time.time() - store_start
            # logging.info(f"Qdrant store took {store_elapsed:.2f}s")

        # Fetch updated history
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

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error in /agent/chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again.")

# ---------------- Supabase Debug Endpoint ----------------
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

# ---------------- Middleware & Routes ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000","https://truth-finder-ai.vercel.app"],  # Replace with frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
