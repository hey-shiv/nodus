import Link from "next/link";

const STAMPS = [
  { year: "2012", org: "Knight Capital", line: "Warning emails went to nobody who was watching.", c: "#D79B82", icon: "chart" },
  { year: "2017", org: "GitLab", line: "Backups were failing silently, and nobody knew until they were needed.", c: "#B9C69E", icon: "db" },
  { year: "2017", org: "AWS", line: "The status page broke along with the thing it reported on.", c: "#B6C4FD", icon: "cloud" },
  { year: "2019", org: "Cloudflare", line: "A routine change skipped the test run and went everywhere at once.", c: "#E6D3A7", icon: "globe" },
  { year: "2024", org: "CrowdStrike", line: "A trusted update passed its one automated check and went out.", c: "#C9B6D8", icon: "shield" },
];

const STORY = [
  ["Something goes wrong.", "A team writes down what happened and why, so it never happens again."],
  ["Time passes.", "A different team plans something new, in different words, for a different system."],
  ["Nobody connects the two.", "The new plan doesn't sound like the old failure, so nobody thinks to look."],
];

const CHECKLIST = [
  ["It's treated as a routine change", true],
  ["It skips the usual small test run first", true],
  ["Only one automatic check stands in the way", true],
  ["Its warnings go to an inbox nobody reads", true],
  ["It goes out to every depot at the same time", false],
] as const;

const DRAWERS = [
  ["Notice", "A plan is saved. NODUS looks at how it's set up: who owns it, what checks it, where its warnings go."],
  ["Compare", "It holds the plan up against every lesson it knows, one fact at a time."],
  ["Count", "If all but one fact match, the plan is one step away from a known failure."],
  ["Warn", "It tells the plan's owner which step to avoid, in plain words, and asks the person who warned last time."],
  ["Remember", "Whatever the team decides is saved, so the next warning is wiser."],
];

