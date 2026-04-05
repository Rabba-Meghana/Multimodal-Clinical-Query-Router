"""
Query Router: Classifies incoming clinical queries into retrieval modalities.
Modalities: TEXT (clinical notes), LABS (time-series lab data),
            GENOMIC (mutation profiles), FUSED (cross-modal join)
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Modality(str, Enum):
    TEXT = "TEXT"
    LABS = "LABS"
    GENOMIC = "GENOMIC"
    FUSED = "FUSED"


@dataclass
class RouterDecision:
    modality: Modality
    confidence: float
    reasoning: str
    extracted_filters: dict


# Rule patterns for deterministic pre-routing (fast path)
_LAB_PATTERNS = [
    r"\b(crp|wbc|hemoglobin|hgb|plt|platelets?|alt|ast|cea|ldh|creatinine)\b",
    r"\b(lab(s|oratory)?|blood (work|test|count|panel)|cbc|bmp|cmp)\b",
    r"\b(trending|trend|over time|serial|longitudinal|time[- ]series)\b",
    r"\b(elevated|high|low|above|below|flag(ged)?)\b.*\b(lab|level|count|value)\b",
]

_GENOMIC_PATTERNS = [
    r"\b(mutation|variant|snv|indel|cnv|fusion|amplification|deletion|alteration)\b",
    r"\b(egfr|kras|braf|tp53|brca[12]|erbb2|her2|alk|ros1|met|ntrk|pik3ca|pten|idh[12]|tert)\b",
    r"\b(genomic(s)?|ngs|next[- ]gen(eration)? sequencing|molecular profile|biomarker)\b",
    r"\b(l858r|g12c|g12d|g12v|v600e|r175h|r248w|h1047r|exon\s*\d+)\b",
    r"\b(msi[- ](h|high|low|stable)|tmb|tumor mutational burden|microsatellite)\b",
]

_FUSED_PATTERNS = [
    r"\b(and|with|who (also|have)|patients (with|having))\b.{0,60}"
    r"\b(crp|wbc|alt|labs?|lab (results?|values?)|genomic|mutation|egfr|kras)\b",
    r"\b(correlat|combin|both|together|cross)\b",
    r"\b(clinical (notes?|records?) (and|with|plus))\b",
    r"\bpatients? (with|having).{0,40}(and|plus|with).{0,40}(mutation|lab|crp|wbc|notes?)\b",
]

_compiled_lab = [re.compile(p, re.IGNORECASE) for p in _LAB_PATTERNS]
_compiled_genomic = [re.compile(p, re.IGNORECASE) for p in _GENOMIC_PATTERNS]
_compiled_fused = [re.compile(p, re.IGNORECASE) for p in _FUSED_PATTERNS]


def _extract_filters(query: str) -> dict:
    """Pull structured filters mentioned in the query."""
    filters = {}

    # Lab thresholds
    lab_threshold = re.search(
        r"\b(crp|wbc|hgb|hemoglobin|alt|ast|cea|ldh|creatinine|plt|platelets?)\b"
        r".{0,30}(above|below|greater than|less than|>|<|>=|<=)\s*(\d+\.?\d*)",
        query, re.IGNORECASE
    )
    if lab_threshold:
        filters["lab_metric"] = lab_threshold.group(1).upper()
        filters["lab_operator"] = lab_threshold.group(2)
        filters["lab_threshold"] = float(lab_threshold.group(3))

    # Gene names
    gene_match = re.findall(
        r"\b(EGFR|KRAS|BRAF|TP53|BRCA[12]|ERBB2|HER2|ALK|ROS1|MET|NTRK|PIK3CA|PTEN|IDH[12])\b",
        query, re.IGNORECASE
    )
    if gene_match:
        filters["genes"] = list(set(g.upper() for g in gene_match))

    # Specific variants
    variant_match = re.findall(
        r"\b([A-Z]\d+[A-Z]|exon\s*\d+\s*del|L858R|G12[CDVAR]|V600E)\b",
        query, re.IGNORECASE
    )
    if variant_match:
        filters["variants"] = list(set(variant_match))

    # Cancer type
    cancer_match = re.search(
        r"\b(lung|breast|colorectal|pancreatic|glioblastoma|nsclc|CRC)\b",
        query, re.IGNORECASE
    )
    if cancer_match:
        filters["cancer_type"] = cancer_match.group(1)

    # Outcome
    progression_match = re.search(
        r"\b(progression|progressive disease|partial response|complete response|stable disease)\b",
        query, re.IGNORECASE
    )
    if progression_match:
        filters["progression"] = progression_match.group(1)

    return filters


def route(query: str) -> RouterDecision:
    """
    Route a clinical query to its retrieval modality.

    Priority: FUSED > LABS > GENOMIC > TEXT
    Falls back to TEXT for natural language / note-based queries.
    """
    lab_hits = sum(1 for p in _compiled_lab if p.search(query))
    genomic_hits = sum(1 for p in _compiled_genomic if p.search(query))
    fused_hits = sum(1 for p in _compiled_fused if p.search(query))

    filters = _extract_filters(query)

    # Cross-modal fusion wins if both signals present OR explicit fusion pattern
    if fused_hits >= 1 and (lab_hits >= 1 or genomic_hits >= 1):
        return RouterDecision(
            modality=Modality.FUSED,
            confidence=min(0.60 + fused_hits * 0.10 + (lab_hits + genomic_hits) * 0.05, 0.97),
            reasoning=(
                f"Cross-modal query detected: {fused_hits} fusion signal(s), "
                f"{lab_hits} lab signal(s), {genomic_hits} genomic signal(s). "
                "Will join clinical notes + lab time-series + genomic profiles."
            ),
            extracted_filters=filters,
        )

    if lab_hits >= 2 or (lab_hits >= 1 and genomic_hits == 0 and fused_hits == 0):
        confidence = min(0.55 + lab_hits * 0.12, 0.96)
        return RouterDecision(
            modality=Modality.LABS,
            confidence=confidence,
            reasoning=(
                f"Lab-focused query: {lab_hits} lab signal(s). "
                "Will search structured lab time-series for matching metrics."
            ),
            extracted_filters=filters,
        )

    if genomic_hits >= 1:
        confidence = min(0.58 + genomic_hits * 0.10, 0.96)
        return RouterDecision(
            modality=Modality.GENOMIC,
            confidence=confidence,
            reasoning=(
                f"Genomic query: {genomic_hits} genomic signal(s). "
                "Will search NGS mutation profiles."
            ),
            extracted_filters=filters,
        )

    # Default: semantic search over clinical notes
    return RouterDecision(
        modality=Modality.TEXT,
        confidence=0.72,
        reasoning=(
            "No structured signals detected. "
            "Routing to semantic search over clinical notes."
        ),
        extracted_filters=filters,
    )
