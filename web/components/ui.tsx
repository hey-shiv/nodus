import Link from "next/link";
import type { Level } from "@/lib/api";
import { LEVEL_WORDS } from "@/lib/api";

export function Spec({ rows }: { rows: [string, React.ReactNode, boolean?][] }) {
  return (
    <dl className="spec">
      {rows.map(([k, v, red], i) => (
        <div key={i} className="contents">
          <dt>{k}</dt>
          <dd className={red ? "red" : ""}>{v}</dd>
        </div>
      ))}
    </dl>
  );
}

export function LevelTag({ level }: { level: Level }) {
  return <span className={`lvl lvl-${level}`}>{LEVEL_WORDS[level]}</span>;
}

// Our own SVG, generated server-side from the match result with every text node escaped.
export function Svg({ html, label }: { html: string; label?: string }) {
  return <span className="drawing inline-block w-full" aria-label={label} dangerouslySetInnerHTML={{ __html: html }} />;
}

export function Strip({ html }: { html: string }) {
  return <span className="inline-flex" aria-hidden="true" dangerouslySetInnerHTML={{ __html: html }} />;
}

const TABS = [
  { href: "/demo", label: "Plans" },
  { href: "/demo/echo", label: "Side by side" },
  { href: "/demo/inbox", label: "Messages" },
  { href: "/demo/lessons", label: "Lessons" },
];

export function DemoNav({ active }: { active: string }) {
  return (
    <div className="mx-auto mt-8 flex max-w-[1180px] flex-wrap items-center justify-between gap-4 px-6">
      <nav aria-label="Demo" className="flex rounded-2xl border border-line bg-white p-1">
        {TABS.map((t) => (
          <Link key={t.href} href={t.href} aria-current={active === t.href ? "page" : undefined}
            className={`rounded-xl px-5 py-2 text-[15px] font-medium transition-colors ${
              active === t.href ? "bg-peri-soft text-peri-ink" : "text-ink/70 hover:text-ink"}`}>
            {t.label}
          </Link>
        ))}
      </nav>
      <span className="pill-label">Your own copy of a made-up company</span>
    </div>
  );
}

export function Loading({ what }: { what: string }) {
  return <p className="label mx-auto max-w-[1180px] px-6 py-16" role="status">Loading {what}…</p>;
}

export function ErrorNote({ error }: { error: string }) {
  return (
    <div role="alert" className="quote mx-auto my-10 max-w-[1180px] text-terra-ink">
      <p className="label mb-1 !text-terra-ink">Something went wrong</p>
      <p>{error} Reload the page to try again.</p>
    </div>
  );
}
