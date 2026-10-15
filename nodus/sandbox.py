"""Per-visitor sandboxes for the public website.

The demo world lives in a template graph. Each visitor gets a private copy (GRAPH.COPY), so
editing a plan or recording an outcome never changes what the next visitor sees. Old copies
are deleted: anything older than MAX_AGE_S, and the oldest beyond MAX_SANDBOXES, which keeps a
free 100 MB FalkorDB Cloud instance safe.
"""
import os
import re
import secrets
import time

TEMPLATE = os.environ.get("NODUS_TEMPLATE_GRAPH", "nodus_template")
PREFIX = os.environ.get("NODUS_SANDBOX_PREFIX", "sbx")
MAX_AGE_S = int(os.environ.get("NODUS_SANDBOX_MAX_AGE_S", str(2 * 3600)))
MAX_SANDBOXES = int(os.environ.get("NODUS_MAX_SANDBOXES", "40"))
_NAME = re.compile(rf"^{re.escape(PREFIX)}_(\d{{10}})_[0-9a-f]{{8}}$")


def build_template(db, approve_as="NODUS demo"):
    """(Re)build the template graph: synthetic world + approved lessons + the agent's first pass."""
    from nodus.agent import observe_all
    from scripts.setup_demo import build
    g = db.select_graph(TEMPLATE)
    build(g, approve_as)
    observe_all(g)
    return g


def _sandboxes(db):
    out = []
    for name in db.list_graphs():
        m = _NAME.match(name)
        if m:
            out.append((int(m.group(1)), name))
    return sorted(out)


def cleanup(db, now=None):
    now = now or int(time.time())
    boxes = _sandboxes(db)
    stale = [n for t, n in boxes if now - t > MAX_AGE_S]
    fresh = [n for t, n in boxes if now - t <= MAX_AGE_S]
    stale += fresh[: max(0, len(fresh) - (MAX_SANDBOXES - 1))]       # room for one more
    for name in stale:
        db.select_graph(name).delete()
    return stale


def create(db, now=None):
    """A fresh private copy of the template. Returns its id."""
    if TEMPLATE not in db.list_graphs():
        build_template(db)
    cleanup(db, now)
    name = f"{PREFIX}_{now or int(time.time())}_{secrets.token_hex(4)}"
    db.connection.execute_command("GRAPH.COPY", TEMPLATE, name)
    return name


def is_valid(db, name):
    return bool(name and _NAME.match(name)) and name in db.list_graphs()
