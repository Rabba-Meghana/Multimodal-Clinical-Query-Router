"""
Modality-specific retrievers for the Multimodal Clinical Query Router.

TEXT    → ChromaDB semantic search over clinical notes
LABS    → Pandas filter + aggregation over lab time-series
GENOMIC → Exact + fuzzy match over genomic profiles
FUSED   → Cross-modal join across all three stores
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

import chromadb
import pandas as pd
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

_chroma_client: Optional[chromadb.Client] = None
_notes_collection = None


def _get_chroma():
    global _chroma_client, _notes_collection
    if _chroma_client is None:
        _chroma_client = chromadb.Client()
        _notes_collection = _chroma_client.get_or_create_collection(
            name="clinical_notes",
            embedding_function=DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
        _load_notes_into_chroma()
    return _notes_collection


def _load_notes_into_chroma():
    notes_path = os.path.join(DATA_DIR, "clinical_notes.json")
    if not os.path.exists(notes_path):
        raise FileNotFoundError(
            "clinical_notes.json not found. Run: python scripts/generate_data.py"
        )
    with open(notes_path) as f:
        notes = json.load(f)

    ids, docs, metas = [], [], []
    for n in notes:
        ids.append(n["note_id"])
        docs.append(n["text"])
        metas.append({
            "patient_id": n["patient_id"],
            "date": n["date"],
            "cancer_type": n["metadata"]["cancer_type"],
            "mutation": n["metadata"]["mutation"],
            "treatment": n["metadata"]["treatment"],
            "stage": n["metadata"]["stage"],
            "progression": n["metadata"]["progression"],
        })

    if ids:
        _notes_collection.upsert(ids=ids, documents=docs, metadatas=metas)


_labs_df: Optional[pd.DataFrame] = None
_genomic_df: Optional[pd.DataFrame] = None
_patients_df: Optional[pd.DataFrame] = None


def _get_labs() -> pd.DataFrame:
    global _labs_df
    if _labs_df is None:
        path = os.path.join(DATA_DIR, "lab_results.json")
        if not os.path.exists(path):
            raise FileNotFoundError("lab_results.json not found. Run generate_data.py")
        _labs_df = pd.read_json(path)
        _labs_df["date"] = pd.to_datetime(_labs_df["date"])
    return _labs_df


def _get_genomic() -> pd.DataFrame:
    global _genomic_df
    if _genomic_df is None:
        path = os.path.join(DATA_DIR, "genomic_profiles.json")
        if not os.path.exists(path):
            raise FileNotFoundError("genomic_profiles.json not found. Run generate_data.py")
        _genomic_df = pd.read_json(path)
    return _genomic_df


def _get_patients() -> pd.DataFrame:
    global _patients_df
    if _patients_df is None:
        path = os.path.join(DATA_DIR, "patients.json")
        if not os.path.exists(path):
            raise FileNotFoundError("patients.json not found. Run generate_data.py")
        _patients_df = pd.read_json(path)
    return _patients_df


def retrieve_text(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Semantic search over clinical notes via ChromaDB."""
    collection = _get_chroma()
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    output = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        output.append({
            "source": "clinical_notes",
            "patient_id": meta["patient_id"],
            "date": meta["date"],
            "score": round(1 - dist, 4),
            "snippet": doc[:600] + ("..." if len(doc) > 600 else ""),
            "metadata": meta,
        })
    return output


_METRIC_ALIASES = {
    "CRP": ["crp", "c-reactive protein", "c reactive protein"],
    "WBC": ["wbc", "white blood cell", "white blood count", "leukocyte"],
    "HGB": ["hgb", "hemoglobin", "haemoglobin"],
    "PLT": ["plt", "platelet", "thrombocyte"],
    "ALT": ["alt", "alanine aminotransferase", "sgpt"],
    "AST": ["ast", "aspartate aminotransferase", "sgot"],
    "CEA": ["cea", "carcinoembryonic antigen"],
    "LDH": ["ldh", "lactate dehydrogenase"],
    "CREATININE": ["creatinine", "creat", "cr"],
}

_OP_MAP = {
    "above": ">", "greater than": ">", "more than": ">", "over": ">", ">": ">",
    "below": "<", "less than": "<", "under": "<", "<": "<",
    "at least": ">=", ">=": ">=",
    "at most": "<=", "<=": "<=",
    "equal to": "==", "=": "==",
}


def _canonical_metric(text: str) -> Optional[str]:
    text_l = text.lower()
    for canonical, aliases in _METRIC_ALIASES.items():
        if any(a in text_l for a in aliases):
            return canonical
    return None


