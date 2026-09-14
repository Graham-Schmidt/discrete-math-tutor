"""FastAPI app: serves the frontend static files and the tutor query endpoint."""

from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import chromadb
from openai import OpenAI

from tutor import fetch_answer
from config import CHROMA_PERSIST_DIR, TEST_COLLECTION_NAME
from ingestion.store import get_collection
from query_limiter import check_query_limit

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


class Query(BaseModel):
    """Request body for POST /query-tutor/."""

    text: str


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(root_path="/api/v1")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
@limiter.limit("5/minute")
async def health(request: Request):
    """Liveness check."""
    return {"message": "Hello Graham"}


@app.post("/query-tutor/")
@limiter.limit("5/minute")
# TODO move limit-per-minute detail message to SlowAPI return handler
async def query_tutor(request: Request, query: Query):
    """Answer a student's question using the persisted Chroma collection."""
    over_query_limit = check_query_limit(ip_address=request.client.host)
    if over_query_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            # detail="The daily query limit has been reached."
            headers={"error": "The daily query limit has been reached."},
        )
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = get_collection(
        client=chroma_client, collection_name=TEST_COLLECTION_NAME
    )
    openai_client = OpenAI()
    answer = fetch_answer(
        user_query=query.text,
        chroma_client=chroma_client,
        openai_client=openai_client,
        collection=collection,
    )
    return {"message": answer}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
