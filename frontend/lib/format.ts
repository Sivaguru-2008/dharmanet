export const DIM_LABEL: Record<string, string> = {
  consequences: "Consequences",
  duty: "Duty",
  fairness: "Fairness",
  virtue: "Virtue",
  care: "Care",
  stakeholder_impact: "Stakeholders",
  dharma: "Dharma-inspired",
};

export const DIM_ORDER = ["consequences", "duty", "fairness", "virtue", "care", "stakeholder_impact", "dharma"];

/** Categorical colours for actions on light sky-blue background. */
export const ACTION_COLORS = ["#0284c7", "#0ea5e9", "#2563eb", "#6366f1", "#059669", "#0891b2", "#d97706", "#7c3aed"];

/** Sequential heat for 0-10 scores on a crisp light card: low = soft rose, mid = neutral ice, high = light sky blue. */
export function heat(score: number): string {
  const t = Math.max(0, Math.min(1, score / 10));
  if (t < 0.5) {
    const k = t / 0.5;
    return `rgba(244, 63, 94, ${0.35 * (1 - k) + 0.05})`;
  }
  const k = (t - 0.5) / 0.5;
  return `rgba(2, 132, 199, ${0.4 * k + 0.06})`;
}

export const pct = (x: number) => `${Math.round(x * 100)}%`;
export const f1 = (x: number) => x.toFixed(1);
export const f2 = (x: number) => x.toFixed(2);

export function stabilityTone(label: string) {
  if (label === "Stable") return "bg-emerald-50 text-emerald-800 border border-emerald-200";
  if (label === "Moderately Sensitive") return "bg-sky-50 text-sky-800 border border-sky-200";
  return "bg-amber-50 text-amber-800 border border-amber-200";
}

export const humanize = (s: string) => s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
