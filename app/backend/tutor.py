import chromadb
from chromadb.api import ClientAPI
from openai import OpenAI
from tqdm import tqdm

from ingestion.chunk import chunk_markdown_file
from chat import answer_user_question
from ingestion.embed import embed_chapter_file, embed_query
from ingestion.store import write_to_collection, get_collection
from retrieval.retrieve import retrieve
from ingestion.extract import convert_pdf_to_md
from utils import read_jsonl
from models import EmbeddedChunk
from config import (
    CHAPTER_2_MD_FILE_PATH,
    CHAPTER_2_PDF_FILE_PATH,
    CHROMA_PERSIST_DIR,
    CHUNK_JSONL_DIR,
    RAW_CHUNKS_FILE,
    EMBEDDED_CHUNK_DIR,
    EMBEDDED_CHUNKS_FILE,
    TEST_COLLECTION_NAME,
)
from init_utils.utils import get_all_chapter_pdf_file_paths

from testing.test_queries import TEST_QUERIES

TEST_QUERY = "what is the axiomatic method?"


def prepare_data(chroma_client: ClientAPI, openai_client: OpenAI):
    # TODO replace hardcoded destination
    chunk_markdown_file(CHAPTER_2_MD_FILE_PATH, client=openai_client)
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


def convert_all_pdfs_to_md():
    file_paths = get_all_chapter_pdf_file_paths()
    for path in tqdm(file_paths):
        convert_pdf_to_md(file_path=path)


def main():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    openai_client = OpenAI()
    collection = get_collection(
        client=chroma_client, collection_name=TEST_COLLECTION_NAME
    )

    """ !!!! EXPENSIVE FUNCTION !!!! """
    # convert_all_pdfs_to_md()
    """ !!!! EXPENSIVE FUNCTION !!!! """

    """Chunks, embeds, and stores data | EXPENSIVE"""
    prepare_data(chroma_client=chroma_client, openai_client=openai_client)

    """Test single query"""
    # answer = fetch_answer(
    #     user_query=TEST_QUERIES[0],
    #     chroma_client=chroma_client,
    #     openai_client=openai_client,
    #     collection=collection,
    # )
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
