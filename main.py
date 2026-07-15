import chromadb
from openai import OpenAI

from chunk import chunk_markdown_file
from embed import embed_chapter_file, embed_query
from store import write_to_collection, get_collection
from retrieve import retrieve
from utils import read_jsonl
from models import EmbeddedChunk
from config import (
    TEST_FILE_PATH,
    CHROMA_PERSIST_DIR,
    CHUNK_JSONL_DIR,
    RAW_CHUNKS_FILE,
    EMBEDDED_CHUNK_DIR,
    EMBEDDED_CHUNKS_FILE,
    TEST_COLLECTION_NAME,
)

TEST_QUERY = "what is the axiomatic method?"


def main():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    openai_client = OpenAI()
    # PART 1: DATA INJESTION
    # convert markdown chapter into chunks
    chunk_markdown_file(TEST_FILE_PATH)
    # get embeddings for chunks, write to disk
    embed_chapter_file(
        input_dir=CHUNK_JSONL_DIR,
        input_file_name=RAW_CHUNKS_FILE,
        output_dir=EMBEDDED_CHUNK_DIR,
        output_file_name=EMBEDDED_CHUNKS_FILE,
        client=openai_client,
    )

    # read embedded chunks
    embedded_chunks = read_jsonl(
        dir=EMBEDDED_CHUNK_DIR, file_name=EMBEDDED_CHUNKS_FILE, cls=EmbeddedChunk
    )
    # determine chroma collection to inteact with
    collection = get_collection(
        client=chroma_client, collection_name=TEST_COLLECTION_NAME
    )
    # write embedded chunks to chroma DB
    write_to_collection(
        client=chroma_client, collection=collection, chunks=embedded_chunks
    )

    # PART 2: QUERY COMPARISON
    user_query = TEST_QUERY

    # lookup k nearest neighbors from collection
    closest_match = retrieve(
        user_query=user_query,
        collection=collection,
        n_results=5,
        openai_client=openai_client,
    )
    print(closest_match[0].text)


def just_embed_user():
    # chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    openai_client = OpenAI()
    user_query = TEST_QUERY
    user_query_embedding = embed_query(text=user_query, client=openai_client)
    print(user_query_embedding)


if __name__ == "__main__":
    main()
    # just_embed_user()
