"""Chunk, embed, and load documents into Chroma."""

import json
import logging
import sys
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COLLECTION_NAME = "advisor_kb"
SEED_FILE = Path(__file__).parent / "seed_chunks.json"
SOURCES_DIR = Path(__file__).parent / "sources"


def get_client():
    chroma_path = Path(settings.chroma_path)
    chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def ingest_seed_data(reset: bool = False):
    """Load seed chunks into Chroma."""
    client = get_client()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            logger.info("Deleted existing collection")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"kb_version": settings.kb_version},
    )

    with open(SEED_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Upsert in batches
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    logger.info("Ingested %d chunks into %s (kb_version=%s)", len(ids), COLLECTION_NAME, settings.kb_version)
    return collection.count()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest knowledge base into Chroma")
    parser.add_argument("--reset", action="store_true", help="Reset collection before ingest")
    args = parser.parse_args()

    count = ingest_seed_data(reset=args.reset)
    print(f"Knowledge base ready: {count} chunks")
