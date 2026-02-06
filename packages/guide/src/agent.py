"""
108 Guide Agent

LangGraph-powered conversational agent with personality adaptation.
This is the brain of the 108 Personal Life Operating System.

Architecture:
    START
      ↓
    [classify_intent] → Determine user intent
      ↓
    [load_context] → Load birth chart, dasha, transits
      ↓
    [check_memory] → Recall relevant memories
      ↓
    [route_by_intent]
      ├─→ [calculate] → Run ephemeris tools (if needed)
      ├─→ [analyze_patterns] → Detect yogas/doshas
      ├─→ [predict] → Make predictions with dasha/transits
      └─→ [general] → Answer general questions
      ↓
    [interpret] → Generate personalized interpretation
      ↓
    [save_memory] → Store important facts
      ↓
    END → Return response
"""

import logging
import os
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from typing_extensions import TypedDict

# Optional dependencies - may not be installed
try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
    from langgraph.graph import END, StateGraph

    _HAS_LANGGRAPH = True
except ImportError:
    _HAS_LANGGRAPH = False
    ChatAnthropic = None
    AIMessage = None
    BaseMessage = None
    HumanMessage = None
    SystemMessage = None
    END = None
    StateGraph = None

# Configure logging
logger = logging.getLogger(__name__)


# =====================
# Type Definitions
# =====================


class IntentType(StrEnum):
    """User intent types."""

    CALCULATE = "calculate"  # User wants calculations (positions, charts)
    ANALYZE = "analyze"  # User wants chart analysis (yogas, doshas)
    PREDICT = "predict"  # User wants predictions
    TIMING = "timing"  # User asks about muhurta/timing
    DASHA = "dasha"  # User asks about dasha periods
    TRANSIT = "transit"  # User asks about transits
    REMEDY = "remedy"  # User asks for remedies
    GENERAL = "general"  # General questions about astrology
    PERSONAL = "personal"  # Personal questions about their chart
    UNKNOWN = "unknown"  # Can't determine intent


class AgentState(TypedDict):
    """State that flows through the agent graph."""

    # Conversation
    messages: Annotated[list[BaseMessage], "Conversation history"]
    user_input: str
    response: str | None

    # User context
    user_id: str
    birth_chart: dict[str, Any] | None
    current_dasha: dict[str, Any] | None
    current_transits: dict[str, Any] | None
    detected_yogas: list[dict[str, Any]]
    detected_doshas: list[dict[str, Any]]

    # Analysis results
    analysis_results: dict[str, Any]

    # Memory
    memories: list[dict[str, Any]]

    # Routing
    intent: IntentType | None
    personality_style: str | None

    # Metadata
    session_id: str
    timestamp: str


# =====================
# Personality Mapping
# =====================

PERSONALITY_STYLES = {
    "aries": {
        "name": "Aries",
        "tone": "direct and action-oriented",
        "approach": "Focus on what they can DO. Be concise and energetic.",
        "avoid": "Long philosophical explanations",
        "keywords": ["action", "movement", "initiative", "courage", "bold"],
    },
    "taurus": {
        "name": "Taurus",
        "tone": "grounded and practical",
        "approach": "Emphasize stability and tangible outcomes. Be patient.",
        "avoid": "Rushing or pushing for quick changes",
        "keywords": ["stability", "tangible", "sensory", "value", "comfort"],
    },
    "gemini": {
        "name": "Gemini",
        "tone": "curious and conversational",
        "approach": "Offer multiple perspectives. Be intellectually engaging.",
        "avoid": "Being too serious or one-dimensional",
        "keywords": ["communication", "curiosity", "variety", "flexibility", "learning"],
    },
    "cancer": {
        "name": "Cancer",
        "tone": "nurturing and supportive",
        "approach": "Acknowledge emotions. Be caring and protective.",
        "avoid": "Being cold or dismissive of feelings",
        "keywords": ["emotion", "nurturing", "family", "protection", "intuition"],
    },
    "leo": {
        "name": "Leo",
        "tone": "confident and inspiring",
        "approach": "Highlight their strengths and potential. Be warm.",
        "avoid": "Being overly critical or diminishing",
        "keywords": ["creativity", "courage", "leadership", "confidence", "warmth"],
    },
    "virgo": {
        "name": "Virgo",
        "tone": "analytical and detailed",
        "approach": "Provide precise information. Be thorough and practical.",
        "avoid": "Vague or imprecise statements",
        "keywords": ["analysis", "precision", "service", "improvement", "detail"],
    },
    "libra": {
        "name": "Libra",
        "tone": "balanced and diplomatic",
        "approach": "Present both sides. Be harmonious and fair.",
        "avoid": "Extreme statements or conflict",
        "keywords": ["balance", "harmony", "relationships", "fairness", "aesthetic"],
    },
    "scorpio": {
        "name": "Scorpio",
        "tone": "deep and transformative",
        "approach": "Go beneath the surface. Be honest and profound.",
        "avoid": "Superficial answers",
        "keywords": ["depth", "transformation", "truth", "intensity", "healing"],
    },
    "sagittarius": {
        "name": "Sagittarius",
        "tone": "philosophical and optimistic",
        "approach": "Connect to bigger picture. Be enthusiastic and wise.",
        "avoid": "Limiting or pessimistic views",
        "keywords": ["philosophy", "expansion", "wisdom", "optimism", "adventure"],
    },
    "capricorn": {
        "name": "Capricorn",
        "tone": "structured and goal-oriented",
        "approach": "Focus on practical steps and long-term success.",
        "avoid": "Unrealistic or whimsical advice",
        "keywords": ["structure", "goals", "responsibility", "time", "achievement"],
    },
    "aquarius": {
        "name": "Aquarius",
        "tone": "innovative and unique",
        "approach": "Offer unconventional insights. Respect their individuality.",
        "avoid": "Conventional or restrictive advice",
        "keywords": ["innovation", "uniqueness", "humanity", "vision", "rebellion"],
    },
    "pisces": {
        "name": "Pisces",
        "tone": "intuitive and compassionate",
        "approach": "Honor their sensitivity. Be gentle and spiritual.",
        "avoid": "Harsh realities without compassion",
        "keywords": ["intuition", "compassion", "spirituality", "dreams", "unity"],
    },
}


# =====================
# Intent Classification
# =====================

