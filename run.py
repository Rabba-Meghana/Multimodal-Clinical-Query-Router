#!/usr/bin/env python3
"""
CLI entry point for Multimodal Clinical Query Router.

Usage:
  python run.py --query "Which EGFR patients have CRP above 10?"
  python run.py --demo
  python run.py --benchmark
"""

import argparse
import json
import sys


def _print_result(result: dict) -> None:
    r = result["routing"]
    f = result["faithfulness"]
    lat = result["latency_ms"]

    print("\n" + "═" * 70)
    print(f"  QUERY: {result['query']}")
    print("═" * 70)
    print(f"\n  🔀 ROUTING")
    print(f"     Modality   : {r['modality']}  (confidence: {r['confidence']:.2f})")
    print(f"     Reasoning  : {r['reasoning']}")
    if r["filters"]:
        print(f"     Filters    : {json.dumps(r['filters'], indent=None)}")

    print(f"\n  📋 ANSWER  ({result['evidence_used']} records retrieved)")
    for line in result["answer"].split("\n"):
        print(f"     {line}")

    print(f"\n  🎯 FAITHFULNESS")
    print(f"     Grounding    : {f['grounding_score']:.3f}")
    print(f"     Hallucination Risk : {f['hallucination_risk']:.3f}")
    print(f"     Completeness : {f['completeness']:.3f}")
    if f.get("flags"):
        print(f"     Flags        : {', '.join(f['flags'])}")

    print(f"\n  ⏱  LATENCY")
    print(f"     Route {lat['routing']}ms | Retrieve {lat['retrieval']}ms | "
          f"Generate {lat['generation']}ms | Total {lat['total']}ms")
    print()


DEMO_QUERIES = [
    "Which EGFR patients have CRP above 10 and documented progression?",
    "Find all patients with KRAS G12C alterations",
    "Which patients have hemoglobin below 9 g/dL?",
    "Summarize notes for patients who received palliative care referrals",
]


def main():
    parser = argparse.ArgumentParser(description="Multimodal Clinical Query Router")
    parser.add_argument("--query", "-q", type=str, help="Run a single query")
    parser.add_argument("--demo", action="store_true", help="Run demo queries")
    parser.add_argument("--benchmark", action="store_true", help="Run routing benchmark")
    parser.add_argument("--top-k", type=int, default=5, help="Max retrieved records")
    args = parser.parse_args()

    # Always generate data first if missing
    import os
    if not os.path.exists("data/clinical_notes.json"):
        print("⚙  Generating synthetic data...")
        from scripts.generate_data import main as gen_main
        gen_main()

    if args.benchmark:
        from src.benchmark import run_routing_benchmark, print_benchmark_report
        print("Running routing benchmark on 50 labeled queries...")
        report = run_routing_benchmark()
        print_benchmark_report(report)
        return

    from src.pipeline import run_query

    if args.query:
        result = run_query(args.query, top_k=args.top_k)
        _print_result(result)
        return

    if args.demo:
        for q in DEMO_QUERIES:
            result = run_query(q, top_k=args.top_k)
            _print_result(result)
        return

    # Interactive mode
    print("\nMultimodal Clinical Query Router — Interactive Mode")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            query = input("Query> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in ("exit", "quit", "q"):
            break
        if not query:
            continue
        result = run_query(query, top_k=args.top_k)
        _print_result(result)


if __name__ == "__main__":
    sys.exit(main())
