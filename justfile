set dotenv-load := true

collect-course-materials:
    python course-downloader.py

delete-course-materials:
    rm -rf $COURSE_MATERIALS_PATH

echo-vars:
    echo $COURSE_MATERIALS_PATH

format:
    black .