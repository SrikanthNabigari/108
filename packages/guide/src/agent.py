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

from typing import TypedDict, List, Dict, Any, Optional, Literal, Annotated
from datetime import datetime
from enum import Enum
import json
import logging

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import Tool

# Configure logging
logger = logging.getLogger(__name__)


# =====================
# Type Definitions
# =====================

class IntentType(str, Enum):
    """User intent types."""
    CALCULATE = "calculate"      # User wants calculations (positions, charts)
    ANALYZE = "analyze"          # User wants chart analysis (yogas, doshas)
    PREDICT = "predict"          # User wants predictions
    TIMING = "timing"            # User asks about muhurta/timing
    DASHA = "dasha"              # User asks about dasha periods
    TRANSIT = "transit"          # User asks about transits
    REMEDY = "remedy"            # User asks for remedies
    GENERAL = "general"          # General questions about astrology
    PERSONAL = "personal"        # Personal questions about their chart
    UNKNOWN = "unknown"          # Can't determine intent


class AgentState(TypedDict):
    """State that flows through the agent graph."""
    # Conversation
    messages: Annotated[List[BaseMessage], "Conversation history"]
    user_input: str
    response: Optional[str]

    # User context
    user_id: str
    birth_chart: Optional[Dict[str, Any]]
    current_dasha: Optional[Dict[str, Any]]
    current_transits: Optional[Dict[str, Any]]
    detected_yogas: List[Dict[str, Any]]
    detected_doshas: List[Dict[str, Any]]

    # Analysis results
    analysis_results: Dict[str, Any]

    # Memory
    memories: List[Dict[str, Any]]

    # Routing
    intent: Optional[IntentType]
    personality_style: Optional[str]

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
    IntentType.CALCULATE: ["position", "where is", "degree", "longitude", "location", "chart", "calculate"],
    IntentType.ANALYZE: ["yoga", "dosha", "strength", "weakness", "pattern", "combination", "aspect"],
    IntentType.PREDICT: ["predict", "future", "will", "when will", "happen", "outcome", "result"],
    IntentType.DASHA: ["dasha", "mahadasha", "antardasha", "period", "timing"],
    IntentType.TRANSIT: ["transit", "gochara", "sade sati", "saturn", "passing through"],
    IntentType.TIMING: ["muhurta", "good time", "auspicious", "inauspicious", "when should"],
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
    - Recalls relevant memories from Mem0
    - Routes to appropriate handlers (calculate, analyze, predict, general)
    - Generates personality-adapted responses
    - Learns from every interaction via memory storage

    The agent operates as a state machine with the following nodes:
    - classify_intent: Determine what user is asking
    - load_context: Fetch user's birth chart and current planetary positions
    - check_memory: Retrieve relevant past facts
    - route_by_intent: Conditional routing to specialist nodes
    - calculate: Run ephemeris calculations via MCP
    - analyze_patterns: Detect yogas and doshas
    - predict: Generate predictions using dasha/transit analysis
    - general: Answer general questions
    - interpret: Build personalized response using LLM
    - save_memory: Store important facts for future reference
    """

    def __init__(
        self,
        model: str = "claude-opus-4-5-20251101",
        api_key: Optional[str] = None,
        debug: bool = False
    ):
        """
        Initialize the Guide agent.

        Args:
            model: Claude model to use (default: latest Opus)
            api_key: Anthropic API key (uses env var if not provided)
            debug: Enable debug logging
        """
        self.model = model
        self.api_key = api_key
        self.debug = debug

        # Initialize LLM
        self.llm = ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=0.7,
        )

        # Build the state machine
        self.graph = self._build_graph()
        self._compiled_graph = self.graph.compile()

        if debug:
            logger.setLevel(logging.DEBUG)

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.

        Graph Structure:
            START
              ↓
            classify_intent
              ↓
            load_context
              ↓
            check_memory
              ↓
            [route_by_intent]
              ├─→ calculate ──┐
              ├─→ analyze ────┤
              ├─→ predict ────┼→ interpret
              └─→ general ────┤
              ↓
            save_memory
              ↓
            END
        """
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
            }
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
        """
        Classify user's intent from their message.

        Uses multi-level classification:
        1. Keyword matching for quick classification
        2. LLM classification for ambiguous cases

        Args:
            state: Current agent state

        Returns:
            Updated state with intent classified
        """
        user_input = state["user_input"].lower()

        # Try keyword-based classification first
        intent = IntentType.UNKNOWN
        max_matches = 0

        for intent_type, keywords in INTENT_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in user_input)
            if matches > max_matches:
                max_matches = matches
                intent = intent_type

        # If low confidence or ambiguous, use LLM
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

