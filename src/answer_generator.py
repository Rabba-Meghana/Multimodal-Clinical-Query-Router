"""
Answer Generator: Synthesizes retrieved evidence into a grounded clinical answer.
Uses Groq (llama-3.3-70b-versatile) for generation + self-evaluation.
"""

import json
import os
import time
from typing import Any

from groq import Groq

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not set. Export it: export GROQ_API_KEY=your_key"
            )
        _client = Groq(api_key=api_key)
    return _client


_SYSTEM_PROMPT = """You are a clinical decision support assistant embedded in an oncology \
informatics platform (similar to Tempus or Foundation Medicine).

You answer clinician questions using ONLY the retrieved evidence provided. \
Your answers must be:
  1. Factually grounded — cite patient IDs and data points directly from evidence
  2. Concise but complete — lead with the direct answer, follow with supporting details
  3. Clinically precise — use proper oncology terminology
  4. Honest about uncertainty — if evidence is insufficient, say so explicitly

Format:
  - Start with a 1–2 sentence direct answer
  - Follow with a bullet-point evidence summary (patient IDs + key data)
  - End with a clinical caveat if appropriate

NEVER fabricate patient data. If the evidence doesn't answer the question, say so."""

_FAITHFULNESS_PROMPT = """You are evaluating whether an AI-generated clinical answer is \
faithfully grounded in the provided evidence.

Score on three dimensions (0.0–1.0 each):
1. grounding_score: Are all specific facts in the answer traceable to the evidence?
2. hallucination_risk: Inverse — 0.0 = no hallucination, 1.0 = severe hallucination
3. completeness: Does the answer address all aspects of the question?

Respond ONLY with a JSON object (no markdown fences):
{
  "grounding_score": <float>,
  "hallucination_risk": <float>,
  "completeness": <float>,
  "flags": [<list of specific concerns, empty if none>]
}"""


def _format_evidence(retrieved: list[dict[str, Any]], modality: str) -> str:
    """Serialize retrieved records into a compact evidence block."""
    if not retrieved:
        return "No evidence retrieved."

    lines = [f"=== RETRIEVED EVIDENCE (modality: {modality}) ===\n"]

    if modality == "FUSED":
        for i, record in enumerate(retrieved[:6], 1):
            lines.append(f"[Patient {record['patient_id']} — sources: {', '.join(record.get('sources', []))}]")
            if "genomic" in record:
                g = record["genomic"]
                lines.append(
                    f"  Genomic: {g['primary_alteration']} | {g.get('cancer_type','')} | "
                    f"TMB {g.get('tmb_score','')} ({g.get('tmb_class','')}) | MSI: {g.get('msi_status','')}"
                )
            if "labs" in record:
                snap = record["labs"].get("snapshot", {})
                lab_str = " | ".join(f"{k}={v}" for k, v in snap.items() if v is not None)
                lines.append(f"  Labs ({record['labs'].get('date','')}): {lab_str}")
                if record["labs"].get("flag") and record["labs"]["flag"] != "UNKNOWN":
                    lines.append(f"  ⚑ {record['labs']['metric']} = {record['labs']['value']} ({record['labs']['flag']})")
            if "notes" in record:
                lines.append(f"  Note snippet: {record['notes'].get('snippet','')[:300]}")
            lines.append("")
    elif modality == "LABS":
        for r in retrieved[:12]:
            snap = r.get("snapshot", {})
            snap_str = " | ".join(f"{k}={v}" for k, v in snap.items() if v is not None)
            flag = f" ⚑ {r['flag']}" if r.get("flag") not in (None, "NORMAL", "UNKNOWN") else ""
            lines.append(
                f"[{r['patient_id']}] {r.get('date','')} Visit {r.get('visit','')} | "
                f"{r.get('metric','')}={r.get('value','')}{flag} | {snap_str}"
            )
    elif modality == "GENOMIC":
        for r in retrieved[:10]:
            co = ", ".join(r.get("co_alterations") or []) or "none"
            lines.append(
                f"[{r['patient_id']}] {r['cancer_type']} | Primary: {r['primary_alteration']} | "
                f"Co-alt: {co} | TMB={r['tmb_score']} ({r['tmb_class']}) | "
                f"MSI={r['msi_status']} | PD-L1 TPS={r['pdl1_tps']}%"
            )
    else:  # TEXT
        for r in retrieved[:5]:
            lines.append(f"[{r['patient_id']}] Score={r['score']} Date={r['date']}")
            lines.append(f"  {r.get('snippet','')[:400]}")
            lines.append("")

    return "\n".join(lines)


def generate_answer(
    query: str,
    retrieved: list[dict[str, Any]],
    modality: str,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Generate a grounded clinical answer and compute faithfulness scores."""
    client = _get_client()
    evidence_block = _format_evidence(retrieved, modality)

    user_prompt = (
        f"CLINICAL QUESTION: {query}\n\n"
        f"{evidence_block}\n\n"
        "Provide a grounded answer using only the evidence above."
    )

    answer_text = ""
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.15,
                max_tokens=600,
            )
            answer_text = response.choices[0].message.content.strip()
            break
        except Exception as e:
            if attempt == max_retries:
                answer_text = f"[Generation failed after {max_retries+1} attempts: {e}]"
            else:
                time.sleep(1.5 * (attempt + 1))

    # Faithfulness evaluation
    faithfulness = _evaluate_faithfulness(client, query, evidence_block, answer_text)

    return {
        "answer": answer_text,
        "evidence_used": len(retrieved),
        "modality": modality,
        "faithfulness": faithfulness,
    }


def _evaluate_faithfulness(
    client: Groq, query: str, evidence: str, answer: str
) -> dict[str, Any]:
    """LLM-as-judge faithfulness scorer."""
    eval_prompt = (
        f"QUESTION: {query}\n\n"
        f"EVIDENCE:\n{evidence[:2000]}\n\n"
        f"ANSWER TO EVALUATE:\n{answer}\n\n"
        "Score this answer on grounding_score, hallucination_risk, and completeness."
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _FAITHFULNESS_PROMPT},
                {"role": "user", "content": eval_prompt},
            ],
            temperature=0.0,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        scores = json.loads(raw)
        return {
            "grounding_score": round(float(scores.get("grounding_score", 0.0)), 3),
            "hallucination_risk": round(float(scores.get("hallucination_risk", 0.0)), 3),
            "completeness": round(float(scores.get("completeness", 0.0)), 3),
            "flags": scores.get("flags", []),
        }
    except Exception as e:
        return {
            "grounding_score": 0.0,
            "hallucination_risk": 0.0,
            "completeness": 0.0,
            "flags": [f"Evaluation failed: {e}"],
        }
