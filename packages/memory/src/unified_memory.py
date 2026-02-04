"""
108 Unified Memory Interface

Provides a single interface for memory operations that works with:
1. Mem0 Cloud (if API key available)
2. Local PostgreSQL + pgvector (fallback)

This ensures 108 works in both cloud and self-hosted deployments.
"""
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .embeddings import EmbeddingService, get_embedding_service

# Lazy import for PostgreSQL store (requires asyncpg)
MemoryStore = None
Memory = None
SearchResult = None

def _import_postgres_store():
    """Lazy import PostgreSQL store."""
    global MemoryStore, Memory, SearchResult
    if MemoryStore is None:
        try:
            from .store import MemoryStore as _MemoryStore
            from .store import Memory as _Memory
            from .store import SearchResult as _SearchResult
            MemoryStore = _MemoryStore
            Memory = _Memory
            SearchResult = _SearchResult
        except ImportError:
            pass
    return MemoryStore is not None

logger = logging.getLogger(__name__)


class MemoryBackend(str, Enum):
    """Available memory backends."""
    MEM0_CLOUD = "mem0_cloud"
    POSTGRES = "postgres"
    MOCK = "mock"


@dataclass
class UnifiedMemory:
    """Standardized memory representation."""
    id: str
    user_id: str
    content: str
    category: str
    metadata: Dict[str, Any]
    importance: float
    created_at: datetime
    source: MemoryBackend

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "category": self.category,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source.value
        }


@dataclass
class UnifiedSearchResult:
    """Standardized search result."""
    memory: UnifiedMemory
    similarity: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory": self.memory.to_dict(),
            "similarity": self.similarity
        }


