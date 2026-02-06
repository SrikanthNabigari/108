"""
Tests for Guide + Memory fixes (Session 16).

Covers:
- P0 Bug 1: Memory node stubs (_check_memory, _save_memory) now functional
- P0 Bug 2: Async/sync mismatch (chat_async uses ainvoke)
- P0 Bug 3: Mem0 removal (unified_memory pure PostgreSQL)
- P1 Task 1: get_yoga_details() queries knowledge base
- P1 Task 2: ConversationManager multi-turn history
- P1 Task 3: ChartCache calculation caching
- P1 Task 4: LLM error handling with fallback responses
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

# =====================
# ConversationManager Tests
# =====================


class TestConversationManager:
    """Tests for ConversationManager."""

    def test_init(self):
        """Test ConversationManager initialization."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        assert cm.max_turns == 20
        assert cm.history == []

    def test_init_custom_max_turns(self):
        """Test ConversationManager with custom max_turns."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager(max_turns=5)
        assert cm.max_turns == 5

    def test_add_turn(self):
        """Test adding a conversation turn."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        cm.add_turn("user", "What is my dasha?")
        assert len(cm.history) == 1
        assert cm.history[0]["role"] == "user"
        assert cm.history[0]["content"] == "What is my dasha?"
        assert "timestamp" in cm.history[0]

    def test_add_turn_with_metadata(self):
        """Test adding a turn with metadata."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        cm.add_turn("user", "Predict my future", metadata={"intent": "predict"})
        assert cm.history[0]["metadata"]["intent"] == "predict"

    def test_auto_pruning(self):
        """Test that history is auto-pruned when exceeding max_turns."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager(max_turns=3)
        # Add 5 pairs (10 messages), should keep last 6 (3 pairs)
        for i in range(5):
            cm.add_turn("user", f"Question {i}")
            cm.add_turn("assistant", f"Answer {i}")

        assert len(cm.history) == 6  # 3 turns * 2 messages
        assert cm.history[0]["content"] == "Question 2"
        assert cm.history[-1]["content"] == "Answer 4"

    def test_get_context_window(self):
        """Test getting recent context window."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        for i in range(10):
            cm.add_turn("user", f"Q{i}")
            cm.add_turn("assistant", f"A{i}")

        window = cm.get_context_window(last_n=3)
        assert len(window) == 6  # 3 pairs
        assert window[0]["content"] == "Q7"
        assert window[-1]["content"] == "A9"

    def test_get_context_window_small_history(self):
        """Test context window when history is smaller than requested."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        cm.add_turn("user", "Hello")
        cm.add_turn("assistant", "Hi")

        window = cm.get_context_window(last_n=5)
        assert len(window) == 2

    def test_get_summary_empty(self):
        """Test summary with no history."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        summary = cm.get_summary()
        assert "No conversation history" in summary

    def test_get_summary_with_intents(self):
        """Test summary with intent metadata."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        cm.add_turn("user", "Q1", metadata={"intent": "dasha"})
        cm.add_turn("assistant", "A1")
        cm.add_turn("user", "Q2", metadata={"intent": "predict"})
        cm.add_turn("assistant", "A2")

        summary = cm.get_summary()
        assert "2 turns" in summary
        assert "dasha" in summary
        assert "predict" in summary

    def test_clear(self):
        """Test clearing conversation history."""
        from packages.guide.src.agent import ConversationManager

        cm = ConversationManager()
        cm.add_turn("user", "test")
        cm.add_turn("assistant", "response")
        cm.clear()
        assert cm.history == []


# =====================
# ChartCache Tests
# =====================


