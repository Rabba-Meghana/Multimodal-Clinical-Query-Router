"""
Generate synthetic oncology dataset for Multimodal Clinical Query Router.
Produces: clinical notes, lab time-series, genomic profiles.
All data is synthetic and HIPAA-safe.
"""

import json
import os
import random
from datetime import datetime, timedelta

random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

PATIENTS = [
    {
        "id": f"P{i:03d}",
        "name": f"Patient-{i:03d}",
        "age": random.randint(45, 78),
        "sex": random.choice(["M", "F"]),
        "cancer_type": random.choice([
            "Non-Small Cell Lung Cancer",
            "Colorectal Adenocarcinoma",
            "Breast Invasive Carcinoma",
            "Pancreatic Ductal Adenocarcinoma",
            "Glioblastoma Multiforme",
        ]),
    }
    for i in range(1, 26)
]

MUTATIONS = {
    "Non-Small Cell Lung Cancer": [
        "EGFR L858R", "EGFR exon19del", "KRAS G12C", "ALK fusion", "ROS1 fusion",
        "MET exon14 skipping", "BRAF V600E",
    ],
    "Colorectal Adenocarcinoma": [
        "KRAS G12D", "BRAF V600E", "MSI-H", "NRAS Q61H", "PIK3CA E545K",
        "KRAS G12V", "RNF43 mut",
    ],
    "Breast Invasive Carcinoma": [
        "PIK3CA H1047R", "TP53 R175H", "ERBB2 amplification", "BRCA1 del",
        "CDH1 mut", "ESR1 D538G", "PTEN loss",
    ],
    "Pancreatic Ductal Adenocarcinoma": [
        "KRAS G12V", "TP53 R248W", "CDKN2A del", "SMAD4 loss", "BRCA2 mut",
    ],
    "Glioblastoma Multiforme": [
        "EGFR amplification", "PTEN loss", "IDH1 R132H", "TERT promoter", "NF1 mut",
    ],
}

TREATMENTS = [
    "Pembrolizumab", "Osimertinib", "Bevacizumab + FOLFOX", "Carboplatin + Paclitaxel",
    "Trastuzumab + Pertuzumab", "Olaparib", "Temozolomide", "Erlotinib",
    "Sotorasib", "Encorafenib + Binimetinib", "Sacituzumab govitecan",
    "Atezolizumab + Nab-paclitaxel",
]

ATTENDINGS = ["Chen", "Patel", "Williams", "Rodriguez", "Kim", "Okonkwo", "Barrientos"]
STAGES = ["Stage IIA", "Stage IIB", "Stage IIIA", "Stage IIIB", "Stage IVA", "Stage IVB"]
ECOG = [
    "ECOG 0 (fully active)",
    "ECOG 1 (restricted in physically strenuous activity)",
    "ECOG 2 (ambulatory, capable of all self-care)",
    "ECOG 3 (limited self-care, confined to bed >50% of waking hours)",
]
PROGRESSIONS = [
    "stable disease (SD)", "partial response (PR)", "progressive disease (PD)",
    "complete response (CR)", "mixed response",
]


def generate_clinical_notes():
    notes = []
    base_date = datetime(2023, 1, 1)
    for patient in PATIENTS:
        mutation = random.choice(MUTATIONS[patient["cancer_type"]])
        treatment = random.choice(TREATMENTS)
        stage = random.choice(STAGES)
        progression = random.choice(PROGRESSIONS)
        visit_date = base_date + timedelta(days=random.randint(0, 365))
        ps = random.choice(ECOG)
        attending = random.choice(ATTENDINGS)
        cycle = random.randint(2, 14)
        ae = random.choice([
            "Grade 1 fatigue and mild nausea, managed conservatively.",
            "Grade 2 peripheral neuropathy; dose reduced by 20%.",
            "Grade 1 rash, topical steroids initiated.",
            "No clinically significant adverse events this cycle.",
            "Grade 3 neutropenia; held treatment for 7 days, now recovered.",
        ])
        trial = (
            f"Patient consented to clinical trial NCT0{random.randint(1000000,9999999)} "
            f"evaluating {random.choice(['combination immunotherapy', 'targeted inhibitor', 'ADC therapy'])} "
            f"given {mutation} status."
            if random.random() > 0.55 else
            "No eligible clinical trials identified at this time. Will re-evaluate at next visit."
        )
        note_text = (
            f"ONCOLOGY PROGRESS NOTE\n"
            f"Date: {visit_date.strftime('%Y-%m-%d')}\n"
            f"Patient: {patient['name']}  |  Age: {patient['age']}  |  Sex: {patient['sex']}\n"
            f"MRN: {patient['id']}\n\n"
            f"DIAGNOSIS: {patient['cancer_type']}, {stage}\n"
            f"GENOMIC PROFILE: {mutation} — confirmed on tissue NGS panel (FoundationOne CDx).\n\n"
            f"HISTORY OF PRESENT ILLNESS:\n"
            f"Patient presents for Cycle {cycle} of {treatment}. "
            f"Performance status: {ps}. "
            f"Most recent CT imaging ({(visit_date - timedelta(days=14)).strftime('%Y-%m-%d')}) demonstrates {progression}. "
            f"Adverse events this cycle: {ae} "
            f"{'Weight loss of '+str(random.randint(2,9))+' lbs noted since last visit.' if random.random()>0.4 else 'Weight stable at baseline.'}\n\n"
            f"ASSESSMENT AND PLAN:\n"
            f"1. Continue {treatment} at {'current dose' if 'reduced' not in ae else 'dose-reduced protocol'}.\n"
            f"2. {'Refer to palliative care for symptom management and goals-of-care discussion.' if random.random()>0.55 else 'Continue supportive care per current plan.'}\n"
            f"3. Repeat CT chest/abdomen/pelvis in {'6' if progression not in ['progressive disease (PD)'] else '4'}-8 weeks.\n"
            f"4. {trial}\n"
            f"5. Labs reviewed and within acceptable parameters for treatment continuation.\n\n"
            f"Attending Oncologist: Dr. {attending}, MD\n"
            f"Fellow: Dr. {random.choice(ATTENDINGS)}, MD (Fellow)\n"
        )
        notes.append({
            "patient_id": patient["id"],
            "note_id": f"NOTE-{patient['id']}-{visit_date.strftime('%Y%m%d')}",
            "date": visit_date.strftime("%Y-%m-%d"),
            "note_type": "Oncology Progress Note",
            "text": note_text,
            "metadata": {
                "mutation": mutation,
                "treatment": treatment,
                "stage": stage,
                "progression": progression,
                "cancer_type": patient["cancer_type"],
                "attending": attending,
            },
        })
    return notes


