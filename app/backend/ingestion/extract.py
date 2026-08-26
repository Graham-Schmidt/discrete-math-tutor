"""Utility to call Marker via python"""

from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import save_output

from config import MARKER_OUTPUT_DIR


def build_pdf_converter() -> PdfConverter:
    """Convert provided PDF file to Markdown via Marker"""
    return PdfConverter(artifact_dict=create_model_dict())


def extract_pdf_file(converter: PdfConverter, file_path: Path):
    """Render `file_path` to markdown and write it under MARKER_OUTPUT_DIR/<stem>/."""
    rendered = converter(str(file_path))
    out_folder = MARKER_OUTPUT_DIR / file_path.stem
    out_folder.mkdir(parents=True, exist_ok=True)
    save_output(
        rendered=rendered, output_dir=str(out_folder), fname_base=file_path.stem
    )


def convert_pdf_to_md(file_path: Path):
    """Build a fresh converter and extract `file_path` to markdown."""
    converter = build_pdf_converter()
    extract_pdf_file(converter=converter, file_path=file_path)
