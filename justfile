set dotenv-load := true

collect-course-materials:
    python course_downloader.py

delete-course-materials:
    rm -rf $COURSE_MATERIALS_PATH

echo-vars:
    echo $COURSE_MATERIALS_PATH

format:
    black .

init-nltk:
    python init-utils/nltk_download.py