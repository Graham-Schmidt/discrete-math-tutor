from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import chromadb
from openai import OpenAI

from tutor import fetch_answer
from config import CHROMA_PERSIST_DIR, TEST_COLLECTION_NAME
from ingestion.store import get_collection

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


class Query(BaseModel):
    text: str


app = FastAPI(root_path="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health():
    return {"message": "Hello Graham"}


@app.post("/query-tutor/")
async def query_tutor(query: Query):
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
