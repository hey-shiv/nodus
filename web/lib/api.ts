"use client";
// Talks to the NODUS Python API. Each visitor gets a private sandbox graph; its id is kept in
// localStorage and sent as X-Nodus-Sandbox. An expired sandbox is replaced automatically.

const KEY = "nodus-sandbox";

async function newSandbox(): Promise<string> {
  const r = await fetch("/api/sandbox", { method: "POST" });
  if (!r.ok) throw new Error("The demo database is unavailable right now.");
  const { sandbox } = await r.json();
  try { localStorage.setItem(KEY, sandbox); } catch {}
  return sandbox;
}

export async function sandboxId(): Promise<string> {
  let id: string | null = null;
  try { id = localStorage.getItem(KEY); } catch {}
  return id ?? newSandbox();
}

export async function resetSandbox(): Promise<string> {
  try { localStorage.removeItem(KEY); } catch {}
  return newSandbox();
}

export async function api<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
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

export type Level = "full" | "foresight" | "strong" | "note" | "ignore";
export const LEVEL_WORDS: Record<Level, string> = {
  full: "Full shape", foresight: "One step away", strong: "Strong echo", note: "Note", ignore: "Quiet",
};
