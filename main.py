from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from openai import OpenAI

from tutor import fetch_answer
from config import CHROMA_PERSIST_DIR, TEST_COLLECTION_NAME
from ingestion.store import get_collection


class Query(BaseModel):
    text: str


app = FastAPI(root_path="/api/v1")


@app.get("/")
async def root():
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
