"""Pytest configuration – patch out the real database for the entire test session."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True, scope="session")
def mock_db_create_all():
    """Prevent SQLAlchemy from trying to connect to a real database."""
    with patch("sqlalchemy.schema.MetaData.create_all"):
        yield
