"""
POST /embed — Generate embeddings via SentenceTransformers.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter

from app.pipelines import embeddings as embeddings_pipeline
from app.schemas.requests import EmbedRequest
from app.schemas.responses import EmbedResponse
from app.utils.text_cleaner import clean_texts

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/embed", response_model=EmbedResponse)
async def generate_embeddings(request: EmbedRequest):
    """
    Generate dense vector embeddings for the provided texts.

    Optionally stores to pgvector if ``store=true`` (paid mode).
    Returns the embedding matrix, dimensions, and count.
    """
    logger.info("Embedding requested for %d texts", len(request.texts))

    cleaned = clean_texts(request.texts)

    # SentenceTransformer encode is CPU-bound
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(
        None, embeddings_pipeline.encode_batch, cleaned
    )

    response_data = {
        "embeddings": embeddings,
        "dimension": len(embeddings[0]) if embeddings else 0,
        "count": len(embeddings),
    }

    # Optional pgvector storage (paid mode)
    if request.store:
        storage_result = await embeddings_pipeline.store_to_pgvector(
            cleaned, embeddings, request.metadata
        )
        response_data["storage"] = storage_result

    return EmbedResponse(**response_data)
