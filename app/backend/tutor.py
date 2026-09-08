"""CLI orchestration for the ingestion pipeline and end-to-end tutor Q&A."""

from chromadb.api import ClientAPI
from openai import OpenAI

from chat import answer_user_question
from retrieval.retrieve import retrieve

TEST_QUERY = "what is the axiomatic method?"


def fetch_answer(
    user_query: str, chroma_client: ClientAPI, openai_client: OpenAI, collection
):
    """Retrieve the chunks most relevant to `user_query` and answer it from them."""
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
