"use client";
import { useCallback, useEffect, useState } from "react";
import { ErrorNote, Loading, Spec } from "@/components/ui";
import { api } from "@/lib/api";

type Citation = { quote: string; title: string; url: string | null; publisher: string };
type Lesson = { id: string; name: string; origin: string; status: string; version: number; approved_by: string | null;
  track: { raised: number; heeded: number; dismissed: number; escalated: number; open: number; reasons: string[] };
  conditions: { id: string; text: string; kind: string; citations: Citation[] }[] };

export default function LessonsClient() {
  const [lessons, setLessons] = useState<Lesson[] | null>(null);
  const [error, setError] = useState("");
  const [reviewer, setReviewer] = useState("Visitor");

  const load = useCallback(async () => {
    try { setLessons(await api<Lesson[]>("/api/lessons")); } catch (e) { setError((e as Error).message); }
  }, []);
  useEffect(() => {
    let cancelled = false;
    api<Lesson[]>("/api/lessons")
      .then((l) => { if (!cancelled) setLessons(l); })
      .catch((e) => { if (!cancelled) setError((e as Error).message); });
    return () => { cancelled = true; };
  }, []);

  async function decide(id: string, approve: boolean) {
    await api(`/api/lessons/${id}`, { method: "POST", body: JSON.stringify({ approve, by: reviewer || "Visitor" }) });
    load();
  }

  if (error) return <ErrorNote error={error} />;
  if (!lessons) return <Loading what="lessons" />;
  return (
    <div className="mx-auto max-w-[1240px] px-5 pt-8">
      <h1 className="sheet-title text-[clamp(2.2rem,5.4vw,4.4rem)]">Lessons NODUS watches for</h1>
      <p className="prose-body mt-4">A lesson is a few conditions about roles and relationships. Each condition quotes the sentence
        it comes from, checked word for word. Nothing is matched until a person approves it.</p>
      <label className="mt-6 flex max-w-sm flex-col gap-2"><span className="label">Your name, for approvals</span>
        <input type="text" value={reviewer} onChange={(e) => setReviewer(e.target.value)} />
      </label>
      <ol className="mt-8">
        {lessons.map((l) => (
          <li key={l.id} className="border-t border-ink py-6">
            <h2 className="text-2xl font-bold tracking-tight text-ink">{l.name}</h2>
            <div className="mt-3 max-w-[760px]">
              <Spec rows={[
                ["Source", l.origin === "public" ? "public post-mortems" : "internal post-mortem (synthetic)"],
                ["Status", `${l.status}, version ${l.version}${l.approved_by && l.status === "approved" ? `, by ${l.approved_by}` : ""}`],
                ["Track record", `raised ${l.track.raised}, heeded ${l.track.heeded}, dismissed ${l.track.dismissed}, escalated ${l.track.escalated}, open ${l.track.open}`],
              ]} />
            </div>
            {l.track.reasons.map((r) => <p key={r} className="label mt-2">Dismissed because : {r}</p>)}
            <details className="mt-4">
              <summary className="label cursor-pointer py-2 text-ink">Conditions and sources</summary>
              <ol className="mt-3 flex flex-col gap-4">
                {l.conditions.map((c) => (
                  <li key={c.id} className="grid gap-2 md:grid-cols-[80px_1fr]">
                    <span className="font-mono text-sm text-pencil">{c.id}</span>
                    <div className="flex flex-col gap-2">
                      <p className="font-bold text-ink">{c.text}{c.kind === "absent" ? "  ∅" : ""}</p>
                      {c.citations.map((q, i) => (
                        <blockquote key={i} className="quote"><p>“{q.quote}”</p>
                          <footer className="label mt-2">{q.url ? <a className="underline underline-offset-4" href={q.url}>{q.publisher}</a> : q.publisher}</footer>
                        </blockquote>
                      ))}
                    </div>
                  </li>
                ))}
              </ol>
            </details>
            {l.status !== "approved" && (
              <div className="mt-4 flex gap-3">
                <button className="btn btn-primary" onClick={() => decide(l.id, true)}><span>Approve</span><span aria-hidden="true">→</span></button>
                <button className="btn" onClick={() => decide(l.id, false)}><span>Reject</span></button>
              </div>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