function Icon({ name }: { name: string }) {
  const p = { fill: "none", stroke: "#232323", strokeWidth: 1.6, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  return (
    <svg width="64" height="64" viewBox="0 0 64 64" aria-hidden="true">
      {name === "chart" && <><path d="M10 50 L24 34 L34 42 L52 18" {...p} /><path d="M44 18 H52 V26" {...p} /><path d="M10 54 H54" {...p} /></>}
      {name === "db" && <><ellipse cx="32" cy="16" rx="16" ry="6" {...p} /><path d="M16 16 V46 C16 50 23 52 32 52 C41 52 48 50 48 46 V16" {...p} /><path d="M16 31 C16 35 23 37 32 37 C41 37 48 35 48 31" {...p} /></>}
      {name === "cloud" && <><path d="M20 44 H46 C52 44 55 39 54 34 C53 29 48 27 44 28 C42 21 36 18 30 20 C25 22 22 26 22 31 C16 31 13 35 14 39 C15 42 17 44 20 44 Z" {...p} /><path d="M26 52 L30 48 M36 52 L40 48" {...p} /></>}
      {name === "globe" && <><circle cx="32" cy="32" r="20" {...p} /><path d="M12 32 H52 M32 12 C24 20 24 44 32 52 C40 44 40 20 32 12" {...p} /></>}
      {name === "shield" && <><path d="M32 10 L50 17 V31 C50 42 42 50 32 54 C22 50 14 42 14 31 V17 Z" {...p} /><path d="M24 32 L30 38 L41 26" {...p} /></>}
    </svg>
  );
}

export default function Home() {
  return (
    <>
      {/* Hero: Bharat Digital's composition. An original dithered gateway; the headline sits in its opening. */}
      <section aria-labelledby="hero-title">
        <div className="relative mx-auto w-full max-w-[1600px]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/art/hero.png" alt="" className="block w-full select-none" style={{ imageRendering: "pixelated" }} />
          <div className="absolute flex items-center justify-center bg-paper px-[1.4%] text-center"
            style={{ left: "40%", width: "20%", top: "28.4%", height: "53%" }}>
            <h1 id="hero-title" className="display text-[clamp(1.5rem,3.05vw,3.3rem)] !leading-[1.15]">
              LEARN <em>from the</em> MISTAKES <em>you never</em> MADE
            </h1>
          </div>
        </div>
        <div className="mx-auto flex max-w-[760px] flex-col items-center px-6 pt-12 text-center">
          <p className="text-[1.15rem] leading-relaxed text-ink/85">
            Companies keep repeating failures they already wrote down. NODUS remembers what went wrong before, at your
            company and at others, and tells you in plain words when a new plan is about to repeat it.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/demo" className="btn btn-primary">Try the live demo</Link>
            <a href="#story" className="btn">How it works</a>
          </div>
        </div>

        {/* The collection: five real failures as stamps (Bharat Digital) */}
        <div className="mx-auto mt-10 flex max-w-[1180px] items-start justify-center px-6 pb-6" aria-label="Five famous failures">
          {STAMPS.map((s, i) => {
            const turn = (i - 2) * 7;
            return (
              <div key={s.org} className="stamp w-[196px] shrink-0" style={{ ["--c" as string]: s.c, transform: `rotate(${turn}deg) translateY(${Math.abs(i - 2) * 22}px)`, margin: "0 -6px" }}>
                <div className="stamp-inner min-h-[248px]">
                  <span className="label !text-ink/70 !text-[11px]">{s.org}</span>
                  <div className="flex flex-1 items-center justify-center"><Icon name={s.icon} /></div>
                  <p className="text-[13px] leading-snug text-ink/85">{s.line}</p>
                  <span className="font-display text-3xl leading-none">{s.year}</span>
                </div>
              </div>
            );
          })}
        </div>
        <p className="section-title mx-auto max-w-[900px] px-6 pb-24 pt-14 text-center text-[clamp(1.6rem,2.6vw,2.2rem)]">
          Five famous failures. Different companies, different words, <em>the same few mistakes.</em>
        </p>
      </section>

      {/* The story, from first principles */}
      <section id="story" className="mx-auto max-w-[1180px] scroll-mt-24 px-6 pt-24">
        <p className="section-title text-center text-[1.6rem] text-ink/45">Forgetting through <em>new words</em></p>
        <h2 className="section-title mt-10 max-w-[22ch] text-[clamp(2.2rem,3.6vw,3rem)]">Most companies already know the answer. <em>They just can’t find it in time.</em></h2>
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {STORY.map(([title, text], i) => (
            <div key={title} className="card p-7">
              <span className="label">Step {i + 1}</span>
              <h3 className="mt-3 font-serif text-2xl">{title}</h3>
              <p className="mt-2 text-muted">{text}</p>
            </div>
          ))}
        </div>
        <p className="prose-body mt-10 text-lg">
          The trouble is that we look for lessons by what things <em>sound</em> like. NODUS looks at how things are
          <em> set up</em> instead, and a setup doesn’t change when the words do.
        </p>
      </section>

      {/* Different words, same shape */}
      <section className="mx-auto grid max-w-[1180px] items-center gap-12 px-6 pt-28 md:grid-cols-[1fr_1.05fr]">
        <div>
          <span className="label">What NODUS actually checks</span>
          <h2 className="section-title mt-3 text-[clamp(2.2rem,3.6vw,3rem)]">Different words, <em>same shape</em></h2>
          <p className="prose-body mt-5">
            Every lesson is a short checklist of facts about how a plan is set up. Here is the one learned from the
            Cloudflare and CrowdStrike outages, checked against a plan at a made-up freight company. The plan never mentions
            software, servers or security. It doesn’t need to.
          </p>
          <p className="prose-body mt-4">
            Four facts are already true. The fifth is the step that would complete the failure, and it hasn’t happened yet.
            That is the moment NODUS speaks up.
          </p>
        </div>
        <div className="card p-7 md:p-8">
          <span className="label">A new plan</span>
          <h3 className="mt-2 font-serif text-[1.7rem] leading-tight">Refresh tariff tables for every depot</h3>
          <ul className="mt-6 flex flex-col">
            {CHECKLIST.map(([text, done]) => (
              <li key={text} className={`flex items-center gap-4 border-t border-line py-3.5 ${done ? "" : "text-terra-ink"}`}>
                {done ? (
                  <span className="grid size-6 place-items-center rounded-full bg-ink text-[13px] text-paper" aria-hidden="true">✓</span>
                ) : (
                  <span className="size-6 rounded-full border-2 border-dashed border-terra-ink" aria-hidden="true" />
                )}
                <span className={done ? "" : "font-semibold"}>{text}</span>
                <span className="sr-only">{done ? "already true" : "not yet, the step to avoid"}</span>
              </li>
            ))}
          </ul>
          <div className="mt-5 flex items-center justify-between rounded-xl bg-[#F6DED3] px-4 py-3 text-terra-ink">
            <span className="font-medium">4 of 5 already true</span>
            <span className="label !text-terra-ink">One step away</span>
          </div>
        </div>
      </section>

      {/* How it works: Bharat Digital's drawers */}
      <section id="how" className="mx-auto max-w-[1180px] scroll-mt-24 px-6 pt-28">
        <p className="section-title text-center text-[1.6rem] text-ink/45">Remembering through <em>shape</em></p>
        <div className="mt-10 text-center">
          <h2 className="section-title mx-auto max-w-[24ch] text-[clamp(2.2rem,3.6vw,3rem)]">Five things happen <em>every time a plan is saved</em></h2>
        </div>
        <ol className="mt-12 grid gap-4 md:grid-cols-5">
          {DRAWERS.map(([tag, text]) => (
            <li key={tag} className="drawer">
              <div className="drawer-face">
                <span className="drawer-tag">{tag}</span>
                <span className="knob" aria-hidden="true" />
                <p className="text-[14.5px] leading-snug text-ink">{text}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* What it tells you */}
      <section className="mx-auto grid max-w-[1180px] items-center gap-12 px-6 pt-28 md:grid-cols-[1.05fr_1fr]">
        <div className="card p-7 md:p-8">
          <div className="flex items-center justify-between">
            <span className="label">Message to Lena, the plan’s owner</span>
            <span className="lvl lvl-foresight">One step away</span>
          </div>
          <p className="mt-4 font-serif text-[1.35rem] leading-snug">
            “Refresh tariff tables for every depot” already has 4 of the 5 facts behind a known failure. The last one is
            sending it to every depot at once. Consider not doing that as planned.
          </p>
          <p className="silence mt-5">Nobody is recorded as watching the tariff-errors inbox.</p>
          <p className="silence mt-2">Nobody is recorded as owning it either.</p>
          <div className="mt-6 flex items-center gap-3 rounded-xl bg-peri-soft px-4 py-3 text-peri-ink">
            <span className="dot !bg-peri-ink" />
            <span>Asha Rao is invited: she asked for a small test run first the last time this happened.</span>
          </div>
        </div>
        <div>
          <span className="label">What you see</span>
          <h2 className="section-title mt-3 text-[clamp(2.2rem,3.6vw,3rem)]">A warning <em>a person can act on</em></h2>
          <ul className="mt-6 flex flex-col gap-3 text-[1.02rem]">
            {["Which past failure the plan resembles, and why", "The one step to avoid, before anyone takes it",
              "What’s missing from the record, like an inbox nobody watches",
              "Who to ask: the person who warned last time, never a score"].map((t) => (
              <li key={t} className="flex items-start gap-3"><span className="dot mt-2.5" />{t}</li>
            ))}
          </ul>
        </div>
      </section>

      {/* Hear it */}
      <section className="mx-auto max-w-[1180px] px-6 pt-28">
        <div className="card grid items-center gap-8 p-8 md:grid-cols-[1.2fr_1fr] md:p-10">
          <div>
            <span className="label">Listen</span>
            <h2 className="section-title mt-3 text-[clamp(1.9rem,3vw,2.5rem)]">Four notes, <em>and the fifth held back</em></h2>
            <p className="prose-body mt-4">Each fact that’s already true plays a note. The last note, the one that would finish the
              tune, is the step not to take. Your ear hears that something is unfinished before your eyes do.</p>
          </div>
          <div className="flex flex-col gap-3">
            <span className="label">The plan as it is</span>
            <audio controls preload="none" src="/generated/melody-unresolved.wav" className="w-full" />
            <span className="label mt-2">If it took the last step</span>
            <audio controls preload="none" src="/generated/melody-resolved.wav" className="w-full" />
          </div>
        </div>
      </section>

      {/* Honest results */}
      <section className="mx-auto max-w-[1180px] px-6 pt-28">
        <p className="section-title text-center text-[1.6rem] text-ink/45">Trusting through <em>honesty</em></p>
        <div className="mt-10 text-center">
          <span className="label">Does it work?</span>
          <h2 className="section-title mx-auto mt-3 max-w-[24ch] text-[clamp(2.2rem,3.6vw,3rem)]">Tested honestly, <em>including where it falls short</em></h2>
        </div>
        <div className="mt-12 grid gap-5 md:grid-cols-2">
          <div className="card p-8">
            <h3 className="font-serif text-2xl">What we tested</h3>
            <p className="mt-2 text-muted">We wrote down the test before running it, then ran it once, on made-up plans.</p>
            <ul className="mt-5 flex flex-col gap-3">
              {[["Plans built like a past failure, in new words", "caught 18 of 18"],
                ["Plans that use a failure’s words but are set up safely", "0 false alarms in 18"],
                ["A plain keyword search, on the same plans", "flagged all 18 safe ones"]].map(([a, b]) => (
                <li key={a} className="flex items-start justify-between gap-4 border-t border-line pt-3">
                  <span className="flex gap-3"><span className="dot mt-2.5" />{a}</span><span className="whitespace-nowrap font-medium">{b}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="card p-8">
            <h3 className="font-serif text-2xl">What it can’t do</h3>
            <p className="mt-2 text-muted">These limits matter, so they’re on the front page.</p>
            <ul className="mt-5 flex flex-col gap-3">
              {["It only knows what’s recorded about a plan. Missing records hide risks.",
                "It can’t tell how much is at stake: a tiny change set up riskily still gets a warning.",
                "The test plans were made up. Real companies are messier."].map((t) => (
                <li key={t} className="flex items-start gap-3 border-t border-line pt-3"><span className="dot mt-2.5 !bg-terra" />{t}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-[1180px] px-6 pt-28">
        <div className="glow card flex flex-col items-center px-8 py-16 text-center">
          <h2 className="display text-[clamp(2.2rem,4vw,3.4rem)]">SEE IT <em>catch a mistake</em> BEFORE IT HAPPENS</h2>
          <p className="prose-body mt-4">You get your own copy of a made-up company. Change a plan, take the risky step, and watch
            what NODUS says.</p>
          <Link href="/demo" className="btn btn-primary mt-8">Try the live demo</Link>
        </div>
      </section>
    </>
  );
}
