from pathlib import Path
import re

from config import COURSE_DATA_DIR

CHAP_PATTERN = re.compile(r"chap(\d{2})")


def get_all_chapter_pdf_file_paths() -> list[Path]:
    static_resource_path = Path(COURSE_DATA_DIR) / "static_resources"
    output = []
    for item in static_resource_path.iterdir():
        if item.is_file():
            is_match = CHAP_PATTERN.search(item.name)
            if is_match:
                output.append(item)

    return output
