"""Writes and reads embedded chunks in a Chroma collection."""

import chromadb
from chromadb.api import ClientAPI

from models import EmbeddedChunk


def get_collection(client: ClientAPI, collection_name: str):
    """Get the named Chroma collection, creating it (with cosine distance) if it doesn't exist."""
    collection = client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )
    return collection


def _chunks_to_chroma_format(chunks: list[EmbeddedChunk]) -> dict:
    """Reshape chunks into the parallel-list format Chroma's upsert expects."""
    output = {"ids": [], "embeddings": [], "documents": [], "metadatas": []}
    for chunk in chunks:
        output["ids"].append(chunk.id)
        output["embeddings"].append(chunk.embedding)
        output["documents"].append(chunk.text)
        output["metadatas"].append(
            {
                "chapter": chunk.chapter,
                "token_size": chunk.token_size,
                "content_type": chunk.content_type,
                "section_number": chunk.section_number,
                "section_title": chunk.section_title,
                "parent_id": chunk.parent_id,
            }
        )
    return output


def write_to_collection(
    client: ClientAPI, collection: chromadb.Collection, chunks: list[EmbeddedChunk]
) -> None:
    """Upsert embedded chunks into `collection`, asserting the batch fits Chroma's max batch size."""
    data = _chunks_to_chroma_format(chunks=chunks)
    batch_size = len(data["ids"])
    _check_batch_size(client=client, n=batch_size)

    collection.upsert(
        ids=data["ids"],
        embeddings=data["embeddings"],
        documents=data["documents"],
        metadatas=data["metadatas"],
    )


def _check_batch_size(client: ClientAPI, n: int) -> None:
    """`n` = number of records in batch"""
    max_batch_size = client.get_max_batch_size()
    assert n <= max_batch_size, f"{n} chunks exceeds max batch size of {max_batch_size}"
