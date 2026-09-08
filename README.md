# Study Buddy for MIT's Mathematics for Computer Science | 6.042J
This application serves as an AI-powered reference guide and study helper for MIT's Mathematics for Computer Science class 6.042J. It uses Retrieval Augmented Generation (RAG) to ground its answers in the textbooks provided for this course, and always cites the location of its findings to serve as easy reference for students.

## Quick Start

This project requires Docker to be installed.

- Run 'just build' to build the Docker image.
- Run 'just build-data-backend' to process all source data and build the vector database.
    - This is a **heavy** process and may take over 24 hours depending on your hardware.
- Run 'just serve' to serve application.
