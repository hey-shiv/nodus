"use client";
// Recorded run: when the live database is offline, the demo reads real API responses captured
// by scripts/record_replay.py from web/public/replay. Every plan setup one save away from the
// starting company is recorded; the visitor's current change and answers live in sessionStorage.

type Ref = string | { e: number; d: string };
type Fresh = { reads: Record<string, Ref>; melody: Record<string, string>; configs: Record<string, string> };
type Setups = Record<string, { save: string; reads: Record<string, Ref> }>;
type Answer = { outcome: string; reason: string };
type State = { edit: { plan: string; cfg: string } | null; answers: Record<string, Answer> };

const BASE = "/replay";
const KEY = "nodus-replay";
const json = (url: string) => fetch(url).then((r) => {
  if (!r.ok) throw new Error("The recorded demo could not load.");
  return r.json();
});

let fresh: Promise<Fresh> | null = null;
const setups = new Map<string, Promise<Setups>>();
const loadFresh = () => (fresh ??= json(`${BASE}/fresh.json`));
function loadSetups(plan: string) {
  if (!setups.has(plan)) setups.set(plan, json(`${BASE}/plans/${plan}.json`));
  return setups.get(plan)!;
}

function getState(): State {
  try {
    const s = sessionStorage.getItem(KEY);
    if (s) return JSON.parse(s);
  } catch {}
  return { edit: null, answers: {} };
}
function setState(s: State) {
  try { sessionStorage.setItem(KEY, JSON.stringify(s)); } catch {}
}
export function reset() { setState({ edit: null, answers: {} }); }

async function ref(path: string): Promise<Ref> {
  const { edit } = getState();
  if (edit) {
    const r = (await loadSetups(edit.plan))[edit.cfg]?.reads[path];
    if (r !== undefined) return r;
  }
  const r = (await loadFresh()).reads[path];
  if (r === undefined) throw new Error("This view isn't part of the recorded run.");
  return r;
}

const bodies = new Map<string, Promise<unknown>>();
async function body<T>(r: Ref): Promise<T> {
  if (typeof r !== "string") throw new Error(r.d || `Request failed (${r.e})`);
  if (!bodies.has(r)) bodies.set(r, json(`${BASE}/r/${r}`));
  return structuredClone(await bodies.get(r)) as T;
}

type Msg = { echo_id: string; outcome: string | null; reason: string | null; status: string };
type Track = { raised: number; heeded: number; dismissed: number; escalated: number; open: number; reasons: string[] };

// Answers aren't recorded (reasons are free text), so they are laid over the recorded reads.
function withAnswers(path: string, data: unknown) {
  const { answers } = getState();
  if (path.startsWith("/api/inbox")) {
    return (data as Msg[]).map((m) => answers[m.echo_id] && !m.outcome
      ? { ...m, ...answers[m.echo_id], status: "acknowledged" } : m);
  }
  if (path === "/api/lessons") {
    return (data as { id: string; track: Track }[]).map((l) => {
      const track = { ...l.track, reasons: [...l.track.reasons] };
      for (const [eid, a] of Object.entries(answers)) {
        if (eid.split(":")[1] !== l.id) continue;          // echo:<lesson>:<plan>
        track.open = Math.max(0, track.open - 1);
        track[a.outcome as "heeded" | "dismissed" | "escalated"] += 1;
        if (a.outcome === "dismissed") track.reasons.push(a.reason);
      }
      return { ...l, track };
    });
  }
  return data;
}

type Step = { id: string; kind: string; scope: string };
type SaveBody = { follows_canary: boolean; peer_review: boolean; add_step: { kind: string; scope: string } | null; remove_steps: string[] };

async function save(plan: string, b: SaveBody) {
  const now = await body<{ steps: Step[] }>(await ref(`/api/plans/${plan}`));
  const steps = now.steps.filter((s) => !b.remove_steps.includes(s.id)).map((s) => `${s.kind}-${s.scope}`);
  if (b.add_step) steps.push(`${b.add_step.kind}-${b.add_step.scope}`);
  const cfg = `f${+b.follows_canary}r${+b.peer_review}:${steps.sort().join(",")}`;
  const setup = (await loadSetups(plan))[cfg];
  if (!setup) {
    throw new Error("That combination isn't in the recorded run. Press “Start over with a fresh copy” and change one thing at a time.");
  }
  const s = getState();
  setState({ ...s, edit: { plan, cfg } });
  return body(setup.save);
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  if (method === "GET") return withAnswers(path, await body(await ref(path))) as T;
  const b = JSON.parse(String(init.body ?? "{}"));
  const plan = path.match(/^\/api\/plans\/([a-z0-9-]+)$/);
  if (plan) return save(plan[1], b) as T;
  if (path === "/api/answer") {
    if (!["heeded", "dismissed", "escalated"].includes(b.outcome)) throw new Error("outcome must be heeded, dismissed or escalated");
    if (b.outcome === "dismissed" && !String(b.reason ?? "").trim()) throw new Error("a dismissal needs a reason");
    const s = getState();
    setState({ ...s, answers: { ...s.answers, [b.echo_id]: { outcome: b.outcome, reason: String(b.reason ?? "") } } });
    return { ok: true } as T;
  }
  if (path.startsWith("/api/lessons/")) return { ok: true } as T;   // every recorded lesson is already approved
  throw new Error("This action isn't part of the recorded run.");
}

export async function melodyUrl(plan: string, lesson: string, resolve: boolean): Promise<string | null> {
  if (getState().edit?.plan === plan) return null;     // recorded for the starting plans only
  const f = (await loadFresh()).melody[`${plan}|${lesson}|${resolve}`];
  return f ? `${BASE}/r/${f}` : null;
}

export async function agentUrl(plan: string): Promise<string> {
  const r = await ref(`agent:${plan}`);
  if (typeof r !== "string") throw new Error("The agent run isn't part of the recorded run.");
  return `${BASE}/r/${r}`;
}
