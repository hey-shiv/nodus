"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorNote, LevelTag, Loading, Spec, Svg } from "@/components/ui";
import { api, melodyUrl, type Level } from "@/lib/api";

type Citation = { doc: string; title: string; url: string | null; origin: string; quote: string; publisher: string };
type Echo = {
  plan: { id: string; title: string }; lesson: { id: string; name: string; origin: string };
  k: number; n: number; level: Level; completion: string; completion_missing: boolean; svg: string;
  headsup: { text: string; silences: string[]; status: string; outcome: string | null; seen: number } | null;
  witness: { name: string; reason: string } | null; sources: { publisher: string; title: string; url: string }[];
  conditions: { id: string; text: string; kind: string; citations: Citation[] }[];
  lessons: { id: string; name: string }[];
};
type Overview = { plans: { id: string; title: string }[] };

export default function EchoClient() {
  const params = useSearchParams();
  const router = useRouter();
  const plan = params.get("plan") ?? "plan-hero";
  const lesson = params.get("lesson") ?? "antibody-1";
  const key = `${plan}|${lesson}`;
  const [loaded, setLoaded] = useState<{ key: string; echo: Echo } | null>(null);
  const [plans, setPlans] = useState<Overview["plans"]>([]);
  const [audio, setAudio] = useState<(string | null)[]>([null, null]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    Promise.all([api<Echo>(`/api/echo?plan=${plan}&lesson=${lesson}`), api<Overview>("/api/plans"),
      melodyUrl(plan, lesson, false), melodyUrl(plan, lesson, true)])
      .then(([e, o, a, b]) => { if (!cancelled) { setLoaded({ key: `${plan}|${lesson}`, echo: e }); setPlans(o.plans); setAudio([a, b]); } })
      .catch((e) => { if (!cancelled) setError((e as Error).message); });
    return () => { cancelled = true; };
  }, [plan, lesson]);

  if (error) return <ErrorNote error={error} />;
  if (!loaded || loaded.key !== key) return <Loading what="the echo" />;
  const data = loaded.echo;
  const go = (p: string, l: string) => router.push(`/demo/echo?plan=${p}&lesson=${l}`);
  const title = data.level === "foresight" ? `One step from “${data.lesson.name}”`
    : data.level === "full" ? `The whole shape of “${data.lesson.name}”`
    : `${data.k} of ${data.n} conditions of “${data.lesson.name}”`;

  return (
    <div className="mx-auto max-w-[1240px] px-5 pt-8">
      <div className="grid gap-3 md:grid-cols-2">
        <label className="flex flex-col gap-2"><span className="label">Plan</span>
          <select value={plan} onChange={(e) => go(e.target.value, lesson)}>
            {plans.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-2"><span className="label">Lesson</span>
          <select value={lesson} onChange={(e) => go(plan, e.target.value)}>
            {data.lessons.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </label>
      </div>

      <h1 className="sheet-title mt-10 max-w-[18ch] text-[clamp(2.2rem,5.4vw,4.4rem)]">{title}</h1>
      <p className="prose-body mt-4">
        {data.level === "foresight" ? <>{data.k} of {data.n} conditions already hold. The remaining one is the step that would
          complete the failure: <strong>{data.completion.toLowerCase()}</strong>.</> :
          data.level === "full" ? "Every condition holds, including the final step." : <>Level: <LevelTag level={data.level} /></>}
      </p>
      <div className="mt-6 max-w-[760px]">
        <Spec rows={[
          ["Plan", data.plan.title],
          ["Lesson", `${data.lesson.name} (${data.lesson.origin === "public" ? "public" : "internal"})`],
          ["Match", `${data.k} of ${data.n} conditions`],
          ["Completion", data.completion + (data.completion_missing ? " (not taken yet)" : ""), ["foresight", "full"].includes(data.level)],
          ["Sources", data.sources.map((s) => s.publisher).join(", ") || "internal post-mortem"],
        ]} />
      </div>

      <figure className="frame mt-10 p-3 md:p-6">
        <Svg html={data.svg} label={`${data.lesson.name} beside ${data.plan.title}`} />
        <figcaption className="mt-4 text-sm text-pencil">
          A filled dot with a tick means the fact is true for this plan. A dot with a slash means something is not
          recorded at all. The dashed red ring is the step that would complete the failure. An empty ring means the fact
          isn’t there. Drawn only from what NODUS found.
        </figcaption>
      </figure>

      <section className="mt-10 grid gap-6 md:grid-cols-2" aria-label="Hear it">
        <div className="flex flex-col gap-2">
          <span className="label">What the plan already has</span>
          <p className="text-sm">One note per condition that holds, a short silence for each ∅, the completion note held back.</p>
          {audio[0] ? <audio controls preload="none" src={audio[0]} /> : <p className="label">Not in the recorded run.</p>}
        </div>
        <div className="flex flex-col gap-2">
          <span className="label">{data.completion_missing ? "Resolved: the step not to take" : "Already resolved"}</span>
          <p className="text-sm">{data.completion_missing ? "The same phrase if the plan took the completion step." : "The completion step is already in the plan."}</p>
          {data.completion_missing && audio[1] && <audio controls preload="none" src={audio[1]} />}
        </div>
      </section>

      <section className="mt-14 border-t border-ink pt-6">
        <h2 className="section-title text-[clamp(1.6rem,3vw,2.4rem)]">What NODUS told the owner</h2>
        {data.headsup ? (
          <div className="mt-4 flex flex-col gap-3">
            <p className="prose-body">{data.headsup.text}</p>
            {data.headsup.silences.map((s) => <p key={s} className="silence">{s}</p>)}
            <p className="label">Status : {data.headsup.status}{data.headsup.outcome ? `, outcome: ${data.headsup.outcome}` : ""}</p>
          </div>
        ) : <p className="prose-body mt-4">No heads-up for this pair: NODUS writes one when a saved plan reaches warning level.</p>}
      </section>

      <section className="mt-14 border-t border-ink pt-6">
        <h2 className="section-title text-[clamp(1.6rem,3vw,2.4rem)]">{data.lesson.origin === "public" ? "Where this lesson comes from" : "Who saw it coming"}</h2>
        {data.lesson.origin === "public" ? (
          <p className="prose-body mt-4">Public post-mortems. Their witnesses are the documents themselves: NODUS never contacts people at other companies.</p>
        ) : (
          <p className="prose-body mt-4">{data.witness ? <>Invited: <strong>{data.witness.name}</strong>, who {data.witness.reason}. An invitation asks for advice; it is not a verdict on anyone.</> : "No witness available."}</p>
        )}
        <ol className="mt-6 flex flex-col gap-5">
          {data.conditions.map((c) => (
            <li key={c.id} className="grid gap-2 md:grid-cols-[80px_1fr]">
              <span className="font-mono text-sm text-pencil">{c.id}</span>
              <div className="flex flex-col gap-2">
                <p className="font-bold text-ink">{c.text}{c.kind === "absent" ? "  ∅" : ""}</p>
                {c.citations.map((q, i) => (
                  <blockquote key={i} className="quote">
                    <p>“{q.quote}”</p>
                    <footer className="label mt-2">{q.url ? <a className="underline underline-offset-4" href={q.url}>{q.publisher}: {q.title}</a> : `${q.publisher}: ${q.title}`}</footer>
                  </blockquote>
                ))}
              </div>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
