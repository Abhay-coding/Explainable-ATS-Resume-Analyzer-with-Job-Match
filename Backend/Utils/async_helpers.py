"""Async utilities for performance optimization."""
import asyncio
import logging
import functools
from typing import Callable, Any, TypeVar, Coroutine
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("ats_resume_scorer")

T = TypeVar("T")

# Executor for running blocking operations in parallel
_executor = ThreadPoolExecutor(max_workers=4)


async def run_in_executor(func: Callable[..., T], *args, **kwargs) -> T:
    """Run a blocking function in a thread pool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, functools.partial(func, *args, **kwargs))


def run_async_safe(coro: Coroutine) -> Any:
    """Run a coroutine safely in sync context (returns result or raises exception)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're already in an async context, return the coroutine as-is
            return coro
        else:
            return asyncio.run(coro)
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(coro)


async def timeout_wrapper(
    coro: Coroutine, timeout_seconds: float, task_name: str = "task"
) -> Any:
    """Wrap a coroutine with a timeout."""
    try:
        result = await asyncio.wait_for(coro, timeout=timeout_seconds)
        logger.info(f"✓ {task_name} completed within {timeout_seconds}s")
        return result
    except asyncio.TimeoutError:
        logger.error(f"✗ {task_name} exceeded {timeout_seconds}s timeout")
        raise TimeoutError(f"{task_name} exceeded {timeout_seconds}s timeout")


async def parallel_groq_parsing(
    resume_text: str,
    job_description: str = None,
    timeout_seconds: float = 90,
):
    """
    Parse resume and job description in parallel using asyncio.
    Much faster than sequential parsing (saves ~30-40 seconds).
    """
    from backend.services.groq_parser import parse_resume, parse_job_description

    async def parse_resume_async():
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, parse_resume, resume_text)

    async def parse_jd_async():
        if not job_description or not job_description.strip():
            return None
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, parse_job_description, job_description.strip())

    try:
        # Run both parsing tasks in parallel
        tasks = [
            timeout_wrapper(parse_resume_async(), timeout_seconds / 2, "Resume parsing"),
        ]
        if job_description and job_description.strip():
            tasks.append(
                timeout_wrapper(parse_jd_async(), timeout_seconds / 2, "JD parsing")
            )

        results = await asyncio.gather(*tasks, return_exceptions=False)
        parsed_resume = results[0]
        parsed_jd = results[1] if len(results) > 1 else None
        return parsed_resume, parsed_jd

    except Exception as exc:
        logger.error(f"Parallel parsing failed: {exc}")
        raise


def batch_encode_embeddings(texts: list, embedder, batch_size: int = 32) -> list:
    """
    Batch encode multiple texts for efficiency.
    Much faster than encoding one-by-one (can save 50%+ time).
    """
    if not texts:
        return []

    # Filter out empty strings
    valid_texts = [t for t in texts if t and isinstance(t, str)]
    if not valid_texts:
        return []

    try:
        # SentenceTransformer.encode with batch_size handles batching internally
        embeddings = embedder.encode(valid_texts, batch_size=batch_size, show_progress_bar=False)
        logger.info(f"✓ Batch encoded {len(valid_texts)} texts in {len(valid_texts)//batch_size + 1} batches")
        return embeddings
    except Exception as exc:
        logger.error(f"Batch encoding failed: {exc}")
        raise


class EmbeddingCache:
    """Simple in-memory cache for embeddings to avoid re-encoding."""

    def __init__(self, max_size: int = 500):
        self.cache = {}
        self.max_size = max_size

    def get(self, text: str):
        """Get cached embedding."""
        return self.cache.get(text)

    def set(self, text: str, embedding):
        """Cache an embedding."""
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[text] = embedding

    def get_or_compute(self, text: str, embedder, cache_key: str = None):
        """Get from cache or compute new embedding."""
        key = cache_key or text
        cached = self.get(key)
        if cached is not None:
            logger.debug(f"✓ Cache hit for '{text[:20]}...'")
            return cached

        embedding = embedder.encode(text, convert_to_tensor=False)
        self.set(key, embedding)
        logger.debug(f"✓ Cached new embedding for '{text[:20]}...'")
        return embedding

    def clear(self):
        """Clear the cache."""
        self.cache.clear()

    def size(self):
        """Return cache size."""
        return len(self.cache)