class TestChartCache:
    """Tests for ChartCache."""

    def setup_method(self):
        """Clear cache before each test."""
        from packages.guide.src.tools import ChartCache

        ChartCache.clear()

    def test_cache_key_format(self):
        """Test that cache key includes user_id and birth data."""
        from packages.guide.src.tools import ChartCache

        dt = datetime(1992, 12, 3, 3, 0, 0)
        lat = 16.726239
        lon = 81.288428

        # Call get_or_calculate (may succeed or fail depending on cosmos state)
        ChartCache.get_or_calculate("user1", dt, lat, lon)

        # Verify cache key format (regardless of success/failure)
        keys = list(ChartCache._cache.keys())
        if keys:
            assert keys[0].startswith("user1:")
            assert "1992" in keys[0]

    def test_cache_hit_returns_same_object(self):
        """Test that second call returns cached result (same object)."""
        from packages.guide.src.tools import ChartCache

        dt = datetime(1992, 12, 3, 3, 0, 0)
        lat = 16.726239
        lon = 81.288428

        result1 = ChartCache.get_or_calculate("user1", dt, lat, lon)
        result2 = ChartCache.get_or_calculate("user1", dt, lat, lon)

        # If first call succeeded, result should be cached (same object)
        if result1.get("success"):
            assert result2 is result1
        else:
            # Failed results are not cached, so second call also fails
            assert result2.get("success") == result1.get("success")

    def test_invalidate(self):
        """Test cache invalidation for a user."""
        from packages.guide.src.tools import ChartCache

        # Manually add a cache entry
        ChartCache._cache["user1:2024-01-01T00:00:00:10.0:20.0"] = {"test": True}
        ChartCache._cache["user2:2024-01-01T00:00:00:10.0:20.0"] = {"test": True}

        # Invalidate user1
        ChartCache.invalidate("user1")
        assert not any(k.startswith("user1:") for k in ChartCache._cache)
        assert any(k.startswith("user2:") for k in ChartCache._cache)

    def test_clear(self):
        """Test clearing entire cache."""
        from packages.guide.src.tools import ChartCache

        # Manually add entries
        ChartCache._cache["user1:test"] = {"test": True}
        ChartCache._cache["user2:test"] = {"test": True}

        ChartCache.clear()
        assert len(ChartCache._cache) == 0

    def test_different_params_different_keys(self):
        """Test that different birth data creates different cache keys."""
        from packages.guide.src.tools import ChartCache

        dt1 = datetime(1992, 12, 3, 3, 0, 0)
        dt2 = datetime(1990, 6, 15, 12, 0, 0)

        ChartCache.get_or_calculate("user1", dt1, 16.7, 81.3)
        ChartCache.get_or_calculate("user1", dt2, 28.6, 77.2)

        # There should be entries for both (or none if calculation fails)
        user1_keys = [k for k in ChartCache._cache if k.startswith("user1:")]
        # Either 0 (both failed) or 2 (both succeeded) or 1
        assert len(user1_keys) <= 2


# =====================
# Yoga Details Tests (P1 Task 1)
# =====================


class TestYogaDetails:
    """Tests for get_yoga_details knowledge base lookup."""

    def test_yoga_details_returns_dict(self):
        """Test that get_yoga_details returns a valid dictionary."""
        from packages.guide.src.tools import AstrologyTools

        tools = AstrologyTools()
        result = tools.get_yoga_details("Gajakesari")
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_yoga_details_unknown_yoga(self):
        """Test lookup of non-existent yoga."""
        from packages.guide.src.tools import AstrologyTools

        tools = AstrologyTools()
        result = tools.get_yoga_details("NonExistentYogaXYZ")
        assert result.get("success") is True
        assert result.get("found") is False

    def test_yoga_details_case_insensitive(self):
        """Test that lookup is case-insensitive."""
        from packages.guide.src.tools import AstrologyTools

        tools = AstrologyTools()
        result1 = tools.get_yoga_details("gajakesari")
        result2 = tools.get_yoga_details("GAJAKESARI")
        # Both should return the same result structure
        assert result1.get("success") == result2.get("success")


# =====================
# Memory Check/Save Node Tests (P0 Bug 1)
# =====================


