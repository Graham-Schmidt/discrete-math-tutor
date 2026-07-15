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

from models import ReadingChapterChunk
from config import CHUNK_JSONL_DIR
from utils import generate_chunk_id, write_jsonl

TEST_FILE_PATH = Path(
    "/Users/grahamschmidt/development/discrete-math-tutor/marker_output/38ca8d7baeedd6aa476010a0cbd041d0_MIT6_042JF10_chap02/38ca8d7baeedd6aa476010a0cbd041d0_MIT6_042JF10_chap02.md"
)
OUTPUT_PATH = Path(
    "/Users/grahamschmidt/development/discrete-math-tutor/jsonl/test.jsonl"
)
ENC = tiktoken.encoding_for_model("text-embedding-3-small")
CHUNK_SIZE_LIMIT = 512

load_dotenv()


@dataclass
class NextChunkResult:
    chunk: ReadingChapterChunk
    line_count: int


# ------------------------
# Public
# ------------------------
def chunk_markdown_file(file_path: Path):
    lines = _read_file(file_path)
    all_chunks = _get_chunks(lines)
    _write_chunks_to_jsonl(all_chunks, CHUNK_JSONL_DIR)


# ------------------------
# Private
# ------------------------
def _write_chunks_to_jsonl(chunk_array: list[ReadingChapterChunk], path: Path):
    write_jsonl(chunk_array, path, "chunks.jsonl")


def _count_tokens(text: str) -> int:
    return len(ENC.encode(text))


def _test_fit_next_paragraph(chunk: ReadingChapterChunk, line_token_size: int) -> bool:
    potential_size = chunk.token_size + line_token_size
    if potential_size <= CHUNK_SIZE_LIMIT:
        return True
    return False


def _get_next_chunk(
    lines: list[str], curr_index: int, sequence: int
) -> NextChunkResult:
    # TODO parse file name to properly extract chapter data
    line_count = 0
    chunk_id = generate_chunk_id("reading", "chap02", sequence)
    curr_chunk = ReadingChapterChunk(id=chunk_id, chapter="chap02")
    i = curr_index

    while i < len(lines):
        line = lines[i]
        line_token_size = _count_tokens(line)
        # Choose to always append first line, even if oversized
        if line_count == 0 or _test_fit_next_paragraph(
            chunk=curr_chunk, line_token_size=line_token_size
        ):
            curr_chunk.text += line
            curr_chunk.token_size += line_token_size
            line_count += 1
            i += 1
        else:
            break

    return NextChunkResult(chunk=curr_chunk, line_count=line_count)


def _get_chunks(lines: list[str]) -> list[ReadingChapterChunk]:
    sequence = 0
    curr_index = 0
    # call _get_next_chunk
    all_chunks = []
    while curr_index < len(lines):
        res = _get_next_chunk(lines, curr_index, sequence)
        all_chunks.append(res.chunk)
        curr_index += res.line_count
        sequence += 1

    return all_chunks


def _read_file(file_name: Path) -> list[str]:
    with open(file_name) as file:
        res = file.readlines()
    return res
