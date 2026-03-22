"""
NLP/Text Agent — FastAPI Application Entrypoint.

Initialises NLP pipeline singletons at startup via @app.on_event("startup").
Mounts all API routers for the 7 endpoints.
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("nlp-text-agent")

# ── App ──────────────────────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Unstructured Text & Semantic Specialist — processes text columns "
        "and documents through batched NLP pipelines (spaCy, Transformers, "
        "BERTopic, SentenceTransformers)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup — lazy-load NLP singletons ───────────────────────────────────────


@app.on_event("startup")
async def startup_load_models():
    """
    Pre-load all NLP pipeline singletons at server startup.
    Models are loaded once and shared across all requests.
    """
    start = time.time()
    logger.info("=" * 60)
    logger.info("NLP/Text Agent starting up…")
    logger.info("LLM Provider : %s", settings.LLM_PROVIDER)
    logger.info("spaCy Model  : %s", settings.SPACY_MODEL)
    logger.info("Sentiment    : %s", settings.SENTIMENT_MODEL)
    logger.info("Embeddings   : %s", settings.EMBEDDING_MODEL)
    logger.info("Batch Size   : %d", settings.NLP_BATCH_SIZE)
    logger.info("=" * 60)

    # Load in sequence (each model logs its own progress)
    try:
        from app.pipelines.sentiment import get_pipeline
        get_pipeline()
    except Exception as e:
        logger.warning("Sentiment model load deferred: %s", e)

    try:
        from app.pipelines.ner import get_nlp
        get_nlp()
    except Exception as e:
        logger.warning("spaCy model load deferred: %s", e)

    try:
        from app.pipelines.embeddings import get_model as get_embed_model
        get_embed_model()
    except Exception as e:
        logger.warning("Embedding model load deferred: %s", e)

    # BERTopic is loaded on first /topics call (heavier init)
    # LLM provider is loaded on first /classify or /summarize call

    elapsed = round(time.time() - start, 2)
    logger.info("Startup complete in %.2f seconds.", elapsed)


# ── Routers ──────────────────────────────────────────────────────────────────

from app.routes.sentiment import router as sentiment_router
from app.routes.entities import router as entities_router
from app.routes.topics import router as topics_router
from app.routes.classify import router as classify_router
from app.routes.embed import router as embed_router
from app.routes.summarize import router as summarize_router
from app.routes.health import router as health_router

app.include_router(sentiment_router, tags=["Sentiment"])
app.include_router(entities_router, tags=["NER"])
app.include_router(topics_router, tags=["Topics"])
app.include_router(classify_router, tags=["Classification"])
app.include_router(embed_router, tags=["Embeddings"])
app.include_router(summarize_router, tags=["Summarization"])
app.include_router(health_router, tags=["Health"])

# ── Root ─────────────────────────────────────────────────────────────────────


@app.get("/")
async def root():
    return {
        "service": "NLP/Text Agent",
        "version": settings.APP_VERSION,
        "port": settings.PORT,
        "docs": "/docs",
    }
