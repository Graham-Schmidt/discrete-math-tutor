"""
retrieval_eval.py's core loop is small — call your existing retrieve() per query,
compare RetrievedChunk.section_number against expected_sections,
aggregate. This slots in as a pure consumer of retrieve.py,
no changes needed to the pipeline itself.
"""

from collections import Counter

from retrieval.retrieve import retrieve
from chromadb import Collection
from openai import OpenAI

from models import RetrievedChunk
from testing.test_queries import (
    TEST_QUERY_1,
    TEST_QUERY_2,
    TEST_QUERY_3,
    TEST_QUERY_4,
    TEST_QUERY_5,
    TEST_QUERIES,
)

EXPECTED_SECTIONS = {
    TEST_QUERY_1: ["2.1.2", "2.1", "2.1", "2.1.1", "2.1"],
    TEST_QUERY_2: ["2.1", "2.1", "2.1.2", "2.1", "2.6.4"],
    TEST_QUERY_3: ["2.1.2", "2.1.2", "2.1.2", "2.1.2", "2.1.2"],
    TEST_QUERY_4: ["2.6.4", "2.6.1", "2.1", "2.6.1", "2.6.1"],
    TEST_QUERY_5: ["2.1.3", "2.3.1", "2.1.3", "2.5", "2.1.3"],
}


def evaluate_retrieval(query: str, collection: Collection, openai_client: OpenAI):
    chunks = retrieve(
        user_query=query,
        collection=collection,
        n_results=5,
        openai_client=openai_client,
    )
    _eval_correct_chunks_retrieved(query=query, chunks=chunks)
    _eval_mrr(queries=TEST_QUERIES, collection=collection, client=openai_client)
    print(f"Evaluation passed for '{query}'")


def _eval_correct_chunks_retrieved(query: str, chunks: list[RetrievedChunk]):
    hit_rate = _hit_rate(query=query, chunks=chunks)
    assert hit_rate == 5


def _eval_mrr(queries: list[str], collection: Collection, client: OpenAI):
    mrr = _check_mrr(queries=TEST_QUERIES, collection=collection, client=client)
    assert mrr > 0.8


def _hit_rate(query: str, chunks: list[RetrievedChunk]) -> int:
    section_numbers = [chunk.section_number for chunk in chunks]
    c_1 = Counter(section_numbers)
    c_2 = Counter(EXPECTED_SECTIONS[query])
    shared_section_numbers = sum((c_1 & c_2).values())
    return shared_section_numbers


def _check_mrr(queries: list[str], collection: Collection, client: OpenAI):
    ranks = [
        _reciprocal_rank(
            query,
            retrieve(
                user_query=query,
                collection=collection,
                n_results=5,
                openai_client=client,
            ),
        )
        for query in queries
    ]
    return sum(ranks) / len(ranks)


def _reciprocal_rank(query: str, chunks: list[RetrievedChunk]):
    correct_section = set(EXPECTED_SECTIONS[query])
    for rank, chunk in enumerate(chunks, start=1):
        if chunk.section_number in correct_section:
            return 1 / rank
    return 0
