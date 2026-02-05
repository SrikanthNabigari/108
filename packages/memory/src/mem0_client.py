"""
108 Mem0 Client

Integration with Mem0 for intelligent memory management.
Mem0 provides enhanced memory accuracy through semantic extraction,
importance scoring, and cross-session persistence.

Memory is core to the 108 experience - storing birth data, yogas,
predictions, preferences, and feedback for personalized guidance.
"""

import json
import logging
import os
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

# In production: from mem0 import Memory

logger = logging.getLogger(__name__)


class MemoryCategory(StrEnum):
    """Memory categories for 108."""

    BIRTH_DATA = "birth_data"
    CORE_FACTS = "core_facts"
    YOGAS = "yogas"
    CHART_ANALYSIS = "chart_analysis"
    PREDICTIONS = "predictions"
    TRANSITS = "transits"
    DASHAS = "dashas"
    PREFERENCES = "preferences"
    FEEDBACK = "feedback"
    LEARNING = "learning"
    INTERACTIONS = "interactions"


class MemoryImportance(float, Enum):
    """Importance scores for memories."""

    CRITICAL = 1.0  # Birth data, core facts
    HIGH = 0.8  # Detected yogas, current dashas
    MEDIUM = 0.5  # Predictions, analysis
    LOW = 0.3  # Temporary notes


