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
    IntentType.DASHA: ["dasha", "mahadasha", "antardasha", "period", "timing"],
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
    ],
    IntentType.REMEDY: ["remedy", "solution", "what should", "help", "fix", "improve"],
    IntentType.PERSONAL: ["my chart", "my birth", "about me", "tell me about", "my future"],
    IntentType.GENERAL: ["tell me", "explain", "what is", "how does", "define", "mean"],
}


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

        # If low confidence, use LLM
        if max_matches < 2:
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
                        if birth_dt.tzinfo:
                            birth_dt = birth_dt.replace(tzinfo=None)
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
        """Check memory for relevant facts about user."""
        # Memory retrieval is async, we'll do it in the async chat method
        # For sync execution, memories should be passed in
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
                    if birth_dt.tzinfo:
                        birth_dt = birth_dt.replace(tzinfo=None)

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
                from packages.context.src import get_full_transit_analysis

                moon_sign = birth_chart.get("moon_rashi", "").lower()
                if moon_sign:
                    analysis = get_full_transit_analysis(moon_sign, datetime.now())
                    state["analysis_results"]["transit_analysis"] = {
                        "overall_trend": analysis.get("overall_trend"),
                        "key_transits": analysis.get("key_transits", [])[:5],
                        "sade_sati": analysis.get("sade_sati_active", False),
                    }
            except Exception as e:
                logger.warning(f"Transit analysis error: {e}")

        elif intent == IntentType.CALCULATE and birth_chart:
            # Planetary positions are already in birth_chart
            state["analysis_results"]["positions_available"] = True

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
                from packages.self.src import DoshaDetector, YogaDetector

                # Build minimal chart structure for detectors
                birth_chart.get("planets", {})
                birth_chart.get("lagna_rashi", "aries").lower()

                # Detect yogas
                YogaDetector()
                # Note: This requires proper BirthChart object, simplified for now
                state["analysis_results"]["yoga_detection_attempted"] = True

                # Detect doshas
                DoshaDetector()
                state["analysis_results"]["dosha_detection_attempted"] = True

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
        """Generate personalized interpretation using LLM."""
        # Get personality style
        personality = state.get("personality_style", "unknown")
        style = PERSONALITY_STYLES.get(personality, {})

        # Build system prompt
        system_prompt = self._build_system_prompt(state, style)

        # Add user input to messages
        messages = state.get("messages", [])
        messages.append(HumanMessage(content=state["user_input"]))

        # Call LLM
        if self.debug:
            logger.debug(f"Calling LLM with personality: {personality}")

        response = self.llm.invoke([SystemMessage(content=system_prompt), *messages])

        state["response"] = response.content
        messages.append(AIMessage(content=response.content))
        state["messages"] = messages

        return state

    def _save_memory(self, state: AgentState) -> AgentState:
        """Save important facts from conversation to memory."""
        # Memory saving is async, we'll do it in the async chat method
        if self.debug:
            logger.debug(f"Memory would be saved for user {state['user_id']}")

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
        if state.get("analysis_results"):
            results = state["analysis_results"]

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
        Process a user message with full async support.

        This version:
        - Loads birth chart from database if not provided
        - Retrieves relevant memories
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
                # Search for birth data in memory
                birth_results = await memory_client.search(
                    query="birth data datetime location",
                    category="birth_data",
                    limit=1,
                    user_id=user_id,
                )
                if birth_results:
                    birth_memory = birth_results[0].memory
                    birth_chart = birth_memory.metadata
                    if self.debug:
                        logger.debug(f"Loaded birth data from memory for {user_id}")
            except Exception as e:
                logger.warning(f"Could not load birth chart: {e}")

        # Load detected patterns from memory
        detected_yogas = []
        detected_doshas = []
        if self._store_connected:
            try:
                # Search for yogas
                yoga_results = await memory_client.search(
                    query="yoga detection pattern", category="yoga", limit=10, user_id=user_id
                )
                for r in yoga_results:
                    detected_yogas.append(r.memory.metadata)

                # Search for doshas
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

        # Run sync chat with loaded context
        result = self.chat(
            user_input=user_input,
            user_id=user_id,
            session_id=session_id,
            birth_chart=birth_chart,
            detected_yogas=detected_yogas,
            detected_doshas=detected_doshas,
            memories=memories,
        )

        # Save conversation to memory store
        if self._store_connected and result.get("response"):
            try:
                # Save conversation as interaction memory
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

                # Save as a higher-importance memory if it contains important information
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
