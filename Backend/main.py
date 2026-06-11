import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import (
    ALLOWED_ORIGINS,
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    SPACY_MODEL_PRIMARY,
    SPACY_MODEL_SECONDARY,
    SENTENCE_TRANSFORMER_MODEL
)

from backend.api.routes import router

logger = logging.getLogger("ats_resume_scorer")


# ✅ CLEAN LIFESPAN (NO HEAVY BLOCKING)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Load models on startup
    import spacy
    
    logger.info(f"Loading spaCy: {SPACY_MODEL_PRIMARY}")
    try:
        app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
    except OSError:
        logger.warning(f"Falling back to {SPACY_MODEL_SECONDARY}")
        app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)
    logger.info("spaCy loaded")

    # ⏳ Lazy load SentenceTransformer on first request (too heavy for startup)
    app.state.embedder = None
    logger.info("SentenceTransformer: will lazy-load on first analysis request")

    logger.info("API ready - waiting for requests")

    yield

    logger.info("Shutting down API")


# ✅ FASTAPI APP
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES
app.include_router(router)


# ✅ ROOT
@app.get("/")
async def root():
    return {
        "name": "ATS Resume Analyzer API",
        "version": "2.0.0",
        "status": "running"
    }