from dataclasses import dataclass, field

from utils import generate_chunk_id


@dataclass
class Chunk:
    id: str
    token_size: int = 0
    text: str = ""


@dataclass
class ReadingChapterChunk(Chunk):
    chapter: str = ""


@dataclass
class EmbeddedChunk(ReadingChapterChunk):
    embedding: list[float] = field(default_factory=list)


@dataclass
class RetrievedChunk(ReadingChapterChunk):
    id: str
    distance: float = 0
