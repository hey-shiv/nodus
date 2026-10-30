"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import AgentTrace from "@/components/AgentTrace";
import { ErrorNote, LevelTag, Loading, Spec, Strip } from "@/components/ui";
import { api, resetSandbox, type Level } from "@/lib/api";

type LessonRow = { lesson: string; name: string; origin: string; k: number; n: number; level: Level; warning: boolean; strip: string };
type Plan = { id: string; title: string; summary: string; risk: string; owner: string; lessons: LessonRow[]; at_risk: boolean };
type Overview = { plans: Plan[]; lessons: number; one_step: number; full: number; at_risk: number };
type Detail = { steps: { id: string; kind: string; scope: string }[]; follows_canary: boolean; peer_review: boolean };
type Raised = { lesson: string; name: string; level: Level; k: number; n: number };

function headline(o: Overview) {
  const total = o.plans.length;
  if (o.one_step) return `${o.one_step} of ${total} plans ${o.one_step === 1 ? "is" : "are"} one step from a known failure`;
  if (o.full) return `${o.full} of ${total} plans ${o.full === 1 ? "has" : "have"} the whole shape of a known failure`;
  return "No plan echoes a known failure right now";
}

export default function PlansClient() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState("");
  const [planId, setPlanId] = useState("plan-hero");
  const [detail, setDetail] = useState<Detail | null>(null);
  const [form, setForm] = useState({ follows: false, review: false, kind: "", scope: "subset", remove: [] as string[] });
  const [saving, setSaving] = useState(false);
  const [raised, setRaised] = useState<Raised[] | null>(null);
  const [saveError, setSaveError] = useState("");

  const load = useCallback(async () => {
    try { setData(await api<Overview>("/api/plans")); setError(""); }
    catch (e) { setError((e as Error).message); }
  }, []);

  const loadDetail = useCallback(async (id: string) => {
    const d = await api<Detail>(`/api/plans/${id}`);
    setDetail(d);
    setForm({ follows: d.follows_canary, review: d.peer_review, kind: "", scope: "subset", remove: [] });
  }, []);

  // Initial load. State is set only in the promise callbacks, and a late response for a
  // previous plan is ignored (cancelled), so a fast click can't show stale data.
  useEffect(() => {
    let cancelled = false;
    api<Overview>("/api/plans")
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError((e as Error).message); });
    return () => { cancelled = true; };
  }, []);
  useEffect(() => {
    let cancelled = false;
    api<Detail>(`/api/plans/${planId}`)
      .then((d) => {
        if (cancelled) return;
        setDetail(d);
        setForm({ follows: d.follows_canary, review: d.peer_review, kind: "", scope: "subset", remove: [] });
      })
      .catch((e) => { if (!cancelled) setError((e as Error).message); });
    return () => { cancelled = true; };
  }, [planId]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true); setSaveError("");
    try {
      const r = await api<{ raised: Raised[] }>(`/api/plans/${planId}`, {
        method: "POST",
        body: JSON.stringify({ follows_canary: form.follows, peer_review: form.review,
          add_step: form.kind ? { kind: form.kind, scope: form.scope } : null, remove_steps: form.remove }),
      });
      setRaised(r.raised);
      await Promise.all([load(), loadDetail(planId)]);
    } catch (err) { setRaised(null); setSaveError((err as Error).message); }
    finally { setSaving(false); }
  }

  if (error) return <ErrorNote error={error} />;
  if (!data) return <Loading what="plans" />;
  const plan = data.plans.find((p) => p.id === planId);

  return (
    <div className="mx-auto max-w-[1180px] px-6 pt-10">
      <h1 className="display max-w-[20ch] text-[clamp(2.2rem,4.4vw,3.6rem)]">{headline(data)}</h1>
      <p className="prose-body mt-4">
        These are the plans at Tern &amp; Tally Freight, a made-up company. NODUS checks each one against {data.lessons} lessons
        from past failures, by how the plan is set up rather than how it&apos;s worded.
      </p>

      <section className="card mt-8 grid gap-6 p-6 md:grid-cols-3" aria-label="Start here">
        {[["Look at the first plan", "“Refresh tariff tables for every depot” is one step away from three past failures."],
          ["See why", "Press “See why” to put the plan beside the failure it resembles, fact by fact."],
          ["Make it worse", "Scroll down, add a rollout to every target, and save. Watch the warning change."]].map(([t, d], i) => (
          <div key={t} className="flex gap-4">
            <span className="grid size-8 shrink-0 place-items-center rounded-full bg-peri-soft font-medium text-peri-ink">{i + 1}</span>
            <div><p className="font-medium">{t}</p><p className="text-sm text-muted">{d}</p></div>
          </div>
        ))}
      </section>

      <ol className="mt-8 flex flex-col gap-4">
        {data.plans.map((p) => (
          <li key={p.id} className="card p-6">
            <h2 className="font-serif text-[1.6rem] leading-tight">{p.title}</h2>
            <div className="mt-4 grid gap-6 md:grid-cols-[minmax(0,0.9fr)_minmax(0,1.4fr)]">
              <Spec rows={[["Owner", p.owner ?? "none recorded"], ["Filed as", p.risk], ["Note", p.summary]]} />
              <ul className="flex flex-col gap-2">
                {p.lessons.filter((l) => l.level !== "ignore").map((l) => (
                  <li key={l.lesson} className="grid grid-cols-[96px_1fr] items-center gap-3 md:grid-cols-[96px_1fr_auto_auto]">
                    <Strip html={l.strip} />
                    <span><span className="font-medium">{l.k} of {l.n}</span> facts of “{l.name}” <span className="text-sm text-muted">({l.origin === "public" ? "a famous outage" : "this company's own history"})</span></span>
                    <LevelTag level={l.level} />
                    {l.warning ? (
                      <Link className="btn !min-h-9 !px-4 !text-sm" href={`/demo/echo?plan=${p.id}&lesson=${l.lesson}`}>See why</Link>
                    ) : <span />}
                  </li>
                ))}
              </ul>
            </div>
          </li>
        ))}
      </ol>

      <section className="card mt-12 p-8" aria-labelledby="edit-title">
        <h2 id="edit-title" className="section-title text-[clamp(1.8rem,3vw,2.4rem)]">Change a plan <em>and watch what happens</em></h2>
        <p className="prose-body mt-3">Edit a plan as its owner would. Saving runs NODUS on it straight away.</p>
        <form onSubmit={save} className="mt-6 grid gap-6 md:grid-cols-2">
          <div className="flex flex-col gap-4">
            <label className="flex flex-col gap-2">
              <span className="label">Plan</span>
              <select value={planId} onChange={(e) => { setPlanId(e.target.value); setRaised(null); setSaveError(""); }}>
                {data.plans.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
              </select>
            </label>
            <p className="font-mono text-sm"><span className="label">Steps : </span>
              {detail?.steps.length ? detail.steps.map((s) => `${s.kind} (${s.scope === "all" ? "every target" : "some targets"})`).join("; ") : "none yet"}</p>
            <label className="flex items-center gap-3">
              <input type="checkbox" checked={form.follows} onChange={(e) => setForm({ ...form, follows: e.target.checked })} className="size-5 accent-ink" />
              Follows the canary procedure
            </label>
            <label className="flex items-center gap-3">
              <input type="checkbox" checked={form.review} onChange={(e) => setForm({ ...form, review: e.target.checked })} className="size-5 accent-ink" />
              Peer review sign-off before release
            </label>
          </div>
          <div className="flex flex-col gap-4">
            <fieldset className="flex flex-col gap-2">
              <legend className="label mb-2">Add a step to the plan</legend>
              <div className="flex flex-wrap gap-2">
                {["", "canary", "test", "review", "rollout"].map((k) => (
                  <label key={k || "none"} className={`btn !min-h-9 !px-4 !text-sm ${form.kind === k ? "btn-primary" : ""}`}>
                    <input type="radio" name="kind" className="sr-only" checked={form.kind === k} onChange={() => setForm({ ...form, kind: k })} />
                    <span>{k || "nothing"}</span>
                  </label>
                ))}
              </div>
            </fieldset>
            <fieldset className="flex flex-col gap-2">
              <legend className="label mb-2">Scope of the new step</legend>
              <div className="flex flex-wrap gap-2">
                {[["subset", "some targets"], ["all", "every target"]].map(([v, t]) => (
                  <label key={v} className={`btn !min-h-9 !px-4 !text-sm ${form.scope === v ? "btn-primary" : ""}`}>
                    <input type="radio" name="scope" className="sr-only" checked={form.scope === v} onChange={() => setForm({ ...form, scope: v })} />
                    <span>{t}</span>
                  </label>
                ))}
              </div>
            </fieldset>
            {detail && detail.steps.length > 0 && (
              <fieldset className="flex flex-col gap-2">
                <legend className="label mb-2">Remove steps</legend>
                {detail.steps.map((s) => (
                  <label key={s.id} className="flex items-center gap-3 text-sm">
                    <input type="checkbox" className="size-4 accent-ink" checked={form.remove.includes(s.id)}
                      onChange={(e) => setForm({ ...form, remove: e.target.checked ? [...form.remove, s.id] : form.remove.filter((x) => x !== s.id) })} />
                    {s.kind} ({s.scope === "all" ? "every target" : "some targets"})
                  </label>
                ))}
              </fieldset>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-4 md:col-span-2">
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : "Save plan"}</button>
            <button type="button" className="btn" onClick={async () => { await resetSandbox(); setRaised(null); setSaveError(""); await load(); await loadDetail(planId); }}>
              Start over with a fresh copy
            </button>
          </div>
        </form>
        {saveError && <p role="alert" className="quote mt-6 text-terra-ink">Not saved: {saveError}</p>}
        {raised && (
          <div role="status" className="quote mt-6">
            <p className="label mb-1">Saved “{plan?.title}”</p>
            {raised.length ? (
              <p>NODUS raised: {raised.map((r, i) => (
                <span key={r.lesson}>{i > 0 && "; "}{r.name} (<LevelTag level={r.level} />)</span>))}</p>
            ) : <p>No lesson echoes this plan now.</p>}
          </div>
        )}
        <details className="mt-8">
          <summary className="cursor-pointer text-[15px] font-medium text-peri-ink">Show the agent’s work (for the technically curious)</summary>
          <AgentTrace planId={planId} />
        </details>
      </section>
    </div>
  );
}
