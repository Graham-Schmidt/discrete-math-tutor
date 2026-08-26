"""Methods to interact with ChatGPT"""

from openai import OpenAI

from config import GPT_4_1_MINI
from models import RetrievedChunk
from prompts import SYSTEM_ANSWER_STUDENT_QUESTION


def get_completion(client: OpenAI, prompt: str, model: str, system_prompt: str = ""):
    """Call the OpenAI Responses API with `prompt` as input and `system_prompt` as instructions."""
    response = client.responses.create(
        model=model, input=prompt, instructions=system_prompt
    )
    return response


# this function belongs in a different module
def answer_user_question(
    openai_client: OpenAI, user_query: str, retrieved_chunks: list[RetrievedChunk]
):
    """Answer a student's question by grounding a chat completion in the retrieved chunks."""
    formatted_chunks = _format_context(chunks=retrieved_chunks)
    full_input = _build_user_input(query=user_query, context=formatted_chunks)
    result = get_completion(
        client=openai_client,
        prompt=full_input,
        model=GPT_4_1_MINI,
        system_prompt=SYSTEM_ANSWER_STUDENT_QUESTION,
    )
    return result


def _format_context(chunks: list[RetrievedChunk]) -> str:
    """Render retrieved chunks as chapter-labeled text blocks for the prompt."""
    return "\n\n".join(f"[Source: Chapter {c.chapter}]\n{c.text}" for c in chunks)


def _build_user_input(query: str, context: str) -> str:
    """intakes raw user string and formatted chunks (via _format_context())"""
    output = ""
    # RAG best practice is context first, query second
    formatted_retrieved_context = f"# retrieved relevant context \n{context}\n\n"
    output += formatted_retrieved_context
    formatted_user_query = f"# user query \n{query}\n\n"
    output += formatted_user_query
    return output
