from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    id: str
    token_size: int = 0
    text: str = ""


@dataclass
class ReadingChapterChunk(Chunk):
    parent_id: str = ""
    content_type: str = ""
    chapter: str = ""
    section_number: str = ""
    section_title: str = ""
    context_for_embedding: str = ""
    file_path: Path | None = None


@dataclass
class EmbeddedChunk(ReadingChapterChunk):
    embedding: list[float] = field(default_factory=list)


@dataclass
class RetrievedChunk(ReadingChapterChunk):
    id: str
    distance: float = 0


@dataclass
class Section:
    id: str
    text: str
    content_type: str
    chapter: str = ""
    section_number: str = ""
    section_title: str = ""
    file_path: Path | None = None
