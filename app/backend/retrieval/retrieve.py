"""Embeds a user query and retrieves the nearest chunks from a Chroma collection."""

from typing import TypeVar

from openai import OpenAI
from chromadb import Collection, QueryResult, Metadata

from ingestion.embed import embed_query
from models import RetrievedChunk

T = TypeVar("T")

TEST_QUERY = "what assumptions can we make during this lecture?"


def retrieve(
    user_query: str, collection: Collection, n_results: int, openai_client: OpenAI
) -> list[RetrievedChunk]:
    """Embed `user_query` and return its `n_results` nearest chunks from `collection`."""
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
    """Query Chroma for the nearest neighbors of `query_embeddings` and format them as `RetrievedChunk`s."""
    raw_res = collection.query(query_embeddings=query_embeddings, n_results=n_results)
    formatted_res = _chroma_result_to_chunks(raw_res)
    return formatted_res


def _validate_metadata_field(metadata: Metadata, key: str, expected_type: type[T]) -> T:
    """Look up `key` in Chroma metadata, asserting it's of `expected_type`."""
    raw_value = metadata[key]
    assert isinstance(
        raw_value, expected_type
    ), f"expected {expected_type.__name__} {key}, got {type(raw_value)}"
    return raw_value


def _chroma_result_to_chunks(query_result: QueryResult) -> list[RetrievedChunk]:
    """Flatten a single-query Chroma `QueryResult` into a list of `RetrievedChunk`s."""
    ids = query_result["ids"][0]
    documents = query_result["documents"]
    metadatas = query_result["metadatas"]
    distances = query_result["distances"]
    assert documents is not None, "expected documents in query result"
    assert metadatas is not None, "expected metadatas in query result"
    assert distances is not None, "expected distances in query result"

    return [
        RetrievedChunk(
            id=id_,
            text=document,
            token_size=_validate_metadata_field(metadata, "token_size", int),
            chapter=_validate_metadata_field(metadata, "chapter", str),
            content_type=_validate_metadata_field(metadata, "content_type", str),
            section_number=_validate_metadata_field(metadata, "section_number", str),
            section_title=_validate_metadata_field(metadata, "section_title", str),
            parent_id=_validate_metadata_field(metadata, "parent_id", str),
            distance=distance,
        )
        for id_, document, metadata, distance in zip(
            ids, documents[0], metadatas[0], distances[0]
        )
    ]
