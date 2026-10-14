"""One place that knows how to reach FalkorDB (settings from the environment)."""
import os

from falkordb import FalkorDB


def get_graph(name=None):
    db = FalkorDB(host=os.environ.get("NODUS_DB_HOST", "localhost"),
                  port=int(os.environ.get("NODUS_DB_PORT", "6379")))
    return db.select_graph(name or os.environ.get("NODUS_GRAPH", "nodus"))


def read(graph, query, params=None):
    """Read-only query; a graph that doesn't exist yet simply has no rows.

    FalkorDB raises "Invalid graph operation on empty key" for reads on a graph
    that has never been written to (found in T12).
    """
    from redis.exceptions import ResponseError
    try:
        return graph.ro_query(query, params).result_set
    except ResponseError as e:
        if "empty key" in str(e):
            return []
        raise