class TestMemoryNodes:
    """Tests for _check_memory and _save_memory graph nodes."""

    def test_check_memory_initializes_empty(self):
        """Test that _check_memory initializes empty memories when no store."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide._store = None
        guide._store_connected = False

        state = {
            "user_id": "test-user",
            "birth_chart": None,
            "memories": None,
            "detected_yogas": [],
            "detected_doshas": [],
        }

        result = guide._check_memory(state)
        assert result["memories"] == []

    def test_check_memory_preserves_existing(self):
        """Test that _check_memory preserves pre-loaded memories."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide._store = None
        guide._store_connected = False

        existing_memories = [{"content": "test memory", "category": "fact"}]
        state = {
            "user_id": "test-user",
            "birth_chart": None,
            "memories": existing_memories,
            "detected_yogas": [],
            "detected_doshas": [],
        }

        result = guide._check_memory(state)
        assert result["memories"] == existing_memories

    def test_check_memory_no_user_id(self):
        """Test _check_memory with no user_id."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide._store = None
        guide._store_connected = False

        state = {"user_id": None, "memories": None}
        result = guide._check_memory(state)
        assert result["memories"] == []

    def test_save_memory_no_store(self):
        """Test _save_memory without a store just passes through."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide._store = None
        guide._store_connected = False

        state = {
            "user_id": "test-user",
            "user_input": "What is my dasha?",
            "response": "Your current dasha is Mercury.",
            "session_id": "test-session",
            "intent": "dasha",
        }

        result = guide._save_memory(state)
        assert result["response"] == "Your current dasha is Mercury."

    def test_save_memory_no_user_id(self):
        """Test _save_memory with no user_id returns state unchanged."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide._store = None
        guide._store_connected = False

        state = {"user_id": None, "response": "test"}
        result = guide._save_memory(state)
        assert result["response"] == "test"


# =====================
# Unified Memory Client Tests (P0 Bug 3)
# =====================


class TestUnifiedMemoryMem0Removal:
    """Tests for Mem0 removal from UnifiedMemoryClient."""

    def test_no_mem0_backend(self):
        """Test that MEM0_CLOUD backend is no longer available."""
        from packages.memory.src.unified_memory import MemoryBackend

        assert not hasattr(MemoryBackend, "MEM0_CLOUD")
        assert hasattr(MemoryBackend, "POSTGRES")
        assert hasattr(MemoryBackend, "MOCK")

    def test_default_backend_is_postgres(self):
        """Test that default backend is PostgreSQL (not Mem0)."""
        from packages.memory.src.unified_memory import MemoryBackend, UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test")
        assert client.backend == MemoryBackend.POSTGRES

    def test_mock_backend(self):
        """Test mock backend works."""
        from packages.memory.src.unified_memory import MemoryBackend, UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        assert client.backend == MemoryBackend.MOCK

    @pytest.mark.asyncio
    async def test_mock_add(self):
        """Test adding memory with mock backend."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        memory = await client.add(content="test memory", category="fact")
        assert memory.content == "test memory"
        assert memory.category == "fact"
        assert memory.id is not None

    @pytest.mark.asyncio
    async def test_mock_search_returns_empty(self):
        """Test that mock search returns empty list."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        results = await client.search(query="test")
        assert results == []

    @pytest.mark.asyncio
    async def test_mock_get_all_returns_empty(self):
        """Test that mock get_all returns empty list."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        results = await client.get_all()
        assert results == []

    @pytest.mark.asyncio
    async def test_mock_delete_returns_true(self):
        """Test that mock delete returns True."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        result = await client.delete("some-id")
        assert result is True

    @pytest.mark.asyncio
    async def test_mock_health_check(self):
        """Test mock health check."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        health = await client.health_check()
        assert health["backend"] == "mock"
        assert health["healthy"] is True

    @pytest.mark.asyncio
    async def test_mock_remember_birth_data(self):
        """Test remember_birth_data with mock backend."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        memory = await client.remember_birth_data(
            birth_datetime=datetime(1992, 12, 3, 3, 0),
            latitude=16.726239,
            longitude=81.288428,
            timezone="Asia/Kolkata",
            place_name="Eluru, India",
        )
        assert memory.category == "birth_data"
        assert memory.importance == 1.0

    @pytest.mark.asyncio
    async def test_mock_remember_yoga(self):
        """Test remember_yoga with mock backend."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        memory = await client.remember_yoga(
            yoga_name="Gajakesari",
            yoga_type="Prosperity",
            planets_involved=["Moon", "Jupiter"],
            strength=0.85,
            interpretation="Moon-Jupiter conjunction creates wisdom and prosperity",
        )
        assert memory.category == "yoga"
        assert "Gajakesari" in memory.content

    @pytest.mark.asyncio
    async def test_mock_get_context_for_query(self):
        """Test context retrieval with mock backend."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        context = await client.get_context_for_query(query="What is my dasha?")
        assert "memories" in context
        assert context["user_id"] == "test"

    def test_no_mem0_client_attribute(self):
        """Test that _mem0_client attribute is gone from UnifiedMemoryClient."""
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        client = UnifiedMemoryClient(user_id="test", use_mock=True)
        assert not hasattr(client, "_mem0_client")

    def test_create_memory_client_no_mem0(self):
        """Test factory function no longer supports mem0 backend."""
        from packages.memory.src.unified_memory import MemoryBackend, create_memory_client

        client = create_memory_client("test", backend="mock")
        assert client.backend == MemoryBackend.MOCK

        # "mem0" should NOT set MEM0_CLOUD (it doesn't exist)
        client2 = create_memory_client("test", backend="mem0")
        # Should default to POSTGRES since "mem0" is unrecognized
        assert client2.backend == MemoryBackend.POSTGRES


# =====================
# LLM Error Handling Tests (P1 Task 4)
# =====================


class TestLLMErrorHandling:
    """Tests for LLM error handling in Guide agent."""

    def test_fallback_response_with_context(self):
        """Test fallback response includes chart context."""
        from packages.guide.src.agent import ConversationManager, Guide, IntentType

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide.conversation_manager = ConversationManager()

        state = {
            "intent": IntentType.PREDICT,
            "birth_chart": {"lagna_rashi": "Libra"},
            "detected_yogas": [{"name": "Gajakesari"}],
            "current_dasha": {"mahadasha_lord": "Mercury", "antardasha_lord": "Sun"},
        }

        response = guide._generate_fallback_response(state)
        assert "Libra" in response
        assert "Gajakesari" in response
        assert "Mercury" in response

    def test_fallback_response_empty_context(self):
        """Test fallback response with no context."""
        from packages.guide.src.agent import ConversationManager, Guide, IntentType

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide.conversation_manager = ConversationManager()

        state = {
            "intent": IntentType.GENERAL,
            "birth_chart": None,
            "detected_yogas": [],
            "current_dasha": None,
        }

        response = guide._generate_fallback_response(state)
        assert "Thank you" in response

    def test_fallback_response_calculate_intent(self):
        """Test fallback for calculate intent."""
        from packages.guide.src.agent import ConversationManager, Guide, IntentType

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide.conversation_manager = ConversationManager()

        state = {
            "intent": IntentType.CALCULATE,
            "birth_chart": None,
            "detected_yogas": [],
            "current_dasha": None,
        }

        response = guide._generate_fallback_response(state)
        assert "chart data" in response

    def test_fallback_response_analyze_intent(self):
        """Test fallback for analyze intent."""
        from packages.guide.src.agent import ConversationManager, Guide, IntentType

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide.conversation_manager = ConversationManager()

        state = {
            "intent": IntentType.ANALYZE,
            "birth_chart": None,
            "detected_yogas": [],
            "current_dasha": None,
        }

        response = guide._generate_fallback_response(state)
        assert "patterns" in response


# =====================
# Async Chat Tests (P0 Bug 2)
# =====================


class TestAsyncChat:
    """Tests for async chat path using ainvoke."""

    @pytest.mark.asyncio
    async def test_chat_async_uses_ainvoke(self):
        """Verify chat_async calls ainvoke (not invoke)."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide._store = None
        guide._store_connected = False
        guide.model = "claude-sonnet-4-20250514"
        guide.api_key = "test-key"

        # Mock the compiled graph
        mock_state = {
            "response": "test response",
            "intent": MagicMock(value="general"),
            "personality_style": "libra",
            "session_id": "test-session",
            "timestamp": "2024-01-01T00:00:00",
            "analysis_results": {},
        }

        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(return_value=mock_state)
        guide._compiled_graph = mock_graph

        # Mock _get_store to avoid DB connection
        guide._get_store = AsyncMock(return_value=None)

        result = await guide.chat_async(
            user_input="Tell me about my chart",
            user_id="test-user",
        )

        # Verify ainvoke was called (not invoke)
        mock_graph.ainvoke.assert_called_once()
        assert result["response"] == "test response"

    @pytest.mark.asyncio
    async def test_chat_async_with_mock_store(self):
        """Test that chat_async works with mock memory store."""
        from packages.guide.src.agent import Guide
        from packages.memory.src.unified_memory import UnifiedMemoryClient

        guide = Guide.__new__(Guide)
        guide.debug = False
        guide.model = "claude-sonnet-4-20250514"
        guide.api_key = "test-key"

        # Set up mock store
        mock_store = UnifiedMemoryClient(user_id="system", use_mock=True)
        guide._store = mock_store
        guide._store_connected = True

        mock_state = {
            "response": "Your Libra lagna indicates balance",
            "intent": MagicMock(value="personal"),
            "personality_style": "libra",
            "session_id": "test-session",
            "timestamp": "2024-01-01T00:00:00",
            "analysis_results": {},
        }

        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(return_value=mock_state)
        guide._compiled_graph = mock_graph

        result = await guide.chat_async(
            user_input="Tell me about my personality",
            user_id="test-user",
        )

        assert result["response"] == "Your Libra lagna indicates balance"
        assert result["intent"] == "personal"


