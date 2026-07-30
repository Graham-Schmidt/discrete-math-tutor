import chromadb
from openai import OpenAI

from eval.retrieval_eval import evaluate_retrieval
from ingestion.store import get_collection
from config import TEST_COLLECTION_NAME, CHROMA_PERSIST_DIR
from testing.test_queries import TEST_QUERIES


def main():
    chroma_client = chromadb.PersistentClient(CHROMA_PERSIST_DIR)
    openai_client = OpenAI()
    collection = get_collection(
        client=chroma_client, collection_name=TEST_COLLECTION_NAME
    )
    for query in TEST_QUERIES:
        evaluate_retrieval(
            query=query, collection=collection, openai_client=openai_client
        )


if __name__ == "__main__":
    main()
