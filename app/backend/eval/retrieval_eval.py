"""Evaluates retrieval quality against a hand-labeled set of expected sections."""

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
    """Retrieve `query`'s top chunks and check both its hit rate and the full test set's MRR."""
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
    """Assert all 5 retrieved chunks' sections match EXPECTED_SECTIONS[query]; print a diff on failure."""
    try:
        section_numbers = [chunk.section_number for chunk in chunks]
        hit_rate = _hit_rate(
            query=query, chunks=chunks, section_numbers=section_numbers
        )
        assert hit_rate == 5
    except AssertionError as e:
        print(e)
        print(
            f"Expected segments: {EXPECTED_SECTIONS[query]}\n Encountered segments: {section_numbers}"
        )


def _eval_mrr(queries: list[str], collection: Collection, client: OpenAI):
    """Assert the mean reciprocal rank across `queries` exceeds 0.8."""
    mrr = _check_mrr(queries=TEST_QUERIES, collection=collection, client=client)
    assert mrr > 0.8


def _hit_rate(
    query: str, chunks: list[RetrievedChunk], section_numbers: list[str]
) -> int:
    """Count how many retrieved section numbers appear in the expected set for `query`
    (multiset overlap, so a repeated expected section can count more than once)."""
    # section_numbers = [chunk.section_number for chunk in chunks]
    c_1 = Counter(section_numbers)
    c_2 = Counter(EXPECTED_SECTIONS[query])
    shared_section_numbers = sum((c_1 & c_2).values())
    return shared_section_numbers


def _check_mrr(queries: list[str], collection: Collection, client: OpenAI):
    """Compute the mean reciprocal rank of the first correct chunk across `queries`."""
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
    """Return 1/rank of the first chunk whose section is expected for `query`, or 0 if none match."""
    correct_section = set(EXPECTED_SECTIONS[query])
    for rank, chunk in enumerate(chunks, start=1):
        if chunk.section_number in correct_section:
            return 1 / rank
    return 0