def generate_lab_results():
    labs = []
    base_date = datetime(2023, 1, 1)
    for patient in PATIENTS:
        crp_trajectory = random.choice(["increasing", "decreasing", "stable"])
        crp_base = random.uniform(1.5, 12.0)
        for visit in range(1, 9):
            visit_date = base_date + timedelta(days=visit * 42 + random.randint(-5, 5))
            if crp_trajectory == "increasing":
                crp = round(crp_base * (1 + visit * 0.3) + random.uniform(-1, 2), 1)
            elif crp_trajectory == "decreasing":
                crp = round(max(0.3, crp_base * (1 - visit * 0.08) + random.uniform(-0.5, 1)), 1)
            else:
                crp = round(crp_base + random.uniform(-2, 2), 1)

            wbc = round(random.uniform(2.1, 12.5), 1)
            hgb = round(random.uniform(8.2, 14.8), 1)
            labs.append({
                "patient_id": patient["id"],
                "visit": visit,
                "date": visit_date.strftime("%Y-%m-%d"),
                "WBC": wbc,
                "WBC_unit": "K/uL",
                "WBC_flag": "LOW" if wbc < 3.5 else ("HIGH" if wbc > 10.5 else "NORMAL"),
                "HGB": hgb,
                "HGB_unit": "g/dL",
                "HGB_flag": "LOW" if hgb < 11.5 else "NORMAL",
                "PLT": random.randint(85, 420),
                "PLT_unit": "K/uL",
                "ALT": random.randint(12, 88),
                "ALT_unit": "U/L",
                "AST": random.randint(10, 75),
                "AST_unit": "U/L",
                "CRP": crp,
                "CRP_unit": "mg/L",
                "CRP_flag": "HIGH" if crp > 10 else "NORMAL",
                "CEA": round(random.uniform(1.2, 145.0), 1),
                "CEA_unit": "ng/mL",
                "LDH": random.randint(140, 580),
                "LDH_unit": "U/L",
                "CREATININE": round(random.uniform(0.6, 2.1), 2),
                "CREATININE_unit": "mg/dL",
            })
    return labs


def generate_genomic_profiles():
    profiles = []
    for patient in PATIENTS:
        primary_mutation = random.choice(MUTATIONS[patient["cancer_type"]])
        co_mutations = random.sample(
            [m for m in MUTATIONS[patient["cancer_type"]] if m != primary_mutation],
            k=min(2, len(MUTATIONS[patient["cancer_type"]]) - 1),
        )
        tmb = round(random.uniform(1.0, 62.0), 1)
        profiles.append({
            "patient_id": patient["id"],
            "cancer_type": patient["cancer_type"],
            "assay": "FoundationOne CDx",
            "report_date": "2023-01-15",
            "primary_alteration": primary_mutation,
            "co_alterations": co_mutations,
            "tmb_score": tmb,
            "tmb_class": "TMB-High" if tmb >= 10 else "TMB-Low",
            "msi_status": random.choice(["MSS", "MSI-L", "MSI-H"]),
            "pdl1_tps": random.randint(0, 100),
            "actionable_tier1": [primary_mutation],
            "actionable_tier2": co_mutations[:1] if co_mutations else [],
        })
    return profiles


def main():
    notes = generate_clinical_notes()
    with open(os.path.join(OUT_DIR, "clinical_notes.json"), "w") as f:
        json.dump(notes, f, indent=2)
    print(f"✅ Generated {len(notes)} clinical notes → data/clinical_notes.json")

    labs = generate_lab_results()
    with open(os.path.join(OUT_DIR, "lab_results.json"), "w") as f:
        json.dump(labs, f, indent=2)
    print(f"✅ Generated {len(labs)} lab records ({len(PATIENTS)} patients × 8 visits) → data/lab_results.json")

    genomic = generate_genomic_profiles()
    with open(os.path.join(OUT_DIR, "genomic_profiles.json"), "w") as f:
        json.dump(genomic, f, indent=2)
    print(f"✅ Generated {len(genomic)} genomic profiles → data/genomic_profiles.json")

    # Patient index
    with open(os.path.join(OUT_DIR, "patients.json"), "w") as f:
        json.dump(PATIENTS, f, indent=2)
    print(f"✅ Generated patient index ({len(PATIENTS)} patients) → data/patients.json")


if __name__ == "__main__":
    main()
