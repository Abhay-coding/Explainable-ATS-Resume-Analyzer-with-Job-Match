import logging
import os
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

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ✅ RESILIENT LIFESPAN WITH RAILWAY FALLBACKS
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Backend starting up...")
    logger.info(f"Environment: SENTENCE_TRANSFORMER_MODEL={SENTENCE_TRANSFORMER_MODEL}")
    logger.info(f"Environment: SPACY_MODEL_PRIMARY={SPACY_MODEL_PRIMARY}")
    
    # ✅ Load spaCy model with fallback
    import spacy
    
    try:
        logger.info(f"Loading spaCy: {SPACY_MODEL_PRIMARY}")
        app.state.nlp = spacy.load(SPACY_MODEL_PRIMARY)
        logger.info("✅ spaCy loaded successfully")
    except OSError as e:
        logger.warning(f"⚠️  Primary model failed: {e}. Falling back to {SPACY_MODEL_SECONDARY}")
        try:
            app.state.nlp = spacy.load(SPACY_MODEL_SECONDARY)
            logger.info("✅ Fallback spaCy model loaded")
        except OSError as e2:
            logger.error(f"❌ Both spaCy models failed: {e2}")
            app.state.nlp = None

    # ⏳ Lazy load SentenceTransformer on first request (too heavy for startup on Railway)
    app.state.embedder = None
    logger.info("📦 SentenceTransformer: will lazy-load on first analysis request")
    logger.info("✅ API is ready!")

    yield

    logger.info("🛑 Backend shutting down...")


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


# ✅ HEALTH CHECK
@app.get("/")
async def root():
    return {
        "name": "ATS Resume Analyzer API",
        "version": APP_VERSION,
        "status": "running"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for Railway"""
    nlp_loaded = getattr(app.state, 'nlp', None) is not None
    return {
        "status": "ok" if nlp_loaded else "degraded",
        "nlp_loaded": nlp_loaded,
        "embedder_loaded": getattr(app.state, 'embedder', None) is not None
    }