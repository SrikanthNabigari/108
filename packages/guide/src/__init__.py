"""
108 Guide Package

LangGraph-powered conversational agent with personality adaptation.
"""
import logging

logger = logging.getLogger(__name__)

# These are always available (basic types)
from .agent import (
    IntentType,
    INTENT_KEYWORDS,
    PERSONALITY_STYLES,
    _HAS_LANGGRAPH,
)

# These require LangGraph
Guide = None
AgentState = None
initialize_guide = None
get_guide = None
get_guide_async = None

if _HAS_LANGGRAPH:
    from .agent import (
        Guide,
        AgentState,
        initialize_guide,
        get_guide,
        get_guide_async,
    )
else:
    logger.debug("LangGraph not installed - Guide agent not available")


def has_langgraph() -> bool:
    """Check if LangGraph is available."""
    return _HAS_LANGGRAPH


__all__ = [
    # Always available
    "IntentType",
    "INTENT_KEYWORDS",
    "PERSONALITY_STYLES",
    "has_langgraph",
    # Requires LangGraph
    "Guide",
    "AgentState",
    "initialize_guide",
    "get_guide",
    "get_guide_async",
]
