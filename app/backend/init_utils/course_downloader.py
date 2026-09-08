"""One-off script to download and unpack the MIT OCW 6.042J course materials."""

import requests
import zipfile
from pathlib import Path

from config import COURSE_DATA_DIR


def _delete_archive(filename: str):
    """Delete the downloaded zip archive, if present."""
    file = Path(filename)
    file.unlink(missing_ok=True)


def _unzip_files(zip_filename: str):
    """Extract the course materials zip into COURSE_DATA_DIR."""
    with zipfile.ZipFile(zip_filename, "r") as zip_ref:
        zip_ref.extractall(COURSE_DATA_DIR)


def _download_course_materials() -> str:
    """writes zip archive to disk, returns zip filename"""
    url = "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/6.042j-fall-2010.zip"
    output_filename = "temp.zip"
    response = requests.get(url)
    response.raise_for_status()

    with open(output_filename, "wb") as file:
        file.write(response.content)

    return output_filename


def download_course():
    """Download, unpack, and clean up the course materials archive."""
    try:
        zip_filename = _download_course_materials()
        _unzip_files(zip_filename)
        _delete_archive(zip_filename)
    except requests.RequestException as e:
        print(f"Download failed: {e}")
        raise SystemExit(1)
    except zipfile.BadZipFile as e:
        print(f"Downlaoded file wasn't a valid zip file: {e}")
        raise SystemExit(1)
