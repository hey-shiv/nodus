"""Generate the synthetic company world (docs/world-story.md) as plain data.

Output: {"nodes": [...], "rels": [...]}. A node is {"label", "id", "props"}; a rel is
{"type", "from", "from_label", "to", "to_label"}. Every node is marked synthetic.
The designed core is fixed; the seed only drives the background plans and people.
"""
import random

DAY = 86_400
T0 = 1_792_454_400  # 2026-10-20 00:00 UTC, the week the current plans are scheduled
SOURCE = "doc-world-tern-tally"


class _World:
    def __init__(self):
        self.nodes, self.rels, self._labels = [], [], {}

    def node(self, label, id_, **props):
        props.setdefault("origin", "synthetic")
        props.setdefault("source", SOURCE)
        self.nodes.append({"label": label, "id": id_, "props": props})
        self._labels[id_] = label
        return id_

    def rel(self, type_, from_id, to_id):
        self.rels.append({"type": type_, "from": from_id, "from_label": self._labels[from_id],
                          "to": to_id, "to_label": self._labels[to_id]})


def _people(w):
    for id_, name, active in [
        ("p-asha", "Asha Rao", True), ("p-tomas", "Tomas Lind", True),
        ("p-mei", "Mei Okafor", True), ("p-ravi", "Ravi Sen", False),
        ("p-lena", "Lena Brandt", True), ("p-diego", "Diego Marín", True),
        ("p-noor", "Noor Haddad", True), ("p-kai", "Kai Tanaka", True),
    ]:
        w.node("Person", id_, name=name, active=active)


def _infrastructure(w):
    w.node("Procedure", "proc-canary", kind="staged_rollout",
           title="Canary batch first, then all depots")
    w.node("Procedure", "proc-review", kind="change_review", title="Two-person change review")
    w.rel("OWNS", "p-diego", "proc-canary")
    w.node("Check", "chk-human", kind="human", title="Peer review sign-off")
    w.node("Check", "chk-schema", kind="automated", title="Config schema lint")

    w.node("Channel", "ch-pager", kind="pager", title="On-call pager")
    w.node("Channel", "ch-ops-chat", kind="chat_alerts", title="#ops-alerts room")
    w.node("Channel", "ch-tariff-mail", kind="email_list", title="tariff-errors@ list")
    w.node("Channel", "ch-maps-mail", kind="email_list", title="maps-notify@ list")
    w.node("Channel", "ch-label-mail", kind="email_list", title="printer-alerts@ list")
    w.rel("OWNS", "p-mei", "ch-pager")
    w.rel("WATCHES", "p-mei", "ch-pager")
    w.rel("WATCHES", "p-kai", "ch-pager")
    w.rel("WATCHES", "p-noor", "ch-ops-chat")
    w.rel("WATCHES", "p-ravi", "ch-tariff-mail")   # Ravi has left: no active watcher

    for id_, name, channel, owner in [
        ("sys-tariff", "Tariff Service", "ch-tariff-mail", "p-lena"),
        ("sys-maps", "Driver Map Tiles", "ch-maps-mail", "p-noor"),
        ("sys-sensor", "Dock Sensor Hub", "ch-pager", "p-kai"),
        ("sys-scanner", "Scanner Handhelds", "ch-ops-chat", "p-noor"),
        ("sys-billing", "Billing Reports", "ch-pager", "p-diego"),
        ("sys-label", "Label Printing", "ch-label-mail", "p-asha"),
        ("sys-invoice", "Invoice Export", "ch-pager", "p-mei"),
    ]:
        w.node("System", id_, name=name)
        w.rel("ALERTS_TO", id_, channel)
        w.rel("OWNS", owner, id_)


def _plan(w, id_, title, risk, change_type, status, owner, system,
          follows=(), gates=(), steps=(), description=""):
    w.node("Plan", id_, title=title, summary=description, risk_class=risk,
           change_type=change_type, status=status)
    w.rel("OWNS", owner, id_)
    w.rel("TARGETS", id_, system)
    for proc in follows:
        w.rel("FOLLOWS", id_, proc)
    for gate in gates:
        w.rel("GATED_BY", id_, gate)
    for i, (kind, scope, day) in enumerate(steps, start=1):
        step = w.node("Step", f"{id_}-s{i}", kind=kind, scope=scope, at=T0 + day * DAY)
        w.rel("HAS_STEP", id_, step)
    return id_


