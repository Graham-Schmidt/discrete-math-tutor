# intake user query
# embed query
# hit chromadb for most similar embedding
# return

from openai import OpenAI
from chromadb.api import ClientAPI
from chromadb import Collection, QueryResult, Metadata

from embed import embed_query
from models import RetrievedChunk

# TEMP IMPORTS FOR EASY TESTING
import chromadb
from config import CHROMA_PERSIST_DIR, TEST_COLLECTION_NAME
from store import get_collection

TEST_QUERY = "what assumptions can we make during this lecture?"


def retrieve(
    user_query: str, collection: Collection, n_results: int, openai_client: OpenAI
):
    """Orchestator"""
    user_query_embeddings = embed_query(text=user_query, client=openai_client)
    # hit collection to get the closest results of the query
    similar_results = query_collection(
        collection=collection,
        query_embeddings=user_query_embeddings,
        n_results=n_results,
    )
    return similar_results


def query_collection(
    collection: Collection, query_embeddings: list[float], n_results: int
) -> list[RetrievedChunk]:
    raw_res = collection.query(query_embeddings=query_embeddings, n_results=n_results)
    formatted_res = _chroma_result_to_chunks(raw_res)
    return formatted_res


def _validate_token_size(metadata: Metadata):
    raw_token_size = metadata["token_size"]
    assert isinstance(
        raw_token_size, int
    ), f"expected int token_size, got {type(raw_token_size)}"
    return raw_token_size


def _validate_chapter_type(metadata: Metadata):
    raw_chapter = metadata["chapter"]
    assert isinstance(
        raw_chapter, str
    ), f"expected str chapter, got {type(raw_chapter)}"
    return raw_chapter


def _chroma_result_to_chunks(query_result: QueryResult) -> list[RetrievedChunk]:
    ids = query_result["ids"][0]
    documents = query_result["documents"][0]
    metadatas = query_result["metadatas"][0]
    distances = query_result["distances"][0]

    return [
        RetrievedChunk(
            id=id_,
            text=document,
            chapter=_validate_chapter_type(metadata),
            token_size=_validate_token_size(metadata),
            distance=distance,
        )
        for id_, document, metadata, distance in zip(
            ids, documents, metadatas, distances
        )
    ]


def main():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = get_collection(chroma_client, TEST_COLLECTION_NAME)
    openai_client = OpenAI()
    results = retrieve(
        user_query=TEST_QUERY,
        collection=collection,
        n_results=5,
        openai_client=openai_client,
    )
    print(results[0].text)


if __name__ == "__main__":
    main()
