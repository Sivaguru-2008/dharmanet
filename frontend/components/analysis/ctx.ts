import type { AnalysisResult } from "@/types/api";

export type Tab = "overview" | "matrix" | "dharma" | "explanation" | "compare" | "sensitivity" | "decision";

export interface Ctx {
  r: AnalysisResult;
  setR: (r: AnalysisResult) => void;
  label: (id: string) => string;
  color: (id: string) => string;
  go: (t: Tab) => void;
}
