"""Shared filesystem/serialization helpers used across ingestion and retrieval."""

from pathlib import Path
import json
from typing import TypeVar
from dataclasses import asdict

T = TypeVar("T")


def generate_chunk_id(source_type: str, chapter: str, sequence: int) -> str:
    """Build a stable, zero-padded id for a chunk, e.g. 'reading_chap02_0007'."""
    return f"{source_type}_{chapter}_{sequence:04d}"


def generate_section_id(
    source_type: str, chapter: str, section_number: str, sequence: int
) -> str:
    """Build a stable, zero-padded id for a section, e.g. 'reading_chap02_2.1_0003'."""
    return f"{source_type}_{chapter}_{section_number}_{sequence:04d}"


def write_jsonl(records: list, dir: Path, file_name: str):
    """Intakes array of record objects to write as JSONL to provided path"""
    serialized_records = [asdict(record) for record in records]

    _check_for_dir(dir)
    full_path = dir / f"{file_name}.jsonl"
    with open(full_path, "w") as file:
        for record in serialized_records:
            file.write(json.dumps(record) + "\n")


def read_jsonl(file_path: Path, cls: type[T]) -> list[T]:
    """Read a JSONL file, constructing one `cls` instance per line."""
    with open(file_path) as file:
        return [cls(**json.loads(line)) for line in file]


def read_md_by_line(file_name: Path) -> list[str]:
    """Read a file and return its lines, newlines included."""
    with open(file_name) as file:
        res = file.readlines()
    return res


def _check_for_dir(dir: Path):
    """Create `dir` (and any missing parents) if it doesn't already exist."""
    if not dir.is_dir():
        Path(dir).mkdir(parents=True, exist_ok=True)
