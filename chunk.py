# 1. open file as I/O
# 2. read file contents while tracking char count
# 3a. when delimeter is found, seperate and return chunk
# 3b. when token limit is reached, make decision about chunk and return
# 4 attach metadata

# util: will adding next chunk break token limit?

from pathlib import Path
import tiktoken
from dataclasses import dataclass
from dotenv import load_dotenv

from models import ReadingChapterChunk, Section
from config import CHUNK_JSONL_DIR
from utils import generate_chunk_id, write_jsonl, read_md_by_line
from segment import segment_markdown_file

ENC = tiktoken.encoding_for_model("text-embedding-3-small")
CHUNK_SIZE_LIMIT = 512

load_dotenv()


@dataclass
class NextChunkResult:
    chunk: ReadingChapterChunk
    line_count: int


def chunk_sections(sections: list[Section]) -> list[ReadingChapterChunk]:
    """intakes list of sections, transforms into chunks"""
    chunks = []
    chunk_counter = 0
    for section in sections:
        chunk = ReadingChapterChunk(
            # TODO hardcoded source type
            id=generate_chunk_id(
                source_type="reading", chapter=section.chapter, sequence=chunk_counter
            ),
            token_size=_count_tokens(section.text),
            text=section.text,
            parent_id=section.id,
            content_type=section.content_type,
            chapter=section.chapter,
            section_title=section.section_title,
            section_number=section.section_number,
        )
        chunks.append(chunk)
        chunk_counter += 1
    return chunks


def chunk_markdown_file(input_file_path: Path):
    """Breaks provided markdown file into chunks, writes to JSONL"""
    sections = segment_markdown_file(file_path=input_file_path)
    chunks = chunk_sections(sections=sections)
    output_file_name = input_file_path.stem[-15:]
    _write_chunks_to_jsonl(
        chunks=chunks, path=CHUNK_JSONL_DIR, file_name=output_file_name
    )


def _write_chunks_to_jsonl(
    chunks: list[ReadingChapterChunk], path: Path, file_name: str
):
    write_jsonl(chunks, path, file_name)


def _count_tokens(text: str) -> int:
    return len(ENC.encode(text))


# def _test_fit_next_paragraph(chunk: ReadingChapterChunk, line_token_size: int) -> bool:
#     potential_size = chunk.token_size + line_token_size
#     if potential_size <= CHUNK_SIZE_LIMIT:
#         return True
#     return False


# def _get_next_chunk(
#     lines: list[str], curr_index: int, sequence: int
# ) -> NextChunkResult:
#     # TODO parse file name to properly extract chapter data
#     line_count = 0
#     chunk_id = generate_chunk_id("reading", "chap02", sequence)
#     curr_chunk = ReadingChapterChunk(id=chunk_id, chapter="chap02")
#     i = curr_index

#     while i < len(lines):
#         line = lines[i]
#         line_token_size = _count_tokens(line)
#         # Choose to always append first line, even if oversized
#         if line_count == 0 or _test_fit_next_paragraph(
#             chunk=curr_chunk, line_token_size=line_token_size
#         ):
#             curr_chunk.text += line
#             curr_chunk.token_size += line_token_size
#             line_count += 1
#             i += 1
#         else:
#             break

#     return NextChunkResult(chunk=curr_chunk, line_count=line_count)


# def _get_chunks(lines: list[str]) -> list[ReadingChapterChunk]:
#     sequence = 0
#     curr_index = 0
#     # call _get_next_chunk
#     all_chunks = []
#     while curr_index < len(lines):
#         res = _get_next_chunk(lines, curr_index, sequence)
#         all_chunks.append(res.chunk)
#         curr_index += res.line_count
#         sequence += 1

#     return all_chunks


# def _read_file(file_name: Path) -> list[str]:
#     with open(file_name) as file:
#         res = file.readlines()
#     return res
