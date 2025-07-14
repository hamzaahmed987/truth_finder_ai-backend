# from qdrant_client import QdrantClient
# from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import uuid
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

load_dotenv()
# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Qdrant setup
# client = QdrantClient(
#     url=os.getenv("qdrant_url"),
#     api_key=os.getenv("qdrant_api_key")
# )

COLLECTION_NAME = "truthfinder_knowledge"

def create_collection():
    # client.recreate_collection(
    #     collection_name=COLLECTION_NAME,
    #     vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    # )
    pass

def embed(text: str) -> list[float]:
    return model.encode(text).tolist()

def store_text(id: int, text: str):
    vector = embed(text)
    # client.upsert(
    #     collection_name=COLLECTION_NAME,
    #     points=[PointStruct(id=id, vector=vector, payload={"text": text})]
    # )
    pass

def search_text(query: str, top_k: int = 5, **kwargs):
    # Accept 'top' as a fallback for compatibility
    if 'top' in kwargs:
        top_k = kwargs['top']
    vector = embed(query)
    # results = client.search(
    #     collection_name=COLLECTION_NAME,
    #     query_vector=vector,
    #     limit=top_k  # Use 'limit' instead of 'top' for compatibility
    # )
    # return [hit.payload["text"] for hit in results]
    return []

# ----------------- ASYNC WRAPPERS -----------------

_executor = ThreadPoolExecutor(max_workers=4)

async def async_store_text(id: int, text: str, timeout: float = 10.0):
    loop = asyncio.get_running_loop()
    try:
        await asyncio.wait_for(
            loop.run_in_executor(_executor, store_text, id, text),
            timeout=timeout
        )
    except (asyncio.TimeoutError, FuturesTimeoutError):
        raise TimeoutError("Qdrant store_text timed out")

async def async_search_text(query: str, top_k: int = 5, timeout: float = 10.0, **kwargs):
    loop = asyncio.get_running_loop()
    def _search():
        return search_text(query, top_k, **kwargs)
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(_executor, _search),
            timeout=timeout
        )
    except (asyncio.TimeoutError, FuturesTimeoutError):
        raise TimeoutError("Qdrant search_text timed out")
