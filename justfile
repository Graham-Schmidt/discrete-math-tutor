set dotenv-load := true

build:
    docker compose build

[working-directory('app/backend')]
serve:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

[working-directory('app/backend')]
build-backend-data:
    python sqlite_utils.py
    python init_utils/nltk_download.py
    python pipeline_builder.py
    
format:
    black .