INTENT_KEYWORDS = {
    IntentType.CALCULATE: [
        "position",
        "where is",
        "degree",
        "longitude",
        "location",
        "chart",
        "calculate",
    ],
    IntentType.ANALYZE: [
        "yoga",
        "dosha",
        "strength",
        "weakness",
        "pattern",
        "combination",
        "aspect",
    ],
    IntentType.PREDICT: [
        "predict",
        "future",
        "will",
        "when will",
        "happen",
        "outcome",
        "result",
    ],
    IntentType.DASHA: [
        "dasha",
        "mahadasha",
        "antardasha",
        "period",
        "timing",
        "ashtottari",
        "yogini",
        "progression",
    ],
    IntentType.TRANSIT: [
        "transit",
        "gochara",
        "sade sati",
        "saturn",
        "passing through",
    ],
    IntentType.TIMING: [
        "muhurta",
        "good time",
        "auspicious",
        "inauspicious",
        "when should",
        "abhijit",
        "brahma muhurta",
        "eclipse",
    ],
    IntentType.REMEDY: ["remedy", "solution", "what should", "help", "fix", "improve"],
    IntentType.PERSONAL: ["my chart", "my birth", "about me", "tell me about", "my future"],
    IntentType.GENERAL: ["tell me", "explain", "what is", "how does", "define", "mean"],
}


# =====================
# Conversation History Manager
# =====================


