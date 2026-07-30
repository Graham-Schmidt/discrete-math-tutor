"""utility to call Marder via python"""

from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import save_output

from config import MARKER_OUTPUT_DIR, CHAPTER_2_PDF_FILE_PATH


def build_pdf_converter() -> PdfConverter:
    """Convert provided PDF file to Markdown via Marker"""
    return PdfConverter(artifact_dict=create_model_dict())


def extract_pdf_file(converter: PdfConverter, file_path: Path):
    rendered = converter(str(file_path))
    out_folder = MARKER_OUTPUT_DIR / file_path.stem
    out_folder.mkdir(parents=True, exist_ok=True)
    save_output(
        rendered=rendered, output_dir=str(out_folder), fname_base=file_path.stem
    )


def main():
    # TODO expand to loop over all chapters found in chapter dir
    chapter_2_path = Path(CHAPTER_2_PDF_FILE_PATH)
    converter = build_pdf_converter()
    extract_pdf_file(converter=converter, file_path=chapter_2_path)


if __name__ == "__main__":
    main()
