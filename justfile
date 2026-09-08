set dotenv-load := true

build:
    docker compose build

[working-directory('app/backend')]
serve:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

build-backend-data:
    python app/backend/init_utils/nltk_download.py
    python app/backend/pipeline_builder.py
    
format:
    black .
