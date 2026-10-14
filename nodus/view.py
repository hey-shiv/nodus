"""Turn a match result into display rows: every row comes from the match, nothing hand-drawn."""
from dataclasses import dataclass

from nodus.db import read
from nodus.lessons import lesson_detail


@dataclass
class Row:
    cid: str
    lesson_text: str
    source: str          # e.g. "Cloudflare, CrowdStrike" or "Post-mortem: label printer…"
    plan_text: str
    state: str           # "holds" | "missing" | "unbound"
    absence: bool
    completion: bool


def _labels(graph, ids):
    rows = read(graph, "MATCH (n) WHERE n.id IN $ids "
                       "RETURN n.id, coalesce(n.title, n.name, n.kind + ' ' + n.scope, n.id), "
                       "labels(n)[0], n.kind, n.scope", {"ids": list(ids)})
    out = {}
    for id_, title, label, kind, scope in rows:
        if label == "Step":
            title = f"step: {kind}" + (" to every target" if scope == "all" else f" ({scope})")
        elif label == "Check":
            title = f"{title} ({kind})"
        out[id_] = title
    return out


def rows_for(graph, plan_id, lesson, result):
    detail = {c["id"]: c for c in lesson_detail(graph, lesson["id"])}
    all_ids = {i for c in result.conditions for i in c.ids} | set(result.bindings.values())
    label = _labels(graph, all_ids)
    rows = []
    for spec, res in zip(lesson["conditions"], result.conditions):
        cits = detail.get(spec["id"], {}).get("citations", [])
        source = ", ".join(dict.fromkeys(
            "internal post-mortem" if c["origin"] == "synthetic" else c["publisher"]
            for c in cits))
        completion = spec["id"] == lesson["completion"]
        if res.state == "unbound":
            plan_text = "couldn't check: nothing recorded to check against"
        elif spec["kind"] == "absent":
            about = result.bindings.get(spec["start"][5:]) if spec["start"].startswith("role:") \
                else result.bindings.get(spec.get("target", {}).get("role", ""))
            name = label.get(about, about) if about else "this plan"
            rel = spec["path"][0][0]
            if rel == "FOLLOWS":
                plan_text = f"not following “{name}”" if res.holds else f"follows “{name}”"
            elif rel == "WATCHES":
                plan_text = (f"nobody active watching “{name}”" if res.holds
                             else f"“{name}” is watched")
            else:
                plan_text = f"none recorded for “{name}”" if res.holds else f"recorded for “{name}”"
        elif spec["kind"] == "attribute_equals":
            node = res.ids[0] if res.ids else None
            prop = spec["property"]
            val = read(graph, f"MATCH (n {{id: $id}}) RETURN n.{prop}", {"id": node}) if node else []
            shown = val[0][0] if val else None
            plan_text = f"{prop.replace('_', ' ')}: {shown}"
        elif res.holds:
            plan_text = "; ".join(label.get(i, i) for i in res.ids[:2])
        else:
            plan_text = "not in the plan yet" if completion else "not in the plan"
        rows.append(Row(spec["id"], spec["text"], source, plan_text, res.state,
                        spec["kind"] == "absent", completion))
    return rows
