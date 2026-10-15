import type { Metadata } from "next";
import { DM_Mono, League_Spartan, Libertinus_Serif, Libertinus_Serif_Display, Public_Sans } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const libertinus = Libertinus_Serif({ subsets: ["latin"], weight: ["400", "600"], style: ["normal", "italic"], variable: "--font-libertinus" });
const libertinusDisplay = Libertinus_Serif_Display({ subsets: ["latin"], weight: "400", variable: "--font-libertinus-display" });
const publicSans = Public_Sans({ subsets: ["latin"], variable: "--font-public-sans" });
const dmMono = DM_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-dm-mono" });
const spartan = League_Spartan({ subsets: ["latin"], weight: ["700"], variable: "--font-spartan" });

export const metadata: Metadata = {
  title: "NODUS: learn from mistakes you never made",
  description:
    "NODUS remembers what went wrong before, at your company and at others, and tells you in plain words when a new plan is about to repeat it.",
};

const NAV = [
  { href: "/#how", label: "How it works" },
  { href: "/demo", label: "Live demo" },
  { href: "/under-the-hood", label: "Under the hood" },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${libertinus.variable} ${libertinusDisplay.variable} ${publicSans.variable} ${dmMono.variable} ${spartan.variable}`}>
      <body className="min-h-dvh antialiased">
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:p-3">Skip to content</a>
        <header className="sticky top-0 z-20 border-b border-line/80 bg-paper/85 backdrop-blur-md">
          <div className="mx-auto grid max-w-[1180px] grid-cols-[1fr_auto_1fr] items-center px-6 py-3.5">
            <Link href="/" className="justify-self-start" aria-label="nodus home"><Logo /></Link>
            <nav aria-label="Main" className="flex gap-8 text-[15px] font-medium">
              {NAV.map((n) => (
                <Link key={n.href} href={n.href} className="text-ink/80 hover:text-ink">{n.label}</Link>
              ))}
            </nav>
            <div className="flex gap-2 justify-self-end">
              <a href="https://github.com/hey-shiv/nodus" className="btn !min-h-9 !px-4 !text-sm">Code</a>
              <Link href="/demo" className="btn btn-primary !min-h-9 !px-4 !text-sm">Try it</Link>
            </div>
          </div>
        </header>
        <main id="main">{children}</main>
        <footer className="mt-28 border-t border-line">
          <div className="mx-auto grid max-w-[1180px] gap-10 px-6 py-14 md:grid-cols-[1.4fr_1fr_1fr]">
            <div className="flex flex-col gap-4">
              <Logo />
              <p className="max-w-[46ch] text-sm text-muted">
                Tern &amp; Tally Freight and everyone in it are made up for this demo. Real companies appear only as cited
                sources: Cloudflare, CrowdStrike, Knight Capital (via the U.S. SEC), GitLab and AWS.
              </p>
            </div>
            <div className="flex flex-col gap-2 text-[15px]">
              <span className="label mb-1">Explore</span>
              <Link href="/#how">How it works</Link>
              <Link href="/demo">Live demo</Link>
              <Link href="/under-the-hood">Under the hood</Link>
            </div>
            <div className="flex flex-col gap-2 text-[15px]">
              <span className="label mb-1">Project</span>
              <a href="https://github.com/hey-shiv/nodus">Code on GitHub ↗</a>
              <span className="text-muted">Graph Hacks 2026</span>
              <span className="text-muted">MIT licence</span>
            </div>
          </div>
          <p className="label mx-auto max-w-[1180px] px-6 pb-10">© 2026 NODUS. A hackathon project. All data is synthetic or cited.</p>
        </footer>
      </body>
    </html>
  );
}

function Logo() {
  // "Nodus" is Latin for knot: the string you tie so you don't forget. A tied loop, and the wordmark.
  return (
    <span className="flex items-center gap-2">
      <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true" fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d="M7 28 C9 25 12 21 14.5 18 C17 15 21.5 11.5 21.5 7.8 C21.5 4.3 18.6 2.2 15 2.2 C11.4 2.2 8.5 4.3 8.5 7.8 C8.5 11.5 13 15 15.5 18" stroke="#232323" strokeWidth="2.6" />
        <path d="M15.5 18 C17.5 20.5 20.5 24.5 23 28" stroke="#FFFBF2" strokeWidth="6" />
        <path d="M15.5 18 C17.5 20.5 20.5 24.5 23 28" stroke="#232323" strokeWidth="2.6" />
        <circle cx="23" cy="28" r="1.9" fill="#9A3F1F" />
      </svg>
      <span className="text-[25px] leading-none tracking-[-0.02em] text-ink" style={{ fontFamily: "var(--font-spartan)", fontWeight: 700 }}>nodus</span>
    </span>
  );
}
