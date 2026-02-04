"""
108 Memory Package

Provides semantic memory storage and retrieval for personalized
Vedic astrology guidance. Supports both Mem0 Cloud and local PostgreSQL.
"""
import logging

logger = logging.getLogger(__name__)

# Always available (no external deps)
from .embeddings import (
    EmbeddingService,
    EmbeddingProvider,
    OpenAIEmbeddings,
    VoyageEmbeddings,
    LocalEmbeddings,
    MockEmbeddings,
    get_embedding_service,
    reset_embedding_service,
)

from .unified_memory import (
    UnifiedMemoryClient,
    UnifiedMemory,
    UnifiedSearchResult,
    MemoryBackend,
    create_memory_client,
)

from .mem0_client import Mem0Client, MemoryCategory, MemoryImportance

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
    # Embeddings (always available)
    "EmbeddingService",
    "EmbeddingProvider",
    "OpenAIEmbeddings",
    "VoyageEmbeddings",
    "LocalEmbeddings",
    "MockEmbeddings",
    "get_embedding_service",
    "reset_embedding_service",
    # Unified Memory (always available)
    "UnifiedMemoryClient",
    "UnifiedMemory",
    "UnifiedSearchResult",
    "MemoryBackend",
    "create_memory_client",
    # Mem0 Client
    "Mem0Client",
    "MemoryCategory",
    "MemoryImportance",
    # PostgreSQL Store (optional)
    "Memory",
    "MemoryStore",
    "SearchResult",
    "has_postgres_support",
]
