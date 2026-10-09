"""Explicit component versions recorded on every analysis run (research reproducibility).

Bump the relevant version whenever behaviour of that component changes.
"""
SYSTEM_VERSION = "0.1.0"
ANALYSIS_VERSION = "0.1.0"
FRAMEWORK_VERSION = "0.1"
SCORING_VERSION = "0.1"
SENSITIVITY_VERSION = "0.1"
PROMPT_VERSION = "0.1"
HEURISTIC_ENGINE_VERSION = "0.1"
# DHARMA_KB version is read from the knowledge file itself.


def version_record(kb_version: str) -> dict[str, str]:
    return {
        "system_version": SYSTEM_VERSION,
        "analysis_version": ANALYSIS_VERSION,
        "framework_version": FRAMEWORK_VERSION,
        "scoring_version": SCORING_VERSION,
        "sensitivity_version": SENSITIVITY_VERSION,
        "prompt_version": PROMPT_VERSION,
        "heuristic_engine_version": HEURISTIC_ENGINE_VERSION,
        "dharma_kb_version": kb_version,
    }


DISCLAIMER = (
    "DharmaNet is an AI-assisted ethical decision-support system. It does not determine "
    "objectively correct moral decisions and does not replace human judgment, professional "
    "advice, institutional policies, or legal requirements. Its Dharma-inspired analysis "
    "represents a computational interpretation of selected philosophical concepts and should "
    "not be treated as definitive religious authority."
)
