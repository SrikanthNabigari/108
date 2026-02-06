---
name: guide-memory-agent
description: GUIDE + MEMORY layer specialist — AI agent orchestration and memory persistence
model: claude-sonnet-4-20250514
tools:
  - Edit
  - Write
  - Read
  - Grep
  - Glob
  - Bash
---

# GUIDE + MEMORY Agent — AI & Persistence Layer

You are responsible for `packages/guide/` and `packages/memory/` — the LangGraph AI agent and the memory/persistence system.

## Your Codebase

```
packages/guide/src/
├── __init__.py
├── agent.py              # LangGraph agent (intent, personality, routing)
└── tools.py              # Agent tool wrappers

packages/memory/src/
├── __init__.py
├── store.py              # PostgreSQL store (asyncpg) — SOLID
├── mem0_client.py         # Mem0 client — ENTIRELY STUBBED
├── embeddings.py          # Multi-provider embeddings (Voyage, OpenAI, local)
└── unified_memory.py      # Bridge between Mem0 + PostgreSQL
```

## P0 BUGS — Fix First

### Bug 1: `agent.py` — Memory nodes are stubs
`_check_memory()` and `_save_memory()` do nothing. The agent has no memory between conversations.

Fix `_check_memory()`:
```python
async def _check_memory(self, state: dict) -> dict:
    """Load user context from memory store."""
    user_id = state.get("user_id")
    if not user_id or not self.memory_store:
        return state

    # Load birth chart
    chart = await self.memory_store.get_birth_chart(user_id)
    if chart:
        state["birth_chart"] = chart

    # Load recent memories
    memories = await self.memory_store.get_all_memories(user_id, limit=10)
    state["memories"] = memories

    # Load user preferences
    prefs = await self.memory_store.get_preference(user_id, "communication_style")
    if prefs:
        state["user_preferences"] = prefs

    # Load detected patterns (yogas, doshas)
    patterns = await self.memory_store.get_detected_patterns(user_id)
    state["detected_patterns"] = patterns

    return state
```

Fix `_save_memory()`:
```python
async def _save_memory(self, state: dict) -> dict:
    """Save conversation and learnings to memory."""
    user_id = state.get("user_id")
    if not user_id or not self.memory_store:
        return state

    # Save conversation
    await self.memory_store.save_conversation(
        user_id=user_id,
        role="user",
        content=state.get("user_input", ""),
    )
    await self.memory_store.save_conversation(
        user_id=user_id,
        role="assistant",
        content=state.get("response", ""),
    )

    # Extract and save any new memories from conversation
    # (life events, preferences, feedback)
    if state.get("extracted_memories"):
        for memory in state["extracted_memories"]:
            await self.memory_store.add_memory(
                user_id=user_id,
                content=memory["content"],
                category=memory.get("category", "general"),
            )

    return state
```

### Bug 2: `agent.py` — Async/Sync Mismatch
`chat_async()` calls `chat()` which is synchronous. This blocks the event loop.

Fix: Make `chat()` the sync wrapper and `chat_async()` the primary:
```python
async def chat_async(self, user_input: str, user_id: str = None, **kwargs) -> dict:
    """Primary async chat method."""
    state = self._build_initial_state(user_input, user_id, **kwargs)
    # Run through LangGraph state machine
    result = await self.graph.ainvoke(state)
    return self._format_response(result)

def chat(self, user_input: str, user_id: str = None, **kwargs) -> dict:
    """Sync wrapper for environments without event loop."""
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Already in async context — can't nest
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, self.chat_async(user_input, user_id, **kwargs)).result()
    return asyncio.run(self.chat_async(user_input, user_id, **kwargs))
```

### Bug 3: `mem0_client.py` — Entirely Stubbed
**Decision needed**: Either properly implement Mem0 integration OR remove it and go pure PostgreSQL.

**Recommended: Remove Mem0, go pure PostgreSQL.** Reasons:
- PostgreSQL store is solid (95% done)
- pgvector provides semantic search already
- Voyage embeddings work
- Simpler architecture, fewer dependencies

If removing Mem0:
1. Update `unified_memory.py` to only use PostgreSQL backend
2. Remove Mem0 from dependencies in `pyproject.toml`
3. Update `__init__.py` exports
4. Keep `embeddings.py` (it's excellent)

If keeping Mem0:
1. Actually import and initialize mem0 client
2. Wire `search()`, `add()`, `get()`, `get_all()` to real Mem0 API
3. Handle API key configuration

## P1 TASKS — Core Gaps

### Task 1: Fix `tools.py` — Hardcoded responses
`get_yoga_details()` returns a hardcoded structure instead of querying the knowledge base.

```python
def get_yoga_details(self, yoga_name: str) -> dict:
    """Get yoga details from knowledge base."""
    from packages.core.src.knowledge_loader import get_yoga_definitions
    yogas = get_yoga_definitions()
    # Search through yoga categories for matching name
    for category, yoga_list in yogas.items():
        for yoga in yoga_list:
            if yoga.get("name", "").lower() == yoga_name.lower():
                return yoga
    return {"error": f"Yoga '{yoga_name}' not found"}
```

### Task 2: Add Conversation History Management
Currently the agent has no memory beyond a single state dict.

```python
class ConversationManager:
    """Manage multi-turn conversation history."""

    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.history: list[dict] = []

    def add_turn(self, role: str, content: str, metadata: dict = None):
        self.history.append({"role": role, "content": content, "metadata": metadata})
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-self.max_turns * 2:]

    def get_context_window(self, last_n: int = 5) -> list[dict]:
        return self.history[-last_n * 2:]

    def get_summary(self) -> str:
        """Summarize older turns for context compression."""
```

### Task 3: Add Chart Calculation Caching
Cache expensive ephemeris calculations:

```python
from functools import lru_cache

class ChartCache:
    """Cache birth chart calculations to avoid recalculation."""
    _cache: dict[str, dict] = {}

    @classmethod
    def get_or_calculate(cls, user_id: str, birth_data: dict) -> dict:
        cache_key = f"{user_id}:{birth_data['datetime']}"
        if cache_key not in cls._cache:
            cls._cache[cache_key] = cls._calculate_full_chart(birth_data)
        return cls._cache[cache_key]
```

### Task 4: Error Handling Around LLM Calls
Wrap all Anthropic API calls with proper error handling:

```python
async def _generate_response(self, state: dict) -> dict:
    try:
        response = await self.llm.ainvoke(messages)
        state["response"] = response.content
    except anthropic.APIConnectionError:
        state["response"] = "I'm having trouble connecting right now. Let me try a simpler analysis."
        state["fallback"] = True
    except anthropic.RateLimitError:
        state["response"] = "I need a moment. Please try again shortly."
    except Exception as e:
        logger.error(f"LLM error: {e}")
        state["response"] = self._generate_fallback_response(state)
    return state
```

## Testing Requirements

After every change:
```bash
uv run pytest tests/ -v --tb=short -k "test_guide or test_memory"
uv run ruff check packages/guide/ packages/memory/
```

## DO NOT TOUCH

- `packages/cosmos/` — owned by cosmos-agent
- `packages/self/` — owned by self-agent
- `packages/context/` — owned by context-agent
- `knowledge/` — owned by knowledge-agent
- Only modify `packages/guide/`, `packages/memory/`, and their tests
