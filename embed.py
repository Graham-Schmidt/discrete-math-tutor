# intakes chunks
# calls embedding API to get vector array
# combines and writes to disk as JSONL

from pathlib import Path
from dotenv import load_dotenv
from dataclasses import asdict

from openai import OpenAI

from models import EmbeddedChunk, ReadingChapterChunk
from utils import read_jsonl, write_jsonl
from config import (
    EMBEDDED_CHUNK_DIR,
    CHUNK_JSONL_DIR,
    EMBEDDED_CHUNKS_FILE,
    RAW_CHUNKS_FILE,
)

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"


def embed_chunks(
    chunks: list[ReadingChapterChunk], client: OpenAI
) -> list[EmbeddedChunk]:
    """Embed a list of chunks in a single batched API call.

    Naive: no retry on rate limits / transient errors, no request-size
    chunking. Fine at one-chapter scale; both become necessary once
    ingesting the full book.
    """
    text_to_embed = [
        f"This chunk is from chapter {chunk.chapter}, Section {chunk.section_title}. {chunk.text}"
        for chunk in chunks
    ]
    vectors_by_position = _call_embedding_api(texts=text_to_embed, client=client)

    return [
        EmbeddedChunk(
            id=chunk.id,
            token_size=chunk.token_size,
            text=chunk.text,
            chapter=chunk.chapter,
            embedding=vectors_by_position[i],
        )
        for i, chunk in enumerate(chunks)
    ]


def embed_query(text: str, client: OpenAI) -> list[float]:
    """
    Get embedding for arbitrary text
    Returns raw dictionary
    """
    return _call_embedding_api(texts=[text], client=client)[0]


def embed_chapter_file(
    input_path: Path,
    client: OpenAI,
) -> None:
    """Read a chapter's chunk JSONL, embed it, write embedded JSONL."""
    input_dir, input_file_name = input_path.parent, input_path.name
    chunks = read_jsonl(
        dir=input_dir, file_name=input_file_name, cls=ReadingChapterChunk
    )
    embedded_chunks = embed_chunks(chunks, client)
    output_file_name = input_path.stem
    write_jsonl(
        records=embedded_chunks, dir=EMBEDDED_CHUNK_DIR, file_name=output_file_name
    )


def _call_embedding_api(
    texts: list[str], client: OpenAI, model: str = EMBEDDING_MODEL
) -> dict:
    response = client.embeddings.create(input=texts, model=model)
    vectors_by_position = {item.index: item.embedding for item in response.data}
    return vectors_by_position


# if __name__ == "__main__":
#     client = OpenAI()
#     embed_chapter_file(
#         # This is a bad pattern, expects complete path + filename
#         input_dir=CHUNK_JSONL_DIR,
#         # TODO temp hardcode
#         input_file_name=RAW_CHUNKS_FILE,
#         output_dir=EMBEDDED_CHUNK_DIR,
#         # TODO temp hardcode
#         output_file_name=EMBEDDED_CHUNKS_FILE,
#         client=client,
#     )
