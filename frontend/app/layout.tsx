import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "DharmaNet — Explainable Multi-Framework Ethical AI",
  description: "An Explainable Multi-Framework AI System for Culturally Contextualized Ethical Decision Support. Preserving human decision authority.",
};

const NAV = [
  { href: "/presentation", label: "Presentation", highlight: true },
  { href: "/new", label: "New Dilemma" },
  { href: "/history", label: "History" },
  { href: "/knowledge", label: "Knowledge Base" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-[#f0f7ff] text-slate-800 antialiased">
        <header className="sticky top-0 z-20 border-b border-sky-100 bg-white/95 backdrop-blur shadow-sm shadow-sky-100/60">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
            <div className="flex items-center gap-3">
              <Link href="/" className="flex items-center gap-2.5 font-bold tracking-tight text-sky-950">
                <span aria-hidden className="grid h-7 w-7 place-items-center rounded-lg bg-sky-600 text-sm font-semibold text-white shadow-sm shadow-sky-600/30">
                  ध
                </span>
                <span className="text-lg font-bold tracking-tight">DharmaNet</span>
              </Link>
              <span className="hidden sm:inline-flex items-center rounded-full bg-sky-50 border border-sky-200 px-2.5 py-0.5 text-[11px] font-semibold text-sky-700">
                Decision Support
              </span>
            </div>

            <nav className="flex items-center gap-1 sm:gap-2 text-sm">
              {NAV.map((n) => (
                <Link
                  key={n.href}
                  href={n.href}
                  className={`rounded-lg px-3 py-1.5 font-semibold transition ${
                    n.highlight
                      ? "bg-sky-50 text-sky-700 border border-sky-300 hover:bg-sky-100 shadow-sm"
                      : "text-slate-600 hover:bg-sky-50 hover:text-sky-800"
                  }`}
                >
                  {n.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-7xl flex-1 px-4 py-6 w-full">{children}</main>

        <footer className="border-t border-sky-100 bg-white/90 mt-12">
          <div className="mx-auto max-w-7xl px-4 py-6 text-xs text-slate-500 space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <p className="font-semibold text-sky-900">
                DharmaNet: Explainable Multi-Framework Ethical Decision Support
              </p>
              <div className="flex gap-4 font-medium text-sky-700">
                <Link href="/presentation" className="hover:underline">Presentation</Link>
                <Link href="/knowledge" className="hover:underline">Knowledge Base</Link>
                <Link href="/history" className="hover:underline">History</Link>
              </div>
            </div>
            <p className="leading-relaxed">
              DharmaNet is an AI-assisted ethical decision-support research system. It does not determine objectively correct moral
              decisions and does not replace human judgment, professional advice, institutional policies, or legal requirements.
              Its Dharma-inspired analysis represents a computational interpretation of selected philosophical concepts and should
              not be treated as definitive religious authority. All evaluations are decision support; the human user retains 100% final moral decision authority.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
