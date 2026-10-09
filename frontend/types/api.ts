// Mirrors backend/app/schemas (keep in sync).
export type Dim = "consequences" | "duty" | "fairness" | "virtue" | "care" | "stakeholder_impact" | "dharma";

export interface ActionFeatures { [k: string]: number }

export interface Stakeholder {
  id: string; name: string; category: string; roles: string[];
  interests: string[]; rights: string[]; responsibilities: string[]; vulnerabilities: string[];
  potential_benefits: string[]; potential_harms: string[]; salience: number; user_edited: boolean;
}
export interface Action {
  id: string; label: string; description: string; kind: string; features: ActionFeatures; user_added: boolean;
}
export interface Conflict { id: string; type: string; title: string; description: string; between: string[]; intensity: number }
export interface ContextCues { severity: number; vulnerability: number; relational_closeness: number; uncertainty: number; legal_dimension: number; urgency: number; scale: number; evidence: string[] }
export interface DilemmaContext { role: string; domain: string; cultural_context: string; time_pressure: string; additional: string }
export interface StructuredDilemma {
  dilemma_text: string; summary: string; domain: string; decision_maker: string; context: DilemmaContext;
  stakeholders: Stakeholder[]; actions: Action[]; conflicts: Conflict[]; constraints: string[];
  uncertainties: string[]; assumptions: string[]; ethical_dimensions: string[]; cues: ContextCues;
}
export interface DimensionScore {
  dimension: string; action_id: string; score: number; uncertainty: number; confidence: number; confidence_type: string;
  rationale: string; principle: string; assumptions: string[]; evidence: string[]; strengths: string[]; weaknesses: string[];
  uncertainties: string[]; potential_disagreement: string; flags: string[]; citations: string[];
}
export interface StakeholderImpact { stakeholder_id: string; action_id: string; impact: number; note: string }
export interface FrameworkEvaluation {
  framework_id: string; framework_name: string; framework_version: string; source: string; summary: string;
  scores: DimensionScore[]; stakeholder_impacts: StakeholderImpact[];
}
export interface RetrievedEntry { entry_id: string; concept: string; citation: string; relevance: number; matched_on: string[] }
export interface ConceptContribution { concept: string; entry_ids: string[]; effect: number; note: string }
export interface DharmaActionReading { action_id: string; score: number; uncertainty: number; confidence: number; interpretation: string; contributions: ConceptContribution[]; limitations: string[] }
export interface DharmaEvaluation { source: string; kb_version: string; retrieved: RetrievedEntry[]; readings: DharmaActionReading[]; overview: string; dropped_claims: number; disclaimer: string }
export interface MatrixCell { score: number; uncertainty: number; confidence: number }
export interface WeightedScore { action_id: string; score: number; uncertainty: number; confidence: number; rank: number }
export interface Recommendation { action_id: string; runner_up_id: string | null; margin: number; clear_preference: boolean; statement: string }
export interface DecisionMatrix {
  dimensions: Dim[]; actions: string[]; cells: Record<string, Record<string, MatrixCell>>; weights: Record<string, number>;
  weighted: WeightedScore[]; equal_weighted: WeightedScore[]; recommendation: Recommendation; equal_weight_recommendation: Recommendation;
}
export interface FlipThreshold { dimension: string; current_weight: number; stays_top_from: number; stays_top_to: number; below_leader: string | null; above_leader: string | null; margin_to_flip: number }
export interface Sensitivity {
  leader: string; flip_thresholds: FlipThreshold[]; weight_stability: number; score_stability: number;
  win_share_weights: Record<string, number>; win_share_scores: Record<string, number>;
  label: "Stable" | "Moderately Sensitive" | "Highly Sensitive"; samples: number; seed: number; method_note: string;
}
export interface TraceStep { step: number; stage: string; summary: string }
export interface Explanation { why: string; principles: string[]; key_stakeholders: string[]; assumptions: string[]; what_could_change: string[]; disagreements: string[]; trace: TraceStep[]; note: string }
export interface ActionComparison {
  action_id: string; label: string; strengths: string[]; weaknesses: string[]; stakeholders_helped: string[]; stakeholders_harmed: string[];
  short_term: string; long_term: string; risks: string[]; uncertainty: string; framework_disagreement: string; dharma_view: string;
  best_dimensions: string[]; worst_dimensions: string[];
}
export interface ProviderInfo { provider: string; model: string; is_llm: boolean; note: string }
export interface Decision { choice: string; action_id: string | null; note: string; recommended_action_id: string; statement: string }
export interface AnalysisResult {
  id: string; parent_id: string | null; created_at: string; versions: Record<string, string>; provider: ProviderInfo;
  structured: StructuredDilemma; evaluations: FrameworkEvaluation[]; dharma: DharmaEvaluation | null; matrix: DecisionMatrix;
  sensitivity: Sensitivity; explanation: Explanation; comparison: ActionComparison[]; fallbacks: string[];
  include_dharma: boolean; seed: number; disclaimer: string; decision: Decision | null;
}
export interface AnalysisSummary { id: string; parent_id: string | null; created_at: string; summary: string; domain: string; recommended_label: string; stability: string; provider: string; decision: string | null }
export interface KBEntry {
  id: string; concept: string; sanskrit_term: string; source: string; chapter: string | null; verse: string | null; citation: string;
  text_type: string; paraphrase: string; interpretation: string; alternative_interpretations: string[]; ethical_dimension: string[];
  applicability: string[]; keywords: string[]; limitations: string[]; verification_status: string;
}
export interface Meta {
  versions: Record<string, string>; provider: ProviderInfo; default_weights: Record<string, number>;
  dimensions: Record<string, string>; disclaimer: string; auth_required: boolean;
  frameworks: { id: string; name: string; dimension: string; definition: string; principle: string; key_questions: string[]; version: string }[];
}
