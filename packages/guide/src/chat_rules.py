"""Chat rules loader and system prompt builder.

Loads extensible rules from knowledge/rules/chat_rules.json and builds
the system prompt for the Anthropic API chat engine.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_RULES_PATH = (
    Path(__file__).parent.parent.parent.parent / "knowledge" / "rules" / "chat_rules.json"
)


def load_rules(path: str | Path | None = None) -> dict[str, Any]:
    """Load chat rules from JSON file.

    Args:
        path: Path to chat_rules.json. Defaults to knowledge/rules/chat_rules.json.

    Returns:
        Parsed rules dict with identity, behavior_rules, response_style.
    """
    rules_path = Path(path) if path else _DEFAULT_RULES_PATH
    try:
        with Path.open(rules_path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Chat rules not found at {rules_path}, using defaults")
        return {
            "identity": {
                "name": "108",
                "role": "Personal Vedic astrology guide",
                "tone": "warm, knowledgeable, concise",
            },
            "behavior_rules": [
                "Always use tools to fetch real data before answering",
                "Keep text responses concise",
            ],
            "response_style": {"max_paragraphs": 2, "prefer_tools": True},
        }


def build_system_prompt(
    rules: dict[str, Any],
    birth_context: dict[str, Any],
    personality_style: str | None = None,
) -> str:
    """Build the system prompt for the Anthropic API.

    Assembles identity, behavior rules, birth chart context, and personality.

    Args:
        rules: Loaded rules dict from load_rules().
        birth_context: User's birth chart context (lagna, moon, dasha, etc.).
        personality_style: Optional personality adaptation key (e.g. moon sign).

    Returns:
        Complete system prompt string.
    """
    identity = rules.get("identity", {})
    behavior = rules.get("behavior_rules", [])
    style = rules.get("response_style", {})

    parts: list[str] = []

    # 1. Identity
    parts.append(
        f"You are {identity.get('name', '108')}, "
        f"a {identity.get('role', 'Vedic astrology guide')}. "
        f"Your tone is {identity.get('tone', 'warm and concise')}."
    )

    # 2. Behavior rules
    if behavior:
        parts.append("\nRules:")
        for rule in behavior:
            parts.append(f"- {rule}")

    # 3. Response style
    max_para = style.get("max_paragraphs", 2)
    parts.append(f"\nKeep responses to {max_para} paragraphs maximum.")
    if style.get("prefer_tools"):
        parts.append("Always prefer calling tools over guessing data.")

    # 4. Birth chart context
    if birth_context:
        parts.append("\nUser's birth chart context:")
        if birth_context.get("lagna_rashi"):
            parts.append(f"- Lagna (Ascendant): {birth_context['lagna_rashi']}")
        if birth_context.get("moon_rashi"):
            parts.append(f"- Moon sign: {birth_context['moon_rashi']}")
        if birth_context.get("moon_nakshatra"):
            parts.append(f"- Moon nakshatra: {birth_context['moon_nakshatra']}")
        if birth_context.get("birth_datetime"):
            parts.append(f"- Birth: {birth_context['birth_datetime']}")

    # 5. Personality adaptation
    if personality_style:
        parts.append(
            f"\nAdapt your communication style for a {personality_style} moon sign personality."
        )

    return "\n".join(parts)
