"""Env-backed paths and model names shared across the backend. Raises if required
environment variables are unset or if COURSE_DATA_DIR doesn't exist on disk."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# KeyError if unset
COURSE_DATA_DIR = Path("data/downloads")
CHUNK_JSONL_DIR = Path("data/chunks/raw-chunks")
EMBEDDED_CHUNK_DIR = Path("data/chunks/embedded-chunks")
CHROMA_PERSIST_DIR = Path("chromadb/")
MARKER_OUTPUT_DIR = Path("data/marker-output")

TEST_COLLECTION_NAME = os.environ["TEST_COLLECTION_NAME"]

GPT_4_1_MINI = os.environ["GPT_4_1_MINI"]
EMBEDDING_MODEL_SMALL = os.environ["EMBEDDING_MODEL_SMALL"]

if not COURSE_DATA_DIR.exists():
    raise FileNotFoundError(f"COURSE_DATA_DIR={COURSE_DATA_DIR} does not exist")
