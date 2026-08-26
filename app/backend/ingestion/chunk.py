"""Splits segmented sections into token-bounded chunks and enriches each with
situating context (via an LLM call) for embedding."""

from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from nltk.tokenize import sent_tokenize

from openai import OpenAI
import tiktoken
from tqdm import tqdm

from models import ReadingChapterChunk, Section
from config import CHUNK_JSONL_DIR, EMBEDDING_MODEL_SMALL, GPT_4_1_MINI
from utils import generate_chunk_id, write_jsonl
from ingestion.segment import segment_markdown_file
from prompts import USER_CONTEXT_CHUNKING_PROMPT
from chat import get_completion

ENC = tiktoken.encoding_for_model(EMBEDDING_MODEL_SMALL)
CHUNK_SIZE_LIMIT = 512

load_dotenv()


@dataclass
class NextChunkResult:
    """A chunk paired with the number of source lines it consumed."""

    chunk: ReadingChapterChunk
    line_count: int


def chunk_sections(
    sections: list[Section], client: OpenAI
) -> list[ReadingChapterChunk]:
    """intakes list of sections, transforms into chunks"""
    chunks = []
    chunk_counter = 0
    for section in tqdm(sections):
        if _count_tokens(section.text) > CHUNK_SIZE_LIMIT:
            child_chunks = _create_child_chunks(
                client=client, section=section, sequence_counter=chunk_counter
            )
            for c in child_chunks:
                chunks.append(c)
        else:
            chunk = _create_reading_chapter_chunk(
                client=client,
                sequence_counter=chunk_counter,
                token_size=_count_tokens(section.text),
                text=section.text,
                parent_id=section.id,
                content_type=section.content_type,
                chapter=section.chapter,
                section_title=section.section_title,
                section_number=section.section_number,
                file_path=section.file_path,
            )
            chunks.append(chunk)
        chunk_counter += 1
    return chunks


def chunk_markdown_file(input_file_path: Path, client: OpenAI):
    """Breaks provided markdown file into chunks, writes to JSONL"""
    sections = segment_markdown_file(file_path=input_file_path)
    chunks = chunk_sections(sections=sections, client=client)
    output_file_name = input_file_path.stem[-15:]
    _write_chunks_to_jsonl(
        chunks=chunks, path=CHUNK_JSONL_DIR, file_name=output_file_name
    )


def get_whole_markdown_doc(file_path: Path) -> str:
    """Read a markdown file's full contents as a single string."""
    with open(file_path) as file:
        return file.read()


def _write_chunks_to_jsonl(
    chunks: list[ReadingChapterChunk], path: Path, file_name: str
):
    """Serialize chunks to `path/file_name.jsonl`."""
    write_jsonl(chunks, path, file_name)


def _count_tokens(text: str) -> int:
    """Count tokens in `text` using the embedding model's tokenizer."""
    return len(ENC.encode(text))


def _create_reading_chapter_chunk(
    client: OpenAI,
    sequence_counter: int,
    token_size: int,
    text: str,
    parent_id: str,
    content_type: str,
    chapter: str,
    section_title: str,
    section_number: str,
    file_path: Path | None,
):
    """Build a `ReadingChapterChunk` and populate its embedding context via an LLM call."""
    chunk = ReadingChapterChunk(
        id=generate_chunk_id(
            source_type=ReadingChapterChunk.source_type,
            chapter=chapter,
            sequence=sequence_counter,
        ),
        token_size=token_size,
        text=text,
        parent_id=parent_id,
        content_type=content_type,
        chapter=chapter,
        section_number=section_number,
        section_title=section_title,
    )
    context = _get_chunk_context(chunk=chunk, client=client, file_path=file_path)
    chunk.context_for_embedding = context
    return chunk


def _get_chunk_context(
    chunk: ReadingChapterChunk, client: OpenAI, file_path: Path | None
) -> str:
    """Ask the LLM to situate `chunk` within its full source document, for retrieval context."""
    if file_path is None:
        print(f"Unable to get context for file {chunk.id}, no file path found")
        return ""
    full_document = get_whole_markdown_doc(file_path=file_path)
    prompt = USER_CONTEXT_CHUNKING_PROMPT.format(
        document=full_document, chunk=chunk.text
    )
    response = get_completion(client=client, prompt=prompt, model=GPT_4_1_MINI)
    return response.output_text


def _create_child_chunks(
    client: OpenAI, section: Section, sequence_counter: int
) -> list[ReadingChapterChunk]:
    """Split an over-limit section into sentence-aligned chunks, each under CHUNK_SIZE_LIMIT tokens."""
    sentences = sent_tokenize(text=section.text)
    index = 0
    child_chunks = []
    text = ""
    while index < len(sentences):
        token_size = _count_tokens(text)
        if token_size < CHUNK_SIZE_LIMIT:
            text += f"{sentences[index]} "
        else:
            child_chunks.append(
                _create_reading_chapter_chunk(
                    client=client,
                    sequence_counter=sequence_counter,
                    token_size=token_size,
                    text=text,
                    parent_id=section.id,
                    content_type=section.content_type,
                    chapter=section.chapter,
                    section_title=section.section_title,
                    section_number=section.section_number,
                    file_path=section.file_path,
                )
            )
            text = f"{sentences[index]} "
            sequence_counter += 1
        index += 1
    if text:
        child_chunks.append(
            _create_reading_chapter_chunk(
                client=client,
                sequence_counter=sequence_counter,
                token_size=_count_tokens(section.text),
                text=text,
                parent_id=section.id,
                content_type=section.content_type,
                chapter=section.chapter,
                section_title=section.section_title,
                section_number=section.section_number,
                file_path=section.file_path,
            )
        )
    return child_chunks
