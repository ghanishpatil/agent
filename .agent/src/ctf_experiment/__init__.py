"""Knowledge-augmented experimental harness and retrieval-quality evaluation.

This package composes the FROZEN solver (`ctf_agent`), the FROZEN benchmark
(`ctf_bench`), and the ingestion/retrieval layer (`ctf_ingest`) to run a controlled A/B
experiment and an independent retrieval-quality evaluation. It imports `ctf_agent` but
never modifies it; `ctf_agent` does not import this package.
"""

from __future__ import annotations

from .ab_harness import ABArm, ABComparison, run_ab_experiment, summarize_report
from .knowledge_dependent_benchmark import KnowledgeDependentCase, build_cases
from .knowledge_dependent_benchmark_v2 import KDCaseV2, build_cases_v2
from .knowledge_dependent_harness import (
    CaseOutcome,
    KnowledgeDependentReport,
    run_knowledge_dependent_experiment,
)
from .knowledge_dependent_harness_v2 import KDv2Outcome, KDv2Report, run_experiment_v2
from .knowledge_reasoning import KnowledgeAugmentedReasoningSource, KnowledgeMetrics
from .knowledge_solver import KnowledgeSolveOutput, solve_with_knowledge
from .knowledge_experiment import (
    ExperimentalSolveOutput,
    ExperimentalTranslationSource,
    IntegrationReport,
    KnowledgeContribution,
    KnowledgeMode,
    KnowledgeTrace,
    classify_contribution,
    run_knowledge_integration_experiment,
    solve_experimental,
)
from .knowledge_translation import (
    Applicability,
    KnowledgeOrigin,
    KnowledgeTranslator,
    MechanismTemplate,
    RunnableSpec,
    TemplateRegistry,
    TrajectoryExtract,
    TranslationContext,
    TranslationProvenance,
    TranslationResult,
    TranslationStatus,
    TranslationSupport,
    extract_trajectory,
)
from .retrieval_eval import (
    LabeledQuery,
    RetrievalQualityReport,
    category_consistency_at_k,
    evaluate_retrieval,
)

__all__ = [
    "ABArm",
    "ABComparison",
    "CaseOutcome",
    "KDCaseV2",
    "KDv2Outcome",
    "KDv2Report",
    "KnowledgeAugmentedReasoningSource",
    "KnowledgeDependentCase",
    "KnowledgeDependentReport",
    "KnowledgeMetrics",
    "KnowledgeSolveOutput",
    "KnowledgeMode",
    "KnowledgeContribution",
    "KnowledgeTrace",
    "ExperimentalSolveOutput",
    "ExperimentalTranslationSource",
    "IntegrationReport",
    "classify_contribution",
    "solve_experimental",
    "run_knowledge_integration_experiment",
    "KnowledgeOrigin",
    "KnowledgeTranslator",
    "MechanismTemplate",
    "RunnableSpec",
    "TemplateRegistry",
    "TrajectoryExtract",
    "TranslationContext",
    "TranslationProvenance",
    "TranslationResult",
    "TranslationStatus",
    "TranslationSupport",
    "Applicability",
    "extract_trajectory",
    "LabeledQuery",
    "build_cases_v2",
    "run_experiment_v2",
    "solve_with_knowledge",
    "RetrievalQualityReport",
    "build_cases",
    "category_consistency_at_k",
    "evaluate_retrieval",
    "run_ab_experiment",
    "run_knowledge_dependent_experiment",
    "summarize_report",
]
