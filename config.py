import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# KeyError if unset
COURSE_DATA_DIR = Path(os.environ["COURSE_MATERIALS_DIR"])
CHUNK_JSONL_DIR = Path(os.environ["CHUNK_JSONL_DIR"])
EMBEDDED_CHUNK_DIR = Path(os.environ["EMBEDDED_CHUNK_DIR"])
CHROMA_PERSIST_DIR = Path(os.environ["CHROMA_PERSIST_DIR"])
MARKER_OUTPUT_DIR = Path(os.environ["MARKER_OUTPUT_DIR"])

EMBEDDED_CHUNKS_FILE = os.environ["EMBEDDED_CHUNKS_FILE"]
RAW_CHUNKS_FILE = os.environ["RAW_CHUNKS_FILE"]

TEST_COLLECTION_NAME = os.environ["TEST_COLLECTION_NAME"]
CHAPTER_2_PDF_FILE_PATH = Path(os.environ["CHAPTER_2_PDF_FILE_PATH"])
CHAPTER_2_MD_FILE_PATH = Path(os.environ["CHAPTER_2_MD_FILE_PATH"])
OUTPUT_PATH = Path(os.environ["OUTPUT_PATH"])

GPT_4_1_MINI = os.environ["GPT_4_1_MINI"]

if not COURSE_DATA_DIR.exists():
    raise FileNotFoundError(f"COURSE_DATA_DIR={COURSE_DATA_DIR} does not exist")
