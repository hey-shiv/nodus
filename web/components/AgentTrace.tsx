"use client";
// Runs the NODUS agent on a plan and shows its AG-UI event stream as it arrives
// (github.com/ag-ui-protocol/ag-ui). Each graph query is a TOOL_CALL with its result.
import { useState } from "react";
import { sandboxId } from "@/lib/api";

type Ev = { type: string; [k: string]: unknown };
type Line = { kind: "step" | "call" | "state" | "text" | "run" | "error"; text: string; detail?: string };

function describe(ev: Ev, args: Map<string, string>): Line | null {
  switch (ev.type) {
    case "RUN_STARTED": return { kind: "run", text: `RUN_STARTED  run ${ev.runId}` };
    case "STEP_STARTED": return { kind: "step", text: String(ev.stepName).toUpperCase() };
    case "STATE_SNAPSHOT": return { kind: "state", text: "STATE_SNAPSHOT  plan structure read from the graph" };
    case "TOOL_CALL_ARGS": args.set(String(ev.toolCallId), String(ev.delta)); return null;
    case "TOOL_CALL_RESULT": {
      const a = JSON.parse(args.get(String(ev.toolCallId)) ?? "{}");
      const r = JSON.parse(String(ev.content));
      const bound = Object.keys(a.bindings ?? {}).length ? `  [roles bound so far: ${Object.entries(a.bindings).map(([k, v]) => `${k}=${v}`).join(", ")}]` : "";
      return { kind: "call", text: `check_condition ${a.lesson} ${a.condition} (${a.kind})${bound}`,
               detail: r.holds ? "holds" : r.state };
    }
    case "STATE_DELTA": {
      const ops = (ev.delta as { path: string; value: unknown }[]).filter((o) => o.path.endsWith("/level") || o.path.endsWith("/echo_id"));
      return { kind: "state", text: "STATE_DELTA  " + ops.map((o) => `${o.path.split("/")[2]}: ${o.value}`).join("  ") };
    }
    case "TEXT_MESSAGE_CONTENT": return { kind: "text", text: String(ev.delta) };
    case "RUN_FINISHED": return { kind: "run", text: "RUN_FINISHED" };
    case "RUN_ERROR": return { kind: "error", text: `RUN_ERROR  ${ev.message}` };
    default: return null;
  }
}

export default function AgentTrace({ planId }: { planId: string }) {
  const [lines, setLines] = useState<Line[]>([]);
  const [running, setRunning] = useState(false);
  const [count, setCount] = useState(0);

  async function run() {
    setRunning(true); setLines([]); setCount(0);
    const args = new Map<string, string>();
    try {
      const r = await fetch("/api/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Nodus-Sandbox": await sandboxId(), Accept: "text/event-stream" },
        body: JSON.stringify({ threadId: `plan-${planId}`, runId: crypto.randomUUID().slice(0, 12),
          state: { plan_id: planId }, messages: [], tools: [], context: [], forwardedProps: {} }),
      });
      if (!r.ok || !r.body) throw new Error(`The agent could not start (${r.status}).`);
      const reader = r.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const frames = buf.split("\n\n");
        buf = frames.pop() ?? "";
        for (const f of frames) {
          if (!f.startsWith("data: ")) continue;
          const ev = JSON.parse(f.slice(6)) as Ev;
          setCount((c) => c + 1);
          const line = describe(ev, args);
          if (line) setLines((ls) => [...ls, line]);
        }
      }
    } catch (e) {
      setLines((ls) => [...ls, { kind: "error", text: (e as Error).message }]);
    } finally {
      setRunning(false);
    }
  }

  return (
    <section className="mt-5 rounded-2xl border border-line bg-paper-2 p-5" aria-labelledby="trace-title">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h3 id="trace-title" className="font-serif text-2xl">Watch the agent <em>think, step by step</em></h3>
          <p className="max-w-[60ch] text-sm text-pencil">
            The same loop that runs when you save, streamed as standard AG-UI events: every graph query is a tool call with
            its arguments and result.
          </p>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={running}>{running ? "Running…" : "Run the agent"}</button>
      </div>
      {lines.length > 0 && (
        <ol className="mt-5 max-h-[420px] overflow-auto border-t border-line pt-3 font-mono text-[0.8rem] leading-relaxed" aria-live="polite">
          {lines.map((l, i) => (
            <li key={i} className={
              l.kind === "step" ? "mt-3 font-medium tracking-wider text-olive" :
              l.kind === "text" ? "my-2 border-l-2 border-peri pl-3 font-sans text-[0.95rem] text-ink whitespace-pre-line" :
              l.kind === "error" ? "text-terra-ink" : l.kind === "run" ? "text-muted" : "text-ink"}>
              {l.kind === "call" ? (
                <span className="flex flex-wrap justify-between gap-2">
                  <span>{l.text}</span>
                  <span className={l.detail === "holds" ? "font-medium" : "text-muted"}>{l.detail}</span>
                </span>
              ) : l.text}
            </li>
          ))}
        </ol>
      )}
      {count > 0 && <p className="label mt-3">{count} AG-UI events received</p>}
    </section>
  );
}
