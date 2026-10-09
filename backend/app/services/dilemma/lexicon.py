"""Transparent lexicons used by the heuristic (offline) analysis engine.

These are deliberately simple keyword rules. They make the pipeline reproducible and testable
without an LLM; they are NOT a claim of semantic understanding (see docs/limitations.md).
"""
from __future__ import annotations

DOMAINS: dict[str, list[str]] = {
    "healthcare": ["patient", "doctor", "nurse", "hospital", "medical", "treatment", "diagnos",
                   "clinic", "medication", "surgery", "health", "drug", "vaccine"],
    "workplace": ["company", "employer", "manager", "boss", "colleague", "coworker", "employee",
                  "corporate", "office", "team", "supervisor", "workplace", "job"],
    "business": ["customer", "product", "client", "profit", "sales", "supplier", "market",
                 "shareholder", "investor", "startup", "contract"],
    "education": ["student", "teacher", "school", "exam", "university", "professor", "cheat",
                  "grade", "class", "thesis", "plagiar"],
    "ai_ethics": ["ai ", "a.i.", "algorithm", "model", "machine learning", "dataset", "automated",
                  "chatbot", "facial recognition", "artificial intelligence"],
    "privacy": ["privacy", "personal data", "personal information", "surveillance", "track",
                "consent", "confidential", "data breach", "monitor"],
    "environment": ["pollut", "environment", "river", "emission", "waste", "forest", "climate",
                    "toxic", "wildlife", "dump"],
    "public_policy": ["government", "policy", "city council", "public funds", "citizens",
                      "regulation", "election", "municipal", "ministry", "law enforcement"],
    "family_social": ["mother", "father", "parent", "sister", "brother", "son", "daughter",
                      "family", "wife", "husband", "friend", "partner", "neighbor", "neighbour"],
    "professional": ["lawyer", "engineer", "accountant", "audit", "journalist", "architect",
                     "professional", "license", "code of conduct", "fiduciary"],
    "technology_governance": ["platform", "content moderation", "open source", "software",
                              "security vulnerability", "app", "users"],
}

# (category, display name, patterns, base roles, vulnerable-by-default)
STAKEHOLDER_LEXICON: list[tuple[str, str, list[str], list[str], bool]] = [
    ("organization", "The organization / employer",
     ["company", "employer", "organization", "organisation", "firm", "business", "corporation",
      "startup", "hospital", "school", "university", "agency"], ["secondary", "direct"], False),
    ("management", "Management / leadership",
     ["manager", "boss", "supervisor", "ceo", "executive", "leadership", "director", "principal"],
     ["secondary", "direct"], False),
    ("employees", "Employees / colleagues",
     ["employees", "workers", "staff", "colleague", "coworker", "co-worker", "jobs", "team"],
     ["secondary", "indirect"], False),
    ("customers", "Customers / users",
     ["customer", "users", "consumer", "client", "passenger", "buyer"], ["primary", "direct"], False),
    ("patients", "Patients", ["patient"], ["primary", "direct", "vulnerable"], True),
    ("public", "The public / community",
     ["public", "community", "society", "citizens", "residents", "people", "town", "village"],
     ["secondary", "indirect"], False),
    ("regulators", "Regulators / authorities",
     ["regulator", "authorities", "authority", "government", "police", "court", "inspector",
      "ombudsman", "ethics board"], ["secondary", "indirect"], False),
    ("children", "Children / minors",
     ["child", "children", "kid", "minor", "son", "daughter", "teen"], ["primary", "vulnerable"], True),
    ("family", "Family members",
     ["family", "mother", "father", "parent", "sister", "brother", "wife", "husband", "partner",
      "grandmother", "grandfather", "uncle", "aunt", "cousin"], ["primary", "direct"], False),
    ("friend", "Friend", ["friend"], ["primary", "direct"], False),
    ("students", "Students", ["student", "classmate", "learner"], ["primary", "direct"], False),
    ("shareholders", "Shareholders / investors", ["shareholder", "investor", "funder", "donor"],
     ["secondary", "indirect"], False),
    ("environment", "Environment / future generations",
     ["environment", "river", "forest", "wildlife", "ecosystem", "future generations", "climate"],
     ["secondary", "indirect", "vulnerable"], True),
    ("data_subjects", "People whose data is involved",
     ["personal data", "personal information", "their data", "user data", "records", "privacy"],
     ["primary", "direct", "vulnerable"], True),
]

