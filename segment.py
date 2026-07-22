"""Segments extracted chapter markdown into typed Section objects."""

import re
from pathlib import Path

from models import Section
from utils import read_md_by_line, generate_segment_id
from config import CHAPTER_2_MD_FILE_PATH

# content_type patterns, first match wins; unmatched text defaults to "exposition".
# TODO naive first: some Theorem/Definition labels in the real text carry zero
_CONTENT_TYPE_PATTERNS = [
    ("theorem", re.compile(r"^\**(Theorem|Lemma|Corollary)\b", re.IGNORECASE)),
    ("definition", re.compile(r"^\**Definition\b", re.IGNORECASE)),
    ("rule", re.compile(r"^\**Rule\s+\d", re.IGNORECASE)),
    ("proof", re.compile(r"^\**Proof\b|^Case\s+\d", re.IGNORECASE)),
    ("example", re.compile(r"^\**Example\b", re.IGNORECASE)),
    ("exercise", re.compile(r"^\**Exercise\b", re.IGNORECASE)),
]

_NUMBERED_HEADER_RE = re.compile(
    r"^#{1,4}\s*(?P<number>\d+(?:\.\d+)*)\.?\s+(?P<title>.+)$"
)
_HEADER_PREFIX_RE = re.compile(r"^#{1,4}\s*")
_CHAPTER_ID_RE = re.compile(r"chap\d+")


def segment_markdown_file(file_path: Path) -> list[Section]:
    chapter = _extract_chapter_id(file_path)
    lines = read_md_by_line(file_path)
    paragraphs = _split_into_paragraphs(lines)
    return _build_sections(paragraphs, chapter, file_path)


def _extract_chapter_id(file_path: Path) -> str:
    match = _CHAPTER_ID_RE.search(file_path.stem)
    assert match is not None, f"no chapter id (e.g. 'chap02') found in {file_path.name}"
    return match.group()


def _split_into_paragraphs(lines: list[str]) -> list[str]:
    """Scanner phase: blank-line-delimited paragraphs. Structural only, no
    understanding of content. A header line also always starts a new
    paragraph -- verified every header in the chapter 2 sample is already
    blank-line-isolated on both sides, but that's enforced explicitly rather
    than relied on silently for chapters not yet checked."""
    paragraphs: list[str] = []
    current = ""
    for line in lines:
        is_header = line.lstrip().startswith("#")
        if line.strip() == "" or is_header:
            if current:
                paragraphs.append(current)
                current = ""
            if is_header:
                paragraphs.append(line)
        else:
            current += line
    if current:
        paragraphs.append(current)
    return paragraphs


def _classify_content_type(text: str) -> str:
    for content_type, pattern in _CONTENT_TYPE_PATTERNS:
        if pattern.match(text):
            return content_type
    return "exposition"


def _parse_numbered_header(stripped_paragraph: str) -> tuple[str, str] | None:
    """None if not a bare/dotted numbered header (e.g. a named subsection with
    no number, or a labeled reference like "Rule 2.1.1." -- callers only reach
    this after content-type classification already ruled labels out)."""
    match = _NUMBERED_HEADER_RE.match(stripped_paragraph)
    if match is None:
        return None
    return match.group("number"), match.group("title").strip()


def _build_sections(
    paragraphs: list[str], chapter: str, file_path: Path
) -> list[Section]:
    """Parser phase: walks paragraphs in order, carrying section_number/
    section_title as running state. Headers are consumed to update that state
    (or, for labeled references like "### Theorem 2.3.2.", classified and
    emitted as real content) -- never emitted as their own Section, since a
    bare title has nothing a query could match against."""
    section_number, section_title = "", ""
    sections: list[Section] = []
    counter = 0
    prev_section_number = ""

    for paragraph in paragraphs:
        stripped = paragraph.strip()
        is_header = stripped.startswith("#")
        body = (
            _HEADER_PREFIX_RE.sub("", stripped, count=1).strip()
            if is_header
            else stripped
        )
        content_type = _classify_content_type(body)

        if is_header and content_type == "exposition":
            numbered = _parse_numbered_header(stripped)
            if numbered is not None:
                number, title = numbered
                if (
                    "." in number
                ):  # bare number = chapter title, already known from filename
                    section_number, section_title = number, title
                    if section_number != prev_section_number:
                        counter = 0
                        prev_section_number = section_number
            elif body:
                # unnumbered header, no recognized label (e.g. "Cardinality", or a
                # "Potential Pitfall" callout) -- naive first: update title only.
                section_title = body
            continue

        sections.append(
            Section(
                # TODO source_type hardcoded for now
                id=generate_segment_id(
                    source_type="reading",
                    chapter=chapter,
                    section_number=section_number,
                    sequence=counter,
                ),
                text=body,
                content_type=content_type,
                chapter=chapter,
                section_number=section_number,
                section_title=section_title,
                file_path=file_path,
            )
        )
        counter += 1

    return sections


def main():
    sections = segment_markdown_file(CHAPTER_2_MD_FILE_PATH)
    for section in sections[:15]:
        print("=" * 40)
        print(section)


if __name__ == "__main__":
    main()
