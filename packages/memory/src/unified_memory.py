"""
108 Unified Memory Interface

Provides a single interface for memory operations that works with:
1. Local PostgreSQL + pgvector (primary backend)
2. Mock backend (for testing/development)

PostgreSQL + pgvector is the sole production backend.
Mem0 Cloud support has been removed in favor of the simpler architecture.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

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
            from .store import Memory as _Memory
            from .store import MemoryStore as _MemoryStore
            from .store import SearchResult as _SearchResult

            MemoryStore = _MemoryStore
            Memory = _Memory
            SearchResult = _SearchResult
        except ImportError:
            pass
    return MemoryStore is not None


logger = logging.getLogger(__name__)


class MemoryBackend(StrEnum):
    """Available memory backends."""

    POSTGRES = "postgres"
    MOCK = "mock"


@dataclass
class UnifiedMemory:
    """Standardized memory representation."""

    id: str
    user_id: str
    content: str
    category: str
    metadata: dict[str, Any]
    importance: float
    created_at: datetime
    source: MemoryBackend

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "category": self.category,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "source": self.source.value,
        }


@dataclass
class UnifiedSearchResult:
    """Standardized search result."""

    memory: UnifiedMemory
    similarity: float

    def to_dict(self) -> dict[str, Any]:
        return {"memory": self.memory.to_dict(), "similarity": self.similarity}


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
        backend: MemoryBackend | None = None,
        postgres_url: str | None = None,
        use_mock: bool = False,
    ):
        """
        Initialize unified memory client.

        Args:
            user_id: Default user ID for operations
            backend: Force specific backend (POSTGRES or MOCK)
            postgres_url: PostgreSQL URL (or use DATABASE_URL env)
            use_mock: Use mock backend for testing
        """
        self.user_id = user_id
        self._postgres_store: MemoryStore | None = None
        self._embedding_service: EmbeddingService | None = None
        self._initialized = False

        # Determine backend
        if use_mock:
            self.backend = MemoryBackend.MOCK
        elif backend:
            self.backend = backend
        else:
            self.backend = MemoryBackend.POSTGRES

        self._postgres_url = postgres_url or os.getenv("DATABASE_URL")

        logger.info(f"UnifiedMemoryClient initialized with backend: {self.backend.value}")

    async def initialize(self) -> None:
        """Initialize the memory backend."""
        if self._initialized:
            return

        if self.backend == MemoryBackend.POSTGRES:
            await self._init_postgres()
        # MOCK doesn't need initialization

        self._initialized = True
        logger.info(f"Memory backend {self.backend.value} initialized")

    async def _init_postgres(self) -> None:
        """Initialize PostgreSQL store."""
        if not _import_postgres_store():
            raise ImportError(
                "PostgreSQL store requires asyncpg. Install with: uv pip install asyncpg pgvector"
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

    async def health_check(self) -> dict[str, Any]:
        """Check memory system health."""
        result = {"backend": self.backend.value, "initialized": self._initialized, "healthy": False}

        if self.backend == MemoryBackend.POSTGRES:
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
        metadata: dict[str, Any] | None = None,
        importance: float = 0.5,
        user_id: str | None = None,
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

        if self.backend == MemoryBackend.POSTGRES:
            return await self._add_postgres(uid, content, category, meta, importance)
        else:
            return await self._add_mock(uid, content, category, meta, importance)

    async def _add_postgres(
        self, user_id: str, content: str, category: str, metadata: dict, importance: float
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
            importance=importance,
        )

        return UnifiedMemory(
            id=memory.id,
            user_id=user_id,
            content=content,
            category=category,
            metadata=metadata,
            importance=importance,
            created_at=memory.created_at,
            source=MemoryBackend.POSTGRES,
        )

    async def _add_mock(
        self, user_id: str, content: str, category: str, metadata: dict, importance: float
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
            source=MemoryBackend.MOCK,
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        category: str | None = None,
        min_similarity: float = 0.7,
        user_id: str | None = None,
    ) -> list[UnifiedSearchResult]:
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

        if self.backend == MemoryBackend.POSTGRES:
            return await self._search_postgres(uid, query, limit, category, min_similarity)
        else:
            return []  # Mock returns empty

    async def _search_postgres(
        self, user_id: str, query: str, limit: int, category: str | None, min_similarity: float
    ) -> list[UnifiedSearchResult]:
        """Search via PostgreSQL."""
        # Generate query embedding
        query_embedding = await self._embedding_service.embed_for_search(query)

        results = await self._postgres_store.search_memories(
            user_id=user_id,
            query_embedding=query_embedding,
            limit=limit,
            category=category,
            min_similarity=min_similarity,
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
                    source=MemoryBackend.POSTGRES,
                ),
                similarity=r.similarity,
            )
            for r in results
        ]

    async def get_all(
        self, category: str | None = None, limit: int = 100, user_id: str | None = None
    ) -> list[UnifiedMemory]:
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

        if self.backend == MemoryBackend.POSTGRES:
            memories = (
                await self._postgres_store.get_memories_by_category(
                    user_id=uid, category=category, limit=limit
                )
                if category
                else await self._postgres_store.get_all_memories(user_id=uid, limit=limit)
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
                    source=MemoryBackend.POSTGRES,
                )
                for m in memories
            ]

        return []  # Mock

    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.

        Args:
            memory_id: Memory ID to delete

        Returns:
            True if deleted successfully
        """
        await self.initialize()

        if self.backend == MemoryBackend.POSTGRES:
            return await self._postgres_store.delete_memory(memory_id)

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
        user_id: str | None = None,
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
                "place_name": place_name,
            },
            importance=1.0,  # Critical importance
            user_id=user_id,
        )

    async def remember_yoga(
        self,
        yoga_name: str,
        yoga_type: str,
        planets_involved: list[str],
        strength: float,
        interpretation: str,
        user_id: str | None = None,
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
                "strength": strength,
            },
            importance=0.8,
            user_id=user_id,
        )

    async def remember_dasha(
        self,
        dasha_lord: str,
        antardasha_lord: str,
        start_date: datetime,
        end_date: datetime,
        themes: list[str],
        user_id: str | None = None,
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
                "themes": themes,
            },
            importance=0.8,
            user_id=user_id,
        )

    async def remember_prediction(
        self,
        prediction: str,
        category: str,
        confidence: float,
        valid_from: datetime,
        valid_until: datetime,
        user_id: str | None = None,
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
                "validated": False,
            },
            importance=0.6,
            user_id=user_id,
        )

    async def remember_preference(
        self, preference_type: str, value: Any, user_id: str | None = None
    ) -> UnifiedMemory:
        """Store user preference."""
        content = f"User prefers {preference_type}: {value}"
        return await self.add(
            content=content,
            category="preference",
            metadata={"preference_type": preference_type, "value": value},
            importance=0.7,
            user_id=user_id,
        )

    async def remember_event_correlation(
        self,
        event_date: str,
        event_type: str,
        event_description: str,
        correlation_score: int,
        dasha_at_event: dict[str, Any] | None = None,
        explanation: str = "",
        user_id: str | None = None,
    ) -> UnifiedMemory:
        """Store a life event correlation result.

        Args:
            event_date: ISO date of the event
            event_type: Type (career, marriage, health, money, etc.)
            event_description: User's description
            correlation_score: Match score (0-100)
            dasha_at_event: Dasha active at event time
            explanation: Correlation explanation
            user_id: Override default user ID

        Returns:
            Created UnifiedMemory
        """
        content = (
            f"Life event ({event_type}) on {event_date}: {event_description}. "
            f"Correlation: {correlation_score}/100. {explanation}"
        )
        return await self.add(
            content=content,
            category="event_correlation",
            metadata={
                "event_date": event_date,
                "event_type": event_type,
                "event_description": event_description,
                "correlation_score": correlation_score,
                "dasha_at_event": dasha_at_event or {},
                "explanation": explanation,
            },
            importance=0.8,
            user_id=user_id,
        )

    async def remember_remedy(
        self,
        remedy_summary: str,
        dasha_lord: str,
        active_doshas: list[str],
        user_id: str | None = None,
    ) -> UnifiedMemory:
        """Store remedy recommendations.

        Args:
            remedy_summary: Summary of recommended remedies
            dasha_lord: Current mahadasha lord
            active_doshas: Active dosha names
            user_id: Override default user ID

        Returns:
            Created UnifiedMemory
        """
        dosha_str = ", ".join(active_doshas) if active_doshas else "none"
        content = f"Remedies for {dasha_lord} dasha, doshas: {dosha_str}. {remedy_summary}"
        return await self.add(
            content=content,
            category="remedy",
            metadata={
                "dasha_lord": dasha_lord,
                "active_doshas": active_doshas,
                "remedy_summary": remedy_summary,
            },
            importance=0.6,
            user_id=user_id,
        )

    async def remember_transit_trigger(
        self,
        trigger_date: str,
        trigger_type: str,
        significance: str,
        effect: str,
        user_id: str | None = None,
    ) -> UnifiedMemory:
        """Store an upcoming transit trigger as a memory.

        Args:
            trigger_date: ISO date of the trigger
            trigger_type: Type (ingress, conjunction, aspect, retrograde, dasha_change)
            significance: Significance level (high, medium, low)
            effect: Expected effect description
            user_id: Override default user ID

        Returns:
            Created UnifiedMemory
        """
        content = (
            f"Transit trigger on {trigger_date}: {trigger_type} "
            f"(significance: {significance}). {effect}"
        )
        return await self.add(
            content=content,
            category="transit_trigger",
            metadata={
                "trigger_date": trigger_date,
                "trigger_type": trigger_type,
                "significance": significance,
                "effect": effect,
            },
            importance=0.7,
            user_id=user_id,
        )

    async def remember_state_vector(
        self,
        query_date: str,
        composite_score: float,
        mental_state: str,
        top_factors: list[str] | None = None,
        top_areas: list[str] | None = None,
        confluence: float = 0.0,
        user_id: str | None = None,
    ) -> Any:
        """Store a state vector snapshot in memory.

        Args:
            query_date: ISO date string for this snapshot
            composite_score: Overall composite score (0-10)
            mental_state: Mental state label (e.g. "positive", "challenging")
            top_factors: Top contributing factors
            top_areas: Top scoring life areas
            confluence: Confluence measure
            user_id: Optional user ID override
        """
        factors_str = ", ".join(top_factors[:3]) if top_factors else "none"
        areas_str = ", ".join(top_areas[:3]) if top_areas else "none"
        content = (
            f"State on {query_date}: composite={composite_score:.1f}/10 "
            f"({mental_state}). Top factors: {factors_str}. "
            f"Top areas: {areas_str}."
        )
        return await self.add(
            content=content,
            category="state_vector",
            metadata={
                "query_date": query_date,
                "composite_score": composite_score,
                "mental_state": mental_state,
                "top_factors": top_factors or [],
                "top_areas": top_areas or [],
                "confluence": confluence,
            },
            importance=0.5,
            user_id=user_id,
        )

    async def get_context_for_query(
        self,
        query: str,
        include_categories: list[str] | None = None,  # noqa: ARG002
        limit: int = 10,
        user_id: str | None = None,
    ) -> dict[str, Any]:
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
            "preferences": [],
            "event_correlations": [],
            "remedies": [],
            "transit_triggers": [],
            "state_vectors": [],
        }

        # Search for relevant memories
        results = await self.search(query=query, limit=limit, user_id=uid)

        for result in results:
            memory = result.memory
            context["memories"].append(
                {
                    "content": memory.content,
                    "category": memory.category,
                    "similarity": result.similarity,
                }
            )

            # Extract specific categories
            if memory.category == "birth_data" and not context["birth_data"]:
                context["birth_data"] = memory.metadata
            elif memory.category == "dasha":
                context["current_dasha"] = memory.metadata
            elif memory.category == "yoga":
                context["active_yogas"].append(memory.metadata)
            elif memory.category == "preference":
                context["preferences"].append(memory.metadata)
            elif memory.category == "event_correlation":
                context["event_correlations"].append(memory.metadata)
            elif memory.category == "remedy":
                context["remedies"].append(memory.metadata)
            elif memory.category == "transit_trigger":
                context["transit_triggers"].append(memory.metadata)
            elif memory.category == "state_vector":
                context["state_vectors"].append(memory.metadata)

        return context


# Factory function
def create_memory_client(
    user_id: str, backend: str | None = None, use_mock: bool = False
) -> UnifiedMemoryClient:
    """
    Create a unified memory client.

    Args:
        user_id: User ID
        backend: Force backend ('postgres', 'mock')
        use_mock: Use mock backend

    Returns:
        UnifiedMemoryClient instance
    """
    backend_enum = None
    if backend == "postgres":
        backend_enum = MemoryBackend.POSTGRES
    elif backend == "mock":
        backend_enum = MemoryBackend.MOCK

    return UnifiedMemoryClient(user_id=user_id, backend=backend_enum, use_mock=use_mock)
