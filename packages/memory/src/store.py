"""
108 Memory Store

PostgreSQL + pgvector storage for semantic memories, user profiles, and predictions.

This module provides async operations for:
- Semantic memory storage and retrieval
- User profile management
- Birth chart data persistence
- Yoga/Dosha pattern detection
- Prediction tracking and validation
- Conversation history
- User preferences
- Dasha timeline caching
"""
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional

import asyncpg
from pgvector.asyncpg import register_vector

logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """A semantic memory unit."""
    id: Optional[str] = None
    user_id: str = ""
    content: str = ""
    category: str = "fact"  # fact, preference, event, prediction, feedback
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert memory to dictionary."""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class SearchResult:
    """Result from semantic search."""
    memory: Memory
    similarity: float

    def to_dict(self) -> dict[str, Any]:
        """Convert search result to dictionary."""
        return {
            "memory": self.memory.to_dict(),
            "similarity": self.similarity
        }


class MemoryStore:
    """
    PostgreSQL + pgvector memory store for 108 Vedic Astrology.

    Handles:
    - Storing memories with vector embeddings
    - Semantic similarity search
    - User profile management
    - Birth chart data persistence
    - Yoga/Dosha pattern detection
    - Prediction tracking and validation
    - Conversation history
    - User preferences
    - Dasha timeline caching

    All operations are async and designed for production use with asyncpg.
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize memory store.

        Args:
            connection_string: PostgreSQL connection string
                             e.g., "postgresql://user:pass@localhost/onezeroeight"
        """
        self.connection_string = (
            connection_string or
            os.environ.get("DATABASE_URL") or
            "postgresql://postgres:postgres@localhost:5432/one_zero_eight"
        )
        self.pool: Optional[asyncpg.Pool] = None
        self._embedding_dimension = 1536  # OpenAI ada-002 dimension
        self._initialized = False
        logger.info(f"MemoryStore initialized")

    async def connect(self) -> None:
        """Establish database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
            # Register pgvector type with the pool
            async with self.pool.acquire() as conn:
                await register_vector(conn)
            self._initialized = True
            logger.info("MemoryStore connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MemoryStore: {e}")
            raise

    async def close(self) -> None:
        """Close database connection pool."""
        if self.pool:
            try:
                await self.pool.close()
                self._initialized = False
                logger.info("MemoryStore connection closed")
            except Exception as e:
                logger.error(f"Error closing MemoryStore: {e}")
                raise

    async def health_check(self) -> bool:
        """Check if memory store is connected and healthy."""
        if not self._initialized or not self.pool:
            return False

        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"MemoryStore health check failed: {e}")
            return False

    # ===================
    # Memory Operations
    # ===================

    async def add_memory(
        self,
        user_id: str,
        content: str,
        category: str = "fact",
        embedding: Optional[list[float]] = None,
        metadata: Optional[dict[str, Any]] = None,
        importance: float = 0.5
    ) -> Memory:
        """
        Add a new memory to the store.

        Args:
            user_id: User's UUID
            content: Memory content text
            category: Memory category (fact|preference|event|prediction|feedback)
            embedding: Vector embedding (1536 dimensions for ada-002)
            metadata: Additional metadata dictionary
            importance: Importance score (0-1)

        Returns:
            Created Memory object with assigned ID
        """
        if not user_id or not content:
            raise ValueError("user_id and content are required")

        if importance < 0 or importance > 1:
            raise ValueError("importance must be between 0 and 1")

        memory_id = str(uuid.uuid4())
        now = datetime.now()

        async with self.pool.acquire() as conn:
            await register_vector(conn)
            await conn.execute(
                """
                INSERT INTO memories (
                    id, user_id, content, category, embedding,
                    metadata, importance, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                uuid.UUID(memory_id),
                uuid.UUID(user_id),
                content,
                category,
                embedding,
                json.dumps(metadata or {}),
                importance,
                now,
                now
            )

        memory = Memory(
            id=memory_id,
            user_id=user_id,
            content=content,
            category=category,
            embedding=embedding,
            metadata=metadata or {},
            importance=importance,
            created_at=now,
            updated_at=now
        )

        logger.debug(f"Added memory {memory_id} for user {user_id}")
        return memory

    async def search_memories(
        self,
        user_id: str,
        query_embedding: list[float],
        limit: int = 10,
        category: Optional[str] = None,
        min_similarity: float = 0.7
    ) -> list[SearchResult]:
        """
        Semantic search for relevant memories using vector similarity.

        Uses cosine distance (<=> operator in pgvector).
        Similarity score = 1 - distance

        Args:
            user_id: User's UUID to filter memories
            query_embedding: Query vector embedding (must match dimension)
            limit: Maximum results to return
            category: Optional category filter
            min_similarity: Minimum cosine similarity threshold (0-1)

        Returns:
            List of SearchResult objects sorted by similarity (highest first)
        """
        if not query_embedding:
            raise ValueError("query_embedding is required")

        if len(query_embedding) != self._embedding_dimension:
            raise ValueError(
                f"Embedding dimension must be {self._embedding_dimension}, "
                f"got {len(query_embedding)}"
            )

        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")

        if min_similarity < 0 or min_similarity > 1:
            raise ValueError("min_similarity must be between 0 and 1")

        async with self.pool.acquire() as conn:
            await register_vector(conn)

            if category:
                rows = await conn.fetch(
                    """
                    SELECT
                        id, user_id, content, category, embedding,
                        metadata, importance, created_at, updated_at,
                        1 - (embedding <=> $2::vector) as similarity
                    FROM memories
                    WHERE user_id = $1
                      AND category = $3
                      AND embedding IS NOT NULL
                      AND 1 - (embedding <=> $2::vector) >= $4
                    ORDER BY embedding <=> $2::vector
                    LIMIT $5
                    """,
                    uuid.UUID(user_id),
                    query_embedding,
                    category,
                    min_similarity,
                    limit
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT
                        id, user_id, content, category, embedding,
                        metadata, importance, created_at, updated_at,
                        1 - (embedding <=> $2::vector) as similarity
                    FROM memories
                    WHERE user_id = $1
                      AND embedding IS NOT NULL
                      AND 1 - (embedding <=> $2::vector) >= $3
                    ORDER BY embedding <=> $2::vector
                    LIMIT $4
                    """,
                    uuid.UUID(user_id),
                    query_embedding,
                    min_similarity,
                    limit
                )

        results = []
        for row in rows:
            memory = Memory(
                id=str(row['id']),
                user_id=str(row['user_id']),
                content=row['content'],
                category=row['category'],
                embedding=list(row['embedding']) if row['embedding'] else None,
                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                importance=float(row['importance']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            results.append(SearchResult(memory=memory, similarity=float(row['similarity'])))

        logger.debug(
            f"Found {len(results)} memories for user {user_id} "
            f"with {min_similarity} threshold"
        )
        return results

    async def get_memories_by_category(
        self,
        user_id: str,
        category: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[Memory]:
        """
        Get all memories of a specific category with pagination.

        Args:
            user_id: User's UUID
            category: Memory category filter
            limit: Maximum results (default 50)
            offset: Pagination offset (default 0)

        Returns:
            List of Memory objects ordered by recency
        """
        if category not in ["fact", "preference", "event", "prediction", "feedback"]:
            raise ValueError(f"Invalid category: {category}")

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, content, category, embedding,
                       metadata, importance, created_at, updated_at
                FROM memories
                WHERE user_id = $1 AND category = $2
                ORDER BY updated_at DESC
                LIMIT $3 OFFSET $4
                """,
                uuid.UUID(user_id),
                category,
                limit,
                offset
            )

        memories = []
        for row in rows:
            memories.append(Memory(
                id=str(row['id']),
                user_id=str(row['user_id']),
                content=row['content'],
                category=row['category'],
                embedding=list(row['embedding']) if row['embedding'] else None,
                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                importance=float(row['importance']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))

        logger.debug(f"Got {len(memories)} {category} memories for user {user_id}")
        return memories

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, content, category, embedding,
                       metadata, importance, created_at, updated_at
                FROM memories WHERE id = $1
                """,
                uuid.UUID(memory_id)
            )

        if not row:
            return None

        return Memory(
            id=str(row['id']),
            user_id=str(row['user_id']),
            content=row['content'],
            category=row['category'],
            embedding=list(row['embedding']) if row['embedding'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            importance=float(row['importance']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        embedding: Optional[list[float]] = None,
        metadata: Optional[dict[str, Any]] = None,
        importance: Optional[float] = None
    ) -> Optional[Memory]:
        """
        Update an existing memory.

        Args:
            memory_id: Memory's UUID
            content: Updated content (optional)
            embedding: Updated embedding vector (optional)
            metadata: Updated metadata (optional, merges with existing)
            importance: Updated importance score (optional)

        Returns:
            Updated Memory object or None if not found
        """
        if importance is not None and (importance < 0 or importance > 1):
            raise ValueError("importance must be between 0 and 1")

        async with self.pool.acquire() as conn:
            await register_vector(conn)
            row = await conn.fetchrow(
                """
                UPDATE memories
                SET
                    content = COALESCE($2, content),
                    embedding = COALESCE($3, embedding),
                    metadata = CASE WHEN $4::jsonb IS NOT NULL
                               THEN metadata || $4::jsonb
                               ELSE metadata END,
                    importance = COALESCE($5, importance),
                    updated_at = NOW()
                WHERE id = $1
                RETURNING id, user_id, content, category, embedding,
                          metadata, importance, created_at, updated_at
                """,
                uuid.UUID(memory_id),
                content,
                embedding,
                json.dumps(metadata) if metadata else None,
                importance
            )

        if not row:
            return None

        logger.debug(f"Updated memory {memory_id}")
        return Memory(
            id=str(row['id']),
            user_id=str(row['user_id']),
            content=row['content'],
            category=row['category'],
            embedding=list(row['embedding']) if row['embedding'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            importance=float(row['importance']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory's UUID

        Returns:
            True if deleted, False if not found
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM memories WHERE id = $1",
                uuid.UUID(memory_id)
            )

        deleted = result == "DELETE 1"
        if deleted:
            logger.debug(f"Deleted memory {memory_id}")
        return deleted

    async def delete_memories_by_category(
        self,
        user_id: str,
        category: str
    ) -> int:
        """
        Delete all memories of a category for a user.

        Args:
            user_id: User's UUID
            category: Category to delete

        Returns:
            Number of deleted memories
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM memories WHERE user_id = $1 AND category = $2",
                uuid.UUID(user_id),
                category
            )

        # Parse "DELETE N" to get count
        count = int(result.split()[-1]) if result else 0
        logger.debug(f"Deleted {count} {category} memories for user {user_id}")
        return count

    # ===================
    # User Operations
    # ===================

    async def create_user(
        self,
        email: str,
        name: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a new user.

        Args:
            email: User's email address (unique)
            name: User's display name (optional)

        Returns:
            Dictionary with user ID and details
        """
        if not email or "@" not in email:
            raise ValueError("Valid email is required")

        user_id = str(uuid.uuid4())
        now = datetime.now()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (id, email, name, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (email) DO NOTHING
                """,
                uuid.UUID(user_id),
                email,
                name,
                now,
                now
            )

        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

        logger.info(f"Created user {user_id} with email {email}")
        return user

    async def get_user(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: User's UUID

        Returns:
            User dictionary or None if not found
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                uuid.UUID(user_id)
            )

        if not row:
            return None

        return {
            "id": str(row['id']),
            "email": row['email'],
            "name": row['name'],
            "created_at": row['created_at'].isoformat() if row['created_at'] else None,
            "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
        }

    async def get_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """
        Get user by email address.

        Args:
            email: User's email

        Returns:
            User dictionary or None if not found
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                email
            )

        if not row:
            return None

        return {
            "id": str(row['id']),
            "email": row['email'],
            "name": row['name'],
            "created_at": row['created_at'].isoformat() if row['created_at'] else None,
            "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
        }

    async def update_user(
        self,
        user_id: str,
        name: Optional[str] = None
    ) -> Optional[dict[str, Any]]:
        """Update user information."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE users
                SET name = COALESCE($2, name), updated_at = NOW()
                WHERE id = $1
                RETURNING *
                """,
                uuid.UUID(user_id),
                name
            )

        if not row:
            return None

        return {
            "id": str(row['id']),
            "email": row['email'],
            "name": row['name'],
            "created_at": row['created_at'].isoformat() if row['created_at'] else None,
            "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
        }

    # ===================
    # Birth Chart Operations
    # ===================

    async def save_birth_chart(
        self,
        user_id: str,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        timezone: str,
        place_name: Optional[str] = None,
        chart_data: Optional[dict[str, Any]] = None,
        ayanamsa: str = "lahiri"
    ) -> dict[str, Any]:
        """
        Save or update user's birth chart.

        Args:
            user_id: User's UUID
            birth_datetime: Exact birth date and time
            latitude: Birth location latitude
            longitude: Birth location longitude
            timezone: Birth timezone (e.g., "Asia/Kolkata")
            place_name: Birth place name (optional)
            chart_data: Dictionary of calculated chart data (planets, houses, etc.)
            ayanamsa: Ayanamsa used (default: lahiri)

        Returns:
            Dictionary with birth chart details
        """
        now = datetime.now()

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO birth_charts (
                    user_id, birth_datetime, latitude, longitude, timezone,
                    place_name, chart_data, ayanamsa, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (user_id) DO UPDATE SET
                    birth_datetime = $2,
                    latitude = $3,
                    longitude = $4,
                    timezone = $5,
                    place_name = $6,
                    chart_data = $7,
                    ayanamsa = $8
                RETURNING *
                """,
                uuid.UUID(user_id),
                birth_datetime,
                latitude,
                longitude,
                timezone,
                place_name,
                json.dumps(chart_data) if chart_data else None,
                ayanamsa,
                now
            )

        birth_chart = {
            "id": str(row['id']),
            "user_id": str(row['user_id']),
            "birth_datetime": row['birth_datetime'].isoformat(),
            "latitude": float(row['latitude']),
            "longitude": float(row['longitude']),
            "timezone": row['timezone'],
            "place_name": row['place_name'],
            "chart_data": json.loads(row['chart_data']) if row['chart_data'] else {},
            "ayanamsa": row['ayanamsa'],
            "created_at": row['created_at'].isoformat()
        }

        logger.info(f"Saved birth chart for user {user_id}")
        return birth_chart

    async def get_birth_chart(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Get user's birth chart.

        Args:
            user_id: User's UUID

        Returns:
            Birth chart dictionary or None if not found
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM birth_charts WHERE user_id = $1",
                uuid.UUID(user_id)
            )

        if not row:
            return None

        return {
            "id": str(row['id']),
            "user_id": str(row['user_id']),
            "birth_datetime": row['birth_datetime'].isoformat(),
            "latitude": float(row['latitude']),
            "longitude": float(row['longitude']),
            "timezone": row['timezone'],
            "place_name": row['place_name'],
            "chart_data": json.loads(row['chart_data']) if row['chart_data'] else {},
            "ayanamsa": row['ayanamsa'],
            "created_at": row['created_at'].isoformat()
        }

    # ===================
    # Pattern Operations
    # ===================

    async def save_detected_patterns(
        self,
        user_id: str,
        patterns: list[dict[str, Any]],
        pattern_type: str
    ) -> int:
        """
        Save detected yogas or doshas.

        Args:
            user_id: User's UUID
            patterns: List of pattern dictionaries
            pattern_type: Type of pattern ('yoga' or 'dosha')

        Returns:
            Number of patterns saved
        """
        if pattern_type not in ["yoga", "dosha"]:
            raise ValueError("pattern_type must be 'yoga' or 'dosha'")

        if not patterns:
            return 0

        count = 0
        async with self.pool.acquire() as conn:
            for pattern in patterns:
                await conn.execute(
                    """
                    INSERT INTO detected_patterns (
                        user_id, pattern_type, pattern_id, pattern_name,
                        category, strength, severity, involved_planets, details
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT DO NOTHING
                    """,
                    uuid.UUID(user_id),
                    pattern_type,
                    pattern.get('id', pattern.get('name', '')),
                    pattern.get('name', ''),
                    pattern.get('category'),
                    pattern.get('strength'),
                    pattern.get('severity'),
                    pattern.get('involved_planets'),
                    json.dumps(pattern)
                )
                count += 1

        logger.info(f"Saved {count} {pattern_type} patterns for user {user_id}")
        return count

    async def get_user_patterns(
        self,
        user_id: str,
        pattern_type: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Get user's detected patterns.

        Args:
            user_id: User's UUID
            pattern_type: Optional filter ('yoga' or 'dosha')

        Returns:
            List of pattern dictionaries
        """
        async with self.pool.acquire() as conn:
            if pattern_type:
                rows = await conn.fetch(
                    """
                    SELECT * FROM detected_patterns
                    WHERE user_id = $1 AND pattern_type = $2
                    ORDER BY detected_at DESC
                    """,
                    uuid.UUID(user_id),
                    pattern_type
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM detected_patterns
                    WHERE user_id = $1
                    ORDER BY detected_at DESC
                    """,
                    uuid.UUID(user_id)
                )

        patterns = []
        for row in rows:
            patterns.append({
                "id": str(row['id']),
                "user_id": str(row['user_id']),
                "pattern_type": row['pattern_type'],
                "pattern_id": row['pattern_id'],
                "pattern_name": row['pattern_name'],
                "category": row['category'],
                "strength": float(row['strength']) if row['strength'] else None,
                "severity": row['severity'],
                "involved_planets": row['involved_planets'],
                "details": json.loads(row['details']) if row['details'] else {},
                "detected_at": row['detected_at'].isoformat()
            })

        return patterns

    async def delete_pattern(
        self,
        user_id: str,
        pattern_name: str
    ) -> bool:
        """Delete a detected pattern."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM detected_patterns
                WHERE user_id = $1 AND pattern_name = $2
                """,
                uuid.UUID(user_id),
                pattern_name
            )

        return "DELETE" in result and int(result.split()[-1]) > 0

    # ===================
    # Prediction Operations
    # ===================

    async def save_prediction(
        self,
        user_id: str,
        prediction_text: str,
        category: str,
        timeframe_start: datetime,
        timeframe_end: datetime,
        confidence: float,
        factors: Optional[dict[str, Any]] = None,
        dasha_period: Optional[dict[str, Any]] = None,
        transit_positions: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Save a prediction for later validation.

        Args:
            user_id: User's UUID
            prediction_text: The prediction description
            category: Prediction category (career, health, relationships, etc.)
            timeframe_start: Prediction start date
            timeframe_end: Prediction end date
            confidence: Confidence level (0-1)
            factors: Dictionary of astrological factors considered
            dasha_period: Dasha period data when prediction made
            transit_positions: Transit positions when prediction made

        Returns:
            Dictionary with prediction details and ID
        """
        if confidence < 0 or confidence > 1:
            raise ValueError("confidence must be between 0 and 1")

        prediction_id = str(uuid.uuid4())
        now = datetime.now()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO predictions (
                    id, user_id, prediction_text, category, confidence,
                    timeframe_start, timeframe_end, factors, dasha_period,
                    transit_positions, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                uuid.UUID(prediction_id),
                uuid.UUID(user_id),
                prediction_text,
                category,
                confidence,
                timeframe_start.date(),
                timeframe_end.date(),
                json.dumps(factors) if factors else None,
                json.dumps(dasha_period) if dasha_period else None,
                json.dumps(transit_positions) if transit_positions else None,
                now
            )

        prediction = {
            "id": prediction_id,
            "user_id": user_id,
            "prediction_text": prediction_text,
            "category": category,
            "confidence": confidence,
            "timeframe_start": timeframe_start.isoformat(),
            "timeframe_end": timeframe_end.isoformat(),
            "factors": factors or {},
            "dasha_period": dasha_period or {},
            "transit_positions": transit_positions or {},
            "created_at": now.isoformat(),
            "status": "pending"
        }

        logger.info(f"Saved prediction {prediction_id} for user {user_id}")
        return prediction

    async def validate_prediction(
        self,
        prediction_id: str,
        outcome: str,
        accuracy: float
    ) -> Optional[dict[str, Any]]:
        """
        Record outcome and accuracy for a prediction.

        Args:
            prediction_id: Prediction's UUID
            outcome: Description of what actually happened
            accuracy: Accuracy score (0-1)

        Returns:
            Updated prediction dictionary or None if not found
        """
        if accuracy < 0 or accuracy > 1:
            raise ValueError("accuracy must be between 0 and 1")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE predictions
                SET outcome = $2, accuracy = $3, validated_at = NOW()
                WHERE id = $1
                RETURNING *
                """,
                uuid.UUID(prediction_id),
                outcome,
                accuracy
            )

        if not row:
            return None

        logger.info(f"Validated prediction {prediction_id} with accuracy {accuracy}")
        return {
            "id": str(row['id']),
            "user_id": str(row['user_id']),
            "prediction_text": row['prediction_text'],
            "category": row['category'],
            "confidence": float(row['confidence']) if row['confidence'] else None,
            "timeframe_start": row['timeframe_start'].isoformat() if row['timeframe_start'] else None,
            "timeframe_end": row['timeframe_end'].isoformat() if row['timeframe_end'] else None,
            "outcome": row['outcome'],
            "accuracy": float(row['accuracy']) if row['accuracy'] else None,
            "validated_at": row['validated_at'].isoformat() if row['validated_at'] else None
        }

    async def get_pending_predictions(
        self,
        user_id: str,
        before_date: Optional[datetime] = None
    ) -> list[dict[str, Any]]:
        """
        Get predictions that need validation.

        Args:
            user_id: User's UUID
            before_date: Get predictions that ended before this date (optional)

        Returns:
            List of pending prediction dictionaries
        """
        async with self.pool.acquire() as conn:
            if before_date:
                rows = await conn.fetch(
                    """
                    SELECT * FROM predictions
                    WHERE user_id = $1
                      AND outcome IS NULL
                      AND timeframe_end <= $2
                    ORDER BY timeframe_end ASC
                    """,
                    uuid.UUID(user_id),
                    before_date.date()
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM predictions
                    WHERE user_id = $1 AND outcome IS NULL
                    ORDER BY timeframe_end ASC
                    """,
                    uuid.UUID(user_id)
                )

        predictions = []
        for row in rows:
            predictions.append({
                "id": str(row['id']),
                "user_id": str(row['user_id']),
                "prediction_text": row['prediction_text'],
                "category": row['category'],
                "confidence": float(row['confidence']) if row['confidence'] else None,
                "timeframe_start": row['timeframe_start'].isoformat() if row['timeframe_start'] else None,
                "timeframe_end": row['timeframe_end'].isoformat() if row['timeframe_end'] else None,
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })

        return predictions

    async def get_user_predictions(
        self,
        user_id: str,
        validated_only: bool = False,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get all predictions for a user."""
        async with self.pool.acquire() as conn:
            if validated_only:
                rows = await conn.fetch(
                    """
                    SELECT * FROM predictions
                    WHERE user_id = $1 AND validated_at IS NOT NULL
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    uuid.UUID(user_id),
                    limit
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM predictions
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    uuid.UUID(user_id),
                    limit
                )

        predictions = []
        for row in rows:
            predictions.append({
                "id": str(row['id']),
                "user_id": str(row['user_id']),
                "prediction_text": row['prediction_text'],
                "category": row['category'],
                "confidence": float(row['confidence']) if row['confidence'] else None,
                "timeframe_start": row['timeframe_start'].isoformat() if row['timeframe_start'] else None,
                "timeframe_end": row['timeframe_end'].isoformat() if row['timeframe_end'] else None,
                "outcome": row['outcome'],
                "accuracy": float(row['accuracy']) if row['accuracy'] else None,
                "validated_at": row['validated_at'].isoformat() if row['validated_at'] else None,
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })

        return predictions

    # ===================
    # Conversation Operations
    # ===================

    async def save_conversation(
        self,
        user_id: str,
        session_id: str,
        messages: list[dict[str, Any]],
        summary: Optional[str] = None,
        topics: Optional[list[str]] = None,
        embedding: Optional[list[float]] = None
    ) -> dict[str, Any]:
        """
        Save conversation history.

        Args:
            user_id: User's UUID
            session_id: Unique session identifier
            messages: List of message dictionaries with role and content
            summary: Optional conversation summary
            topics: Optional list of topics discussed
            embedding: Vector embedding of conversation summary

        Returns:
            Dictionary with conversation details and ID
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now()

        async with self.pool.acquire() as conn:
            await register_vector(conn)
            await conn.execute(
                """
                INSERT INTO conversations (
                    id, user_id, session_id, messages, message_count,
                    summary, topics, embedding, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                uuid.UUID(conversation_id),
                uuid.UUID(user_id),
                session_id,
                json.dumps(messages),
                len(messages),
                summary,
                topics,
                embedding,
                now,
                now
            )

        conversation = {
            "id": conversation_id,
            "user_id": user_id,
            "session_id": session_id,
            "message_count": len(messages),
            "summary": summary,
            "topics": topics or [],
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

        logger.debug(f"Saved conversation {conversation_id} with {len(messages)} messages")
        return conversation

    async def search_conversations(
        self,
        user_id: str,
        query_embedding: list[float],
        limit: int = 5,
        min_similarity: float = 0.6
    ) -> list[dict[str, Any]]:
        """
        Search past conversations by semantic similarity.

        Args:
            user_id: User's UUID
            query_embedding: Query vector embedding
            limit: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of conversation dictionaries with similarity scores
        """
        async with self.pool.acquire() as conn:
            await register_vector(conn)
            rows = await conn.fetch(
                """
                SELECT *,
                    1 - (embedding <=> $2::vector) as similarity
                FROM conversations
                WHERE user_id = $1
                  AND embedding IS NOT NULL
                  AND 1 - (embedding <=> $2::vector) >= $4
                ORDER BY embedding <=> $2::vector
                LIMIT $3
                """,
                uuid.UUID(user_id),
                query_embedding,
                limit,
                min_similarity
            )

        conversations = []
        for row in rows:
            conversations.append({
                "id": str(row['id']),
                "user_id": str(row['user_id']),
                "session_id": row['session_id'],
                "message_count": row['message_count'],
                "summary": row['summary'],
                "topics": row['topics'],
                "similarity": float(row['similarity']),
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })

        return conversations

    async def get_conversation(self, conversation_id: str) -> Optional[dict[str, Any]]:
        """Get a specific conversation by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM conversations WHERE id = $1",
                uuid.UUID(conversation_id)
            )

        if not row:
            return None

        return {
            "id": str(row['id']),
            "user_id": str(row['user_id']),
            "session_id": row['session_id'],
            "messages": json.loads(row['messages']) if row['messages'] else [],
            "message_count": row['message_count'],
            "summary": row['summary'],
            "topics": row['topics'],
            "created_at": row['created_at'].isoformat() if row['created_at'] else None,
            "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
        }

    # ===================
    # Preference Operations
    # ===================

    async def set_preference(
        self,
        user_id: str,
        key: str,
        value: Any
    ) -> None:
        """
        Set a user preference.

        Args:
            user_id: User's UUID
            key: Preference key
            value: Preference value (will be JSON serialized)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_preferences (user_id, preference_key, preference_value)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, preference_key) DO UPDATE SET
                    preference_value = $3,
                    updated_at = NOW()
                """,
                uuid.UUID(user_id),
                key,
                json.dumps(value)
            )

        logger.debug(f"Set preference {key} for user {user_id}")

    async def get_preference(
        self,
        user_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get a user preference.

        Args:
            user_id: User's UUID
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT preference_value FROM user_preferences
                WHERE user_id = $1 AND preference_key = $2
                """,
                uuid.UUID(user_id),
                key
            )

        if not row:
            return default

        return json.loads(row['preference_value'])

    async def get_all_preferences(self, user_id: str) -> dict[str, Any]:
        """
        Get all preferences for a user.

        Args:
            user_id: User's UUID

        Returns:
            Dictionary of all preferences
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT preference_key, preference_value FROM user_preferences
                WHERE user_id = $1
                """,
                uuid.UUID(user_id)
            )

        preferences = {}
        for row in rows:
            preferences[row['preference_key']] = json.loads(row['preference_value'])

        return preferences

    async def delete_preference(self, user_id: str, key: str) -> bool:
        """Delete a user preference."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM user_preferences
                WHERE user_id = $1 AND preference_key = $2
                """,
                uuid.UUID(user_id),
                key
            )

        return "DELETE" in result and int(result.split()[-1]) > 0

    # ===================
    # Dasha Timeline Operations
    # ===================

    async def save_dasha_timeline(
        self,
        user_id: str,
        timeline: list[dict[str, Any]]
    ) -> int:
        """
        Save precomputed dasha timeline.

        Args:
            user_id: User's UUID
            timeline: List of dasha period dictionaries

        Returns:
            Number of periods saved
        """
        if not timeline:
            return 0

        count = 0
        async with self.pool.acquire() as conn:
            for period in timeline:
                await conn.execute(
                    """
                    INSERT INTO dasha_timeline (
                        user_id, level, lord, start_date, end_date, parent_id
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    uuid.UUID(user_id),
                    period.get('level', 'maha'),
                    period['lord'],
                    period['start_date'],
                    period['end_date'],
                    uuid.UUID(period['parent_id']) if period.get('parent_id') else None
                )
                count += 1

        logger.info(f"Saved {count} dasha periods for user {user_id}")
        return count

    async def get_dasha_at_date(
        self,
        user_id: str,
        date: datetime,
        level: str = "antar"
    ) -> Optional[dict[str, Any]]:
        """
        Get the dasha period for a specific date.

        Args:
            user_id: User's UUID
            date: Target date
            level: Dasha level ('maha', 'antar', 'pratyantar')

        Returns:
            Dasha period dictionary or None if not found
        """
        if level not in ["maha", "antar", "pratyantar"]:
            raise ValueError("level must be 'maha', 'antar', or 'pratyantar'")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM dasha_timeline
                WHERE user_id = $1
                  AND level = $2
                  AND start_date <= $3
                  AND end_date > $3
                LIMIT 1
                """,
                uuid.UUID(user_id),
                level,
                date
            )

        if not row:
            return None

        return {
            "id": str(row['id']),
            "user_id": str(row['user_id']),
            "level": row['level'],
            "lord": row['lord'],
            "start_date": row['start_date'].isoformat(),
            "end_date": row['end_date'].isoformat(),
            "parent_id": str(row['parent_id']) if row['parent_id'] else None
        }

    async def get_dasha_timeline(
        self,
        user_id: str,
        level: str = "antar"
    ) -> list[dict[str, Any]]:
        """Get entire dasha timeline for a user."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM dasha_timeline
                WHERE user_id = $1 AND level = $2
                ORDER BY start_date ASC
                """,
                uuid.UUID(user_id),
                level
            )

        timeline = []
        for row in rows:
            timeline.append({
                "id": str(row['id']),
                "user_id": str(row['user_id']),
                "level": row['level'],
                "lord": row['lord'],
                "start_date": row['start_date'].isoformat(),
                "end_date": row['end_date'].isoformat(),
                "parent_id": str(row['parent_id']) if row['parent_id'] else None
            })

        return timeline

    # ===================
    # Bulk Operations
    # ===================

    async def bulk_save_memories(
        self,
        user_id: str,
        memories: list[dict[str, Any]]
    ) -> int:
        """
        Save multiple memories in a single transaction.

        Args:
            user_id: User's UUID
            memories: List of memory data dictionaries

        Returns:
            Number of memories saved
        """
        if not memories:
            return 0

        count = 0
        async with self.pool.acquire() as conn:
            await register_vector(conn)
            async with conn.transaction():
                for mem in memories:
                    await conn.execute(
                        """
                        INSERT INTO memories (
                            id, user_id, content, category, embedding,
                            metadata, importance, created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                        """,
                        uuid.UUID(str(uuid.uuid4())),
                        uuid.UUID(user_id),
                        mem['content'],
                        mem.get('category', 'fact'),
                        mem.get('embedding'),
                        json.dumps(mem.get('metadata', {})),
                        mem.get('importance', 0.5)
                    )
                    count += 1

        logger.info(f"Bulk saved {count} memories for user {user_id}")
        return count

    async def clear_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a user (careful operation).

        Args:
            user_id: User's UUID

        Returns:
            True if successful
        """
        user_uuid = uuid.UUID(user_id)

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM memories WHERE user_id = $1", user_uuid)
                await conn.execute("DELETE FROM predictions WHERE user_id = $1", user_uuid)
                await conn.execute("DELETE FROM conversations WHERE user_id = $1", user_uuid)
                await conn.execute("DELETE FROM user_preferences WHERE user_id = $1", user_uuid)
                await conn.execute("DELETE FROM detected_patterns WHERE user_id = $1", user_uuid)
                await conn.execute("DELETE FROM dasha_timeline WHERE user_id = $1", user_uuid)
                await conn.execute("DELETE FROM birth_charts WHERE user_id = $1", user_uuid)

        logger.warning(f"Cleared all data for user {user_id}")
        return True


# ===================
# Singleton Pattern
# ===================

_store: Optional[MemoryStore] = None


def get_store() -> MemoryStore:
    """
    Get the global memory store instance.

    Returns:
        MemoryStore singleton instance

    Note:
        The store may not be connected. Check with health_check()
        or ensure init_store() was called with await.
    """
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store


async def init_store(
    connection_string: Optional[str] = None
) -> MemoryStore:
    """
    Initialize and connect the memory store.

    Args:
        connection_string: PostgreSQL connection string (optional)

    Returns:
        Connected MemoryStore singleton instance

    Example:
        >>> store = await init_store("postgresql://user:pass@localhost/onezeroeight")
        >>> memories = await store.search_memories(user_id, embedding)
        >>> await store.close()
    """
    global _store
    _store = MemoryStore(connection_string)
    await _store.connect()
    return _store


async def close_store() -> None:
    """Close the memory store connection."""
    global _store
    if _store:
        await _store.close()
        _store = None