Query: "{state['user_input']}"

Respond with ONLY the intent name (e.g., "calculate")"""

            response = self.llm.invoke([HumanMessage(content=classification_prompt)])
            intent_text = response.content.strip().lower()

            try:
                intent = IntentType(intent_text)
            except ValueError:
                intent = IntentType.GENERAL

        state["intent"] = intent

        if self.debug:
            logger.debug(f"Classified intent: {intent.value} (confidence: {max_matches}/3)")

        return state

    def _load_context(self, state: AgentState) -> AgentState:
        """
        Load user context: birth chart, current dasha, current transits.

        In production, this would:
        - Query database for user's birth chart
        - Calculate current dasha using ephemeris
        - Get current planetary transits
        - Detect current yogas and doshas

        Args:
            state: Current agent state

        Returns:
            Updated state with context loaded
        """
        # If birth chart provided, extract lagna for personality
        if state.get("birth_chart"):
            lagna = state["birth_chart"].get("lagna_rashi", "").lower()
            if lagna and lagna in PERSONALITY_STYLES:
                state["personality_style"] = lagna

            if self.debug:
                logger.debug(f"Loaded birth chart for user {state['user_id']}")
                logger.debug(f"Personality style: {state.get('personality_style', 'unknown')}")

        # In production: Load current dasha, transits, etc.
        # For now, initialize empty dicts
        if not state.get("current_dasha"):
            state["current_dasha"] = {}
        if not state.get("current_transits"):
            state["current_transits"] = {}
        if not state.get("analysis_results"):
            state["analysis_results"] = {}

        return state

    def _check_memory(self, state: AgentState) -> AgentState:
        """
        Check memory for relevant facts about user.

        In production, this would query Mem0 to retrieve:
        - Previously mentioned facts about their life
        - Past predictions and their accuracy
        - Remedies recommended before
        - Patterns the user has noticed

        Args:
            state: Current agent state

        Returns:
            Updated state with relevant memories
        """
        user_id = state["user_id"]
        query = state["user_input"]

        # In production:
        # memories = await mem0.search(user_id, query, limit=5)
        # state["memories"] = memories

        # For now, initialize empty list
        state["memories"] = []

        if self.debug and state["memories"]:
            logger.debug(f"Retrieved {len(state['memories'])} relevant memories")

        return state

    def _route_by_intent(self, state: AgentState) -> str:
        """
        Route to appropriate handler based on classified intent.

        Args:
            state: Current agent state

        Returns:
            Node name to route to
        """
        intent = state.get("intent", IntentType.GENERAL)

        # Consolidate intents to handler nodes
        if intent in [IntentType.CALCULATE, IntentType.DASHA, IntentType.TRANSIT]:
            return "calculate"
        elif intent == IntentType.ANALYZE:
            return "analyze"
        elif intent in [IntentType.PREDICT, IntentType.TIMING]:
            return "predict"
        else:
            return "general"

    def _calculate(self, state: AgentState) -> AgentState:
        """
        Run calculations via MCP ephemeris tools.

        Handles requests for:
        - Planetary positions
        - Dasha calculations
        - Transit analysis
        - Chart calculations

        In production, this would call MCP tools like:
        - planetary_positions(datetime, lat, lon)
        - current_dasha(birth_datetime, moon_longitude, query_datetime)
        - houses(datetime, lat, lon, house_system)
        - navamsha(longitude)
        - etc.

        Args:
            state: Current agent state

        Returns:
            Updated state with calculation results
        """
        if self.debug:
            logger.debug(f"Executing calculation for intent: {state['intent'].value}")

        # Store that calculations were performed
        state["analysis_results"]["calculations_performed"] = True
        state["analysis_results"]["calculation_type"] = state["intent"].value

        # In production, actual MCP tool calls would happen here
        # For now, mark as calculated

        return state

    def _analyze_patterns(self, state: AgentState) -> AgentState:
        """
        Analyze birth chart patterns: yogas, doshas, strengths.

        In production, this would:
        - Call yoga detection via MCP
        - Call dosha checking via MCP
        - Perform shadbala (planetary strength) analysis
        - Identify key patterns

        Args:
            state: Current agent state

        Returns:
            Updated state with analysis results
        """
        if self.debug:
            logger.debug("Analyzing chart patterns (yogas, doshas)")

        # Mark that analysis was performed
        state["analysis_results"]["patterns_analyzed"] = True

        # In production:
        # yogas = await mcp.detect_yogas(birth_chart)
        # doshas = await mcp.check_doshas(birth_chart)
        # state["detected_yogas"] = yogas
        # state["detected_doshas"] = doshas

        return state

    def _make_prediction(self, state: AgentState) -> AgentState:
        """
        Generate predictions based on dasha and transit analysis.

        Combines:
        - Current dasha period and its themes
        - Transit analysis (gochara)
        - Key upcoming transitions
        - Timing advice

        In production, this would:
        - Use current_dasha to understand the lifecycle theme
        - Analyze transit strength via ashtakavarga
        - Check for special transits (Sade Sati, Dhaiya)
        - Generate timing predictions

        Args:
            state: Current agent state

        Returns:
            Updated state with prediction results
        """
        if self.debug:
            logger.debug("Generating predictions from dasha/transit analysis")

        state["analysis_results"]["predictions_generated"] = True

        # In production:
        # dasha_lord = state["current_dasha"].get("mahadasha_lord")
        # predictions = await get_dasha_predictions(dasha_lord)
        # state["analysis_results"]["dasha_predictions"] = predictions

        return state

    def _handle_general(self, state: AgentState) -> AgentState:
        """
        Handle general astrology questions.

        For intents like:
        - General astrology education
        - Personal advice without heavy calculation
        - Remedy suggestions

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        if self.debug:
            logger.debug(f"Handling general query: {state['intent'].value}")

        state["analysis_results"]["query_type"] = "general_knowledge"

        return state

    def _interpret(self, state: AgentState) -> AgentState:
        """
        Generate personalized interpretation using LLM.

        This is where the magic happens:
        1. Get user's personality style from lagna
        2. Build context-aware system prompt
        3. Include birth chart, dasha, transits, memories
        4. Call Claude with personality-adapted instructions
        5. Return personalized response

        Args:
            state: Current agent state

        Returns:
            Updated state with response
        """
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

        response = self.llm.invoke(
            [SystemMessage(content=system_prompt)] + messages
        )

        state["response"] = response.content
        messages.append(AIMessage(content=response.content))
        state["messages"] = messages

        return state

    def _save_memory(self, state: AgentState) -> AgentState:
        """
        Save important facts from conversation to memory.

        Extracts and stores:
        - Key facts about user's life
        - Patterns they've noticed
        - Remedies suggested
        - Predictions made

        In production, this would call Mem0 API.

        Args:
            state: Current agent state

        Returns:
            Updated state
        """
        user_id = state["user_id"]

        # Build memory entry
        memory_content = {
            "timestamp": state["timestamp"],
            "user_input": state["user_input"],
            "response": state["response"],
            "intent": state["intent"].value if state["intent"] else "unknown",
            "birth_chart": state.get("birth_chart"),
        }

        # In production: Save to Mem0
        # await mem0.add_memory(
        #     user_id=user_id,
        #     memory=json.dumps(memory_content)
        # )

        if self.debug:
            logger.debug(f"Memory saved for user {user_id}")

        return state

    # ===================
    # Helper Methods
    # ===================

    def _build_system_prompt(self, state: AgentState, style: Dict[str, str]) -> str:
        """
        Build personality-adapted system prompt.

        Args:
            state: Current agent state
            style: Personality style dict

        Returns:
            System prompt string
        """
        context_str = self._format_context(state)

        prompt = f"""You are the 108 Guide, a wise and compassionate Vedic astrology companion.

Your role is to help users understand their birth chart, navigate dasha periods, and plan for their future using Vedic astrology wisdom.

=== PERSONALITY ADAPTATION ===
The user has a {style.get('name', 'Unknown')} Lagna.

Communication Style:
- Tone: {style.get('tone', 'balanced and helpful')}
- Approach: {style.get('approach', 'Be supportive and informative')}
- Avoid: {style.get('avoid', 'Nothing specific')}

Emphasize these themes in your response: {', '.join(style.get('keywords', ['wisdom', 'insight']))}

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
        """
        Format user context for inclusion in system prompt.

        Args:
            state: Current agent state

        Returns:
            Formatted context string
        """
        parts = []

        # Birth chart info
        if state.get("birth_chart"):
            bc = state["birth_chart"]
            parts.append(f"Birth Chart:")
            parts.append(f"  - Ascendant (Lagna): {bc.get('lagna_rashi', 'Unknown')}")
            parts.append(f"  - Moon Sign: {bc.get('moon_rashi', 'Unknown')}")
            parts.append(f"  - Moon Nakshatra: {bc.get('moon_nakshatra', 'Unknown')}")

            if bc.get("lagna_degree"):
                parts.append(f"  - Lagna Degree: {bc['lagna_degree']:.2f}°")

        # Current dasha
        if state.get("current_dasha") and state["current_dasha"]:
            d = state["current_dasha"]
            dasha_str = f"Current Dasha: {d.get('mahadasha_lord', '?')}"
            if d.get("antardasha_lord"):
                dasha_str += f" - {d.get('antardasha_lord')}"
            if d.get("years_remaining"):
                dasha_str += f" ({d.get('years_remaining', '?')} years remaining)"
            parts.append(dasha_str)

        # Current transits
        if state.get("current_transits") and state["current_transits"]:
            parts.append(f"Notable Transits: {state['current_transits'].get('summary', 'Check transits for timing')}")

        # Detected yogas
        if state.get("detected_yogas"):
            yogas = [y.get("name", "Unknown") for y in state["detected_yogas"][:3]]
            parts.append(f"Key Yogas: {', '.join(yogas)}")

        # Detected doshas
        if state.get("detected_doshas"):
            doshas = [d.get("name", "Unknown") for d in state["detected_doshas"]]
            parts.append(f"Important Doshas: {', '.join(doshas)}")

        # Analysis results summary
        if state.get("analysis_results"):
            results = state["analysis_results"]
            if results.get("calculations_performed"):
                parts.append(f"Calculations completed for: {results.get('calculation_type', 'various')}")
            if results.get("patterns_analyzed"):
                parts.append("Chart patterns have been analyzed")
            if results.get("predictions_generated"):
                parts.append("Predictions based on current dasha/transits are available")

        # Memories
        if state.get("memories"):
            parts.append(f"Relevant memories retrieved: {len(state['memories'])} facts from past interactions")

        if not parts:
            parts.append("No specific context loaded - this may be a new user or general question")

        return "\n".join(parts)

    def get_personality_description(self, lagna: str) -> Dict[str, str]:
        """
        Get personality description for a given lagna.

        Args:
            lagna: Lagna/Ascendant sign (e.g., "aries", "taurus")

        Returns:
            Personality style dictionary
        """
        return PERSONALITY_STYLES.get(lagna.lower(), {})

    # ===================
    # Public API
    # ===================

    def chat(
        self,
        user_input: str,
        user_id: str,
        session_id: Optional[str] = None,
        birth_chart: Optional[Dict[str, Any]] = None,
        current_dasha: Optional[Dict[str, Any]] = None,
        current_transits: Optional[Dict[str, Any]] = None,
        detected_yogas: Optional[List[Dict[str, Any]]] = None,
        detected_doshas: Optional[List[Dict[str, Any]]] = None,
        memories: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return response.

        This is the main entry point for interacting with the Guide agent.

        Args:
            user_input: User's message
            user_id: User identifier
            session_id: Session identifier (auto-generated if not provided)
            birth_chart: Birth chart data (optional)
            current_dasha: Current dasha info (optional)
            current_transits: Current transit info (optional)
            detected_yogas: List of detected yogas (optional)
            detected_doshas: List of detected doshas (optional)
            memories: Retrieved memories from Mem0 (optional)

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

    def get_intent(self, user_input: str) -> IntentType:
        """
        Get the intent of a user message without processing.

        Useful for routing without full agent execution.

        Args:
            user_input: User message

        Returns:
            Detected intent
        """
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

    def stream_response(
        self,
        user_input: str,
        user_id: str,
        session_id: Optional[str] = None,
        birth_chart: Optional[Dict[str, Any]] = None,
    ):
        """
        Stream response from the agent (for real-time UI updates).

        Args:
            user_input: User message
            user_id: User identifier
            session_id: Session identifier
            birth_chart: Birth chart data

        Yields:
            Response chunks
        """
        state: AgentState = {
            "messages": [],
            "user_input": user_input,
            "response": None,
            "user_id": user_id,
            "birth_chart": birth_chart,
            "current_dasha": None,
            "current_transits": None,
            "detected_yogas": [],
            "detected_doshas": [],
            "analysis_results": {},
            "memories": [],
            "intent": None,
            "personality_style": None,
            "session_id": session_id or f"session_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
        }

        # Stream from compiled graph
        for output in self._compiled_graph.stream(state):
            # output is a dict with node name as key
            for node_name, node_output in output.items():
                if node_output.get("response"):
                    yield node_output["response"]


# =====================
# Singleton & Utilities
# =====================

_guide: Optional[Guide] = None


def initialize_guide(
    model: str = "claude-opus-4-5-20251101",
    api_key: Optional[str] = None,
    debug: bool = False
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
        raise RuntimeError(
            "Guide not initialized. Call initialize_guide() first."
        )
    return _guide
