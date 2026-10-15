"""One-time setup: build the demo template graph in FalkorDB Cloud.

Run from your own Terminal (it asks for the password without showing it):
    .venv/bin/python scripts/build_cloud_template.py

It loads the synthetic company and the four lessons into a graph named "nodus_template".
Each website visitor then gets a private copy of it (nodus/sandbox.py).
"""
import getpass
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

print("FalkorDB Cloud connection (from your instance's Connect page).")
os.environ["NODUS_DB_HOST"] = input("Host: ").strip()
os.environ["NODUS_DB_PORT"] = input("Port: ").strip()
os.environ["NODUS_DB_USERNAME"] = input("Username (press Enter if none): ").strip()
os.environ["NODUS_DB_PASSWORD"] = getpass.getpass("Password (hidden): ")

from nodus import sandbox  # noqa: E402
from nodus.db import get_db  # noqa: E402

db = get_db()
db.connection.ping()
print("Connected. Building the template (takes up to a minute over the internet)...")
t = time.time()
sandbox.build_template(db)
print(f"Done in {time.time() - t:.0f}s. Graphs now in the instance: {db.list_graphs()}")
name = sandbox.create(db)
print(f"Test sandbox created and works: {name}")
db.select_graph(name).delete()
print("Cleaned up the test sandbox. The cloud database is ready.")
