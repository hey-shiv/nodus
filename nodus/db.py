"""One place that knows how to reach FalkorDB (settings from the environment)."""
import os

from falkordb import FalkorDB


def get_graph(name=None):
    db = FalkorDB(host=os.environ.get("NODUS_DB_HOST", "localhost"),
                  port=int(os.environ.get("NODUS_DB_PORT", "6379")))
    return db.select_graph(name or os.environ.get("NODUS_GRAPH", "nodus"))
