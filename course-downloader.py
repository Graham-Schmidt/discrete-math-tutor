import requests
import zipfile
from pathlib import Path

from config import COURSE_DATA_DIR


def delete_archive(filename: str):
    file = Path(filename)
    file.unlink(missing_ok=True)


def unzip_files(zip_filename: str):
    with zipfile.ZipFile(zip_filename, "r") as zip_ref:
        zip_ref.extractall(COURSE_DATA_DIR)


def download_course_materials() -> str:
    """returns zip filename"""
    url = "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/6.042j-fall-2010.zip"
    output_filename = "temp.zip"
    response = requests.get(url)
    response.raise_for_status()

    with open(output_filename, "wb") as file:
        file.write(response.content)

    return output_filename


def main():
    try:
        zip_filename = download_course_materials()
        unzip_files(zip_filename)
        delete_archive(zip_filename)
    except requests.RequestException as e:
        print(f"Download failed: {e}")
        raise SystemExit(1)
    except zipfile.BadZipFile as e:
        print(f"Downlaoded file wasn't a valid zip file: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
