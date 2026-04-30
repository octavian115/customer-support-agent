"""
Reliability utilities for the TaskFlow support agent.

Provides retry logic with exponential backoff for external API calls
(OpenAI, Pinecone) and graceful fallback patterns for node failures.

Usage:
    from backend.reliability import retry_with_backoff, safe_llm_call, safe_embed

Why a separate module:
    Every node makes external calls that can fail. Rather than duplicating
    try/except + retry logic in every node, shared utilities keep nodes
    focused on business logic while handling transient failures consistently.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retryable_exceptions: tuple = (Exception,),
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (total calls = max_retries + 1)
        base_delay: Initial delay in seconds (doubles each retry)
        max_delay: Cap on delay between retries
        retryable_exceptions: Tuple of exception types that trigger a retry.
                              Non-retryable exceptions propagate immediately.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )

            raise last_exception

        return wrapper
    return decorator


# ============================================================
# Safe wrappers for common external calls
# ============================================================

@retry_with_backoff(max_retries=2, base_delay=1.0)
def safe_llm_call(llm, messages: list) -> Any:
    """Call an LLM with retry logic. Handles OpenAI timeouts and rate limits."""
    return llm.invoke(messages)


@retry_with_backoff(max_retries=2, base_delay=1.0)
def safe_embed(embeddings, query: str) -> list[float]:
    """Embed a query with retry logic."""
    return embeddings.embed_query(query)


@retry_with_backoff(max_retries=2, base_delay=1.0)
def safe_pinecone_query(index, vector: list[float], top_k: int, namespace: str) -> dict:
    """Query Pinecone with retry logic."""
    return index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace,
    )
