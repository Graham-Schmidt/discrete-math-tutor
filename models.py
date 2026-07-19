from dataclasses import dataclass, field


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
