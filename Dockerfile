FROM python:3.13
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=ghcr.io/casey/just:latest /just /usr/local/bin/just

COPY app .
EXPOSE 8000

RUN useradd app
USER app

WORKDIR /usr/local/app/backend

CMD ["just", "serve"]