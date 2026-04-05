"""
Labeled benchmark query set for routing accuracy evaluation.
50 queries across 4 modalities, representative of real oncology informatics use cases.
"""

BENCHMARK_QUERIES = [
    # TEXT (13)
    {"query": "What was the ECOG performance status documented at the last visit for patient P001?", "expected_modality": "TEXT"},
    {"query": "Summarize treatment history for patients with documented FOLFOX toxicity", "expected_modality": "TEXT"},
    {"query": "Which patients were referred to palliative care in their most recent note?", "expected_modality": "TEXT"},
    {"query": "Show oncology progress notes mentioning dose reduction", "expected_modality": "TEXT"},
    {"query": "What clinical trial was mentioned in the latest note for lung cancer patients?", "expected_modality": "TEXT"},
    {"query": "Find notes documenting complete response to pembrolizumab", "expected_modality": "TEXT"},
    {"query": "Which patients had weight loss documented in their progress notes?", "expected_modality": "TEXT"},
    {"query": "Retrieve notes where attending oncologist is Dr. Chen", "expected_modality": "TEXT"},
    {"query": "What adverse events were recorded for patients on osimertinib?", "expected_modality": "TEXT"},
    {"query": "Find progress notes documenting grade 3 neutropenia", "expected_modality": "TEXT"},
    {"query": "Which glioblastoma patients had stable disease at last imaging?", "expected_modality": "TEXT"},
    {"query": "Show notes for patients in Stage IVB with partial response", "expected_modality": "TEXT"},
    {"query": "Find all notes documenting peripheral neuropathy as an adverse event", "expected_modality": "TEXT"},

    # LABS (13)
    {"query": "Which patients have CRP above 10 mg/L?", "expected_modality": "LABS"},
    {"query": "Show patients with hemoglobin below 9 g/dL", "expected_modality": "LABS"},
    {"query": "Find patients with WBC greater than 11 K/uL at any visit", "expected_modality": "LABS"},
    {"query": "Which patients have elevated ALT above 60 U/L?", "expected_modality": "LABS"},
    {"query": "Show patients with trending CRP increase over serial visits", "expected_modality": "LABS"},
    {"query": "Retrieve lab results for patients with platelet count below 100", "expected_modality": "LABS"},
    {"query": "Which patients have CEA above 50 ng/mL?", "expected_modality": "LABS"},
    {"query": "Show CBC results for patients flagged as LOW for hemoglobin", "expected_modality": "LABS"},
    {"query": "Find patients with LDH above 400 U/L in the last blood panel", "expected_modality": "LABS"},
    {"query": "Which patients have creatinine above 1.5 mg/dL?", "expected_modality": "LABS"},
    {"query": "Show longitudinal CRP trends across all visits", "expected_modality": "LABS"},
    {"query": "Find patients with WBC below 3.5 K/uL — possible neutropenia", "expected_modality": "LABS"},
    {"query": "Retrieve complete metabolic panel results where AST is elevated above 50", "expected_modality": "LABS"},

    # GENOMIC (12)
    {"query": "Which patients have EGFR L858R mutations?", "expected_modality": "GENOMIC"},
    {"query": "Find all patients with KRAS G12C alterations", "expected_modality": "GENOMIC"},
    {"query": "Show genomic profiles for BRAF V600E positive patients", "expected_modality": "GENOMIC"},
    {"query": "Which patients have TMB-High tumors?", "expected_modality": "GENOMIC"},
    {"query": "Find patients with BRCA2 mutations eligible for PARP inhibitors", "expected_modality": "GENOMIC"},
    {"query": "Show NGS reports for patients with MSI-H status", "expected_modality": "GENOMIC"},
    {"query": "Which lung cancer patients have ALK fusions on FoundationOne CDx?", "expected_modality": "GENOMIC"},
    {"query": "Find patients with TP53 R248W variant in their molecular profile", "expected_modality": "GENOMIC"},
    {"query": "Show patients with IDH1 R132H mutation — glioblastoma cohort", "expected_modality": "GENOMIC"},
    {"query": "Which patients have ERBB2 amplification?", "expected_modality": "GENOMIC"},
    {"query": "Find colorectal patients with KRAS or NRAS wild-type status", "expected_modality": "GENOMIC"},
    {"query": "Show all patients with PIK3CA H1047R and PD-L1 TPS above 50%", "expected_modality": "GENOMIC"},

    # FUSED (12)
    {"query": "Which EGFR patients have CRP above 10 and documented progression?", "expected_modality": "FUSED"},
    {"query": "Find KRAS G12C patients with both elevated LDH and progressive disease in notes", "expected_modality": "FUSED"},
    {"query": "Show patients with BRAF V600E and hemoglobin below 10 g/dL", "expected_modality": "FUSED"},
    {"query": "Which MSI-H patients have elevated CRP and stable disease on pembrolizumab?", "expected_modality": "FUSED"},
    {"query": "Find TMB-High patients with WBC below 3.5 and dose reduction in their notes", "expected_modality": "FUSED"},
    {"query": "Show BRCA2 patients with CEA trending up and palliative care referral", "expected_modality": "FUSED"},
    {"query": "Which ALK fusion patients have elevated ALT and adverse events documented?", "expected_modality": "FUSED"},
    {"query": "Find patients with EGFR exon19del and CRP flagged HIGH at any visit", "expected_modality": "FUSED"},
    {"query": "Show patients who have both KRAS mutations and creatinine above 1.4", "expected_modality": "FUSED"},
    {"query": "Find patients on osimertinib with EGFR mutations and any abnormal CBC", "expected_modality": "FUSED"},
    {"query": "Which IDH1-mutant glioblastoma patients have LDH above 350 and partial response?", "expected_modality": "FUSED"},
    {"query": "Find patients with TP53 alterations, elevated CRP, and grade 3 toxicity documented", "expected_modality": "FUSED"},
]
