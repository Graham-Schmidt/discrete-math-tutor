import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# KeyError if unset
COURSE_DATA_DIR = Path(os.environ["COURSE_MATERIALS_DIR"])
CHUNK_JSONL_DIR = Path(os.environ["CHUNK_JSONL_DIR"])
EMBEDDED_CHUNK_DIR = Path(os.environ["EMBEDDED_CHUNK_DIR"])
CHROMA_PERSIST_DIR = Path(os.environ["CHROMA_PERSIST_DIR"])

EMBEDDED_CHUNKS_FILE = os.environ["EMBEDDED_CHUNKS_FILE"]
RAW_CHUNKS_FILE = os.environ["RAW_CHUNKS_FILE"]

TEST_COLLECTION_NAME = os.environ["TEST_COLLECTION_NAME"]
TEST_FILE_PATH = Path(os.environ["TEST_FILE_PATH"])
OUTPUT_PATH = Path(os.environ["OUTPUT_PATH"])

# if not COURSE_DATA_DIR.exists():
#        raise FileNotFoundError(f"COURSE_DATA_DIR={COURSE_DATA_DIR} does not exist")
# if not CHUNK_JSONL_DIR.exists():
#        raise FileNotFoundError(f"CHUNK_JSONL_DIR={CHUNK_JSONL_DIR} does not exist")
# if not EMBEDDED_CHUNK_DIR.exists():
#        raise FileNotFoundError(f"EMBEDDED_CHUNK_DIR={EMBEDDED_CHUNK_DIR} does not exist")
