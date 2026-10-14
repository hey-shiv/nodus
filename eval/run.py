"""Run the declared evaluation. Usage: python -m eval.run dev   |   python -m eval.run test

dev: computes metrics and chooses the baseline threshold (saved to eval/threshold.json).
test: uses the saved threshold; run once. Results are printed as Markdown.
"""
import json
import sys
from pathlib import Path

from eval.generate import COMPLETION, generate
from nodus.baseline import TfIdf, lesson_text
from nodus.db import get_graph
from nodus.lessons import approve, load_lesson_file, load_sources, store
from nodus.loader import load
from nodus.matcher import evaluate
from nodus.severity import is_warning, level

SEEDS = {"dev": 101, "test": 202}
HERE = Path(__file__).resolve().parent
LESSONS = [load_lesson_file(p) for p in sorted((HERE.parent / "data" / "lessons").glob("*.json"))]


def build(split):
    world, plans = generate(SEEDS[split])
    g = get_graph(f"nodus_eval_{split}")
    try:
        g.delete()
    except Exception:
        pass
    load(g, world)
    sources = load_sources()
    for les in LESSONS:
        store(g, les, sources)
        approve(g, les.id, "evaluation")
    return g, plans


def nodus_results(g, plans):
    out = {}
    for p in plans:
        out[p["id"]] = {}
        for les in LESSONS:
            r = evaluate(g, p["id"], les.as_matcher_input())
            out[p["id"]][les.id] = (r.k, r.n, r.missing, level(r.k, r.n, r.missing, les.completion))
    return out


def baseline_scores(plans, dev_plans):
    texts = {les.id: lesson_text(les) for les in LESSONS}
    model = TfIdf(list(texts.values()) + [p["text"] for p in dev_plans])
    return {p["id"]: {lid: model.similarity(p["text"], t) for lid, t in texts.items()} for p in plans}


def score(plans, raised):
    """raised(plan) -> set of lesson ids raised. Returns the declared metrics as (x, y)."""
    fam = lambda f: [p for p in plans if p["family"] == f]
    f1 = sum(p["target"] in raised(p) for p in fam("F1"))
    f2 = sum(bool(raised(p)) for p in fam("F2"))
    f4 = sum(bool(raised(p)) for p in fam("F4"))
    return {"F1 hits": (f1, len(fam("F1"))), "F2 false alarms": (f2, len(fam("F2"))),
            "F4 false alarms": (f4, len(fam("F4")))}


def choose_threshold(plans, scores):
    best = None
    for t in sorted({s for v in scores.values() for s in v.values()}):
        m = score(plans, lambda p: {l for l, s in scores[p["id"]].items() if s >= t})
        value = m["F1 hits"][0] - m["F2 false alarms"][0]
        if best is None or value >= best[0]:
            best = (value, t)
    return best[1]


def main(split):
    g, plans = build(split)
    _, dev_plans = generate(SEEDS["dev"])
    res = nodus_results(g, plans)
    scores = baseline_scores(plans, dev_plans)
    tfile = HERE / "threshold.json"
    if split == "dev":
        t = choose_threshold(plans, scores)
        tfile.write_text(json.dumps({"B2_tfidf": t}))
    else:
        t = json.loads(tfile.read_text())["B2_tfidf"]

    nodus_raised = lambda p: {l for l, (k, n, m, lvl) in res[p["id"]].items() if is_warning(lvl)}
    b2_raised = lambda p: {l for l, s in scores[p["id"]].items() if s >= t}
    m_nodus, m_b2 = score(plans, nodus_raised), score(plans, b2_raised)
    f3 = [p for p in plans if p["family"] == "F3"]
    f3_ok = sum(res[p["id"]][p["target"]][0] == res[p["id"]][p["target"]][1] - 1
                and res[p["id"]][p["target"]][2] == [p["expect"]] for p in f3)

    print(f"## Split: {split} (seed {SEEDS[split]}), synthetic, {len(plans)} plans\n")
    print(f"B2 TF-IDF threshold t = {t:.3f} (chosen on dev)\n")
    print("| Metric | NODUS | B2 keywords (TF-IDF) |\n|---|---|---|")
    for key in m_nodus:
        (a, n), (b, _) = m_nodus[key], m_b2[key]
        print(f"| {key} | {a} of {n} | {b} of {n} |")
    print(f"| F3 foresight (k = n−1 and the right missing condition) | {f3_ok} of {len(f3)} | not applicable |")
    positive = sorted({s for v in scores.values() for s in v.values() if s > 0})
    if positive:
        tp = positive[0]
        m_pos = score(plans, lambda p: {l for l, s in scores[p["id"]].items() if s >= tp})
        print(f"\nDescriptive (not the declared operating point): B2 at the smallest positive "
              f"threshold t = {tp:.3f} gives F1 hits {m_pos['F1 hits'][0]} of {m_pos['F1 hits'][1]}, "
              f"F2 false alarms {m_pos['F2 false alarms'][0]} of {m_pos['F2 false alarms'][1]}, "
              f"F4 false alarms {m_pos['F4 false alarms'][0]} of {m_pos['F4 false alarms'][1]}.")
    print("\n**F5 adversarial cases (descriptive):**\n")
    names = {"a": "trivial change with the full risky shape", "b": "risky shape, risk class not recorded",
             "c": "completion replaced by a partial rollout, still off the procedure"}
    for p in [p for p in plans if p["family"] == "F5"]:
        k, n, missing, lvl = res[p["id"]]["antibody-1"]
        b2 = scores[p["id"]]["antibody-1"]
        print(f"- ({p['expect']}) {names[p['expect']]}: NODUS antibody-1 {k}/{n}, {lvl}, missing "
              f"{missing or 'none'}; B2 similarity {b2:.3f} ({'raised' if b2 >= t else 'quiet'})")
    fails = [(p["id"], p["family"], p["target"]) for p in plans if
             (p["family"] == "F1" and p["target"] not in nodus_raised(p)) or
             (p["family"] in ("F2", "F4") and nodus_raised(p))]
    print(f"\n**NODUS failures on F1/F2/F4:** {fails or 'none'}")
    g.delete()


if __name__ == "__main__":
    main(sys.argv[1])
