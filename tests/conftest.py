import uuid

import pytest
from falkordb import FalkorDB


@pytest.fixture
def graph():
    """A throwaway graph with a random name, deleted after the test."""
    db = FalkorDB(host="localhost", port=6379)
    g = db.select_graph(f"lab_{uuid.uuid4().hex[:8]}")
    yield g
    try:
        g.delete()
    except Exception:
        pass  # graph was never created (test made no writes)
