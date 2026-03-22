"""
Embedding pipeline — SentenceTransformers.

Uses all-MiniLM-L6-v2 (free) or all-mpnet-base-v2 (paid).
Loaded once at startup as a singleton.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Singleton ────────────────────────────────────────────────────────────────

_model_instance = None


def get_model():
    """Return the cached SentenceTransformer model (lazy-loaded)."""
    global _model_instance
    if _model_instance is None:
        from sentence_transformers import SentenceTransformer

        settings = get_settings()
        logger.info("Loading SentenceTransformer model: %s", settings.EMBEDDING_MODEL)
        _model_instance = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            cache_folder=settings.HF_CACHE_DIR,
        )
        logger.info("SentenceTransformer model loaded successfully.")
    return _model_instance


# ── Batch encoding ───────────────────────────────────────────────────────────

def encode_batch(texts: list[str]) -> list[list[float]]:
    """
    Encode *texts* into dense vector embeddings.

    Returns a list of embedding vectors (list of floats).
    """
    model = get_model()
    embeddings = model.encode(texts, batch_size=len(texts), show_progress_bar=False)
    return embeddings.tolist()


# ── Optional pgvector storage ────────────────────────────────────────────────

async def store_to_pgvector(
    texts: list[str],
    embeddings: list[list[float]],
    metadata: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Store embeddings in pgvector (paid mode only).

    Returns a status dict with count of stored vectors.
    """
    settings = get_settings()

    if settings.VECTOR_STORE_TYPE != "pgvector" or not settings.PGVECTOR_URL:
        return {"stored": False, "reason": "pgvector not configured"}

    try:
        import asyncpg

        conn = await asyncpg.connect(settings.PGVECTOR_URL)

        # Ensure table exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS text_embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(%s),
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """ % len(embeddings[0]))

        # Insert embeddings
        for i, (text, emb) in enumerate(zip(texts, embeddings)):
            meta = metadata[i] if metadata else {}
            await conn.execute(
                """
                INSERT INTO text_embeddings (content, embedding, metadata)
                VALUES ($1, $2::vector, $3::jsonb)
                """,
                text,
                str(emb),
                str(meta),
            )

        await conn.close()
        return {"stored": True, "count": len(embeddings)}

    except Exception as e:
        logger.error("Failed to store embeddings in pgvector: %s", e)
        return {"stored": False, "reason": str(e)}
