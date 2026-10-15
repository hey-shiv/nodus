"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ErrorNote, LevelTag, Loading } from "@/components/ui";
import { api, type Level } from "@/lib/api";

type Person = { id: string; name: string };
type Msg = { echo_id: string; plan_id: string; plan: string; lesson_id: string; lesson: string; origin: string;
  level: Level; k: number; n: number; headsup: string; silences: string[] | null; status: string;
  outcome: string | null; reason: string | null; is_owner: boolean };

const OUTCOMES: [string, string][] = [["heeded", "Change the plan"], ["dismissed", "Dismiss"], ["escalated", "Escalate"]];

export default function InboxClient() {
  const [people, setPeople] = useState<Person[]>([]);
  const [who, setWho] = useState("p-lena");
  const [msgs, setMsgs] = useState<Msg[] | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(async (person: string) => {
    try { setMsgs(await api<Msg[]>(`/api/inbox?person=${person}`)); }
    catch (e) { setError((e as Error).message); }
  }, []);

  useEffect(() => { api<Person[]>("/api/people").then(setPeople).catch((e) => setError((e as Error).message)); }, []);
  useEffect(() => {
    let cancelled = false;
    api<Msg[]>(`/api/inbox?person=${who}`)
      .then((m) => { if (!cancelled) setMsgs(m); })
      .catch((e) => { if (!cancelled) setError((e as Error).message); });
    return () => { cancelled = true; };
  }, [who]);

  if (error) return <ErrorNote error={error} />;
  const name = people.find((p) => p.id === who)?.name ?? "";

  return (
    <div className="mx-auto max-w-[1240px] px-5 pt-8">
      <label className="flex max-w-sm flex-col gap-2"><span className="label">Viewing as</span>
        <select value={who} onChange={(e) => setWho(e.target.value)}>
          {people.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </label>
      <h1 className="sheet-title mt-10 text-[clamp(2.2rem,5.4vw,4.4rem)]">{name ? `${name}'s inbox` : "Inbox"}</h1>
      {!msgs ? <Loading what="messages" /> : msgs.length === 0 ? (
        <p className="prose-body mt-6">Nothing here. NODUS writes when a plan this person owns echoes a lesson, or when they are invited as a witness.</p>
      ) : (
        <ol className="mt-8">
          {msgs.map((m) => <Message key={m.echo_id} m={m} me={name} onDone={() => load(who)} />)}
        </ol>
      )}
    </div>
  );
}

function Message({ m, me, onDone }: { m: Msg; me: string; onDone: () => void }) {
  const [outcome, setOutcome] = useState("heeded");
  const [reason, setReason] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true); setErr("");
    try {
      await api("/api/answer", { method: "POST", body: JSON.stringify({ echo_id: m.echo_id, person: me, outcome, reason }) });
      onDone();
    } catch (x) { setErr((x as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <li className="border-t border-ink py-6">
      <p className="label">{m.is_owner ? "Heads-up on your plan" : "You're invited as a witness"}</p>
      <h2 className="mt-1 text-2xl font-bold tracking-tight text-ink">{m.plan}</h2>
      <p className="mt-2"><LevelTag level={m.level} /> <span className="font-mono text-sm">{m.k} OF {m.n}</span> “{m.lesson}” <span className="label">{m.origin === "public" ? "public lesson" : "internal lesson"}</span></p>
      <p className="prose-body mt-3">{m.headsup}</p>
      {(m.silences ?? []).map((s) => <p key={s} className="silence mt-2">{s}</p>)}
      <div className="mt-4 flex flex-wrap items-start gap-4">
        <Link className="btn" href={`/demo/echo?plan=${m.plan_id}&lesson=${m.lesson_id}`}><span>Open echo</span></Link>
        {m.outcome ? (
          <p className="label self-center">Recorded : {m.outcome}{m.reason ? ` (${m.reason})` : ""}</p>
        ) : m.is_owner ? (
          <form onSubmit={submit} className="frame flex flex-1 flex-col gap-3 p-4">
            <fieldset className="flex flex-wrap gap-2">
              <legend className="label mb-2">What will you do?</legend>
              {OUTCOMES.map(([v, t]) => (
                <label key={v} className={`btn ${outcome === v ? "btn-primary" : ""}`}>
                  <input type="radio" className="sr-only" name={`o-${m.echo_id}`} checked={outcome === v} onChange={() => setOutcome(v)} />
                  <span>{t}</span>
                </label>
              ))}
            </fieldset>
            <label className="flex flex-col gap-1">
              <span className="label">Reason {outcome === "dismissed" ? "(required to dismiss)" : "(optional)"}</span>
              <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} aria-describedby={err ? `e-${m.echo_id}` : undefined} />
            </label>
            {err && <p id={`e-${m.echo_id}`} role="alert" className="text-sm text-oxide">Not recorded: {err}.</p>}
            <button className="btn btn-primary self-start" disabled={busy}><span>{busy ? "Recording" : "Record my answer"}</span><span aria-hidden="true">→</span></button>
          </form>
        ) : <p className="label self-center">Witnesses advise; the plan owner records what happens.</p>}
      </div>
    </li>
  );
}
