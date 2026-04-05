"""
Benchmark: Evaluates routing accuracy and answer quality over labeled query sets.
"""

import json
import time
from typing import Any

from src.router import route, Modality
from src.benchmark_queries import BENCHMARK_QUERIES


def run_routing_benchmark() -> dict[str, Any]:
    """
    Evaluate routing accuracy against gold-labeled benchmark queries.
    Returns per-modality precision/recall and overall accuracy.
    """
    results = []
    correct = 0

    for item in BENCHMARK_QUERIES:
        query = item["query"]
        expected = item["expected_modality"]

        decision = route(query)
        predicted = decision.modality.value
        is_correct = predicted == expected

        if is_correct:
            correct += 1

        results.append({
            "query": query[:80] + ("..." if len(query) > 80 else ""),
            "expected": expected,
            "predicted": predicted,
            "confidence": decision.confidence,
            "correct": is_correct,
        })

    total = len(BENCHMARK_QUERIES)
    accuracy = correct / total if total else 0.0

    # Per-modality breakdown
    modalities = [m.value for m in Modality]
    per_modality: dict[str, dict] = {}
    for mod in modalities:
        tp = sum(1 for r in results if r["expected"] == mod and r["predicted"] == mod)
        fp = sum(1 for r in results if r["expected"] != mod and r["predicted"] == mod)
        fn = sum(1 for r in results if r["expected"] == mod and r["predicted"] != mod)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_modality[mod] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "support": tp + fn,
        }

    return {
        "total_queries": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "per_modality": per_modality,
        "results": results,
    }


def print_benchmark_report(report: dict[str, Any]) -> None:
    print("\n" + "=" * 65)
    print("  ROUTING BENCHMARK REPORT")
    print("=" * 65)
    print(f"  Overall Accuracy : {report['accuracy']*100:.1f}%  "
          f"({report['correct']}/{report['total_queries']})")
    print()
    print(f"  {'Modality':<12} {'Precision':>10} {'Recall':>10} {'F1':>8} {'Support':>9}")
    print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*8} {'-'*9}")
    for mod, scores in report["per_modality"].items():
        print(
            f"  {mod:<12} {scores['precision']:>10.3f} {scores['recall']:>10.3f} "
            f"{scores['f1']:>8.3f} {scores['support']:>9}"
        )
    print("=" * 65)
    print()

    wrong = [r for r in report["results"] if not r["correct"]]
    if wrong:
        print(f"  Misclassified queries ({len(wrong)}):")
        for r in wrong:
            print(f"    ✗ [{r['expected']} → {r['predicted']}] {r['query']}")
    else:
        print("  All queries correctly classified ✓")
    print()
