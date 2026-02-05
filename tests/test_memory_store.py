"""
Tests for the MemoryStore with actual PostgreSQL connection.
"""

import asyncio
from datetime import datetime

import pytest

# Skip if no database available
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def store():
    """Create and connect memory store."""
    from packages.memory.src.store import MemoryStore

    store = MemoryStore("postgresql://postgres:postgres@localhost:5432/one_zero_eight")
    try:
        await store.connect()
        yield store
    finally:
        await store.close()


@pytest.mark.asyncio
async def test_health_check(store):
    """Test database health check."""
    result = await store.health_check()
    assert result is True


@pytest.mark.asyncio
async def test_create_user(store):
    """Test user creation."""
    user = await store.create_user(email="test@example.com", name="Test User")

    assert user["email"] == "test@example.com"
    assert user["name"] == "Test User"
    assert "id" in user


@pytest.mark.asyncio
async def test_get_user_by_email(store):
    """Test retrieving user by email."""
    # Create user first
    await store.create_user(email="lookup@example.com", name="Lookup User")

    # Look up user
    user = await store.get_user_by_email("lookup@example.com")

    assert user is not None
    assert user["email"] == "lookup@example.com"


@pytest.mark.asyncio
async def test_add_memory(store):
    """Test adding a memory."""
    # Need a user first
    user = await store.create_user(
        email=f"memory_test_{datetime.now().timestamp()}@example.com", name="Memory Test User"
    )

    memory = await store.add_memory(
        user_id=user["id"],
        content="Test memory content",
        category="fact",
        importance=0.8,
        metadata={"source": "test"},
    )

    assert memory.content == "Test memory content"
    assert memory.category == "fact"
    assert memory.importance == 0.8


@pytest.mark.asyncio
async def test_save_birth_chart(store):
    """Test saving birth chart."""
    user = await store.create_user(
        email=f"chart_test_{datetime.now().timestamp()}@example.com", name="Chart Test User"
    )

    chart = await store.save_birth_chart(
        user_id=user["id"],
        birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
        latitude=16.726239,
        longitude=81.288428,
        timezone="Asia/Kolkata",
        place_name="Eluru, India",
        chart_data={"lagna": "Libra", "moon_sign": "Aquarius"},
    )

    assert chart["latitude"] == 16.726239
    assert chart["timezone"] == "Asia/Kolkata"


@pytest.mark.asyncio
async def test_get_birth_chart(store):
    """Test retrieving birth chart."""
    user = await store.create_user(
        email=f"get_chart_{datetime.now().timestamp()}@example.com", name="Get Chart User"
    )

    # Save chart
    await store.save_birth_chart(
        user_id=user["id"],
        birth_datetime=datetime(1990, 1, 1, 12, 0, 0),
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
        place_name="New York, USA",
    )

    # Retrieve chart
    chart = await store.get_birth_chart(user["id"])

    assert chart is not None
    assert chart["place_name"] == "New York, USA"


@pytest.mark.asyncio
async def test_save_detected_patterns(store):
    """Test saving yoga/dosha patterns."""
    user = await store.create_user(
        email=f"pattern_test_{datetime.now().timestamp()}@example.com", name="Pattern Test User"
    )

    patterns = [
        {
            "name": "Budha-Aditya Yoga",
            "category": "wealth",
            "strength": 0.85,
            "involved_planets": ["Sun", "Mercury"],
        },
        {
            "name": "Gajakesari Yoga",
            "category": "prosperity",
            "strength": 0.75,
            "involved_planets": ["Moon", "Jupiter"],
        },
    ]

    count = await store.save_detected_patterns(
        user_id=user["id"], patterns=patterns, pattern_type="yoga"
    )

    assert count == 2


@pytest.mark.asyncio
async def test_set_and_get_preference(store):
    """Test user preferences."""
    user = await store.create_user(
        email=f"pref_test_{datetime.now().timestamp()}@example.com", name="Preference Test User"
    )

    # Set preference
    await store.set_preference(user_id=user["id"], key="language", value="en")

    # Get preference
    value = await store.get_preference(user_id=user["id"], key="language")

    assert value == "en"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
