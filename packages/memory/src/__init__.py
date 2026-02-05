"""
108 Memory Package

Provides semantic memory storage and retrieval for personalized
Vedic astrology guidance. Supports both Mem0 Cloud and local PostgreSQL.
"""

import logging

from .embeddings import (
    EmbeddingProvider,
    EmbeddingService,
    LocalEmbeddings,
    MockEmbeddings,
    OpenAIEmbeddings,
    VoyageEmbeddings,
    get_embedding_service,
    reset_embedding_service,
)
from .mem0_client import Mem0Client, MemoryCategory, MemoryImportance
from .unified_memory import (
    MemoryBackend,
    UnifiedMemory,
    UnifiedMemoryClient,
    UnifiedSearchResult,
    create_memory_client,
)

logger = logging.getLogger(__name__)

# PostgreSQL store (requires asyncpg)
try:
    from .store import Memory, MemoryStore, SearchResult

    _HAS_POSTGRES = True
except ImportError as e:
    logger.debug(f"PostgreSQL store not available: {e}")
    Memory = None
    MemoryStore = None
    SearchResult = None
    _HAS_POSTGRES = False


def has_postgres_support() -> bool:
    """Check if PostgreSQL support is available."""
    return _HAS_POSTGRES


__all__ = [
    "EmbeddingProvider",
    # Embeddings (always available)
    "EmbeddingService",
    "LocalEmbeddings",
    # Mem0 Client
    "Mem0Client",
    # PostgreSQL Store (optional)
    "Memory",
    "MemoryBackend",
    "MemoryCategory",
    "MemoryImportance",
    "MemoryStore",
    "MockEmbeddings",
    "OpenAIEmbeddings",
    "SearchResult",
    "UnifiedMemory",
    # Unified Memory (always available)
    "UnifiedMemoryClient",
    "UnifiedSearchResult",
    "VoyageEmbeddings",
    "create_memory_client",
    "get_embedding_service",
    "has_postgres_support",
    "reset_embedding_service",
]