class ConversationManager:
    """Manage multi-turn conversation history with automatic pruning."""

    def __init__(self, max_turns: int = 20):
        """
        Initialize conversation manager.

        Args:
            max_turns: Maximum number of turns to retain (each turn = user + assistant)
        """
        self.max_turns = max_turns
        self.history: list[dict[str, Any]] = []

    def add_turn(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a conversation turn.

        Args:
            role: Speaker role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata (intent, timestamp, etc.)
        """
        self.history.append(
            {
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
            }
        )
        # Auto-prune if exceeding limit (keep last max_turns * 2 messages)
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def get_context_window(self, last_n: int = 5) -> list[dict[str, Any]]:
        """Get recent conversation turns for context.

        Args:
            last_n: Number of recent turn pairs to return

        Returns:
            List of recent conversation messages
        """
        return self.history[-(last_n * 2) :]

    def get_summary(self) -> str:
        """Summarize conversation history for context compression.

        Returns:
            Text summary of the conversation topics
        """
        if not self.history:
            return "No conversation history."

        topics = set()
        for msg in self.history:
            intent = msg.get("metadata", {}).get("intent")
            if intent:
                topics.add(intent)

        turn_count = len(self.history) // 2
        topic_str = ", ".join(topics) if topics else "general discussion"
        return f"Conversation with {turn_count} turns covering: {topic_str}"

    def clear(self) -> None:
        """Clear conversation history."""
        self.history = []


# =====================
# Guide Agent
# =====================


class Guide:
    """
    The 108 Guide Agent.

    A LangGraph-powered agent that:
    - Understands user intent via multi-level classification
    - Loads personalized context (birth chart, dasha, transits)
    - Recalls relevant memories from the memory store
    - Routes to appropriate handlers (calculate, analyze, predict, general)
    - Generates personality-adapted responses
    - Learns from every interaction via memory storage
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
        debug: bool = False,
    ):
        """
        Initialize the Guide agent.

        Args:
            model: Claude model to use
            api_key: Anthropic API key (uses env var if not provided)
            debug: Enable debug logging
        """
        if not _HAS_LANGGRAPH:
            raise ImportError(
                "Guide agent requires LangGraph and LangChain. "
                "Install with: uv pip install langgraph langchain-anthropic langchain-core"
            )

        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.debug = debug

        # Memory store (lazy initialized)
        self._store = None
        self._store_connected = False

        # Conversation history manager
        self.conversation_manager = ConversationManager()

        # Initialize LLM
        self.llm = ChatAnthropic(
            model=model,
            api_key=self.api_key,
            temperature=0.7,
        )

        # Build the state machine
        self.graph = self._build_graph()
        self._compiled_graph = self.graph.compile()

        if debug:
            logger.setLevel(logging.DEBUG)

    async def _get_store(self):
        """Get or initialize memory store."""
        if self._store is None:
            try:
                from packages.memory.src import UnifiedMemoryClient

                # Try PostgreSQL first, fall back to mock
                self._store = UnifiedMemoryClient(
                    user_id="system",  # Will be overridden per-request
                    backend=None,  # Auto-detect
                )
                await self._store.initialize()
                self._store_connected = True
                logger.info(f"Memory store connected: {self._store.backend.value}")
            except Exception as e:
                logger.warning(f"Could not connect to memory store: {e}")
                # Fall back to mock
                try:
                    from packages.memory.src import UnifiedMemoryClient

                    self._store = UnifiedMemoryClient(user_id="system", use_mock=True)
                    self._store_connected = True
                    logger.info("Using mock memory store")
                except Exception:
                    self._store_connected = False
        return self._store

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(AgentState)

        # Add all nodes
        graph.add_node("classify_intent", self._classify_intent)
        graph.add_node("load_context", self._load_context)
        graph.add_node("check_memory", self._check_memory)
        graph.add_node("calculate", self._calculate)
        graph.add_node("analyze", self._analyze_patterns)
        graph.add_node("predict", self._make_prediction)
        graph.add_node("general", self._handle_general)
        graph.add_node("interpret", self._interpret)
        graph.add_node("save_memory", self._save_memory)

        # Define edges
        graph.set_entry_point("classify_intent")

        # Linear path through context loading
        graph.add_edge("classify_intent", "load_context")
        graph.add_edge("load_context", "check_memory")

        # Conditional routing based on intent
        graph.add_conditional_edges(
            "check_memory",
            self._route_by_intent,
            {
                IntentType.CALCULATE.value: "calculate",
                IntentType.DASHA.value: "calculate",
                IntentType.TRANSIT.value: "calculate",
                IntentType.ANALYZE.value: "analyze",
                IntentType.PREDICT.value: "predict",
                IntentType.TIMING.value: "predict",
                IntentType.REMEDY.value: "general",
                IntentType.PERSONAL.value: "general",
                IntentType.GENERAL.value: "general",
                IntentType.UNKNOWN.value: "general",
            },
        )

        # Convergence paths
        graph.add_edge("calculate", "interpret")
        graph.add_edge("analyze", "interpret")
        graph.add_edge("predict", "interpret")
        graph.add_edge("general", "interpret")

        # Final steps
        graph.add_edge("interpret", "save_memory")
        graph.add_edge("save_memory", END)

        return graph

    # ===================
    # Graph Nodes
    # ===================

    def _classify_intent(self, state: AgentState) -> AgentState:
        """Classify user's intent from their message."""
        user_input = state["user_input"].lower()

        # Try keyword-based classification first
        intent = IntentType.UNKNOWN
        max_matches = 0

        for intent_type, keywords in INTENT_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in user_input)
            if matches > max_matches:
                max_matches = matches
                intent = intent_type

        # If low confidence, try LLM classification with error handling
        if max_matches < 2:
            try:
                classification_prompt = f"""Classify this user query into one of these intents:
- calculate: User wants planetary positions, chart calculations, degrees
- analyze: User wants chart analysis (yogas, doshas, patterns)
- predict: User wants predictions or future events
- dasha: User asks about dasha periods
- transit: User asks about planetary transits or gochara
- timing: User asks about auspicious timing (muhurta)
- remedy: User asks for remedies or solutions
- personal: User asks personal questions about their chart
- general: General astrology questions
- unknown: Cannot determine

Query: "{state["user_input"]}"

Respond with ONLY the intent name (e.g., "calculate")"""

                response = self.llm.invoke([HumanMessage(content=classification_prompt)])
                intent_text = response.content.strip().lower()

                try:
                    intent = IntentType(intent_text)
                except ValueError:
                    intent = IntentType.GENERAL
            except Exception as e:
                logger.warning(f"LLM classification failed, using keyword result: {e}")
                # Fall back to keyword-based result (already set above)
                if intent == IntentType.UNKNOWN:
                    intent = IntentType.GENERAL

        state["intent"] = intent

        if self.debug:
            logger.debug(f"Classified intent: {intent.value}")

        return state

    def _load_context(self, state: AgentState) -> AgentState:
        """Load user context: birth chart, current dasha, current transits."""
        # If birth chart provided, extract lagna for personality
        if state.get("birth_chart"):
            lagna = state["birth_chart"].get("lagna_rashi", "").lower()
            if lagna and lagna in PERSONALITY_STYLES:
                state["personality_style"] = lagna

            # Calculate current dasha if we have birth data
            if not state.get("current_dasha") and state["birth_chart"].get("moon_longitude"):
                try:
                    from packages.context.src import get_current_dasha

                    birth_dt_str = state["birth_chart"].get("birth_datetime")
                    moon_lon = state["birth_chart"].get("moon_longitude")
                    if birth_dt_str and moon_lon:
                        birth_dt = datetime.fromisoformat(birth_dt_str.replace("Z", "+00:00"))
                        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC
                        dasha = get_current_dasha(birth_dt, moon_lon, datetime.now())
                        state["current_dasha"] = {
                            "mahadasha_lord": dasha["mahadasha"]["lord"],
                            "antardasha_lord": dasha["antardasha"]["lord"],
                            "mahadasha_end": dasha["mahadasha"]["end_date"].isoformat(),
                            "antardasha_end": dasha["antardasha"]["end_date"].isoformat(),
                        }
                except Exception as e:
                    logger.warning(f"Could not calculate dasha: {e}")

            if self.debug:
                logger.debug(f"Loaded birth chart, personality: {state.get('personality_style')}")

        # Initialize empty dicts if not provided
        if not state.get("current_dasha"):
            state["current_dasha"] = {}
        if not state.get("current_transits"):
            state["current_transits"] = {}
        if not state.get("analysis_results"):
            state["analysis_results"] = {}

        return state

    def _check_memory(self, state: AgentState) -> AgentState:
        """Check memory for relevant facts about user.

        Loads user context from memory store if connected.
        For sync execution, memories should be pre-populated via chat() args.
        For async execution via chat_async(), the store is queried directly.
        """
        user_id = state.get("user_id")
        if not user_id:
            if not state.get("memories"):
                state["memories"] = []
            return state

        # Try to load from memory store if connected
        if self._store_connected and self._store:
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Already in async context - data should be pre-loaded
                    # via chat_async() before entering graph
                    pass
                else:
                    # Sync context - load from store
                    store = self._store

                    # Load birth chart if not already provided
                    if not state.get("birth_chart"):
                        chart = loop.run_until_complete(
                            store.search(
                                query="birth data datetime location",
                                category="birth_data",
                                limit=1,
                                user_id=user_id,
                            )
                        )
                        if chart:
                            state["birth_chart"] = chart[0].memory.metadata

                    # Load recent memories
                    if not state.get("memories"):
                        memories = loop.run_until_complete(store.get_all(limit=10, user_id=user_id))
                        state["memories"] = [
                            {
                                "content": m.content,
                                "category": m.category,
                                "importance": m.importance,
                            }
                            for m in memories
                        ]

                    # Load user preferences
                    if not state.get("user_preferences"):
                        prefs = loop.run_until_complete(
                            store.search(
                                query="communication style preference",
                                category="preference",
                                limit=5,
                                user_id=user_id,
                            )
                        )
                        if prefs:
                            state["user_preferences"] = {
                                r.memory.metadata.get(
                                    "preference_type", "unknown"
                                ): r.memory.metadata.get("value")
                                for r in prefs
                            }

                    # Load detected patterns (yogas, doshas)
                    if not state.get("detected_yogas"):
                        yoga_results = loop.run_until_complete(
                            store.search(
                                query="yoga detection pattern",
                                category="yoga",
                                limit=10,
                                user_id=user_id,
                            )
                        )
                        state["detected_yogas"] = [r.memory.metadata for r in yoga_results]

                    if not state.get("detected_doshas"):
                        dosha_results = loop.run_until_complete(
                            store.search(
                                query="dosha detection",
                                category="dosha",
                                limit=5,
                                user_id=user_id,
                            )
                        )
                        state["detected_doshas"] = [r.memory.metadata for r in dosha_results]

            except Exception as e:
                logger.warning(f"Could not load from memory store: {e}")

        # Ensure memories is initialized
        if not state.get("memories"):
            state["memories"] = []

        if self.debug and state["memories"]:
            logger.debug(f"Retrieved {len(state['memories'])} relevant memories")

        return state

    def _route_by_intent(self, state: AgentState) -> str:
        """Route to appropriate handler based on classified intent."""
        intent = state.get("intent", IntentType.GENERAL)

        if intent in [IntentType.CALCULATE, IntentType.DASHA, IntentType.TRANSIT]:
            return "calculate"
        elif intent == IntentType.ANALYZE:
            return "analyze"
        elif intent in [IntentType.PREDICT, IntentType.TIMING]:
            return "predict"
        else:
            return "general"

    def _calculate(self, state: AgentState) -> AgentState:
        """Run calculations for positions, dasha, transits."""
        if self.debug:
            logger.debug(f"Executing calculation for intent: {state['intent'].value}")

        intent = state.get("intent")
        birth_chart = state.get("birth_chart")

        # Perform actual calculations based on intent
        if intent == IntentType.DASHA and birth_chart:
            try:
                from packages.context.src import get_current_dasha, get_mahadasha_sequence

                birth_dt_str = birth_chart.get("birth_datetime")
                moon_lon = birth_chart.get("moon_longitude")
                if birth_dt_str and moon_lon:
                    birth_dt = datetime.fromisoformat(birth_dt_str.replace("Z", "+00:00"))
                    # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

                    # Get current dasha
                    current = get_current_dasha(birth_dt, moon_lon, datetime.now())
                    state["analysis_results"]["current_dasha"] = {
                        "mahadasha": current["mahadasha"]["lord"],
                        "antardasha": current["antardasha"]["lord"],
                        "pratyantardasha": current.get("pratyantardasha", {}).get("lord"),
                    }

                    # Get full sequence
                    sequence = get_mahadasha_sequence(birth_dt, moon_lon)
                    state["analysis_results"]["dasha_sequence"] = [
                        {
                            "lord": p["lord"],
                            "start": p["start_date"].isoformat(),
                            "end": p["end_date"].isoformat(),
                        }
                        for p in sequence[:5]  # Next 5 mahadashas
                    ]
            except Exception as e:
                logger.warning(f"Dasha calculation error: {e}")

        elif intent == IntentType.TRANSIT and birth_chart:
            try:
                from packages.context.src import get_full_transit_analysis, get_transit_positions
                from packages.cosmos.src import RASHI_NAMES, get_julian_day

                moon_sign = birth_chart.get("moon_rashi", "").lower()
                if moon_sign:
                    # Convert moon sign name to rashi index (0-11)
                    rashi_names_lower = [r.lower() for r in RASHI_NAMES]
                    natal_moon_rashi = (
                        rashi_names_lower.index(moon_sign) if moon_sign in rashi_names_lower else 0
                    )

                    # Get current transit positions as {planet: rashi_int}
                    current_jd = get_julian_day(datetime.now())
                    raw_transits = get_transit_positions(current_jd)
                    transit_rashis = {
                        planet: data["rashi_num"] for planet, data in raw_transits.items()
                    }

                    analysis = get_full_transit_analysis(natal_moon_rashi, transit_rashis)
                    summary = analysis.get("summary", {})
                    state["analysis_results"]["transit_analysis"] = {
                        "overall_trend": summary.get("overall_trend", "neutral"),
                        "key_transits": [
                            {
                                "planet": p,
                                "from_moon": t.get("house_from_moon"),
                                "favorable": t.get("is_favorable"),
                            }
                            for p, t in analysis.get("planet_transits", {}).items()
                        ][:5],
                        "sade_sati": analysis.get("sade_sati", {}).get("active", False),
                        "dhaiya": analysis.get("dhaiya", {}).get("active", False),
                    }
            except Exception as e:
                logger.warning(f"Transit analysis error: {e}")

        elif intent == IntentType.CALCULATE and birth_chart:
            # Planetary positions are already in birth_chart
            state["analysis_results"]["positions_available"] = True

            # Add aspect analysis
            try:
                from packages.cosmos.src import RASHI_NAMES as _RASHI_NAMES
                from packages.cosmos.src.aspects import get_all_aspects

                planets_data = birth_chart.get("planets", {})
                lagna_rashi_str = birth_chart.get("lagna_rashi", "aries").lower()
                lagna_names_lower = [r.lower() for r in _RASHI_NAMES]
                lagna_idx = (
                    lagna_names_lower.index(lagna_rashi_str)
                    if lagna_rashi_str in lagna_names_lower
                    else 0
                )

                planet_houses = {}
                for pname, pdata in planets_data.items():
                    rashi_idx = pdata.get("rashi_num", int(pdata.get("longitude", 0) // 30))
                    planet_houses[pname] = ((rashi_idx - lagna_idx) % 12) + 1

                if planet_houses:
                    aspects = get_all_aspects(planet_houses)
                    state["analysis_results"]["aspects"] = aspects
            except Exception as e:
                logger.warning(f"Aspect calculation error: {e}")

        state["analysis_results"]["calculations_performed"] = True
        state["analysis_results"]["calculation_type"] = intent.value if intent else "general"

        return state

    def _analyze_patterns(self, state: AgentState) -> AgentState:
        """Analyze birth chart patterns: yogas, doshas, strengths."""
        if self.debug:
            logger.debug("Analyzing chart patterns")

        birth_chart = state.get("birth_chart")

        if birth_chart and birth_chart.get("planets"):
            try:
                from packages.core.src.constants import Planet, Rashi
                from packages.core.src.models import (
                    BirthChart,
                    BirthData,
                    HouseCusps,
                    PlanetPosition,
                )
                from packages.self.src import DoshaDetector, YogaDetector

                planets_raw = birth_chart.get("planets", {})
                lagna_str = birth_chart.get("lagna_rashi", "aries").lower()

                # Build PlanetPosition dict for BirthChart model
                planet_positions: dict[Planet, PlanetPosition] = {}
                lagna_rashi_idx = (
                    list(Rashi).index(Rashi(lagna_str))
                    if lagna_str in [r.value for r in Rashi]
                    else 0
                )

                for name, data in planets_raw.items():
                    try:
                        planet_enum = Planet(name.lower())
                        rashi_idx = data.get("rashi_num", int(data.get("longitude", 0) // 30))
                        rashi_enum = list(Rashi)[rashi_idx]
                        lon = data.get("longitude", 0.0)
                        nak_info = data.get("nakshatra", "")
                        nak_pada = data.get("nakshatra_pada", 1)
                        nak_lord_str = data.get("nakshatra_lord", name)
                        house = data.get("house", ((rashi_idx - lagna_rashi_idx) % 12) + 1)

                        try:
                            nak_lord = Planet(nak_lord_str.lower())
                        except (ValueError, AttributeError):
                            nak_lord = planet_enum

                        planet_positions[planet_enum] = PlanetPosition(
                            planet=planet_enum,
                            longitude=lon,
                            latitude=data.get("latitude", 0.0),
                            speed=data.get("speed", 0.0),
                            rashi=rashi_enum,
                            rashi_degree=lon % 30,
                            nakshatra=nak_info if isinstance(nak_info, str) else str(nak_info),
                            nakshatra_pada=max(1, min(4, nak_pada)),
                            nakshatra_lord=nak_lord,
                            is_retrograde=data.get("is_retrograde", False),
                            house=house,
                        )
                    except (ValueError, KeyError, IndexError) as e:
                        logger.debug(f"Skipping planet {name}: {e}")
                        continue

                if planet_positions:
                    # Build BirthChart model
                    moon_pos = planet_positions.get(Planet.MOON)
                    moon_rashi = moon_pos.rashi if moon_pos else Rashi(lagna_str)
                    moon_nak = moon_pos.nakshatra if moon_pos else ""

                    houses_data = birth_chart.get("houses", {})
                    cusps = houses_data.get(
                        "cusps", [(lagna_rashi_idx * 30 + i * 30) % 360 for i in range(12)]
                    )

                    chart = BirthChart(
                        user_id=state.get("user_id", "unknown"),
                        birth_data=BirthData(
                            # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC
                            datetime_utc=datetime.fromisoformat(
                                birth_chart.get(
                                    "birth_datetime", datetime.now().isoformat()
                                ).replace("Z", "+00:00")
                            ),
                            latitude=birth_chart.get("latitude", 0.0),
                            longitude=birth_chart.get("longitude", 0.0),
                            timezone=birth_chart.get("timezone", "UTC"),
                            place_name=birth_chart.get("place_name"),
                        ),
                        planets=planet_positions,
                        houses=HouseCusps(
                            ascendant=houses_data.get("ascendant", lagna_rashi_idx * 30.0),
                            mc=houses_data.get("mc", 0.0),
                            cusps=cusps,
                        ),
                        lagna_rashi=Rashi(lagna_str),
                        moon_rashi=moon_rashi,
                        moon_nakshatra=moon_nak,
                        ayanamsa=birth_chart.get("ayanamsa", 23.85),
                        calculated_at=datetime.now(),
                    )

                    # Detect yogas
                    yoga_detector = YogaDetector()
                    detected_yogas = yoga_detector.detect_all_yogas(chart)
                    yoga_dicts = [
                        {
                            "name": y.name,
                            "category": y.category,
                            "strength": y.strength,
                            "involved_planets": y.involved_planets,
                            "description": y.description,
                        }
                        for y in detected_yogas
                    ]
                    state["detected_yogas"] = yoga_dicts
                    state["analysis_results"]["detected_yogas"] = yoga_dicts

                    # Detect doshas
                    dosha_detector = DoshaDetector()
                    detected_doshas = dosha_detector.detect_all(chart)
                    dosha_dicts = [
                        {
                            "name": d.name,
                            "severity": d.severity,
                            "involved_planets": d.involved_planets,
                            "description": d.description,
                            "remedies": d.remedies if hasattr(d, "remedies") else [],
                        }
                        for d in detected_doshas
                    ]
                    state["detected_doshas"] = dosha_dicts
                    state["analysis_results"]["detected_doshas"] = dosha_dicts

                    logger.info(
                        f"Detected {len(detected_yogas)} yogas, {len(detected_doshas)} doshas"
                    )

                    # Calculate Bhava Bala for strongest/weakest houses
                    try:
                        from packages.self.src import StrengthCalculator as SC

                        sc = SC()
                        all_balas = sc.get_all_bhava_balas(chart)
                        ranked = sorted(
                            all_balas.items(),
                            key=lambda x: x[1].get("total", 0),
                            reverse=True,
                        )
                        state["analysis_results"]["strongest_houses"] = [
                            {"house": h, "total": data.get("total", 0)} for h, data in ranked[:3]
                        ]
                        state["analysis_results"]["weakest_houses"] = [
                            {"house": h, "total": data.get("total", 0)} for h, data in ranked[-3:]
                        ]
                    except Exception as e:
                        logger.debug(f"Bhava Bala calculation skipped: {e}")

            except Exception as e:
                logger.warning(f"Pattern analysis error: {e}")

        state["analysis_results"]["patterns_analyzed"] = True
        return state

    def _make_prediction(self, state: AgentState) -> AgentState:
        """Generate predictions based on dasha and transit analysis."""
        if self.debug:
            logger.debug("Generating predictions")

        # Combine dasha and transit information for predictions
        prediction_factors = []

        if state.get("current_dasha"):
            dasha = state["current_dasha"]
            prediction_factors.append(
                f"Current Mahadasha: {dasha.get('mahadasha_lord', 'Unknown')}"
            )
            prediction_factors.append(
                f"Current Antardasha: {dasha.get('antardasha_lord', 'Unknown')}"
            )

        if state.get("analysis_results", {}).get("transit_analysis"):
            transit = state["analysis_results"]["transit_analysis"]
            prediction_factors.append(
                f"Overall transit trend: {transit.get('overall_trend', 'neutral')}"
            )
            if transit.get("sade_sati"):
                prediction_factors.append("Sade Sati is active")

        # Check Ashtottari Dasha if birth data available
        if state.get("birth_chart"):
            try:
                from packages.context.src.ashtottari_dasha import get_current_ashtottari

                bc = state["birth_chart"]
                birth_dt_str = bc.get("birth_datetime")
                moon_nak_num = bc.get("moon_nakshatra_number")
                moon_deg = bc.get("degree_in_nakshatra")

                if birth_dt_str and moon_nak_num and moon_deg:
                    birth_dt = datetime.fromisoformat(birth_dt_str.replace("Z", "+00:00"))
                    # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC
                    ashtottari = get_current_ashtottari(birth_dt, moon_nak_num, moon_deg)
                    prediction_factors.append(
                        f"Ashtottari Dasha: {ashtottari['mahadasha']['lord']}-{ashtottari['antardasha']['lord']}"
                    )
                    state["analysis_results"]["ashtottari_current"] = {
                        "mahadasha": ashtottari["mahadasha"]["lord"],
                        "antardasha": ashtottari["antardasha"]["lord"],
                    }
            except Exception as e:
                logger.debug(f"Ashtottari check skipped: {e}")

            # Check Secondary Progressions
            try:
                from packages.context.src.progressions import get_current_progressions

                bc = state["birth_chart"]
                birth_dt_str = bc.get("birth_datetime")
                lat = bc.get("latitude")
                lon = bc.get("longitude")

                if birth_dt_str and lat and lon:
                    birth_dt = datetime.fromisoformat(birth_dt_str.replace("Z", "+00:00"))
                    # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC
                    prog = get_current_progressions(birth_dt, lat, lon)
                    active_aspects = prog.get("active_aspects", [])
                    if active_aspects:
                        top_aspects = active_aspects[:3]
                        for asp in top_aspects:
                            prediction_factors.append(
                                f"Progressed {asp.get('progressed_planet', '?')} {asp.get('aspect', '?')} natal {asp.get('natal_planet', '?')}"
                            )
                        state["analysis_results"]["progression_aspects"] = top_aspects
            except Exception as e:
                logger.debug(f"Progressions check skipped: {e}")

        state["analysis_results"]["predictions_generated"] = True
        state["analysis_results"]["prediction_factors"] = prediction_factors

        return state

    def _handle_general(self, state: AgentState) -> AgentState:
        """Handle general astrology questions."""
        if self.debug:
            logger.debug(
                f"Handling general query: {state['intent'].value if state['intent'] else 'unknown'}"
            )

        state["analysis_results"]["query_type"] = "general_knowledge"
        return state

    def _interpret(self, state: AgentState) -> AgentState:
        """Generate personalized interpretation using LLM with error handling."""
        # Get personality style
        personality = state.get("personality_style", "unknown")
        style = PERSONALITY_STYLES.get(personality, {})

        # Build system prompt
        system_prompt = self._build_system_prompt(state, style)

        # Add user input to messages
        messages = state.get("messages", [])
        messages.append(HumanMessage(content=state["user_input"]))

        # Call LLM with error handling
        if self.debug:
            logger.debug(f"Calling LLM with personality: {personality}")

        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), *messages])
            state["response"] = response.content
            messages.append(AIMessage(content=response.content))
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"LLM error ({error_type}): {e}")

            # Check for specific error types
            if "rate" in str(e).lower() or "429" in str(e):
                state[
                    "response"
                ] = "I need a moment to gather my thoughts. Please try again shortly."
            elif "connection" in str(e).lower() or "timeout" in str(e).lower():
                state["response"] = (
                    "I'm having trouble connecting right now. " "Let me try a simpler analysis."
                )
            else:
                state["response"] = self._generate_fallback_response(state)

            messages.append(AIMessage(content=state["response"]))

        state["messages"] = messages

        # Track in conversation manager
        self.conversation_manager.add_turn(
            "user",
            state["user_input"],
            metadata={
                "intent": state.get("intent", "unknown").value
                if hasattr(state.get("intent", ""), "value")
                else str(state.get("intent", "unknown"))
            },
        )
        self.conversation_manager.add_turn("assistant", state["response"])

        return state

    def _generate_fallback_response(self, state: AgentState) -> str:
        """Generate a fallback response when LLM is unavailable."""
        intent = state.get("intent")
        context_parts = []

        if state.get("birth_chart"):
            bc = state["birth_chart"]
            context_parts.append(f"Your chart has {bc.get('lagna_rashi', 'an')} Lagna")

        if state.get("detected_yogas"):
            yoga_names = [y.get("name", "Unknown") for y in state["detected_yogas"][:3]]
            context_parts.append(f"Key yogas: {', '.join(yoga_names)}")

        if state.get("current_dasha"):
            d = state["current_dasha"]
            context_parts.append(
                f"Current dasha: {d.get('mahadasha_lord', '?')}-{d.get('antardasha_lord', '?')}"
            )

        context_str = ". ".join(context_parts) if context_parts else ""

        if intent and intent.value in ("calculate", "dasha", "transit"):
            base = "I have your chart data ready for analysis"
        elif intent and intent.value == "analyze":
            base = "Your chart patterns have been detected"
        elif intent and intent.value == "predict":
            base = "I have the dasha and transit data for your prediction"
        else:
            base = "Thank you for your question"

        if context_str:
            return f"{base}. {context_str}. I'll provide a detailed interpretation once my connection is restored."
        return f"{base}. I'll provide a detailed interpretation once my connection is restored."

    def _save_memory(self, state: AgentState) -> AgentState:
        """Save important facts from conversation to memory.

        Saves conversation turns and extracted memories to the store.
        For async execution via chat_async(), saving happens after graph completes.
        For sync execution with a connected store, saves directly.
        """
        user_id = state.get("user_id")
        if not user_id:
            return state

        if self._store_connected and self._store:
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Async context - saving handled in chat_async() after graph
                    pass
                else:
                    store = self._store

                    # Save user message
                    user_input = state.get("user_input", "")
                    if user_input:
                        loop.run_until_complete(
                            store.add(
                                content=f"User query: {user_input[:500]}",
                                category="interaction",
                                metadata={
                                    "role": "user",
                                    "session_id": state.get("session_id", ""),
                                    "intent": state.get("intent", "unknown")
                                    if isinstance(state.get("intent"), str)
                                    else state.get("intent", "unknown").value
                                    if state.get("intent")
                                    else "unknown",
                                },
                                importance=0.3,
                                user_id=user_id,
                            )
                        )

                    # Save assistant response
                    response = state.get("response", "")
                    if response:
                        loop.run_until_complete(
                            store.add(
                                content=f"Guide response: {response[:500]}",
                                category="interaction",
                                metadata={
                                    "role": "assistant",
                                    "session_id": state.get("session_id", ""),
                                },
                                importance=0.3,
                                user_id=user_id,
                            )
                        )

                    # Save any extracted memories
                    extracted = state.get("extracted_memories", [])
                    for memory in extracted:
                        loop.run_until_complete(
                            store.add(
                                content=memory.get("content", ""),
                                category=memory.get("category", "fact"),
                                metadata=memory.get("metadata", {}),
                                importance=memory.get("importance", 0.5),
                                user_id=user_id,
                            )
                        )

            except Exception as e:
                logger.warning(f"Could not save to memory store: {e}")

        if self.debug:
            logger.debug(f"Memory save completed for user {state['user_id']}")

        return state

    # ===================
    # Helper Methods
    # ===================

    def _build_system_prompt(self, state: AgentState, style: dict[str, str]) -> str:
        """Build personality-adapted system prompt."""
        context_str = self._format_context(state)

        prompt = f"""You are the 108 Guide, a wise and compassionate Vedic astrology companion.

Your role is to help users understand their birth chart, navigate dasha periods, and plan for their future using Vedic astrology wisdom.

=== PERSONALITY ADAPTATION ===
The user has a {style.get("name", "Unknown")} Lagna.

Communication Style:
- Tone: {style.get("tone", "balanced and helpful")}
- Approach: {style.get("approach", "Be supportive and informative")}
- Avoid: {style.get("avoid", "Nothing specific")}

Emphasize these themes in your response: {", ".join(style.get("keywords", ["wisdom", "insight"]))}

=== USER CONTEXT ===
{context_str}

=== GUIDELINES ===
1. Be warm, insightful, and practical in your guidance
2. Connect to the user's specific chart when relevant
3. Provide actionable advice aligned with their Lagna nature
4. Reference dasha periods, transits, and yogas when they apply
5. Suggest remedies when appropriate (mantras, gemstones, rituals)
6. Always explain astrology concepts in accessible language
7. Remember that the user may be new to astrology - educate gently

=== TONE ===
Be the user's trusted guide on their life journey. Combine Vedic wisdom with compassion."""

        return prompt

    def _format_context(self, state: AgentState) -> str:
        """Format user context for inclusion in system prompt."""
        parts = []

        # Birth chart info
        if state.get("birth_chart"):
            bc = state["birth_chart"]
            parts.append("Birth Chart:")
            parts.append(f"  - Ascendant (Lagna): {bc.get('lagna_rashi', 'Unknown')}")
            parts.append(f"  - Moon Sign: {bc.get('moon_rashi', 'Unknown')}")
            parts.append(f"  - Moon Nakshatra: {bc.get('moon_nakshatra', 'Unknown')}")

        # Current dasha
        if state.get("current_dasha") and state["current_dasha"]:
            d = state["current_dasha"]
            dasha_str = f"Current Dasha: {d.get('mahadasha_lord', '?')}"
            if d.get("antardasha_lord"):
                dasha_str += f" - {d.get('antardasha_lord')}"
            parts.append(dasha_str)

        # Analysis results
        results = state.get("analysis_results") or {}

        if results.get("current_dasha"):
            cd = results["current_dasha"]
            parts.append(f"Dasha Period: {cd.get('mahadasha')}-{cd.get('antardasha')}")

        if results.get("transit_analysis"):
            ta = results["transit_analysis"]
            parts.append(f"Transit Trend: {ta.get('overall_trend', 'neutral')}")
            if ta.get("sade_sati"):
                parts.append("Note: Sade Sati is currently active")

        if results.get("prediction_factors"):
            parts.append("Prediction factors:")
            for factor in results["prediction_factors"]:
                parts.append(f"  - {factor}")

        # Detected yogas
        if state.get("detected_yogas"):
            yogas = [y.get("name", "Unknown") for y in state["detected_yogas"][:3]]
            parts.append(f"Key Yogas: {', '.join(yogas)}")

        # Detected doshas
        if state.get("detected_doshas"):
            doshas = [d.get("name", "Unknown") for d in state["detected_doshas"]]
            parts.append(f"Important Doshas: {', '.join(doshas)}")

        # Bhava Bala (house strengths)
        if results.get("strongest_houses"):
            strong = results["strongest_houses"]
            labels = ", ".join("H{}({})".format(h["house"], h["total"]) for h in strong)
            parts.append(f"Strongest houses: {labels}")

        if results.get("weakest_houses"):
            weak = results["weakest_houses"]
            labels = ", ".join("H{}({})".format(h["house"], h["total"]) for h in weak)
            parts.append(f"Weakest houses: {labels}")

        # Ashtottari
        if results.get("ashtottari_current"):
            ac = results["ashtottari_current"]
            parts.append(f"Ashtottari Dasha: {ac.get('mahadasha')}-{ac.get('antardasha')}")

        # Progressions
        if results.get("progression_aspects"):
            prog_aspects = results["progression_aspects"]
            parts.append(f"Active progressed aspects: {len(prog_aspects)}")

        # Memories
        if state.get("memories"):
            parts.append(
                f"Relevant memories: {len(state['memories'])} facts from past interactions"
            )

        if not parts:
            parts.append("No specific context loaded - this may be a new user")

        return "\n".join(parts)

    # ===================
    # Public API
    # ===================

    def chat(
        self,
        user_input: str,
        user_id: str,
        session_id: str | None = None,
        birth_chart: dict[str, Any] | None = None,
        current_dasha: dict[str, Any] | None = None,
        current_transits: dict[str, Any] | None = None,
        detected_yogas: list[dict[str, Any]] | None = None,
        detected_doshas: list[dict[str, Any]] | None = None,
        memories: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Process a user message and return response (sync version).

        Args:
            user_input: User's message
            user_id: User identifier
            session_id: Session identifier (auto-generated if not provided)
            birth_chart: Birth chart data (optional)
            current_dasha: Current dasha info (optional)
            current_transits: Current transit info (optional)
            detected_yogas: List of detected yogas (optional)
            detected_doshas: List of detected doshas (optional)
            memories: Retrieved memories (optional)

        Returns:
            Dictionary with response and metadata
        """
        # Initialize state
        state: AgentState = {
            "messages": [],
            "user_input": user_input,
            "response": None,
            "user_id": user_id,
            "birth_chart": birth_chart,
            "current_dasha": current_dasha,
            "current_transits": current_transits,
            "detected_yogas": detected_yogas or [],
            "detected_doshas": detected_doshas or [],
            "analysis_results": {},
            "memories": memories or [],
            "intent": None,
            "personality_style": None,
            "session_id": session_id or f"session_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
        }

        # Run through graph
        if self.debug:
            logger.debug(f"Processing query from user {user_id}: {user_input[:50]}...")

        final_state = self._compiled_graph.invoke(state)

        return {
            "response": final_state["response"],
            "intent": final_state["intent"].value if final_state["intent"] else "unknown",
            "personality_style": final_state["personality_style"],
            "session_id": final_state["session_id"],
            "timestamp": final_state["timestamp"],
            "analysis_results": final_state.get("analysis_results", {}),
        }

    async def chat_async(
        self,
        user_input: str,
        user_id: str,
        session_id: str | None = None,
        birth_chart: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process a user message with full async support (primary async method).

        This version:
        - Loads birth chart from database if not provided
        - Retrieves relevant memories
        - Runs the LangGraph state machine via ainvoke (non-blocking)
        - Saves conversation to memory store

        Args:
            user_input: User's message
            user_id: User identifier
            session_id: Session identifier
            birth_chart: Birth chart data (loads from DB if not provided)

        Returns:
            Dictionary with response and metadata
        """
        memory_client = await self._get_store()

        # Load birth chart from memory if not provided
        if not birth_chart and self._store_connected:
            try:
                birth_results = await memory_client.search(
                    query="birth data datetime location",
                    category="birth_data",
                    limit=1,
                    user_id=user_id,
                )
                if birth_results:
                    birth_chart = birth_results[0].memory.metadata
                    if self.debug:
                        logger.debug(f"Loaded birth data from memory for {user_id}")
            except Exception as e:
                logger.warning(f"Could not load birth chart: {e}")

        # Load detected patterns from memory
        detected_yogas = []
        detected_doshas = []
        if self._store_connected:
            try:
                yoga_results = await memory_client.search(
                    query="yoga detection pattern", category="yoga", limit=10, user_id=user_id
                )
                for r in yoga_results:
                    detected_yogas.append(r.memory.metadata)

                dosha_results = await memory_client.search(
                    query="dosha detection mangal kaal sarp",
                    category="dosha",
                    limit=5,
                    user_id=user_id,
                )
                for r in dosha_results:
                    detected_doshas.append(r.memory.metadata)
            except Exception as e:
                logger.warning(f"Could not load patterns: {e}")

        # Get relevant context for the query
        memories = []
        if self._store_connected:
            try:
                context = await memory_client.get_context_for_query(
                    query=user_input, limit=10, user_id=user_id
                )
                memories = context.get("memories", [])
            except Exception as e:
                logger.warning(f"Could not load memories: {e}")

        # Build initial state with pre-loaded memory data
        session = session_id or f"session_{datetime.now().timestamp()}"
        state: AgentState = {
            "messages": [],
            "user_input": user_input,
            "response": None,
            "user_id": user_id,
            "birth_chart": birth_chart,
            "current_dasha": None,
            "current_transits": None,
            "detected_yogas": detected_yogas,
            "detected_doshas": detected_doshas,
            "analysis_results": {},
            "memories": memories,
            "intent": None,
            "personality_style": None,
            "session_id": session,
            "timestamp": datetime.now().isoformat(),
        }

        # Run through graph asynchronously (non-blocking)
        if self.debug:
            logger.debug(f"Processing async query from user {user_id}: {user_input[:50]}...")

        final_state = await self._compiled_graph.ainvoke(state)

        result = {
            "response": final_state["response"],
            "intent": final_state["intent"].value if final_state["intent"] else "unknown",
            "personality_style": final_state["personality_style"],
            "session_id": final_state["session_id"],
            "timestamp": final_state["timestamp"],
            "analysis_results": final_state.get("analysis_results", {}),
        }

        # Save conversation to memory store (post-graph)
        if self._store_connected and result.get("response"):
            try:
                conversation_content = (
                    f"User ({result['intent']}): {user_input[:200]}\n"
                    f"Guide response: {result['response'][:200]}..."
                )
                await memory_client.add(
                    content=conversation_content,
                    category="interaction",
                    metadata={
                        "session_id": result["session_id"],
                        "intent": result["intent"],
                        "timestamp": result["timestamp"],
                    },
                    importance=0.4,
                    user_id=user_id,
                )

                # Save higher-importance memory for analytical queries
                if result["intent"] in ["predict", "analyze", "remedy"]:
                    await memory_client.add(
                        content=f"User asked about {result['intent']}: {user_input[:100]}",
                        category="event",
                        metadata={
                            "intent": result["intent"],
                            "timestamp": result["timestamp"],
                        },
                        importance=0.6,
                        user_id=user_id,
                    )
            except Exception as e:
                logger.warning(f"Could not save to memory: {e}")

        return result

    def get_intent(self, user_input: str) -> IntentType:
        """Get the intent of a user message without processing."""
        state: AgentState = {
            "messages": [],
            "user_input": user_input,
            "response": None,
            "user_id": "temp",
            "birth_chart": None,
            "current_dasha": None,
            "current_transits": None,
            "detected_yogas": [],
            "detected_doshas": [],
            "analysis_results": {},
            "memories": [],
            "intent": None,
            "personality_style": None,
            "session_id": "temp",
            "timestamp": datetime.now().isoformat(),
        }

        state = self._classify_intent(state)
        return state["intent"]


# =====================
# Singleton & Utilities
# =====================

_guide: Guide | None = None


def initialize_guide(
    model: str = "claude-sonnet-4-20250514",
    api_key: str | None = None,
    debug: bool = False,
) -> Guide:
    """
    Initialize the global Guide agent.

    Args:
        model: Claude model to use
        api_key: Anthropic API key
        debug: Enable debug logging

    Returns:
        Initialized Guide instance
    """
    global _guide
    _guide = Guide(model=model, api_key=api_key, debug=debug)
    return _guide


def get_guide() -> Guide:
    """
    Get the global Guide agent instance.

    Raises:
        RuntimeError: If guide not initialized

    Returns:
        Guide instance
    """
    global _guide
    if _guide is None:
        raise RuntimeError("Guide not initialized. Call initialize_guide() first.")
    return _guide


async def get_guide_async(
    model: str = "claude-sonnet-4-20250514",
    api_key: str | None = None,
    debug: bool = False,
) -> Guide:
    """
    Get or initialize the Guide agent with async support.

    Args:
        model: Claude model to use
        api_key: Anthropic API key
        debug: Enable debug logging

    Returns:
        Guide instance with connected memory store
    """
    global _guide
    if _guide is None:
        _guide = Guide(model=model, api_key=api_key, debug=debug)

    # Ensure store is connected
    await _guide._get_store()

    return _guide
