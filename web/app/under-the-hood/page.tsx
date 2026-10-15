import Link from "next/link";

export const metadata = { title: "Under the hood: NODUS" };

const PARTS = [
  ["The graph", "FalkorDB holds everything: the made-up company (plans, systems, alert inboxes, people, past incidents), the lessons with the sentences they quote, and the agent's memory of every warning and answer. Remove FalkorDB and nothing can be matched."],
  ["Lessons as data", "Each lesson is 3 to 6 conditions of four kinds: something is present, something is absent, a property has a value, or there is exactly a certain number of something. Every condition quotes its source word for word, checked by a script; a person approves the lesson."],
  ["A compiler, not an AI", "A small compiler turns each condition into one parameterised Cypher query from a hand-written template. Names are checked against the graph model, paths are type-checked, values travel as parameters. No AI writes a query that runs."],
  ["Anchor-first matching", "Every query starts from the plan. When one condition finds something (an alert inbox, a procedure), its id is passed to the next, so “the inbox” means the same inbox throughout. With two candidates, the one giving the most matches wins."],
  ["A published rule", "All conditions true: full shape. All but the lesson's last step: one step away. Otherwise a note or nothing. It's a rule anyone can read, not a judgement."],
  ["The agent and AG-UI", "Saving a plan runs the loop: notice, compare, count, warn, remember. The same run streams as standard AG-UI events, so every graph query appears as a tool call with its arguments and result."],
];

const EVAL = [
  ["Same structure, different words: right lesson raised", "18 of 18", "18 of 18 only at threshold 0; 1 of 18 above it"],
  ["Same words, different structure: false alarms", "0 of 18", "18 of 18"],
  ["Unrelated plans: false alarms", "0 of 10", "10 of 10"],
  ["One condition missing: the right one named", "20 of 20", "not applicable"],
];

const CYPHER = `// "This plan does not follow the staged procedure" (an absence)
MATCH (s:Plan) WHERE s.id = $start
OPTIONAL MATCH (s)-[r1:FOLLOWS]->(t) WHERE t.id = $target
RETURN count(r1) = 0 AS holds, [s.id] AS ids

// "Nobody active is watching that inbox"
MATCH (s) WHERE s.id = $start
OPTIONAL MATCH (s)<-[r1:WATCHES]-(t:Person) WHERE t.active = $tp0
RETURN count(r1) = 0 AS holds, [s.id] AS ids`;

export default function UnderTheHood() {
  return (
    <div className="mx-auto max-w-[1180px] px-6 pt-20">
      <p className="section-title text-center text-[1.6rem] text-ink/45">Building through <em>graphs</em></p>
      <h1 className="display mx-auto mt-10 max-w-[18ch] text-center text-[clamp(2.4rem,4.6vw,3.8rem)]">
        UNDER <em>the</em> HOOD
      </h1>
      <p className="prose-body mx-auto mt-5 text-center">For judges and engineers: how NODUS actually works, what it was tested on,
        and where to read the code.</p>

      <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {PARTS.map(([t, d]) => (
          <div key={t} className="card p-7">
            <h2 className="font-serif text-2xl">{t}</h2>
            <p className="mt-2 text-[15px] leading-relaxed text-muted">{d}</p>
          </div>
        ))}
      </div>

      <section className="mt-20 grid items-start gap-10 md:grid-cols-[1fr_1.2fr]">
        <div>
          <span className="label">The real queries</span>
          <h2 className="section-title mt-3 text-[clamp(2rem,3.2vw,2.6rem)]">Two conditions, <em>as they run</em></h2>
          <p className="prose-body mt-4">These are produced by the compiler for the demo plan. Relationships are always named when
            counted: we found that FalkorDB counts two parallel unnamed relationships as one.</p>
          <a className="btn mt-6" href="https://github.com/hey-shiv/nodus/blob/main/nodus/compiler.py">Read the compiler ↗</a>
        </div>
        <pre className="card overflow-x-auto p-6 font-mono text-[13px] leading-relaxed text-ink">{CYPHER}</pre>
      </section>

      <section className="mt-20">
        <span className="label">Evaluation, declared before it was run</span>
        <h2 className="section-title mt-3 text-[clamp(2rem,3.2vw,2.6rem)]">Synthetic test, <em>run once</em></h2>
        <div className="card mt-6 overflow-x-auto p-2">
          <table className="w-full min-w-[640px] border-collapse text-[15px]">
            <thead>
              <tr className="text-left">
                <th className="label px-4 py-3 font-medium">Test split</th>
                <th className="label px-4 py-3 font-medium">NODUS</th>
                <th className="label px-4 py-3 font-medium">Keyword search</th>
              </tr>
            </thead>
            <tbody>
              {EVAL.map(([a, b, c]) => (
                <tr key={a} className="border-t border-line">
                  <td className="px-4 py-3">{a}</td><td className="px-4 py-3 font-medium">{b}</td><td className="px-4 py-3 text-muted">{c}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="prose-body mt-5">The test plans are generated from the same definitions as the lessons, so this shows the queries
          implement the lessons and that wording is neither needed nor enough. It is not evidence of accuracy on real company data.
          Full details are in <a className="underline underline-offset-4" href="https://github.com/hey-shiv/nodus/blob/main/eval/RESULTS.md">eval/RESULTS.md</a>.</p>
      </section>

      <section className="mt-20 grid gap-5 md:grid-cols-3">
        {[["Code", "Python engine, FastAPI service, this Next.js site, 129 tests.", "https://github.com/hey-shiv/nodus"],
          ["Graph model", "Every node and relationship, and the condition each one exists for.", "https://github.com/hey-shiv/nodus/blob/main/docs/graph-model.md"],
          ["Build diary", "Every step, decision, problem and fix, written as it happened.", "https://github.com/hey-shiv/nodus/tree/main/docs/diary"]].map(([t, d, href]) => (
          <a key={t} href={href} className="card block p-7 hover:border-ink/30">
            <h3 className="font-serif text-2xl">{t} ↗</h3><p className="mt-2 text-[15px] text-muted">{d}</p>
          </a>
        ))}
      </section>
      <div className="mt-16 text-center"><Link href="/demo" className="btn btn-primary">Try the live demo</Link></div>
    </div>
  );
}
