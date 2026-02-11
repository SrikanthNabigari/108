"""AI Chat Engine using native Anthropic SDK with tool use.

Claude calls calculation tools to get data, then the backend
deterministically generates render_blocks from tool results.

Architecture:
    User message -> ChatEngine
        -> System prompt (rules + birth chart context)
        -> Anthropic API (tool_use loop)
        -> Block Builder (tool results -> render_blocks)
        -> Returns ChatResult(text, blocks, tokens_used)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import anthropic

from .chat_blocks import build_blocks
from .chat_rules import build_system_prompt, load_rules
from .chat_tools import execute_tool, get_tool_definitions

logger = logging.getLogger(__name__)

# Default model for chat — fast, good at tool use, cost-effective
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
MAX_TOOL_ROUNDS = 5
MAX_TOKENS = 1024


@dataclass
class ChatResult:
    """Result from a chat engine call."""

    text: str
    blocks: list[dict[str, Any]]
    tokens_used: int
    tool_calls: list[str] = field(default_factory=list)


class ChatEngine:
    """AI chat engine using native Anthropic SDK with tool use loop.

    Claude decides WHAT data to fetch (via tools).
    Backend decides HOW to display it (via block builders).
    """

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        rules_path: str | None = None,
        max_tool_rounds: int = MAX_TOOL_ROUNDS,
    ):
        """Initialize the chat engine.

        Args:
            api_key: Anthropic API key.
            model: Model ID (default: claude-sonnet-4-5-20250929).
            rules_path: Path to chat_rules.json (default: knowledge/rules/chat_rules.json).
            max_tool_rounds: Maximum tool call iterations (default: 5).
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or DEFAULT_MODEL
        self.rules = load_rules(rules_path)
        self.tool_defs = get_tool_definitions()
        self.max_tool_rounds = max_tool_rounds

    def chat(
        self,
        message: str,
        birth_context: dict[str, Any],
        chat_history: list[dict[str, str]] | None = None,
        personality_style: str | None = None,
    ) -> ChatResult:
        """Process a chat message through the AI engine.

        Args:
            message: User's message text.
            birth_context: User's birth chart context dict with keys:
                birth_datetime, birth_lat, birth_lon, natal_planets,
                moon_longitude, lagna_rashi, moon_rashi, moon_nakshatra.
            chat_history: Previous messages as [{role, content}] dicts.
            personality_style: Optional personality adaptation key.

        Returns:
            ChatResult with text, blocks, tokens_used, and tool_calls.
        """
        # 1. Build system prompt
        system_prompt = build_system_prompt(self.rules, birth_context, personality_style)

        # 2. Build messages from history + new message
        messages = _build_messages(chat_history, message)

        # 3. Tool-use loop
        text_parts: list[str] = []
        tool_results: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
        tool_names: list[str] = []
        total_tokens = 0

        for _ in range(self.max_tool_rounds):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                tools=self.tool_defs,
                messages=messages,
            )

            # Track tokens
            total_tokens += response.usage.input_tokens + response.usage.output_tokens

            # Process content blocks
            assistant_content: list[dict[str, Any]] = []
            tool_use_blocks: list[dict[str, Any]] = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                    assistant_content.append(
                        {
                            "type": "text",
                            "text": block.text,
                        }
                    )
                elif block.type == "tool_use":
                    tool_names.append(block.name)
                    assistant_content.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )
                    tool_use_blocks.append(
                        {
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

            # If there were tool calls, execute them and add results
            if tool_use_blocks:
                messages.append({"role": "assistant", "content": assistant_content})

                tool_result_content: list[dict[str, Any]] = []
                for tool_block in tool_use_blocks:
                    result = execute_tool(
                        tool_block["name"],
                        tool_block["input"],
                        birth_context,
                    )
                    tool_results.append(
                        (
                            tool_block["name"],
                            tool_block["input"],
                            result,
                        )
                    )
                    tool_result_content.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block["id"],
                            "content": json.dumps(result, default=str),
                        }
                    )

                messages.append({"role": "user", "content": tool_result_content})

            # If stop reason is end_turn (no more tool calls needed), break
            if response.stop_reason == "end_turn":
                break
        else:
            logger.warning(f"Chat hit max tool rounds ({self.max_tool_rounds})")

        # 4. Build render_blocks from all tool results
        blocks = build_blocks(tool_results)

        # 5. Assemble final text
        final_text = "\n\n".join(text_parts) if text_parts else ""

        return ChatResult(
            text=final_text,
            blocks=blocks,
            tokens_used=total_tokens,
            tool_calls=tool_names,
        )


def _build_messages(
    chat_history: list[dict[str, str]] | None,
    new_message: str,
) -> list[dict[str, Any]]:
    """Convert chat history + new message to Anthropic messages format.

    Args:
        chat_history: Previous messages as [{role, content}] dicts.
        new_message: The new user message.

    Returns:
        List of message dicts for the Anthropic API.
    """
    messages: list[dict[str, Any]] = []

    if chat_history:
        for msg in chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": new_message})

    # Ensure messages start with user role (Anthropic requirement)
    if messages and messages[0].get("role") != "user":
        messages = [m for m in messages if m.get("role") == "user" or messages.index(m) > 0]

    return messages