def _current_plans(w):
    w.node("Check", "chk-tariff-format", kind="automated", title="Tariff sheet format checker")
    _plan(w, "plan-hero", "Refresh tariff tables for every depot", "routine",
          "config_change", "planned", "p-lena", "sys-tariff",
          gates=["chk-tariff-format"], steps=[("test", "subset", 1)],
          description="Weekly tariff sheet refresh. Same layout as the last thirty "
                      "refreshes, so it is filed as a routine change.")
    _plan(w, "plan-maps", "Swap map tile provider in the driver app", "standard",
          "infra_change", "planned", "p-noor", "sys-maps",
          gates=["chk-schema", "chk-human"],
          steps=[("test", "subset", 1), ("rollout", "all", 3)],
          description="Move the driver app to the new tile provider in one switch-over.")
    _plan(w, "plan-sensor", "Global rollout of dock sensor content update", "standard",
          "config_change", "planned", "p-kai", "sys-sensor",
          follows=["proc-canary"], gates=["chk-schema", "chk-human"],
          steps=[("canary", "subset", 1), ("rollout", "all", 4)],
          description="New channel file for the dock sensor fleet; the content update "
                      "passes the validator, then a global rollout after the canary.")
    _plan(w, "plan-scanner", "Scanner handheld OS patch", "routine",
          "code_deploy", "planned", "p-noor", "sys-scanner",
          gates=["chk-schema", "chk-human"], steps=[("test", "subset", 2)],
          description="Monthly vendor patch for the warehouse handhelds.")
    _plan(w, "plan-billing", "Billing report column rename", "standard",
          "code_deploy", "planned", "p-diego", "sys-billing",
          follows=["proc-canary"], gates=["chk-human"],
          steps=[("canary", "subset", 1), ("rollout", "subset", 2)],
          description="Rename two columns in the monthly billing export.")


def _episodes(w):
    # E1: the episode behind the internal lesson "The quiet push"
    _plan(w, "plan-e1", "Label printer firmware push", "routine", "code_deploy", "done",
          "p-tomas", "sys-label", gates=["chk-schema"],
          steps=[("rollout", "all", -580)])
    w.node("Document", "doc-pm-e1", title="Post-mortem: label printer firmware push",
           path="data/postmortems/e1-label-printer.md")
    w.node("Episode", "ep-e1", title="Label printers down at every depot", at=T0 - 580 * DAY)
    w.rel("INVOLVED", "ep-e1", "plan-e1")
    w.rel("DESCRIBED_IN", "ep-e1", "doc-pm-e1")
    w.rel("AUTHORED", "p-tomas", "doc-pm-e1")
    w.node("Concern", "c-e1", summary="Asked for a canary batch before all depots",
           resolution="overruled")
    w.rel("RAISED", "p-asha", "c-e1")
    w.rel("ABOUT", "c-e1", "plan-e1")

    # E2: a near-incident where the concern was accepted
    _plan(w, "plan-e2", "Invoice export cutover", "standard", "data_migration", "done",
          "p-mei", "sys-invoice", follows=["proc-canary"], gates=["chk-human"],
          steps=[("canary", "subset", -460), ("rollout", "all", -455)])
    w.node("Document", "doc-pm-e2", title="Review: invoice export cutover",
           path="data/postmortems/e2-invoice-export.md")
    w.node("Episode", "ep-e2", title="Invoice export cutover delayed", at=T0 - 460 * DAY)
    w.rel("INVOLVED", "ep-e2", "plan-e2")
    w.rel("DESCRIBED_IN", "ep-e2", "doc-pm-e2")
    w.rel("AUTHORED", "p-diego", "doc-pm-e2")
    w.node("Concern", "c-e2", summary="Reconciliation step missing from the cutover",
           resolution="accepted")
    w.rel("RAISED", "p-mei", "c-e2")
    w.rel("ABOUT", "c-e2", "plan-e2")


_VERBS = ["Tune", "Upgrade", "Rotate", "Resize", "Patch", "Migrate"]
_THINGS = ["route cache", "depot dashboard", "parcel API", "fleet telemetry", "rate limiter",
           "customs export", "driver roster", "warehouse search"]


def _background(w, rng, count):
    """Done plans that followed the staged procedure: 'most changes are staged'."""
    systems = ["sys-maps", "sys-sensor", "sys-scanner", "sys-billing", "sys-invoice"]
    owners = ["p-diego", "p-mei", "p-noor", "p-kai", "p-lena"]
    for i in range(count):
        title = f"{rng.choice(_VERBS)} {rng.choice(_THINGS)}"
        day = -rng.randint(20, 400)
        _plan(w, f"plan-bg{i:02d}", title, rng.choice(["routine", "standard"]),
              rng.choice(["config_change", "code_deploy"]), "done",
              rng.choice(owners), rng.choice(systems),
              follows=["proc-canary"], gates=rng.choice([["chk-human"], ["chk-schema", "chk-human"]]),
              steps=[("canary", "subset", day), ("rollout", "all", day + 2)])


def generate(seed=7, background=12):
    rng = random.Random(seed)
    w = _World()
    w.node("Document", SOURCE, title="Tern & Tally Freight synthetic world (generated)",
           path="docs/world-story.md")
    _people(w)
    _infrastructure(w)
    _current_plans(w)
    _episodes(w)
    _background(w, rng, background)
    return {"nodes": w.nodes, "rels": w.rels}
