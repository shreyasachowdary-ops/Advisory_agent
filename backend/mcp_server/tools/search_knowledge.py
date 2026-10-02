"""Vector retrieval against local Chroma knowledge base."""

import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "advisor_kb"


def _get_collection():
    client = chromadb.PersistentClient(
        path=settings.chroma_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(name=COLLECTION_NAME)


def search_knowledge(
    query: str,
    audience: str = "both",
    age_band: str | None = None,
    topics: list[str] | None = None,
    max_results: int = 4,
) -> dict[str, Any]:
    """Search curated knowledge base with optional metadata filters."""
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        logger.warning("Knowledge base is empty — run ingestion first")
        return {"results": [], "kb_version": settings.kb_version, "total_chunks": 0}

    where_filter: dict[str, Any] | None = None
    if age_band:
        where_filter = {"age_band": {"$in": [age_band, "all"]}}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(max_results, count),
            where=where_filter,
        )
    except Exception as exc:
        logger.error("Chroma query failed: %s", exc)
        return {"results": [], "kb_version": settings.kb_version, "error": str(exc)}

    snippets: list[dict[str, Any]] = []
    if results and results.get("documents"):
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [1.0] * len(docs)

        for doc, meta, chunk_id, dist in zip(docs, metas, ids, distances):
            meta_audience = meta.get("audience", "both")
            if audience != "both" and meta_audience not in (audience, "both"):
                continue
            if topics:
                chunk_topic = meta.get("topic", "")
                if chunk_topic and chunk_topic not in topics:
                    continue

            confidence = max(0.0, 1.0 - dist) if dist is not None else 0.5
            snippets.append(
                {
                    "chunk_id": chunk_id,
                    "text": doc,
                    "title": meta.get("title", "Unknown"),
                    "url": meta.get("source_url", ""),
                    "topic": meta.get("topic", ""),
                    "audience": meta_audience,
                    "age_band": meta.get("age_band", "all"),
                    "source": meta.get("source", ""),
                    "confidence": round(confidence, 3),
                }
            )

    return {
        "results": snippets[:max_results],
        "kb_version": settings.kb_version,
        "total_chunks": count,
    }