STAKEHOLDER_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "decision_maker": {
        "interests": ["acting with integrity", "protecting own livelihood and wellbeing"],
        "rights": ["freedom of conscience", "protection from retaliation"],
        "responsibilities": ["responsibilities attached to their role", "honest communication"],
        "vulnerabilities": ["possible retaliation, career or relationship costs"],
    },
    "organization": {
        "interests": ["continuity", "reputation", "legal compliance"],
        "rights": ["fair process before public accusations"],
        "responsibilities": ["duty of care toward people affected by its operations"],
        "vulnerabilities": ["financial and reputational damage"],
    },
    "management": {
        "interests": ["organizational performance", "control over response"],
        "rights": ["opportunity to respond to concerns"],
        "responsibilities": ["acting on credible risk reports", "not retaliating"],
        "vulnerabilities": ["accountability for past decisions"],
    },
    "employees": {
        "interests": ["job security", "safe and fair workplace"],
        "rights": ["fair treatment", "safe working conditions"],
        "responsibilities": ["professional conduct"],
        "vulnerabilities": ["income loss if the organization is harmed"],
    },
    "customers": {
        "interests": ["safety", "honest information", "value"],
        "rights": ["informed choice", "protection from known hazards"],
        "responsibilities": [],
        "vulnerabilities": ["exposure to harms they cannot see or control"],
    },
    "patients": {
        "interests": ["health", "honest information", "dignity"],
        "rights": ["informed consent", "competent care", "confidentiality"],
        "responsibilities": [],
        "vulnerabilities": ["dependence on caregivers", "information asymmetry"],
    },
    "public": {
        "interests": ["safety", "trust in institutions"],
        "rights": ["protection from serious harm"],
        "responsibilities": [],
        "vulnerabilities": ["diffuse harms that individuals cannot detect"],
    },
    "regulators": {
        "interests": ["compliance", "public protection"],
        "rights": ["accurate information"],
        "responsibilities": ["fair investigation", "proportionate enforcement"],
        "vulnerabilities": [],
    },
    "children": {
        "interests": ["safety", "wellbeing", "development"],
        "rights": ["protection", "having their interests given special weight"],
        "responsibilities": [],
        "vulnerabilities": ["limited ability to advocate for themselves"],
    },
    "family": {
        "interests": ["wellbeing", "trust", "relationship continuity"],
        "rights": ["honesty", "respect for autonomy"],
        "responsibilities": ["mutual care"],
        "vulnerabilities": ["emotional harm", "dependency"],
    },
    "friend": {
        "interests": ["trust", "support", "privacy"],
        "rights": ["confidence they shared being respected where appropriate"],
        "responsibilities": ["honesty within the friendship"],
        "vulnerabilities": ["emotional harm", "loss of trust"],
    },
    "students": {
        "interests": ["fair assessment", "learning", "future opportunities"],
        "rights": ["fair and consistent treatment"],
        "responsibilities": ["academic honesty"],
        "vulnerabilities": ["power imbalance with institution"],
    },
    "shareholders": {
        "interests": ["return on investment", "accurate disclosures"],
        "rights": ["truthful reporting"],
        "responsibilities": ["oversight"],
        "vulnerabilities": ["financial loss"],
    },
    "environment": {
        "interests": ["ecological integrity"],
        "rights": ["(contested) moral consideration for ecosystems and future people"],
        "responsibilities": [],
        "vulnerabilities": ["cannot speak for itself", "long-term, cumulative harm"],
    },
    "data_subjects": {
        "interests": ["privacy", "control over personal information"],
        "rights": ["consent", "data protection"],
        "responsibilities": [],
        "vulnerabilities": ["unaware of how their data is used"],
    },
}

SEVERE = ["death", "die", "dying", "kill", "fatal", "serious", "life", "lives", "injur", "dangerous",
          "safety", "abuse", "toxic", "poison", "crash", "explod", "suicide", "violence",
          "overdose", "incorrect dose", "wrong dose", "insulin", "collapse"]
HARM = ["harm", "risk", "damage", "fraud", "hurt", "loss", "lose", "defect", "unsafe", "illegal",
        "cheat", "steal", "discriminat", "bias"]
VULNERABLE = ["child", "children", "patient", "elderly", "vulnerable", "disabled", "poor", "minor",
              "student", "customer", "refugee", "low-income", "sick", "pregnant"]
CLOSE = ["friend", "family", "mother", "father", "brother", "sister", "partner", "mentor",
         "colleague", "wife", "husband", "son", "daughter", "best friend"]
HEDGES = ["may", "might", "could", "possibly", "not sure", "unclear", "suspect", "rumor", "rumour",
          "i think", "seems", "uncertain", "maybe", "perhaps", "allegedly", "unverified"]
CERTAIN = ["confirmed", "proof", "evidence", "documented", "know for sure", "verified", "certain"]
LEGAL = ["law", "legal", "illegal", "regulation", "contract", "compliance", "police", "court",
         "policy", "nda", "license", "regulator", "lawsuit"]
URGENT = ["immediately", "urgent", "tomorrow", "soon", "right now", "deadline", "emergency",
          "tonight", "today", "within", "hours"]
SCALE = ["hundreds", "thousands", "millions", "public", "community", "everyone", "customers",
         "employees", "society", "citizens", "users", "many people"]
CONCEAL = ["hiding", "hide", "conceal", "cover up", "cover-up", "covering up", "secret", "lie",
           "lying", "falsif", "fake", "fraud", "misreport", "suppress", "not disclos"]
SELF_RISK = ["my job", "my career", "promotion", "retaliat", "fired", "my reputation", "lose my",
             "blacklist", "my visa", "my position"]
