from unittest.mock import patch

import pytest


@pytest.fixture
def mock_execute_readonly_query():
    """
    Reusable fixture for patching app.db.mssql.execute_readonly_query
    to provide deterministic mock returns in backend tests.
    """
    with patch("app.db.mssql.execute_readonly_query") as mock_query:
        yield mock_query