def retrieve_labs(query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
    df = _get_labs().copy()

    metric = None
    operator = None
    threshold = None

    if filters:
        metric = filters.get("lab_metric")
        operator_raw = filters.get("lab_operator", "")
        threshold = filters.get("lab_threshold")
        operator = _OP_MAP.get(operator_raw.lower().strip(), ">")

    if metric is None:
        m = re.search(
            r"\b(crp|wbc|hgb|hemoglobin|alt|ast|cea|ldh|creatinine|plt|platelets?)\b"
            r".{0,30}(above|below|greater than|less than|>|<|>=|<=|at least|at most)\s*(\d+\.?\d*)",
            query, re.IGNORECASE,
        )
        if m:
            metric = _canonical_metric(m.group(1)) or m.group(1).upper()
            operator = _OP_MAP.get(m.group(2).lower().strip(), ">")
            threshold = float(m.group(3))

    results = []

    if metric and metric in df.columns and threshold is not None:
        mask = df.eval(f"{metric} {operator} {threshold}")
        subset = df[mask].sort_values(metric, ascending=(operator in ["<", "<="]))
        for _, row in subset.head(20).iterrows():
            results.append({
                "source": "lab_results",
                "patient_id": row["patient_id"],
                "date": str(row["date"].date()),
                "visit": int(row["visit"]),
                "metric": metric,
                "value": row[metric],
                "flag": row.get(f"{metric}_flag", "UNKNOWN"),
                "snapshot": {
                    k: row[k] for k in ["WBC", "HGB", "PLT", "ALT", "CRP", "CEA", "LDH"]
                    if k in row
                },
            })
    else:
        latest = df.sort_values("date").groupby("patient_id").last().reset_index()
        for _, row in latest.head(10).iterrows():
            results.append({
                "source": "lab_results",
                "patient_id": row["patient_id"],
                "date": str(row["date"].date()),
                "visit": int(row["visit"]),
                "metric": "ALL",
                "snapshot": {
                    k: row[k] for k in ["WBC", "HGB", "PLT", "ALT", "CRP", "CEA", "LDH"]
                    if k in row
                },
            })

    return results


def retrieve_genomic(query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
    df = _get_genomic().copy()

    genes = []
    variants = []

    if filters:
        genes = [g.upper() for g in filters.get("genes", [])]
        variants = filters.get("variants", [])

    if not genes:
        gene_match = re.findall(
            r"\b(EGFR|KRAS|BRAF|TP53|BRCA[12]|ERBB2|HER2|ALK|ROS1|MET|NTRK|PIK3CA|PTEN|IDH[12])\b",
            query, re.IGNORECASE,
        )
        genes = list(set(g.upper() for g in gene_match))

    results = []
    for _, row in df.iterrows():
        all_alts = [row["primary_alteration"]] + (row["co_alterations"] or [])
        all_alts_str = " ".join(all_alts).upper()

        match = False
        if genes:
            match = any(g in all_alts_str for g in genes)
        if variants:
            match = match or any(v.upper() in all_alts_str for v in variants)

        if match or (not genes and not variants):
            results.append({
                "source": "genomic_profiles",
                "patient_id": row["patient_id"],
                "cancer_type": row["cancer_type"],
                "primary_alteration": row["primary_alteration"],
                "co_alterations": row["co_alterations"],
                "tmb_score": row["tmb_score"],
                "tmb_class": row["tmb_class"],
                "msi_status": row["msi_status"],
                "pdl1_tps": row["pdl1_tps"],
                "assay": row["assay"],
            })

    return results[:15]


def retrieve_fused(query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
    genomic_results = retrieve_genomic(query, filters)
    lab_results = retrieve_labs(query, filters)
    text_results = retrieve_text(query, n_results=8)

    genomic_patients = {r["patient_id"] for r in genomic_results}
    lab_patients = {r["patient_id"] for r in lab_results}
    text_patients = {r["patient_id"] for r in text_results}

    all_patient_ids = genomic_patients | lab_patients | text_patients
    intersection = genomic_patients & lab_patients & text_patients

    priority_ids = intersection if intersection else (genomic_patients & lab_patients) or all_patient_ids

    genomic_map = {r["patient_id"]: r for r in genomic_results}
    lab_map: Dict = {}
    for r in lab_results:
        if r["patient_id"] not in lab_map:
            lab_map[r["patient_id"]] = r
    text_map = {r["patient_id"]: r for r in text_results}

    merged = []
    for pid in list(priority_ids)[:10]:
        record: Dict[str, Any] = {"patient_id": pid, "sources": []}
        if pid in genomic_map:
            record["genomic"] = genomic_map[pid]
            record["sources"].append("genomic")
        if pid in lab_map:
            record["labs"] = lab_map[pid]
            record["sources"].append("labs")
        if pid in text_map:
            record["notes"] = text_map[pid]
            record["sources"].append("notes")
        merged.append(record)

    return merged
