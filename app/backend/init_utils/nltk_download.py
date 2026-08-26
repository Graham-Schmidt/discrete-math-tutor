"""One-off script to fetch the NLTK sentence tokenizer data used by ingestion/chunk.py."""

import nltk

nltk.download("punkt_tab")
