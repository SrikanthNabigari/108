---
name: memory-manager
description: Manage long-term memory, project notes, and user context for the 108 Personal Life Operating System using Mem0 and LangMem
triggers:
  - save memory
  - recall
  - remember
  - project notes
  - track decision
  - log
  - user context
globs:
  - "packages/memory/**/*.py"
  - "docs/project_notes/**/*.md"
---

# Memory Manager Skill

You are responsible for 108's memory system - making it learn and evolve with each interaction.

## Memory Philosophy

> "Memory is what transforms 108 from a calculator into a companion."

The memory system uses two complementary approaches:
1. **Mem0** - Automatic extraction of important information
2. **LangMem** - Explicit agent-controlled memory tools

## Memory Types for 108

| Type | Lifecycle | Purpose |
|------|-----------|---------|
| `birth_chart` | Permanent | Birth data, calculated positions |
| `personality` | Permanent | Detected yogas, doshas, personality type |
| `preferences` | Evolving | Communication style, topics of interest |
| `life_events` | Growing | Major events shared, prediction validations |
| `conversations` | Growing | Summarized chat history |
| `predictions` | Growing | Predictions made and outcomes |
| `tasks` | Active | Scheduled reminders and tasks |

## Project Notes Structure

Maintain project memory in `docs/project_notes/`:

```
docs/project_notes/
├── decisions/           # Architectural decisions
│   ├── ADR-001-use-uv.md
│   └── ADR-002-memory-stack.md
├── bugs/               # Bug tracking with solutions
│   └── BUG-001-yoga-detection.md
├── learnings/          # Knowledge gained
│   └── LEARN-001-sidereal-time.md
└── work_log.md         # Daily progress log
```

## Decision Record Template

```markdown
# ADR-XXX: [Title]

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue that we're seeing that motivates this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult because of this change?

## Date
YYYY-MM-DD
```

## Bug Record Template

```markdown
# BUG-XXX: [Short Description]

## Symptoms
What was observed?

## Root Cause
What was actually wrong?

## Solution
How was it fixed?

## Prevention
How do we prevent this in the future?

## Related Files
- path/to/file1.py
- path/to/file2.py
```

## Mem0 Integration

```python
from mem0 import Memory

class JyotishMemory:
    def __init__(self):
        self.memory = Memory.from_config({
            "vector_store": {
                "provider": "pgvector",
                "config": {
                    "collection_name": "jyotish_memories"
                }
            },
            "llm": {
                "provider": "anthropic",
                "config": {"model": "claude-sonnet-4-20250514"}
            }
        })

    async def add(self, user_id: str, messages: list, metadata: dict = None):
        """Store conversation and auto-extract memories."""
        self.memory.add(
            messages=messages,
            user_id=user_id,
            metadata=metadata or {}
        )

    async def recall(self, user_id: str, query: str, limit: int = 5):
        """Recall relevant memories for context."""
        return self.memory.search(
            query=query,
            user_id=user_id,
            limit=limit
        )

    async def get_all(self, user_id: str):
        """Get all memories for a user."""
        return self.memory.get_all(user_id=user_id)
```

## LangMem Tools

Define explicit memory tools for the LangGraph agent:

```python
from langchain_core.tools import tool

@tool
def save_important_fact(user_id: str, fact: str, category: str):
    """Save an important fact about the user.

    Args:
        user_id: The user's identifier
        fact: The fact to remember
        category: One of: personality, preference, life_event, prediction
    """
    # Implementation
    pass

@tool
def recall_user_context(user_id: str, topic: str = None):
    """Recall relevant context about a user.

    Args:
        user_id: The user's identifier
        topic: Optional topic to focus recall on
    """
    # Implementation
    pass

@tool
def log_prediction(user_id: str, prediction: str, timeframe: str, confidence: float):
    """Log a prediction for later validation.

    Args:
        user_id: The user's identifier
        prediction: What was predicted
        timeframe: When it should manifest
        confidence: 0-1 confidence score
    """
    # Implementation
    pass

@tool
def validate_prediction(prediction_id: str, outcome: str, accuracy: float):
    """Validate a past prediction against actual outcome.

    Args:
        prediction_id: ID of the prediction
        outcome: What actually happened
        accuracy: 0-1 how accurate the prediction was
    """
    # Implementation
    pass
```

## When to Save Memory

**ALWAYS save when:**
- User shares birth details
- User mentions a life event
- User expresses a preference
- A prediction is made
- User corrects information
- Important insight is discovered

**NEVER save:**
- Casual greetings
- Generic questions
- Repeated information already saved

## Memory Retrieval Pattern

```python
async def get_conversation_context(user_id: str, current_query: str) -> dict:
    """Build context for a new conversation turn."""
    return {
        "birth_chart": await get_birth_chart(user_id),
        "personality": await get_detected_patterns(user_id),
        "relevant_memories": await recall(user_id, current_query, limit=5),
        "recent_predictions": await get_recent_predictions(user_id, limit=3),
        "active_tasks": await get_active_tasks(user_id)
    }
```

## File Locations

- **Memory package**: `packages/memory/src/`
- **Project notes**: `docs/project_notes/`
- **Memory tests**: `tests/unit/test_memory.py`

## Best Practices

1. **Be selective** - Not everything needs to be remembered
2. **Consolidate** - Merge similar memories to reduce duplication
3. **Validate** - Track prediction accuracy to improve over time
4. **Prune** - Remove outdated or irrelevant memories
5. **Privacy** - Never expose raw memories to users without processing
