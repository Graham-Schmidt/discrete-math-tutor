"""Dataclasses shared across the ingestion/retrieval pipeline.

Pipeline flow: a source document is segmented into `Section`s, which are
split into `Chunk`s (`ReadingChapterChunk`), which are embedded
(`EmbeddedChunk`) and stored; a query then comes back as `RetrievedChunk`s.
"""

from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class SourceTypes(Enum):
    """Origin of a document, used as the id prefix for chunks/sections."""

    READING = "reading"


@dataclass
class Chunk:
    """Base unit of text sized for embedding/retrieval."""

    id: str
    token_size: int = 0
    text: str = ""


@dataclass
class ReadingChapterChunk(Chunk):
    """A `Chunk` sourced from a textbook reading chapter."""

    # class var, not a dataclass field: fixed per-class, not per-instance
    source_type = SourceTypes.READING.value
    parent_id: str = ""
    content_type: str = ""
    chapter: str = ""
    section_number: str = ""
    section_title: str = ""
    context_for_embedding: str = ""
    file_path: Path | None = None


@dataclass
class EmbeddedChunk(ReadingChapterChunk):
    """A `ReadingChapterChunk` with its embedding vector attached."""

    embedding: list[float] = field(default_factory=list)


@dataclass
class RetrievedChunk(ReadingChapterChunk):
    """A chunk returned from a similarity query, with its distance to the query."""

    id: str
    distance: float = 0


@dataclass
class Section:
    """A contiguous, classified span of a document produced by segmentation,
    before it's split into chunks."""

    id: str
    text: str
    content_type: str
    chapter: str = ""
    section_number: str = ""
    section_title: str = ""
    file_path: Path | None = None
