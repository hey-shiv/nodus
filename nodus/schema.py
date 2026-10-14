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
    "DEPENDS_ON", "FALLBACK_FOR",
    "RAISED", "ABOUT", "AUTHORED", "INVOLVED", "DESCRIBED_IN",
    "HAS_CONDITION", "CITES", "LEARNED_FROM", "OF_LESSON", "ON_PLAN", "INVITED",
})

PROPERTIES = frozenset({
    "id", "title", "name", "change_type", "risk_class", "status", "kind", "scope",
    "at", "active", "summary", "resolution", "origin", "source", "url",
})

# Controlled vocabularies (docs/graph-model.md). A lesson may only filter on these
# properties, with these values: free-text matches (e.g. name = "canary procedure") would
# make an "absent" condition true everywhere and never generalise.
VOCAB = {
    "risk_class": {"routine", "standard", "high"},
    "change_type": {"config_change", "code_deploy", "infra_change", "data_migration"},
    "status": {"planned", "in_progress", "done"},
    "kind": {"review", "test", "canary", "rollout",                    # Step
             "staged_rollout", "change_review", "backup_restore_test",  # Procedure
             "automated", "human",                                       # Check
             "pager", "chat_alerts", "email_list",                       # Channel
             "service", "recovery_tool"},                                # System
    "scope": {"subset", "all"},
    "resolution": {"accepted", "overruled", "open"},
    "active": {True, False},
}

# Which labels each relationship connects (from, to). None = any label.
ENDS = {
    "HAS_STEP": ("Plan", "Step"), "FOLLOWS": ("Plan", "Procedure"), "GATED_BY": ("Plan", "Check"),
    "TARGETS": ("Plan", "System"), "ALERTS_TO": ("System", "Channel"),
    "DEPENDS_ON": ("System", "System"), "FALLBACK_FOR": ("System", "System"),
    "WATCHES": ("Person", "Channel"), "OWNS": ("Person", None), "RAISED": ("Person", "Concern"),
    "ABOUT": ("Concern", "Plan"), "AUTHORED": ("Person", "Document"),
    "INVOLVED": ("Episode", "Plan"), "DESCRIBED_IN": ("Episode", "Document"),
    "HAS_CONDITION": ("Lesson", "Condition"), "CITES": ("Condition", "Document"),
    "LEARNED_FROM": ("Lesson", None), "OF_LESSON": ("Echo", "Lesson"),
    "ON_PLAN": ("Echo", "Plan"), "INVITED": ("Echo", "Person"),
}

# "kind" means different things on different labels.
KIND_BY_LABEL = {
    "Step": {"review", "test", "canary", "rollout"},
    "Procedure": {"staged_rollout", "change_review", "backup_restore_test"},
    "Check": {"automated", "human"},
    "Channel": {"pager", "chat_alerts", "email_list"},
    "System": {"service", "recovery_tool"},
}
