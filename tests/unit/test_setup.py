"""Verify project setup."""


def test_import_main_package() -> None:
    """Test that the main package can be imported."""
    import one_zero_eight

    assert one_zero_eight.__version__ == "2.0.0"


def test_import_pydantic() -> None:
    """Test that pydantic is installed."""
    import pydantic

    assert pydantic.VERSION is not None


def test_import_fastapi() -> None:
    """Test that FastAPI is installed."""
    import fastapi

    assert fastapi.__version__ is not None
