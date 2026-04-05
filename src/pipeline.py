"""
Pipeline: Orchestrates routing → retrieval → generation for a single query.
"""

import time
from typing import Any

from src.router import route, Modality
from src.retrievers import retrieve_text, retrieve_labs, retrieve_genomic, retrieve_fused
from src.answer_generator import generate_answer


def run_query(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Full pipeline for one clinical query.

    Returns a structured result dict with:
      - routing decision (modality, confidence, reasoning, filters)
      - retrieved records
      - generated answer
      - faithfulness scores
      - wall-clock latency per stage
    """
    t0 = time.perf_counter()

    # 1. Route
    decision = route(query)
    t_route = time.perf_counter()

    # 2. Retrieve
    modality = decision.modality
    filters = decision.extracted_filters

    if modality == Modality.TEXT:
        retrieved = retrieve_text(query, n_results=top_k)
    elif modality == Modality.LABS:
        retrieved = retrieve_labs(query, filters)
    elif modality == Modality.GENOMIC:
        retrieved = retrieve_genomic(query, filters)
    else:  # FUSED
        retrieved = retrieve_fused(query, filters)

    t_retrieve = time.perf_counter()

    # 3. Generate answer
    result = generate_answer(query, retrieved, modality.value)
    t_generate = time.perf_counter()

    return {
        "query": query,
        "routing": {
            "modality": modality.value,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "filters": decision.extracted_filters,
        },
        "retrieved": retrieved,
        "answer": result["answer"],
        "evidence_used": result["evidence_used"],
        "faithfulness": result["faithfulness"],
        "latency_ms": {
            "routing": round((t_route - t0) * 1000, 1),
            "retrieval": round((t_retrieve - t_route) * 1000, 1),
            "generation": round((t_generate - t_retrieve) * 1000, 1),
            "total": round((t_generate - t0) * 1000, 1),
        },
    }