class Mem0Client:
    """
    Mem0 memory client for 108.

    Mem0 automatically:
    - Extracts important facts from conversations
    - Scores memory importance
    - Handles semantic search
    - Manages memory lifecycle

    All memories are tagged with metadata for efficient retrieval
    and personalized context generation.
    """

    def __init__(
        self,
        api_key: str | None = None,
        user_id: str | None = None,
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize Mem0 client.

        Args:
            api_key: Mem0 API key (or use env MEM0_API_KEY)
            user_id: Default user ID for operations
            config: Additional Mem0 configuration
        """
        self.api_key = api_key or os.getenv("MEM0_API_KEY")
        self.default_user_id = user_id
        self.config = config or {}
        self._client = None

        logger.info(f"Mem0Client initialized for user: {user_id}")

        # In production:
        # from mem0 import Memory
        # self._client = Memory(api_key=api_key, **config)

    def _get_client(self):
        """Get or initialize Mem0 client."""
        if self._client is None:
            # from mem0 import Memory
            # self._client = Memory(api_key=self.api_key, **self.config)
            pass
        return self._client

    # ===================
    # Core Memory Operations
    # ===================

    def add(
        self,
        content: str,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        categories: list[str] | None = None,
        importance: float = MemoryImportance.MEDIUM,
    ) -> dict[str, Any]:
        """
        Add a memory.

        Args:
            content: Memory content (Mem0 auto-extracts facts)
            user_id: User ID (uses default if not provided)
            metadata: Additional metadata to store
            categories: Memory categories for filtering
            importance: Importance score (0.0 to 1.0)

        Returns:
            Created memory with ID and extracted facts
        """
        user_id = user_id or self.default_user_id

        # Build metadata
        mem_metadata = {
            "source": "108_astrology",
            "timestamp": datetime.now().isoformat(),
            "importance": importance,
            **(metadata or {}),
        }

        if categories:
            mem_metadata["categories"] = categories

        # In production:
        # result = self._get_client().add(
        #     content,
        #     user_id=user_id,
        #     metadata=mem_metadata
        # )

        # Mock result
        memory_id = f"mem_{int(datetime.now().timestamp() * 1000000)}"
        result = {
            "id": memory_id,
            "content": content,
            "user_id": user_id,
            "metadata": mem_metadata,
            "extracted_facts": self._extract_facts_mock(content),
            "created_at": datetime.now().isoformat(),
        }

        logger.info(f"Memory added: {memory_id} (importance: {importance})")

        return result

    def add_conversation(
        self,
        messages: list[dict[str, str]],
        user_id: str | None = None,
        session_id: str | None = None,
        categories: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Add memories from a conversation.

        Mem0 automatically extracts important facts from the conversation.

        Args:
            messages: List of {role: "user"|"assistant", content: str}
            user_id: User ID
            session_id: Session identifier
            categories: Categories to tag conversation memories

        Returns:
            Extracted memories from conversation
        """
        user_id = user_id or self.default_user_id

        # In production:
        # result = self._get_client().add(
        #     messages,
        #     user_id=user_id,
        #     metadata={"session_id": session_id, "type": "conversation"}
        # )

        # Mock extraction
        extracted = []
        for msg in messages:
            if msg["role"] == "user":
                facts = self._extract_facts_mock(msg["content"])
                extracted.extend(facts)

        result = {
            "user_id": user_id,
            "session_id": session_id,
            "memories_added": len(extracted),
            "extracted_facts": extracted,
            "categories": categories or [],
        }

        logger.info(f"Conversation memory added: {len(extracted)} facts extracted")

        return result

    def search(
        self,
        query: str,
        user_id: str | None = None,
        limit: int = 10,
        categories: list[str] | None = None,  # noqa: ARG002
        min_importance: float = 0.0,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """
        Search memories semantically.

        Mem0 performs intelligent semantic search across memories,
        returning the most relevant results ranked by relevance.

        Args:
            query: Search query
            user_id: User ID to search within
            limit: Max results
            categories: Filter by categories
            min_importance: Minimum importance threshold

        Returns:
            List of relevant memories with relevance scores
        """
        user_id = user_id or self.default_user_id

        logger.info(f"Searching memories: query='{query}', limit={limit}")

        # In production:
        # results = self._get_client().search(
        #     query,
        #     user_id=user_id,
        #     limit=limit
        # )
        # Filter by categories and importance if provided
        # if categories:
        #     results = [r for r in results if any(c in r.get('categories', []) for c in categories)]
        # if min_importance > 0:
        #     results = [r for r in results if r.get('metadata', {}).get('importance', 0) >= min_importance]

        # Mock results
        return []

    def get_all(
        self,
        user_id: str | None = None,
        limit: int = 100,  # noqa: ARG002
        categories: list[str] | None = None,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """
        Get all memories for a user.

        Args:
            user_id: User ID
            limit: Maximum memories to return
            categories: Filter by categories

        Returns:
            List of all memories
        """
        user_id = user_id or self.default_user_id

        # In production:
        # results = self._get_client().get_all(user_id=user_id)
        # if categories:
        #     results = [r for r in results if any(c in r.get('metadata', {}).get('categories', []) for c in categories)]
        # return results[:limit]

        return []

    def get(self, memory_id: str) -> dict[str, Any] | None:  # noqa: ARG002
        """
        Get a specific memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory object or None if not found
        """
        # In production:
        # return self._get_client().get(memory_id)
        return None

    def update(
        self,
        memory_id: str,
        content: str | None = None,  # noqa: ARG002
        metadata: dict[str, Any] | None = None,  # noqa: ARG002
        categories: list[str] | None = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """
        Update a memory.

        Args:
            memory_id: Memory ID
            content: New content
            metadata: Updated metadata
            categories: Updated categories

        Returns:
            Updated memory
        """
        logger.info(f"Updating memory: {memory_id}")

        # In production:
        # return self._get_client().update(
        #     memory_id,
        #     content=content,
        #     metadata={**metadata or {}, "updated_at": datetime.now().isoformat()}
        # )

        return {"id": memory_id, "updated": True, "updated_at": datetime.now().isoformat()}

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory ID

        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting memory: {memory_id}")

        # In production:
        # self._get_client().delete(memory_id)

        return True

    # ===================
    # 108-Specific Methods
    # ===================

    def remember_birth_data(
        self,
        user_id: str,
        birth_datetime: str,
        place: str,
        latitude: float | None = None,
        longitude: float | None = None,
        lagna: str | None = None,
        lagna_degree: float | None = None,
        moon_sign: str | None = None,
        moon_degree: float | None = None,
        nakshatra: str | None = None,
        nakshatra_pada: int | None = None,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """
        Store birth data as core memories.

        These are foundational facts that should always be recalled
        with maximum importance.

        Args:
            user_id: User ID
            birth_datetime: Birth date/time in ISO format
            place: Birth place
            latitude: Geographic latitude
            longitude: Geographic longitude
            lagna: Ascendant sign name
            lagna_degree: Ascendant degree
            moon_sign: Moon sign
            moon_degree: Moon degree
            nakshatra: Moon nakshatra
            nakshatra_pada: Nakshatra pada (1-4)
            timezone: Timezone offset

        Returns:
            Created memory
        """
        content = f"""
Birth Chart Data for {place}:
- Date and Time: {birth_datetime}
- Place: {place}
"""

        if latitude and longitude:
            content += f"- Coordinates: {latitude}°N, {longitude}°E\n"
        if timezone:
            content += f"- Timezone: {timezone}\n"
        if lagna:
            content += f"- Ascendant (Lagna): {lagna}"
            if lagna_degree:
                content += f" ({lagna_degree}°)"
            content += "\n"
        if moon_sign:
            content += f"- Moon Sign (Rashi): {moon_sign}"
            if moon_degree:
                content += f" ({moon_degree}°)"
            content += "\n"
        if nakshatra:
            content += f"- Moon Nakshatra: {nakshatra}"
            if nakshatra_pada:
                content += f" (Pada {nakshatra_pada})"
            content += "\n"

        metadata = {
            "type": "birth_data",
            "birth_datetime": birth_datetime,
            "place": place,
            "latitude": latitude,
            "longitude": longitude,
            "lagna": lagna,
            "lagna_degree": lagna_degree,
            "moon_sign": moon_sign,
            "moon_degree": moon_degree,
            "nakshatra": nakshatra,
            "nakshatra_pada": nakshatra_pada,
            "timezone": timezone,
            "permanent": True,
        }

        return self.add(
            content=content,
            user_id=user_id,
            metadata=metadata,
            categories=[MemoryCategory.BIRTH_DATA, MemoryCategory.CORE_FACTS],
            importance=MemoryImportance.CRITICAL,
        )

    def remember_planetary_positions(
        self, user_id: str, planet_positions: dict[str, dict[str, Any]], chart_type: str = "natal"
    ) -> dict[str, Any]:
        """
        Store planetary positions from a birth chart.

        Args:
            user_id: User ID
            planet_positions: Dict of planet data with sign, degree, house, etc.
            chart_type: Type of chart (natal, transit, progressions, etc.)

        Returns:
            Created memory
        """
        planet_list = []
        for planet, data in planet_positions.items():
            rashi = data.get("rashi", "")
            degree = data.get("degree", 0)
            house = data.get("house", "")
            retrograde = data.get("retrograde", False)

            planet_str = f"{planet} in {rashi} {degree:.2f}°"
            if house:
                planet_str += f" (House {house})"
            if retrograde:
                planet_str += " [Retrograde]"
            planet_list.append(planet_str)

        content = f"""
Planetary Positions ({chart_type.capitalize()} Chart):
{chr(10).join(planet_list)}
"""

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "planetary_positions",
                "chart_type": chart_type,
                "planet_count": len(planet_positions),
            },
            categories=[MemoryCategory.CHART_ANALYSIS, MemoryCategory.CORE_FACTS],
            importance=MemoryImportance.HIGH,
        )

    def remember_yoga(
        self,
        user_id: str,
        yoga_name: str,
        yoga_type: str,
        description: str,
        effects: list[str],
        planets_involved: list[str],
        strength: str = "medium",
    ) -> dict[str, Any]:
        """
        Store a detected yoga as a memory.

        Args:
            user_id: User ID
            yoga_name: Name of the yoga
            yoga_type: Type (Pancha Mahapurusha, Dhana yoga, etc.)
            description: Description of the yoga
            effects: List of expected effects
            planets_involved: Planets forming the yoga
            strength: Yoga strength (weak, medium, strong)

        Returns:
            Created memory
        """
        content = f"""
Yoga Detected: {yoga_name}
Type: {yoga_type}
Description: {description}
Planets Involved: {", ".join(planets_involved)}
Expected Effects:
{chr(10).join(f"- {effect}" for effect in effects)}
Strength: {strength.upper()}
"""

        importance_map = {
            "weak": MemoryImportance.LOW,
            "medium": MemoryImportance.MEDIUM,
            "strong": MemoryImportance.HIGH,
        }

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "yoga",
                "yoga_name": yoga_name,
                "yoga_type": yoga_type,
                "strength": strength,
                "planets_involved": planets_involved,
            },
            categories=[MemoryCategory.YOGAS, MemoryCategory.CHART_ANALYSIS],
            importance=importance_map.get(strength, MemoryImportance.MEDIUM),
        )

    def remember_dasha(
        self,
        user_id: str,
        dasha_lord: str,
        antardasha_lord: str,
        start_date: str,
        end_date: str,
        characteristics: list[str],
        challenges: list[str] | None = None,
        opportunities: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Store current dasha period information.

        Args:
            user_id: User ID
            dasha_lord: Mahadasha lord
            antardasha_lord: Antardasha lord
            start_date: Period start date
            end_date: Period end date
            characteristics: Dasha characteristics
            challenges: Potential challenges
            opportunities: Opportunities during period

        Returns:
            Created memory
        """
        content = f"""
Current Dasha Period:
- Mahadasha: {dasha_lord}
- Antardasha: {antardasha_lord}
- Period: {start_date} to {end_date}
- Characteristics:
{chr(10).join(f"  - {char}" for char in characteristics)}
"""

        if challenges:
            content += f"""- Challenges:
{chr(10).join(f"  - {ch}" for ch in challenges)}
"""

        if opportunities:
            content += f"""- Opportunities:
{chr(10).join(f"  - {opp}" for opp in opportunities)}
"""

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "dasha",
                "dasha_lord": dasha_lord,
                "antardasha_lord": antardasha_lord,
                "start_date": start_date,
                "end_date": end_date,
            },
            categories=[MemoryCategory.DASHAS, MemoryCategory.CHART_ANALYSIS],
            importance=MemoryImportance.HIGH,
        )

    def remember_transit(
        self,
        user_id: str,
        planet: str,
        transit_date: str,
        from_sign: str,
        to_sign: str,
        expected_effects: list[str],
        duration: str | None = None,
    ) -> dict[str, Any]:
        """
        Store important transit information.

        Args:
            user_id: User ID
            planet: Transiting planet
            transit_date: Date of transit
            from_sign: Sign being transited from
            to_sign: Sign being transited to
            expected_effects: Expected effects
            duration: Duration of transit

        Returns:
            Created memory
        """
        content = f"""
Transit Alert:
- Planet: {planet}
- Date: {transit_date}
- Transit: {from_sign} → {to_sign}
"""

        if duration:
            content += f"- Duration: {duration}\n"

        content += f"""- Expected Effects:
{chr(10).join(f"  - {effect}" for effect in expected_effects)}
"""

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "transit",
                "planet": planet,
                "transit_date": transit_date,
                "from_sign": from_sign,
                "to_sign": to_sign,
            },
            categories=[MemoryCategory.TRANSITS, MemoryCategory.PREDICTIONS],
            importance=MemoryImportance.MEDIUM,
        )

    def remember_prediction(
        self,
        user_id: str,
        prediction: str,
        area: str,
        timeframe: str,
        confidence: float,
        factors: list[str],
        reasoning: str | None = None,
    ) -> dict[str, Any]:
        """
        Store a prediction for later validation.

        Args:
            user_id: User ID
            prediction: The prediction
            area: Area of life (career, relationships, health, etc.)
            timeframe: When the prediction applies
            confidence: Confidence score (0.0 to 1.0)
            factors: Astrological factors supporting prediction
            reasoning: Detailed reasoning

        Returns:
            Created memory
        """
        content = f"""
Prediction:
- Statement: {prediction}
- Area: {area}
- Timeframe: {timeframe}
- Confidence: {confidence * 100:.0f}%
- Supporting Factors:
{chr(10).join(f"  - {factor}" for factor in factors)}
"""

        if reasoning:
            content += f"\n- Reasoning: {reasoning}\n"

        content += f"- Made on: {datetime.now().isoformat()}\n"

        importance = confidence  # Use confidence as importance

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "prediction",
                "area": area,
                "timeframe": timeframe,
                "confidence": confidence,
                "factors": factors,
                "status": "pending_validation",
                "created_date": datetime.now().isoformat(),
            },
            categories=[MemoryCategory.PREDICTIONS],
            importance=importance,
        )

    def remember_preference(
        self, user_id: str, preference_type: str, value: str, category: str | None = None
    ) -> dict[str, Any]:
        """
        Store a user preference.

        Args:
            user_id: User ID
            preference_type: Type of preference (reading_style, detail_level, etc.)
            value: Preference value
            category: Optional category

        Returns:
            Created memory
        """
        content = f"User Preference - {preference_type}: {value}"

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "preference",
                "preference_type": preference_type,
                "value": value,
                "category": category,
            },
            categories=[MemoryCategory.PREFERENCES],
            importance=MemoryImportance.MEDIUM,
        )

    def remember_feedback(
        self,
        user_id: str,
        prediction_id: str,
        prediction_text: str,
        outcome: str,
        accuracy: float,
        lessons: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Store feedback on a prediction for learning and validation.

        This feedback helps improve future predictions.

        Args:
            user_id: User ID
            prediction_id: ID of the prediction
            prediction_text: Original prediction
            outcome: Actual outcome
            accuracy: Accuracy rating (0.0 to 1.0)
            lessons: Lessons learned

        Returns:
            Created memory
        """
        content = f"""
Prediction Validation:
- Prediction ID: {prediction_id}
- Original Prediction: {prediction_text}
- Actual Outcome: {outcome}
- Accuracy: {accuracy * 100:.0f}%
"""

        if lessons:
            content += f"""- Lessons Learned:
{chr(10).join(f"  - {lesson}" for lesson in lessons)}
"""

        content += f"- Validated on: {datetime.now().isoformat()}\n"

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "feedback",
                "prediction_id": prediction_id,
                "accuracy": accuracy,
                "validated_date": datetime.now().isoformat(),
            },
            categories=[MemoryCategory.FEEDBACK, MemoryCategory.LEARNING],
            importance=accuracy,  # Higher accuracy = higher importance
        )

    def remember_interaction(
        self,
        user_id: str,
        question: str,
        response: str,
        topic: str,
        user_rating: float | None = None,
    ) -> dict[str, Any]:
        """
        Store a conversation interaction.

        Helps improve personalization over time.

        Args:
            user_id: User ID
            question: User's question
            response: Assistant's response
            topic: Topic of interaction
            user_rating: User rating (0.0 to 1.0)

        Returns:
            Created memory
        """
        content = f"""
Interaction History:
- Topic: {topic}
- Question: {question}
- Response Summary: {response[:200]}...
"""

        if user_rating:
            content += f"- User Rating: {user_rating * 100:.0f}%\n"

        content += f"- Date: {datetime.now().isoformat()}\n"

        importance = user_rating if user_rating else MemoryImportance.LOW

        return self.add(
            content=content,
            user_id=user_id,
            metadata={
                "type": "interaction",
                "topic": topic,
                "user_rating": user_rating,
            },
            categories=[MemoryCategory.INTERACTIONS],
            importance=importance,
        )

    # ===================
    # Context Retrieval
    # ===================

    def get_context_for_query(
        self,
        user_id: str,
        query: str,
        include_birth_data: bool = True,
        include_yogas: bool = True,
        include_current_dasha: bool = True,
        include_recent_transits: bool = True,
        include_preferences: bool = True,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Get relevant context for answering a user query.

        This is the main method used by the Guide agent to get
        personalized context before generating a response.

        Args:
            user_id: User ID
            query: User's question/query
            include_birth_data: Whether to include birth data
            include_yogas: Whether to include detected yogas
            include_current_dasha: Whether to include dasha info
            include_recent_transits: Whether to include transits
            include_preferences: Whether to include preferences
            limit: Max memories to retrieve per category

        Returns:
            Contextualized memory data for response generation
        """
        context = {
            "user_id": user_id,
            "query": query,
            "birth_data": None,
            "yogas": [],
            "current_dasha": None,
            "recent_transits": [],
            "preferences": {},
            "relevant_memories": [],
            "context_quality": 0.0,  # Score of how much context found
        }

        found_items = 0
        total_expected = 0

        # Get birth data if requested
        if include_birth_data:
            total_expected += 1
            birth_memories = self.search(
                "birth data ascendant moon nakshatra lagna",
                user_id=user_id,
                limit=1,
                categories=[MemoryCategory.BIRTH_DATA],
                min_importance=MemoryImportance.CRITICAL,
            )
            if birth_memories:
                context["birth_data"] = birth_memories[0]
                found_items += 1

        # Get yogas if requested
        if include_yogas:
            total_expected += 1
            yoga_memories = self.search(
                "yoga pancha mahapurusha dhana effects",
                user_id=user_id,
                limit=limit,
                categories=[MemoryCategory.YOGAS],
                min_importance=MemoryImportance.LOW,
            )
            if yoga_memories:
                context["yogas"] = yoga_memories
                found_items += 1

        # Get current dasha if requested
        if include_current_dasha:
            total_expected += 1
            dasha_memories = self.search(
                "dasha mahadasha antardasha current",
                user_id=user_id,
                limit=1,
                categories=[MemoryCategory.DASHAS],
                min_importance=MemoryImportance.MEDIUM,
            )
            if dasha_memories:
                context["current_dasha"] = dasha_memories[0]
                found_items += 1

        # Get recent transits if requested
        if include_recent_transits:
            total_expected += 1
            transit_memories = self.search(
                "transit planet sign movement",
                user_id=user_id,
                limit=limit,
                categories=[MemoryCategory.TRANSITS],
                min_importance=MemoryImportance.LOW,
            )
            if transit_memories:
                context["recent_transits"] = transit_memories
                found_items += 1

        # Get preferences if requested
        if include_preferences:
            total_expected += 1
            pref_memories = self.search(
                "preference style detail level",
                user_id=user_id,
                limit=10,
                categories=[MemoryCategory.PREFERENCES],
            )
            if pref_memories:
                context["preferences"] = {
                    m.get("metadata", {}).get("preference_type"): m.get("metadata", {}).get("value")
                    for m in pref_memories
                }
                found_items += 1

        # Search for query-relevant memories
        context["relevant_memories"] = self.search(query, user_id=user_id, limit=limit)

        # Calculate context quality
        if total_expected > 0:
            context["context_quality"] = found_items / total_expected

        logger.info(f"Context generated for query: quality={context['context_quality']:.1%}")

        return context

    # ===================
    # Utility Methods
    # ===================

    def _extract_facts_mock(self, content: str) -> list[str]:
        """Mock fact extraction (Mem0 does this automatically in production)."""
        facts = []

        # Simple keyword-based extraction for demo
        keywords = {
            "birth": "Contains birth information",
            "ascendant": "Contains ascendant information",
            "moon": "Contains moon information",
            "planet": "Contains planetary information",
            "yoga": "Contains yoga information",
            "predict": "Contains prediction",
            "dasha": "Contains dasha information",
            "transit": "Contains transit information",
            "prefer": "Contains preference information",
            "feedback": "Contains feedback information",
        }

        content_lower = content.lower()
        for keyword, fact in keywords.items():
            if keyword in content_lower:
                facts.append(fact)

        return list(set(facts))  # Remove duplicates

    def get_memory_stats(self, user_id: str | None = None) -> dict[str, Any]:
        """
        Get memory statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Statistics about user's memories
        """
        user_id = user_id or self.default_user_id

        all_memories = self.get_all(user_id)

        # Count by category
        categories = {}
        total_importance = 0.0

        for mem in all_memories:
            # Count categories
            for cat in mem.get("metadata", {}).get("categories", ["uncategorized"]):
                categories[cat] = categories.get(cat, 0) + 1

            # Sum importance
            importance = mem.get("metadata", {}).get("importance", 0.0)
            total_importance += importance

        avg_importance = total_importance / len(all_memories) if all_memories else 0.0

        return {
            "user_id": user_id,
            "total_memories": len(all_memories),
            "by_category": categories,
            "average_importance": avg_importance,
            "categories_count": len(categories),
        }

    def cleanup_old_memories(
        self,
        user_id: str | None = None,
        days_old: int = 90,
        categories_to_keep: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Clean up old memories while preserving important ones.

        Args:
            user_id: User ID
            days_old: Delete memories older than this
            categories_to_keep: Categories to never delete

        Returns:
            Cleanup statistics
        """
        user_id = user_id or self.default_user_id
        categories_to_keep = categories_to_keep or [
            MemoryCategory.BIRTH_DATA,
            MemoryCategory.CORE_FACTS,
        ]

        all_memories = self.get_all(user_id)

        deleted_count = 0
        preserved_count = 0

        cutoff_date = datetime.now().timestamp() - (days_old * 86400)

        for mem in all_memories:
            created_at = mem.get("created_at", "")
            memory_timestamp = datetime.fromisoformat(created_at).timestamp() if created_at else 0

            categories = mem.get("metadata", {}).get("categories", [])
            importance = mem.get("metadata", {}).get("importance", 0.0)

            # Keep if in protected categories, high importance, or recent
            if (
                any(cat in categories_to_keep for cat in categories)
                or importance >= MemoryImportance.HIGH
                or memory_timestamp > cutoff_date
            ):
                preserved_count += 1
            else:
                self.delete(mem.get("id"))
                deleted_count += 1

        logger.info(f"Cleanup completed: deleted={deleted_count}, preserved={preserved_count}")

        return {"deleted": deleted_count, "preserved": preserved_count, "user_id": user_id}

    def export_user_memories(self, user_id: str | None = None) -> str:
        """
        Export all user memories as JSON.

        Args:
            user_id: User ID

        Returns:
            JSON string of all memories
        """
        user_id = user_id or self.default_user_id

        all_memories = self.get_all(user_id)

        export_data = {
            "user_id": user_id,
            "exported_at": datetime.now().isoformat(),
            "memory_count": len(all_memories),
            "memories": all_memories,
        }

        return json.dumps(export_data, indent=2)


# ===================
# Module-level API
# ===================

_client: Mem0Client | None = None


def get_mem0_client(
    api_key: str | None = None, user_id: str | None = None, force_new: bool = False
) -> Mem0Client:
    """
    Get or create the global Mem0 client.

    Args:
        api_key: Mem0 API key
        user_id: Default user ID
        force_new: If True, create new client even if one exists

    Returns:
        Mem0Client instance
    """
    global _client

    if _client is None or force_new:
        _client = Mem0Client(api_key=api_key, user_id=user_id)

    return _client


def reset_mem0_client():
    """Reset the global Mem0 client."""
    global _client
    _client = None
    logger.info("Mem0 client reset")
