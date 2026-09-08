from pathlib import Path

import chromadb
from chromadb.api import ClientAPI
from openai import OpenAI
from tqdm import tqdm

from ingestion.chunk import chunk_markdown_file
from ingestion.embed import embed_chapter_file
from ingestion.store import write_to_collection, get_collection
from ingestion.extract import convert_pdf_to_md
from utils import read_jsonl
from models import EmbeddedChunk
from config import (
    MARKER_OUTPUT_DIR,
    CHROMA_PERSIST_DIR,
    CHUNK_JSONL_DIR,
    EMBEDDED_CHUNK_DIR,
    TEST_COLLECTION_NAME,
)
from init_utils.utils import get_all_chapter_pdf_file_paths
from init_utils.course_downloader import download_course


def prepare_data(chroma_client: ClientAPI, openai_client: OpenAI):
    """Chunk every extracted chapter markdown file, embed the chunks, and
    upsert them into the Chroma collection. Expensive: calls the OpenAI API
    once per chunk (chunking context) plus once per chapter (embedding)."""
    for subdir in Path(MARKER_OUTPUT_DIR).iterdir():
        if subdir.is_dir():
            for path in subdir.glob("*.md"):
                chunk_markdown_file(path, client=openai_client)

    for path in Path(CHUNK_JSONL_DIR).glob("*.jsonl"):
        print(path.name)
        embed_chapter_file(input_path=path, client=openai_client)

    # read embedded chunks
    for path in Path(EMBEDDED_CHUNK_DIR).glob("*.jsonl"):

        embedded_chunks = read_jsonl(file_path=path, cls=EmbeddedChunk)
        # determine chroma collection to interact with
        collection = get_collection(
            client=chroma_client, collection_name=TEST_COLLECTION_NAME
        )
        # write embedded chunks to chroma DB
        write_to_collection(
            client=chroma_client, collection=collection, chunks=embedded_chunks
        )


def convert_all_pdfs_to_md():
    """Convert every chapter PDF in COURSE_DATA_DIR to markdown via Marker. Expensive."""
    file_paths = get_all_chapter_pdf_file_paths()
    for path in tqdm(file_paths):
        convert_pdf_to_md(file_path=path)


def build_backend_data():
    """(re)build the ingestion pipeline, then run the test queries end-to-end."""
    confirm = input(
        "This command begins a large download and installation process, do you want to proceed? Y/N \n"
    )
    if confirm.lower() == "y":

        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        openai_client = OpenAI()
        collection = get_collection(
            client=chroma_client, collection_name=TEST_COLLECTION_NAME
        )
        download_course()

        """ !!!! EXPENSIVE FUNCTION !!!! """
        convert_all_pdfs_to_md()
        """ !!!! EXPENSIVE FUNCTION !!!! """

        """Chunks, embeds, and stores data | EXPENSIVE"""
        prepare_data(chroma_client=chroma_client, openai_client=openai_client)


if __name__ == "__main__":
    build_backend_data()
