"use client";
// Talks to the NODUS Python API. Each visitor gets a private sandbox graph; its id is kept in
// localStorage and sent as X-Nodus-Sandbox. An expired sandbox is replaced automatically.
// If /api/health fails, the demo switches to the recorded run in lib/replay.ts.

import * as replay from "./replay";

const KEY = "nodus-sandbox";

let mode: Promise<boolean> | null = null;
export function isReplay(): Promise<boolean> {
  return (mode ??= fetch("/api/health").then((r) => !r.ok, () => true));
}

async function newSandbox(): Promise<string> {
  const r = await fetch("/api/sandbox", { method: "POST" });
  if (!r.ok) throw new Error("The demo database is unavailable right now.");
  const { sandbox } = await r.json();
  try { localStorage.setItem(KEY, sandbox); } catch {}
  return sandbox;
}

export async function sandboxId(): Promise<string> {
  if (await isReplay()) return "replay";
  let id: string | null = null;
  try { id = localStorage.getItem(KEY); } catch {}
  return id ?? newSandbox();
}

export async function resetSandbox(): Promise<string> {
  if (await isReplay()) { replay.reset(); return "replay"; }
  try { localStorage.removeItem(KEY); } catch {}
  return newSandbox();
}

export async function api<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  if (await isReplay()) return replay.request<T>(path, init);
  const sbx = await sandboxId();
  const r = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", "X-Nodus-Sandbox": sbx, ...(init.headers ?? {}) },
  });
  if (r.status === 401 && retry) {
    await resetSandbox();
    return api<T>(path, init, false);
  }
  if (!r.ok) {
    const detail = await r.json().catch(() => ({}));
    throw new Error(typeof detail.detail === "string" ? detail.detail : `Request failed (${r.status})`);
  }
  return r.json();
}

/** Audio for the echo melody, or null when the recorded run has none for this pair. */
export async function melodyUrl(plan: string, lesson: string, resolve: boolean): Promise<string | null> {
  if (await isReplay()) return replay.melodyUrl(plan, lesson, resolve);
  return `/api/melody?plan=${plan}&lesson=${lesson}&resolve=${resolve}&sbx=${await sandboxId()}`;
}

/** The AG-UI event stream for one agent run on a plan. */
export async function agentStream(planId: string): Promise<Response> {
  if (await isReplay()) return fetch(await replay.agentUrl(planId));
  return fetch("/api/agent", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Nodus-Sandbox": await sandboxId(), Accept: "text/event-stream" },
    body: JSON.stringify({ threadId: `plan-${planId}`, runId: crypto.randomUUID().slice(0, 12),
      state: { plan_id: planId }, messages: [], tools: [], context: [], forwardedProps: {} }),
  });
}

export type Level = "full" | "foresight" | "strong" | "note" | "ignore";
export const LEVEL_WORDS: Record<Level, string> = {
  full: "Full shape", foresight: "One step away", strong: "Strong echo", note: "Note", ignore: "Quiet",
};
