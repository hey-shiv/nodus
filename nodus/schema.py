"""The graph model's vocabulary (docs/graph-model.md), used as a whitelist.

Labels, relationship types and property names can't be Cypher parameters, so the
compiler only puts names from these sets into query text.
"""

LABELS = frozenset({
    "Plan", "Step", "Procedure", "Check", "System", "Channel", "Person",
    "Concern", "Episode", "Document", "Lesson", "Condition", "Echo",
})

RELATIONSHIPS = frozenset({
    "HAS_STEP", "FOLLOWS", "GATED_BY", "TARGETS", "ALERTS_TO", "WATCHES", "OWNS",
    "RAISED", "ABOUT", "AUTHORED", "INVOLVED", "DESCRIBED_IN",
    "HAS_CONDITION", "CITES", "LEARNED_FROM", "OF_LESSON", "ON_PLAN", "INVITED",
})

PROPERTIES = frozenset({
    "id", "title", "name", "change_type", "risk_class", "status", "kind", "scope",
    "at", "active", "summary", "resolution", "origin", "source", "url",
})
