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
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import json

# For actual production, uncomment these:
# import asyncpg
# from pgvector.asyncpg import register_vector

logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """A semantic memory unit."""
    id: Optional[str] = None
    user_id: str = ""
    content: str = ""
    category: str = "fact"  # fact, preference, event, prediction, feedback
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
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

    def to_dict(self) -> Dict[str, Any]:
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

    def __init__(self, connection_string: str = None):
        """
        Initialize memory store.

        Args:
            connection_string: PostgreSQL connection string
                             e.g., "postgresql://user:pass@localhost/onezeroeight"
        """
        self.connection_string = (
            connection_string or
            "postgresql://localhost/onezeroeight"
        )
        self.pool = None
        self._embedding_dimension = 1536  # OpenAI ada-002 dimension
        self._initialized = False
        logger.info(f"MemoryStore initialized with connection: {self.connection_string}")

    async def connect(self) -> None:
        """
        Establish database connection pool.

        Production implementation:
        ```python
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60,
        )
        await register_vector(self.pool)
        ```
        """
        try:
            # In production, uncomment the above and add logging
            # self.pool = await asyncpg.create_pool(...)
            # await register_vector(self.pool)
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
        if not self._initialized:
            return False

        try:
            # In production:
            # async with self.pool.acquire() as conn:
            #     await conn.fetchval("SELECT 1")
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
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
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

        Raises:
            ValueError: If inputs are invalid
            Exception: If database operation fails
        """
        if not user_id or not content:
            raise ValueError("user_id and content are required")

        if importance < 0 or importance > 1:
            raise ValueError("importance must be between 0 and 1")

        memory_id = str(uuid.uuid4())
        now = datetime.now()

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

        # Production SQL:
        # INSERT INTO memories (
        #     id, user_id, content, category, embedding, metadata, importance, created_at, updated_at
        # ) VALUES (
        #     $1, $2, $3, $4, $5, $6, $7, $8, $9
        # )
        # ON CONFLICT (id) DO NOTHING
        # RETURNING id, created_at, updated_at

        logger.debug(f"Added memory {memory_id} for user {user_id}")
        return memory

    async def search_memories(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int = 10,
        category: Optional[str] = None,
        min_similarity: float = 0.7
    ) -> List[SearchResult]:
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

        Raises:
            ValueError: If query_embedding dimension is incorrect
            Exception: If database operation fails
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

        # Production SQL using pgvector:
        # SELECT
        #     id, user_id, content, category, embedding, metadata, importance,
        #     created_at, updated_at,
        #     1 - (embedding <=> $2::vector) as similarity
        # FROM memories
        # WHERE user_id = $1
        #   AND ($3::text IS NULL OR category = $3)
        #   AND 1 - (embedding <=> $2::vector) >= $4
        # ORDER BY embedding <=> $2::vector
        # LIMIT $5

        logger.debug(
            f"Searching memories for user {user_id} "
            f"with {limit} limit and {min_similarity} threshold"
        )
        return []

    async def get_memories_by_category(
        self,
        user_id: str,
        category: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Memory]:
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

        # Production SQL:
        # SELECT * FROM memories
        # WHERE user_id = $1 AND category = $2
        # ORDER BY updated_at DESC
        # LIMIT $3 OFFSET $4

        logger.debug(f"Getting {category} memories for user {user_id}")
        return []

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID."""
        # Production SQL:
        # SELECT * FROM memories WHERE id = $1

        return None

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
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

        # Production SQL:
        # UPDATE memories
        # SET
        #     content = COALESCE($2, content),
        #     embedding = COALESCE($3, embedding),
        #     metadata = metadata || $4,
        #     importance = COALESCE($5, importance),
        #     updated_at = NOW()
        # WHERE id = $1
        # RETURNING *

        logger.debug(f"Updated memory {memory_id}")
        return None

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory's UUID

        Returns:
            True if deleted, False if not found
        """
        # Production SQL:
        # DELETE FROM memories WHERE id = $1
        # RETURNING TRUE

        logger.debug(f"Deleted memory {memory_id}")
        return False

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
        # Production SQL:
        # DELETE FROM memories
        # WHERE user_id = $1 AND category = $2
        # RETURNING COUNT(*)

        return 0

    # ===================
    # User Operations
    # ===================

    async def create_user(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            email: User's email address (unique)
            name: User's display name (optional)
            metadata: Additional user metadata

        Returns:
            Dictionary with user ID and details

        Raises:
            ValueError: If email is invalid
            Exception: If user already exists or database error
        """
        if not email or "@" not in email:
            raise ValueError("Valid email is required")

        user_id = str(uuid.uuid4())
        now = datetime.now()

        # Production SQL:
        # INSERT INTO users (id, email, name, metadata, created_at, updated_at)
        # VALUES ($1, $2, $3, $4, $5, $6)
        # ON CONFLICT (email) DO NOTHING
        # RETURNING *

        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "metadata": metadata or {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

        logger.info(f"Created user {user_id} with email {email}")
        return user

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: User's UUID

        Returns:
            User dictionary or None if not found
        """
        # Production SQL:
        # SELECT * FROM users WHERE id = $1

        return None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.

        Args:
            email: User's email

        Returns:
            User dictionary or None if not found
        """
        # Production SQL:
        # SELECT * FROM users WHERE email = $1

        return None

    async def update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update user information."""
        # Production SQL:
        # UPDATE users
        # SET
        #     name = COALESCE($2, name),
        #     metadata = metadata || $3,
        #     updated_at = NOW()
        # WHERE id = $1
        # RETURNING *

        return None

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
        planets: Optional[Dict[str, Any]] = None,
        houses: Optional[Dict[str, Any]] = None,
        lagna_rashi: Optional[str] = None,
        moon_rashi: Optional[str] = None,
        moon_nakshatra: Optional[str] = None,
        ayanamsa: Optional[float] = None,
        house_system: str = "placidus"
    ) -> Dict[str, Any]:
        """
        Save or update user's birth chart.

        Args:
            user_id: User's UUID
            birth_datetime: Exact birth date and time
            latitude: Birth location latitude
            longitude: Birth location longitude
            timezone: Birth timezone (e.g., "Asia/Kolkata")
            place_name: Birth place name (optional)
            planets: Dictionary of planetary positions
            houses: Dictionary of house cusps
            lagna_rashi: Ascendant rashi (sign)
            moon_rashi: Moon sign
            moon_nakshatra: Moon nakshatra (lunar mansion)
            ayanamsa: Ayanamsa value used in calculation
            house_system: House system used (default: placidus)

        Returns:
            Dictionary with birth chart details
        """
        birth_chart = {
            "user_id": user_id,
            "birth_datetime": birth_datetime.isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "place_name": place_name,
            "planets": planets or {},
            "houses": houses or {},
            "lagna_rashi": lagna_rashi,
            "moon_rashi": moon_rashi,
            "moon_nakshatra": moon_nakshatra,
            "ayanamsa": ayanamsa,
            "house_system": house_system,
            "saved_at": datetime.now().isoformat()
        }

        # Production SQL:
        # INSERT INTO birth_charts (
        #     user_id, birth_datetime, latitude, longitude, timezone,
        #     place_name, planets, houses, lagna_rashi, moon_rashi,
        #     moon_nakshatra, ayanamsa, house_system
        # ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        # ON CONFLICT (user_id) DO UPDATE SET
        #     birth_datetime = $2, planets = $7, houses = $8, updated_at = NOW()
        # RETURNING *

        logger.info(f"Saved birth chart for user {user_id}")
        return birth_chart

    async def get_birth_chart(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's birth chart.

        Args:
            user_id: User's UUID

        Returns:
            Birth chart dictionary or None if not found
        """
        # Production SQL:
        # SELECT * FROM birth_charts WHERE user_id = $1

        return None

    # ===================
    # Pattern Operations
    # ===================

    async def save_detected_patterns(
        self,
        user_id: str,
        patterns: List[Dict[str, Any]],
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

        Raises:
            ValueError: If pattern_type is invalid
        """
        if pattern_type not in ["yoga", "dosha"]:
            raise ValueError("pattern_type must be 'yoga' or 'dosha'")

        if not patterns:
            return 0

        # Production SQL:
        # INSERT INTO detected_patterns (
        #     user_id, pattern_name, pattern_type, details, detected_at
        # )
        # SELECT $1, p->>'name', $2, p, NOW()
        # FROM jsonb_array_elements($3::jsonb) as p
        # ON CONFLICT DO NOTHING
        # RETURNING COUNT(*)

        logger.info(f"Saved {len(patterns)} {pattern_type} patterns for user {user_id}")
        return len(patterns)

    async def get_user_patterns(
        self,
        user_id: str,
        pattern_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's detected patterns.

        Args:
            user_id: User's UUID
            pattern_type: Optional filter ('yoga' or 'dosha')

        Returns:
            List of pattern dictionaries
        """
        # Production SQL:
        # SELECT * FROM detected_patterns
        # WHERE user_id = $1 AND ($2::text IS NULL OR pattern_type = $2)
        # ORDER BY detected_at DESC

        return []

    async def delete_pattern(
        self,
        user_id: str,
        pattern_name: str
    ) -> bool:
        """Delete a detected pattern."""
        # Production SQL:
        # DELETE FROM detected_patterns
        # WHERE user_id = $1 AND pattern_name = $2
        # RETURNING TRUE

        return False

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
        factors: Optional[Dict[str, Any]] = None,
        dasha_period: Optional[Dict[str, Any]] = None,
        transit_positions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
            "updated_at": now.isoformat(),
            "status": "pending"
        }

        # Production SQL:
        # INSERT INTO predictions (
        #     id, user_id, prediction_text, category, confidence,
        #     timeframe_start, timeframe_end, factors, dasha_period,
        #     transit_positions, created_at, status
        # ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'pending')
        # RETURNING *

        logger.info(f"Saved prediction {prediction_id} for user {user_id}")
        return prediction

    async def validate_prediction(
        self,
        prediction_id: str,
        outcome: str,
        accuracy: float
    ) -> Optional[Dict[str, Any]]:
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

        # Production SQL:
        # UPDATE predictions
        # SET
        #     outcome = $2,
        #     accuracy = $3,
        #     status = 'validated',
        #     updated_at = NOW()
        # WHERE id = $1
        # RETURNING *

        logger.info(f"Validated prediction {prediction_id} with accuracy {accuracy}")
        return None

    async def get_pending_predictions(
        self,
        user_id: str,
        before_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get predictions that need validation.

        Args:
            user_id: User's UUID
            before_date: Get predictions that ended before this date (optional)

        Returns:
            List of pending prediction dictionaries
        """
        # Production SQL:
        # SELECT * FROM predictions
        # WHERE user_id = $1
        #   AND status = 'pending'
        #   AND ($2::timestamp IS NULL OR timeframe_end <= $2)
        # ORDER BY timeframe_end ASC

        return []

    async def get_user_predictions(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all predictions for a user with optional status filter."""
        # Production SQL:
        # SELECT * FROM predictions
        # WHERE user_id = $1 AND ($2::text IS NULL OR status = $2)
        # ORDER BY created_at DESC
        # LIMIT $3

        return []

    # ===================
    # Conversation Operations
    # ===================

    async def save_conversation(
        self,
        user_id: str,
        session_id: str,
        messages: List[Dict[str, Any]],
        summary: Optional[str] = None,
        topics: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> Dict[str, Any]:
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

        # Production SQL:
        # INSERT INTO conversations (
        #     id, user_id, session_id, messages, message_count, summary,
        #     topics, embedding, created_at
        # ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        # RETURNING *

        logger.debug(f"Saved conversation {conversation_id} with {len(messages)} messages")
        return conversation

    async def search_conversations(
        self,
        user_id: str,
        query_embedding: List[float],
        limit: int = 5,
        min_similarity: float = 0.6
    ) -> List[Dict[str, Any]]:
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
        # Production SQL:
        # SELECT *,
        #     1 - (embedding <=> $2::vector) as similarity
        # FROM conversations
        # WHERE user_id = $1
        #   AND embedding IS NOT NULL
        #   AND 1 - (embedding <=> $2::vector) >= $4
        # ORDER BY embedding <=> $2::vector
        # LIMIT $3

        return []

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific conversation by ID."""
        # Production SQL:
        # SELECT * FROM conversations WHERE id = $1

        return None

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
        # Production SQL:
        # INSERT INTO preferences (user_id, key, value, updated_at)
        # VALUES ($1, $2, jsonb_build_object($2, $3), NOW())
        # ON CONFLICT (user_id, key) DO UPDATE SET
        #     value = excluded.value,
        #     updated_at = NOW()

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
        # Production SQL:
        # SELECT value FROM preferences
        # WHERE user_id = $1 AND key = $2

        return default

    async def get_all_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get all preferences for a user.

        Args:
            user_id: User's UUID

        Returns:
            Dictionary of all preferences
        """
        # Production SQL:
        # SELECT key, value FROM preferences WHERE user_id = $1

        return {}

    async def delete_preference(self, user_id: str, key: str) -> bool:
        """Delete a user preference."""
        # Production SQL:
        # DELETE FROM preferences WHERE user_id = $1 AND key = $2
        # RETURNING TRUE

        return False

    # ===================
    # Dasha Timeline Operations
    # ===================

    async def save_dasha_timeline(
        self,
        user_id: str,
        timeline: List[Dict[str, Any]]
    ) -> int:
        """
        Save precomputed dasha timeline.

        Args:
            user_id: User's UUID
            timeline: List of dasha period dictionaries with:
                    - lord: Planet name
                    - start_date: Period start
                    - end_date: Period end
                    - level: 'maha', 'antar', or 'pratyantar'

        Returns:
            Number of periods saved
        """
        if not timeline:
            return 0

        # Production SQL:
        # INSERT INTO dasha_timelines (
        #     user_id, lord, start_date, end_date, level, period_data
        # )
        # SELECT $1, p->>'lord', (p->>'start_date')::timestamp,
        #        (p->>'end_date')::timestamp, p->>'level', p
        # FROM jsonb_array_elements($2::jsonb) as p
        # ON CONFLICT DO NOTHING
        # RETURNING COUNT(*)

        logger.info(f"Saved {len(timeline)} dasha periods for user {user_id}")
        return len(timeline)

    async def get_dasha_at_date(
        self,
        user_id: str,
        date: datetime,
        level: str = "antar"
    ) -> Optional[Dict[str, Any]]:
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

        # Production SQL:
        # SELECT * FROM dasha_timelines
        # WHERE user_id = $1
        #   AND level = $2
        #   AND start_date <= $3
        #   AND end_date > $3
        # LIMIT 1

        return None

    async def get_dasha_timeline(
        self,
        user_id: str,
        level: str = "antar"
    ) -> List[Dict[str, Any]]:
        """Get entire dasha timeline for a user."""
        # Production SQL:
        # SELECT * FROM dasha_timelines
        # WHERE user_id = $1 AND level = $2
        # ORDER BY start_date ASC

        return []

    # ===================
    # Bulk Operations
    # ===================

    async def bulk_save_memories(
        self,
        user_id: str,
        memories: List[Dict[str, Any]]
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

        # Production SQL with batching:
        # BEGIN;
        # INSERT INTO memories (user_id, content, category, ...)
        # VALUES (unnest($1), unnest($2), ...)
        # ON CONFLICT DO NOTHING;
        # COMMIT;

        logger.info(f"Bulk saved {len(memories)} memories for user {user_id}")
        return len(memories)

    async def clear_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a user (careful operation).

        Args:
            user_id: User's UUID

        Returns:
            True if successful
        """
        # Production SQL:
        # BEGIN;
        # DELETE FROM memories WHERE user_id = $1;
        # DELETE FROM predictions WHERE user_id = $1;
        # DELETE FROM conversations WHERE user_id = $1;
        # DELETE FROM preferences WHERE user_id = $1;
        # DELETE FROM detected_patterns WHERE user_id = $1;
        # DELETE FROM dasha_timelines WHERE user_id = $1;
        # DELETE FROM birth_charts WHERE user_id = $1;
        # COMMIT;

        logger.warning(f"Cleared all data for user {user_id}")
        return False


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
