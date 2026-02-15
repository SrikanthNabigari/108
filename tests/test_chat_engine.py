"""Tests for ChatEngine — Anthropic SDK chat with tool use.

Uses mocked Anthropic client to test the tool-use loop, system prompt
building, message conversion, and block generation.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.guide.src.chat_engine import (
    DEFAULT_MODEL,
    ChatEngine,
    ChatResult,
    _build_messages,
)
from packages.guide.src.chat_rules import build_system_prompt, load_rules
from packages.guide.src.chat_tools import get_tool_definitions

# ── Fixtures ──

SAMPLE_BIRTH_CONTEXT: dict[str, Any] = {
    "birth_datetime": "1992-12-03T03:00:00+05:30",
    "birth_lat": 16.726239,
    "birth_lon": 81.288428,
    "natal_planets": {
        "sun": {"longitude": 227.0, "rashi": 7, "house": 2},
        "moon": {"longitude": 326.85, "rashi": 10, "house": 5, "sign": "Aquarius"},
    },
    "moon_longitude": 326.85,
    "lagna_rashi": "Libra",
    "moon_rashi": "Aquarius",
    "moon_nakshatra": "Purva Bhadrapada",
}


# ── Mock Anthropic response objects ──


@dataclass
class MockTextBlock:
    type: str = "text"
    text: str = ""


@dataclass
class MockToolUseBlock:
    type: str = "tool_use"
    id: str = "tool_01"
    name: str = "get_state_now"
    input: dict = None

    def __post_init__(self):
        if self.input is None:
            self.input = {}


@dataclass
class MockUsage:
    input_tokens: int = 100
    output_tokens: int = 50


@dataclass
class MockResponse:
    content: list = None
    stop_reason: str = "end_turn"
    usage: MockUsage = None

    def __post_init__(self):
        if self.content is None:
            self.content = []
        if self.usage is None:
            self.usage = MockUsage()


# ── ChatResult Tests ──


class TestChatResult:
    def test_fields(self):
        r = ChatResult(text="hello", blocks=[], tokens_used=150, tool_calls=["get_state_now"])
        assert r.text == "hello"
        assert r.blocks == []
        assert r.tokens_used == 150
        assert r.tool_calls == ["get_state_now"]

    def test_default_tool_calls(self):
        r = ChatResult(text="hi", blocks=[], tokens_used=0)
        assert r.tool_calls == []


# ── Rules Tests ──


class TestLoadRules:
    def test_loads_from_default_path(self):
        rules = load_rules()
        assert "identity" in rules
        assert "behavior_rules" in rules
        assert rules["identity"]["name"] == "108"

    def test_loads_fallback_on_missing(self, tmp_path):
        rules = load_rules(tmp_path / "nonexistent.json")
        assert rules["identity"]["name"] == "108"
        assert len(rules["behavior_rules"]) >= 1


class TestBuildSystemPrompt:
    def test_includes_identity(self):
        rules = load_rules()
        prompt = build_system_prompt(rules, {})
        assert "108" in prompt
        assert "Vedic astrology" in prompt

    def test_includes_birth_context(self):
        rules = load_rules()
        prompt = build_system_prompt(rules, SAMPLE_BIRTH_CONTEXT)
        assert "Libra" in prompt
        assert "Aquarius" in prompt

    def test_includes_personality(self):
        rules = load_rules()
        prompt = build_system_prompt(rules, {}, personality_style="Aquarius")
        assert "Aquarius" in prompt

    def test_includes_behavior_rules(self):
        rules = load_rules()
        prompt = build_system_prompt(rules, {})
        assert "tools" in prompt.lower() or "tool" in prompt.lower()

    def test_empty_context_still_works(self):
        rules = load_rules()
        prompt = build_system_prompt(rules, {})
        assert len(prompt) > 50


# ── Message Building Tests ──


class TestBuildMessages:
    def test_new_message_only(self):
        msgs = _build_messages(None, "hello")
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"
        assert msgs[0]["content"] == "hello"

    def test_with_history(self):
        history = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello there"},
        ]
        msgs = _build_messages(history, "how's my career?")
        assert len(msgs) == 3
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "assistant"
        assert msgs[2]["role"] == "user"
        assert msgs[2]["content"] == "how's my career?"

    def test_skips_empty_content(self):
        history = [
            {"role": "user", "content": ""},
            {"role": "assistant", "content": "response"},
        ]
        msgs = _build_messages(history, "next question")
        # Empty content message should be skipped
        assert all(m["content"] for m in msgs)

    def test_empty_history(self):
        msgs = _build_messages([], "hello")
        assert len(msgs) == 1


# ── ChatEngine Init Tests ──


class TestChatEngineInit:
    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    def test_init_loads_rules_and_tools(self, _mock_anthropic):
        engine = ChatEngine(api_key="test-key")
        assert engine.rules is not None
        assert "identity" in engine.rules
        assert len(engine.tool_defs) == 29
        assert engine.model == DEFAULT_MODEL

    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    def test_custom_model(self, _mock_anthropic):
        engine = ChatEngine(api_key="test-key", model="claude-haiku-4-5-20251001")
        assert engine.model == "claude-haiku-4-5-20251001"


# ── ChatEngine.chat() Tests (mocked API) ──


class TestChatEngineChat:
    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    def test_simple_text_response(self, mock_anthropic_cls):
        """Test a simple response with no tool calls."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # Response with just text, no tool use
        mock_response = MockResponse(
            content=[MockTextBlock(text="Your career looks great today!")],
            stop_reason="end_turn",
        )
        mock_client.messages.create.return_value = mock_response

        engine = ChatEngine(api_key="test-key")
        result = engine.chat("How is my career?", SAMPLE_BIRTH_CONTEXT)

        assert isinstance(result, ChatResult)
        assert result.text == "Your career looks great today!"
        assert result.blocks == []
        assert result.tokens_used == 150
        assert result.tool_calls == []

    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    @patch("packages.guide.src.chat_engine.execute_tool")
    def test_tool_use_then_text(self, mock_execute, mock_anthropic_cls):
        """Test tool call followed by text response."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # First call: Claude calls a tool
        tool_response = MockResponse(
            content=[
                MockToolUseBlock(id="tool_01", name="get_state_now", input={}),
            ],
            stop_reason="tool_use",
        )
        # Second call: Claude returns text
        text_response = MockResponse(
            content=[MockTextBlock(text="Your composite score is 6.5.")],
            stop_reason="end_turn",
        )
        mock_client.messages.create.side_effect = [tool_response, text_response]

        # Mock tool execution
        mock_execute.return_value = {
            "composite": 6.5,
            "mental_state": "Flowing",
            "factors": [{"id": "panchanga", "short_name": "PAN", "score": 7.0, "label": "Good"}],
            "areas": [{"id": "career", "score": 7.2, "double_transit": True, "active_yogas": []}],
            "success": True,
        }

        engine = ChatEngine(api_key="test-key")
        result = engine.chat("How is my day?", SAMPLE_BIRTH_CONTEXT)

        assert result.text == "Your composite score is 6.5."
        assert result.tool_calls == ["get_state_now"]
        assert result.tokens_used == 300  # 150 * 2
        assert len(result.blocks) > 0
        # Should have score_card, factor_grid, area_list
        block_types = [b["type"] for b in result.blocks]
        assert "score_card" in block_types

    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    @patch("packages.guide.src.chat_engine.execute_tool")
    def test_multiple_tool_calls(self, mock_execute, mock_anthropic_cls):
        """Test Claude calling multiple tools in sequence."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # First call: two tools
        first_response = MockResponse(
            content=[
                MockToolUseBlock(id="t1", name="get_state_now", input={}),
                MockToolUseBlock(id="t2", name="get_current_dasha", input={}),
            ],
            stop_reason="tool_use",
        )
        # Second call: text
        second_response = MockResponse(
            content=[MockTextBlock(text="Here is your analysis.")],
            stop_reason="end_turn",
        )
        mock_client.messages.create.side_effect = [first_response, second_response]

        # Return different results per call
        mock_execute.side_effect = [
            {
                "composite": 5.0,
                "mental_state": "Steady",
                "factors": [],
                "areas": [],
                "success": True,
            },
            {
                "current_mahadasha": {
                    "lord": "Mercury",
                    "start": "2019",
                    "end": "2036",
                    "progress_percent": 40,
                },
                "current_antardasha": {
                    "lord": "Venus",
                    "start": "2025",
                    "end": "2027",
                    "progress_percent": 10,
                },
                "success": True,
            },
        ]

        engine = ChatEngine(api_key="test-key")
        result = engine.chat("Tell me about my chart", SAMPLE_BIRTH_CONTEXT)

        assert result.tool_calls == ["get_state_now", "get_current_dasha"]
        assert result.text == "Here is your analysis."
        # Blocks from both tools
        block_types = [b["type"] for b in result.blocks]
        assert "score_card" in block_types
        assert "dasha_card" in block_types

    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    @patch("packages.guide.src.chat_engine.execute_tool")
    def test_max_iterations_guard(self, mock_execute, mock_anthropic_cls):
        """Test that the loop stops after max_tool_rounds."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # Always return tool_use (never end_turn) to test the guard
        tool_response = MockResponse(
            content=[MockToolUseBlock(id="t1", name="get_panchanga", input={})],
            stop_reason="tool_use",
        )
        mock_client.messages.create.return_value = tool_response
        mock_execute.return_value = {"success": True, "tithi": "test"}

        engine = ChatEngine(api_key="test-key", max_tool_rounds=3)
        result = engine.chat("What's the panchanga?", SAMPLE_BIRTH_CONTEXT)

        # Should have called API exactly 3 times (max_tool_rounds)
        assert mock_client.messages.create.call_count == 3
        assert len(result.tool_calls) == 3

    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    def test_chat_with_history(self, mock_anthropic_cls):
        """Test that chat history is passed correctly."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_response = MockResponse(
            content=[MockTextBlock(text="Following up on that...")],
            stop_reason="end_turn",
        )
        mock_client.messages.create.return_value = mock_response

        engine = ChatEngine(api_key="test-key")
        history = [
            {"role": "user", "content": "previous question"},
            {"role": "assistant", "content": "previous answer"},
        ]
        engine.chat("follow up", SAMPLE_BIRTH_CONTEXT, chat_history=history)

        # Verify messages passed to API
        call_kwargs = mock_client.messages.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        assert len(messages) == 3  # 2 history + 1 new

    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    def test_chat_empty_birth_context(self, mock_anthropic_cls):
        """Test with empty birth context."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_response = MockResponse(
            content=[MockTextBlock(text="I need your birth details.")],
            stop_reason="end_turn",
        )
        mock_client.messages.create.return_value = mock_response

        engine = ChatEngine(api_key="test-key")
        result = engine.chat("hello", {})

        assert result.text == "I need your birth details."
        assert result.tokens_used == 150

    @patch("packages.guide.src.chat_engine.anthropic.Anthropic")
    @patch("packages.guide.src.chat_engine.execute_tool")
    def test_tool_text_interleaved(self, mock_execute, mock_anthropic_cls):
        """Test response with both text and tool_use in same block."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # Response with text + tool in same message
        first_response = MockResponse(
            content=[
                MockTextBlock(text="Let me check that."),
                MockToolUseBlock(id="t1", name="get_life_area", input={"area_id": "career"}),
            ],
            stop_reason="tool_use",
        )
        second_response = MockResponse(
            content=[MockTextBlock(text="Your career score is 7.2.")],
            stop_reason="end_turn",
        )
        mock_client.messages.create.side_effect = [first_response, second_response]
        mock_execute.return_value = {
            "area": {"id": "career", "score": 7.2, "double_transit": True},
            "composite": 6.5,
            "mental_state": "Flowing",
            "success": True,
        }

        engine = ChatEngine(api_key="test-key")
        result = engine.chat("How's my career?", SAMPLE_BIRTH_CONTEXT)

        assert "Let me check that." in result.text
        assert "career score is 7.2" in result.text
        assert result.tool_calls == ["get_life_area"]
        assert len(result.blocks) == 1
        assert result.blocks[0]["type"] == "score_card"


# ── Tool Definitions Tests (verify integration) ──


class TestToolDefinitionsIntegration:
    def test_definitions_count(self):
        defs = get_tool_definitions()
        assert len(defs) == 29

    def test_all_definitions_have_input_schema(self):
        for d in get_tool_definitions():
            assert "input_schema" in d
            assert d["input_schema"]["type"] == "object"
