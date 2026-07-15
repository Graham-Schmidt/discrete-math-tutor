import chromadb
from chromadb.api import ClientAPI

from models import EmbeddedChunk
from utils import read_jsonl
from config import (
    EMBEDDED_CHUNK_DIR,
    EMBEDDED_CHUNKS_FILE,
    CHROMA_PERSIST_DIR,
    TEST_COLLECTION_NAME,
)


def get_collection(client: ClientAPI, collection_name: str):
    collection = client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )
    return collection


def _chunks_to_chroma_format(chunks: list[EmbeddedChunk]) -> dict:
    output = {"ids": [], "embeddings": [], "documents": [], "metadatas": []}
    for chunk in chunks:
        output["ids"].append(chunk.id)
        output["embeddings"].append(chunk.embedding)
        output["documents"].append(chunk.text)
        output["metadatas"].append(
            {"chapter": chunk.chapter, "token_size": chunk.token_size}
        )
    return output


def write_to_collection(
    client: ClientAPI, collection: chromadb.Collection, chunks: list[EmbeddedChunk]
) -> None:
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


def main():
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    # TODO temp hardcode
    collection = get_collection(client=client, collection_name=TEST_COLLECTION_NAME)
    # TODO temp hardcode
    all_chunks = read_jsonl(
        dir=EMBEDDED_CHUNK_DIR, file_name=EMBEDDED_CHUNKS_FILE, cls=EmbeddedChunk
    )
    write_to_collection(collection=collection, chunks=all_chunks, client=client)


if __name__ == "__main__":
    main()
