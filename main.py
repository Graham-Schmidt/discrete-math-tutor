import chromadb
from chromadb.api import ClientAPI
from openai import OpenAI

from chunk import chunk_markdown_file
from chat import answer_user_question
from embed import embed_chapter_file, embed_query
from store import write_to_collection, get_collection
from retrieve import retrieve
from utils import read_jsonl
from models import EmbeddedChunk
from config import (
    CHAPTER_2_MD_FILE_PATH,
    CHROMA_PERSIST_DIR,
    CHUNK_JSONL_DIR,
    RAW_CHUNKS_FILE,
    EMBEDDED_CHUNK_DIR,
    EMBEDDED_CHUNKS_FILE,
    TEST_COLLECTION_NAME,
)

from test_queries import TEST_QUERIES

TEST_QUERY = "what is the axiomatic method?"


def prepare_data(chroma_client: ClientAPI, openai_client: OpenAI):
    chunk_markdown_file(CHAPTER_2_MD_FILE_PATH)
    # get embeddings for chunks, write to disk
    embed_chapter_file(
        input_path=RAW_CHUNKS_FILE,
        client=openai_client,
    )

    # read embedded chunks
    embedded_chunks = read_jsonl(
        dir=EMBEDDED_CHUNK_DIR, file_name=EMBEDDED_CHUNKS_FILE, cls=EmbeddedChunk
    )
    # determine chroma collection to interact with
    collection = get_collection(
        client=chroma_client, collection_name=TEST_COLLECTION_NAME
    )
    # write embedded chunks to chroma DB
    write_to_collection(
        client=chroma_client, collection=collection, chunks=embedded_chunks
    )


def fetch_answer(
    user_query: str, chroma_client: ClientAPI, openai_client: OpenAI, collection
):
    # user_query = TEST_QUERY

    # lookup k nearest neighbors from collection
    closest_matches = retrieve(
        user_query=user_query,
        collection=collection,
        n_results=5,
        openai_client=openai_client,
    )
    answer_for_user = answer_user_question(
        openai_client=openai_client,
        user_query=user_query,
        retrieved_chunks=closest_matches,
    )
    return answer_for_user.output_text


def main():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    openai_client = OpenAI()
    collection = get_collection(
        client=chroma_client, collection_name=TEST_COLLECTION_NAME
    )

    """Chunks, embeds, and stores data | EXPENSIVE"""
    # prepare_data(chroma_client=chroma_client, openai_client=openai_client)

    """Test single query"""
    # answer = fetch_answer(user_query=TEST_QUERIES[0], chroma_client=chroma_client, openai_client=openai_client, collection=collection)
    # print(answer)

    """Test all queries"""
    for query in TEST_QUERIES:
        print(f"# Answer for query '{query}'\n")
        print(
            f"{fetch_answer(user_query=query, chroma_client=chroma_client, openai_client=openai_client, collection=collection)}"
        )
        print("END OF RESPONSE\n")


if __name__ == "__main__":
    main()
