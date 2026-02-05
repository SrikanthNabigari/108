"""
108 Guide Package

LangGraph-powered conversational agent with personality adaptation.
"""

import logging

from .agent import (
    _HAS_LANGGRAPH,
    INTENT_KEYWORDS,
    PERSONALITY_STYLES,
    IntentType,
)

logger = logging.getLogger(__name__)

# These require LangGraph
Guide = None
AgentState = None
initialize_guide = None
get_guide = None
get_guide_async = None

if _HAS_LANGGRAPH:
    from .agent import (
        AgentState,
        Guide,
        get_guide,
        get_guide_async,
        initialize_guide,
    )
else:
    logger.debug("LangGraph not installed - Guide agent not available")


def has_langgraph() -> bool:
    """Check if LangGraph is available."""
    return _HAS_LANGGRAPH


__all__ = [
    "INTENT_KEYWORDS",
    "PERSONALITY_STYLES",
    "AgentState",
    # Requires LangGraph
    "Guide",
    # Always available
    "IntentType",
    "get_guide",
    "get_guide_async",
    "has_langgraph",
    "initialize_guide",
]