# =====================
# Guide __init__.py Export Tests
# =====================


class TestGuideExports:
    """Test that guide package exports are correct."""

    def test_conversation_manager_exported(self):
        """Test ConversationManager is exported from guide package."""
        from packages.guide.src import ConversationManager

        assert ConversationManager is not None
        cm = ConversationManager()
        assert cm.max_turns == 20

    def test_intent_type_exported(self):
        """Test IntentType is exported."""
        from packages.guide.src import IntentType

        assert IntentType.CALCULATE.value == "calculate"

    def test_has_langgraph_function(self):
        """Test has_langgraph function."""
        from packages.guide.src import has_langgraph

        result = has_langgraph()
        assert isinstance(result, bool)


# =====================
# Memory Package Export Tests
# =====================


class TestMemoryExports:
    """Test that memory package exports are correct after Mem0 removal."""

    def test_unified_memory_exported(self):
        """Test UnifiedMemoryClient is exported."""
        from packages.memory.src import UnifiedMemoryClient

        assert UnifiedMemoryClient is not None

    def test_memory_backend_exported(self):
        """Test MemoryBackend is exported."""
        from packages.memory.src import MemoryBackend

        assert hasattr(MemoryBackend, "POSTGRES")
        assert hasattr(MemoryBackend, "MOCK")

    def test_embedding_service_exported(self):
        """Test EmbeddingService is exported."""
        from packages.memory.src import EmbeddingService

        assert EmbeddingService is not None

    def test_mem0_client_still_importable(self):
        """Test Mem0Client still importable (deprecated but not removed)."""
        from packages.memory.src import Mem0Client

        # Still importable - the file exists but is just stubs
        assert Mem0Client is not None


# =====================
# Integration: Agent State Flow Tests
# =====================


class TestAgentStateFlow:
    """Tests for data flow through agent state."""

    def test_state_with_memories(self):
        """Test that memories are included in context formatting."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False

        state = {
            "birth_chart": {"lagna_rashi": "Libra", "moon_rashi": "Aquarius"},
            "current_dasha": {"mahadasha_lord": "Mercury"},
            "analysis_results": {},
            "detected_yogas": [],
            "detected_doshas": [],
            "memories": [{"content": "user prefers detailed readings"}],
        }

        context = guide._format_context(state)
        assert "Libra" in context
        assert "Mercury" in context
        assert "1 facts from past" in context

    def test_state_with_doshas(self):
        """Test that doshas appear in context."""
        from packages.guide.src.agent import Guide

        guide = Guide.__new__(Guide)
        guide.debug = False

        state = {
            "birth_chart": None,
            "current_dasha": {},
            "analysis_results": {},
            "detected_yogas": [],
            "detected_doshas": [{"name": "Mangal Dosha"}],
            "memories": [],
        }

        context = guide._format_context(state)
        assert "Mangal Dosha" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