class UnifiedMemoryClient:
    """
    Unified memory client for 108.

    Automatically selects backend:
    - Mem0 Cloud if MEM0_API_KEY is set
    - PostgreSQL + pgvector otherwise

    Provides consistent API regardless of backend.
    """

    def __init__(
        self,
        user_id: str,
        backend: Optional[MemoryBackend] = None,
        mem0_api_key: Optional[str] = None,
        postgres_url: Optional[str] = None,
        use_mock: bool = False
    ):
        """
        Initialize unified memory client.

        Args:
            user_id: Default user ID for operations
            backend: Force specific backend
            mem0_api_key: Mem0 API key (or use MEM0_API_KEY env)
            postgres_url: PostgreSQL URL (or use DATABASE_URL env)
            use_mock: Use mock backend for testing
        """
        self.user_id = user_id
        self._mem0_client = None
        self._postgres_store: Optional[MemoryStore] = None
        self._embedding_service: Optional[EmbeddingService] = None
        self._initialized = False

        # Determine backend
        if use_mock:
            self.backend = MemoryBackend.MOCK
        elif backend:
            self.backend = backend
        elif mem0_api_key or os.getenv("MEM0_API_KEY"):
            self.backend = MemoryBackend.MEM0_CLOUD
        else:
            self.backend = MemoryBackend.POSTGRES

        self._mem0_api_key = mem0_api_key or os.getenv("MEM0_API_KEY")
        self._postgres_url = postgres_url or os.getenv("DATABASE_URL")

        logger.info(f"UnifiedMemoryClient initialized with backend: {self.backend.value}")

    async def initialize(self) -> None:
        """Initialize the memory backend."""
        if self._initialized:
            return

        if self.backend == MemoryBackend.MEM0_CLOUD:
            await self._init_mem0()
        elif self.backend == MemoryBackend.POSTGRES:
            await self._init_postgres()
        # MOCK doesn't need initialization

        self._initialized = True
        logger.info(f"Memory backend {self.backend.value} initialized")

    async def _init_mem0(self) -> None:
        """Initialize Mem0 cloud client."""
        try:
            from mem0 import Memory
            self._mem0_client = Memory(api_key=self._mem0_api_key)
            logger.info("Mem0 cloud client initialized")
        except ImportError:
            logger.warning("mem0 package not installed, falling back to PostgreSQL")
            self.backend = MemoryBackend.POSTGRES
            await self._init_postgres()
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}, falling back to PostgreSQL")
            self.backend = MemoryBackend.POSTGRES
            await self._init_postgres()

    async def _init_postgres(self) -> None:
        """Initialize PostgreSQL store."""
        if not _import_postgres_store():
            raise ImportError(
                "PostgreSQL store requires asyncpg. "
                "Install with: uv pip install asyncpg pgvector"
            )
        self._postgres_store = MemoryStore(connection_string=self._postgres_url)
        await self._postgres_store.connect()
        self._embedding_service = get_embedding_service()
        logger.info("PostgreSQL memory store initialized")

    async def close(self) -> None:
        """Close connections."""
        if self._postgres_store:
            await self._postgres_store.close()
        self._initialized = False

    async def health_check(self) -> Dict[str, Any]:
        """Check memory system health."""
        result = {
            "backend": self.backend.value,
            "initialized": self._initialized,
            "healthy": False
        }

        if self.backend == MemoryBackend.MEM0_CLOUD:
            result["healthy"] = self._mem0_client is not None
        elif self.backend == MemoryBackend.POSTGRES:
            if self._postgres_store:
                result["healthy"] = await self._postgres_store.health_check()
        else:
            result["healthy"] = True  # Mock is always healthy

        return result

    # ===================
    # Core Memory Operations
    # ===================

    async def add(
        self,
        content: str,
        category: str = "fact",
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        user_id: Optional[str] = None
    ) -> UnifiedMemory:
        """
        Add a memory.

        Args:
            content: Memory content text
            category: Category (birth_data, yoga, prediction, preference, etc.)
            metadata: Additional metadata
            importance: Importance score (0-1)
            user_id: Override default user ID

        Returns:
            Created UnifiedMemory
        """
        await self.initialize()
        uid = user_id or self.user_id
        meta = metadata or {}

        if self.backend == MemoryBackend.MEM0_CLOUD:
            return await self._add_mem0(uid, content, category, meta, importance)
        elif self.backend == MemoryBackend.POSTGRES:
            return await self._add_postgres(uid, content, category, meta, importance)
        else:
            return await self._add_mock(uid, content, category, meta, importance)

    async def _add_mem0(
        self, user_id: str, content: str, category: str,
        metadata: Dict, importance: float
    ) -> UnifiedMemory:
        """Add memory via Mem0."""
        # Mem0 auto-extracts memories from content
        result = self._mem0_client.add(
            content,
            user_id=user_id,
            metadata={**metadata, "category": category, "importance": importance}
        )

        # Extract the created memory ID
        memory_id = result.get("id") or result.get("results", [{}])[0].get("id", "unknown")

        return UnifiedMemory(
            id=memory_id,
            user_id=user_id,
            content=content,
            category=category,
            metadata=metadata,
            importance=importance,
            created_at=datetime.now(),
            source=MemoryBackend.MEM0_CLOUD
        )

    async def _add_postgres(
        self, user_id: str, content: str, category: str,
        metadata: Dict, importance: float
    ) -> UnifiedMemory:
        """Add memory via PostgreSQL."""
        # Generate embedding
        embedding = await self._embedding_service.embed(content)

        memory = await self._postgres_store.add_memory(
            user_id=user_id,
            content=content,
            category=category,
            embedding=embedding,
            metadata=metadata,
            importance=importance
        )

        return UnifiedMemory(
            id=memory.id,
            user_id=user_id,
            content=content,
            category=category,
            metadata=metadata,
            importance=importance,
            created_at=memory.created_at,
            source=MemoryBackend.POSTGRES
        )

    async def _add_mock(
        self, user_id: str, content: str, category: str,
        metadata: Dict, importance: float
    ) -> UnifiedMemory:
        """Add memory to mock store."""
        import uuid
        return UnifiedMemory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=content,
            category=category,
            metadata=metadata,
            importance=importance,
            created_at=datetime.now(),
            source=MemoryBackend.MOCK
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_similarity: float = 0.7,
        user_id: Optional[str] = None
    ) -> List[UnifiedSearchResult]:
        """
        Search memories semantically.

        Args:
            query: Search query text
            limit: Maximum results
            category: Filter by category
            min_similarity: Minimum similarity threshold
            user_id: Override default user ID

        Returns:
            List of UnifiedSearchResult sorted by relevance
        """
        await self.initialize()
        uid = user_id or self.user_id

        if self.backend == MemoryBackend.MEM0_CLOUD:
            return await self._search_mem0(uid, query, limit, category)
        elif self.backend == MemoryBackend.POSTGRES:
            return await self._search_postgres(uid, query, limit, category, min_similarity)
        else:
            return []  # Mock returns empty

    async def _search_mem0(
        self, user_id: str, query: str, limit: int, category: Optional[str]
    ) -> List[UnifiedSearchResult]:
        """Search via Mem0."""
        results = self._mem0_client.search(
            query,
            user_id=user_id,
            limit=limit
        )

        unified_results = []
        for item in results.get("results", []):
            # Filter by category if specified
            item_category = item.get("metadata", {}).get("category", "fact")
            if category and item_category != category:
                continue

            unified_results.append(UnifiedSearchResult(
                memory=UnifiedMemory(
                    id=item.get("id", ""),
                    user_id=user_id,
                    content=item.get("memory", ""),
                    category=item_category,
                    metadata=item.get("metadata", {}),
                    importance=item.get("metadata", {}).get("importance", 0.5),
                    created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.now(),
                    source=MemoryBackend.MEM0_CLOUD
                ),
                similarity=item.get("score", 0.0)
            ))

        return unified_results

    async def _search_postgres(
        self, user_id: str, query: str, limit: int,
        category: Optional[str], min_similarity: float
    ) -> List[UnifiedSearchResult]:
        """Search via PostgreSQL."""
        # Generate query embedding
        query_embedding = await self._embedding_service.embed_for_search(query)

        results = await self._postgres_store.search_memories(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=limit,
            category=category,
            min_similarity=min_similarity
        )

        return [
            UnifiedSearchResult(
                memory=UnifiedMemory(
                    id=r.memory.id,
                    user_id=r.memory.user_id,
                    content=r.memory.content,
                    category=r.memory.category,
                    metadata=r.memory.metadata,
                    importance=r.memory.importance,
                    created_at=r.memory.created_at,
                    source=MemoryBackend.POSTGRES
                ),
                similarity=r.similarity
            )
            for r in results
        ]

    async def get_all(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[UnifiedMemory]:
        """
        Get all memories for a user.

        Args:
            category: Filter by category
            limit: Maximum results
            user_id: Override default user ID

        Returns:
            List of UnifiedMemory
        """
        await self.initialize()
        uid = user_id or self.user_id

        if self.backend == MemoryBackend.MEM0_CLOUD:
            results = self._mem0_client.get_all(user_id=uid)
            memories = []
            for item in results.get("results", [])[:limit]:
                item_category = item.get("metadata", {}).get("category", "fact")
                if category and item_category != category:
                    continue
                memories.append(UnifiedMemory(
                    id=item.get("id", ""),
                    user_id=uid,
                    content=item.get("memory", ""),
                    category=item_category,
                    metadata=item.get("metadata", {}),
                    importance=item.get("metadata", {}).get("importance", 0.5),
                    created_at=datetime.fromisoformat(item["created_at"]) if item.get("created_at") else datetime.now(),
                    source=MemoryBackend.MEM0_CLOUD
                ))
            return memories

        elif self.backend == MemoryBackend.POSTGRES:
            memories = await self._postgres_store.get_memories_by_category(
                user_id=uid,
                category=category,
                limit=limit
            ) if category else await self._postgres_store.get_all_memories(
                user_id=uid,
                limit=limit
            )
            return [
                UnifiedMemory(
                    id=m.id,
                    user_id=m.user_id,
                    content=m.content,
                    category=m.category,
                    metadata=m.metadata,
                    importance=m.importance,
                    created_at=m.created_at,
                    source=MemoryBackend.POSTGRES
                )
                for m in memories
            ]

        return []  # Mock

    async def delete(self, memory_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete a memory by ID.

        Args:
            memory_id: Memory ID to delete
            user_id: User ID (for verification)

        Returns:
            True if deleted successfully
        """
        await self.initialize()
        uid = user_id or self.user_id

        if self.backend == MemoryBackend.MEM0_CLOUD:
            self._mem0_client.delete(memory_id)
            return True
        elif self.backend == MemoryBackend.POSTGRES:
            return await self._postgres_store.delete_memory(memory_id, uid)

        return True  # Mock always succeeds

    # ===================
    # 108-Specific Memory Operations
    # ===================

    async def remember_birth_data(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        timezone: str,
        place_name: str,
        user_id: Optional[str] = None
    ) -> UnifiedMemory:
        """Store birth data as a high-importance memory."""
        content = (
            f"Birth data: {birth_datetime.strftime('%Y-%m-%d %H:%M')} "
            f"at {place_name} ({latitude}, {longitude}), timezone {timezone}"
        )
        return await self.add(
            content=content,
            category="birth_data",
            metadata={
                "birth_datetime": birth_datetime.isoformat(),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone,
                "place_name": place_name
            },
            importance=1.0,  # Critical importance
            user_id=user_id
        )

    async def remember_yoga(
        self,
        yoga_name: str,
        yoga_type: str,
        planets_involved: List[str],
        strength: float,
        interpretation: str,
        user_id: Optional[str] = None
    ) -> UnifiedMemory:
        """Store detected yoga."""
        content = f"{yoga_name} ({yoga_type}): {interpretation}"
        return await self.add(
            content=content,
            category="yoga",
            metadata={
                "yoga_name": yoga_name,
                "yoga_type": yoga_type,
                "planets_involved": planets_involved,
                "strength": strength
            },
            importance=0.8,
            user_id=user_id
        )

    async def remember_dasha(
        self,
        dasha_lord: str,
        antardasha_lord: str,
        start_date: datetime,
        end_date: datetime,
        themes: List[str],
        user_id: Optional[str] = None
    ) -> UnifiedMemory:
        """Store dasha period information."""
        content = (
            f"Current period: {dasha_lord}-{antardasha_lord} dasha "
            f"({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}). "
            f"Themes: {', '.join(themes)}"
        )
        return await self.add(
            content=content,
            category="dasha",
            metadata={
                "dasha_lord": dasha_lord,
                "antardasha_lord": antardasha_lord,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "themes": themes
            },
            importance=0.8,
            user_id=user_id
        )

    async def remember_prediction(
        self,
        prediction: str,
        category: str,
        confidence: float,
        valid_from: datetime,
        valid_until: datetime,
        user_id: Optional[str] = None
    ) -> UnifiedMemory:
        """Store a prediction for later validation."""
        content = f"Prediction ({category}): {prediction}"
        return await self.add(
            content=content,
            category="prediction",
            metadata={
                "prediction_category": category,
                "confidence": confidence,
                "valid_from": valid_from.isoformat(),
                "valid_until": valid_until.isoformat(),
                "validated": False
            },
            importance=0.6,
            user_id=user_id
        )

    async def remember_preference(
        self,
        preference_type: str,
        value: Any,
        user_id: Optional[str] = None
    ) -> UnifiedMemory:
        """Store user preference."""
        content = f"User prefers {preference_type}: {value}"
        return await self.add(
            content=content,
            category="preference",
            metadata={
                "preference_type": preference_type,
                "value": value
            },
            importance=0.7,
            user_id=user_id
        )

    async def get_context_for_query(
        self,
        query: str,
        include_categories: Optional[List[str]] = None,
        limit: int = 10,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get relevant context for a user query.

        Retrieves memories across categories that are relevant
        to the query for context-aware responses.

        Returns:
            Dictionary with categorized relevant memories
        """
        await self.initialize()
        uid = user_id or self.user_id

        context = {
            "user_id": uid,
            "query": query,
            "memories": [],
            "birth_data": None,
            "current_dasha": None,
            "active_yogas": [],
            "preferences": []
        }

        # Search for relevant memories
        results = await self.search(
            query=query,
            limit=limit,
            user_id=uid
        )

        for result in results:
            memory = result.memory
            context["memories"].append({
                "content": memory.content,
                "category": memory.category,
                "similarity": result.similarity
            })

            # Extract specific categories
            if memory.category == "birth_data" and not context["birth_data"]:
                context["birth_data"] = memory.metadata
            elif memory.category == "dasha":
                context["current_dasha"] = memory.metadata
            elif memory.category == "yoga":
                context["active_yogas"].append(memory.metadata)
            elif memory.category == "preference":
                context["preferences"].append(memory.metadata)

        return context


# Factory function
def create_memory_client(
    user_id: str,
    backend: Optional[str] = None,
    use_mock: bool = False
) -> UnifiedMemoryClient:
    """
    Create a unified memory client.

    Args:
        user_id: User ID
        backend: Force backend ('mem0', 'postgres', 'mock')
        use_mock: Use mock backend

    Returns:
        UnifiedMemoryClient instance
    """
    backend_enum = None
    if backend == "mem0":
        backend_enum = MemoryBackend.MEM0_CLOUD
    elif backend == "postgres":
        backend_enum = MemoryBackend.POSTGRES
    elif backend == "mock":
        backend_enum = MemoryBackend.MOCK

    return UnifiedMemoryClient(
        user_id=user_id,
        backend=backend_enum,
        use_mock=use_mock
    )
