from pathlib import Path
import json
from typing import TypeVar
from dataclasses import asdict

T = TypeVar("T")


def generate_chunk_id(source_type: str, chapter: str, sequence: int) -> str:
    return f"{source_type}_{chapter}_{sequence:04d}"


def write_jsonl(records: list, dir: Path, file_name: str):
    """Intakes array of record objects to write as JSONL to provided path"""
    serialized_records = [asdict(record) for record in records]

    _check_for_dir(dir)
    full_path = dir / file_name
    with open(full_path, "w") as file:
        for record in serialized_records:
            file.write(json.dumps(record) + "\n")


def read_jsonl(dir: Path, file_name: str, cls: type[T]) -> list[T]:
    with open(dir / file_name) as file:
        return [cls(**json.loads(line)) for line in file]

def read_md_by_line(file_name: Path) -> list[str]:
    with open(file_name) as file:
        res = file.readlines()
    return res

def _check_for_dir(dir: Path):
    if not dir.is_dir():
        Path(dir).mkdir(parents=True, exist_ok=True)
