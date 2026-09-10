import os
import csv
import json
import random
from datetime import datetime, timedelta

def create_directories():
    dirs = [
        "data/patient",
        "data/medication",
        "data/appointment",
        "data/doctor",
        "data/knowledge",
        "data/safety"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("Created data directories.")

def generate_hospitals():
    hospitals = [
        {
            "hospital_id": "HOSP_001",
            "hospital_name": "Apollo Super Specialty Hospital",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "emergency_contact": "+91-44-2829-0200",
            "trauma_level": "Level 1"
        },
        {
            "hospital_id": "HOSP_002",
            "hospital_name": "Fortis Memorial Healthcare Institute",
            "city": "Bengaluru",
            "state": "Karnataka",
            "emergency_contact": "+91-80-6621-4444",
            "trauma_level": "Level 1"
        },
        {
            "hospital_id": "HOSP_003",
            "hospital_name": "AIIMS Medical Center",
            "city": "New Delhi",
            "state": "Delhi",
            "emergency_contact": "+91-11-2658-8500",
            "trauma_level": "Level 1"
        }
    ]
    with open("data/doctor/hospitals.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=hospitals[0].keys())
        writer.writeheader()
        writer.writerows(hospitals)
    print("Generated hospitals.csv")

def generate_doctors():
    doctors = [
        {
            "doctor_id": "DOC_101",
            "hospital_id": "HOSP_001",
            "doctor_name": "Dr. Arvind Ramanathan",
            "specialization": "Cardiology",
            "qualification": "MD, DM (Cardiology), FACC",
            "experience_years": 18,
            "email": "dr.arvind.r@apollohealth.org",
            "phone": "+91-98401-22334"
        },
        {
            "doctor_id": "DOC_102",
            "hospital_id": "HOSP_001",
            "doctor_name": "Dr. Sunita Deshmukh",
            "specialization": "Endocrinology & Diabetology",
            "qualification": "MD (Internal Med), DNB (Endocrinology)",
            "experience_years": 14,
            "email": "dr.sunita.d@apollohealth.org",
            "phone": "+91-98402-44556"
        },
        {
            "doctor_id": "DOC_103",
            "hospital_id": "HOSP_002",
            "doctor_name": "Dr. Rajeshwar Rao",
            "specialization": "Pulmonology",
            "qualification": "MD (Pulmonary Medicine)",
            "experience_years": 16,
            "email": "dr.rao@fortishealth.org",
            "phone": "+91-98403-66778"
        },
        {
            "doctor_id": "DOC_104",
            "hospital_id": "HOSP_003",
            "doctor_name": "Dr. Priya Venkatesh",
            "specialization": "General Medicine",
            "qualification": "MBBS, MD (General Medicine)",
            "experience_years": 10,
            "email": "dr.priya@aiims.gov.in",
            "phone": "+91-98404-88990"
        }
    ]
    with open("data/doctor/doctors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=doctors[0].keys())
        writer.writeheader()
        writer.writerows(doctors)
    print("Generated doctors.csv")

def generate_patients():
    patients = [
        {
            "patient_id": "PAT_001",
            "first_name": "Ramesh",
            "last_name": "Krishnamurthy",
            "age": 58,
            "gender": "Male",
            "blood_group": "B+",
            "primary_condition": "Hypertensive Heart Disease & Stage 2 Hypertension",
            "allergies": "Penicillin, Sulfa drugs",
            "emergency_contact_name": "Kavitha Krishnamurthy (Wife)",
            "emergency_contact_phone": "+91-98840-11223",
            "assigned_doctor_id": "DOC_101",
            "risk_tier": "HIGH"
        },
        {
            "patient_id": "PAT_002",
            "first_name": "Meera",
            "last_name": "Nambiar",
            "age": 52,
            "gender": "Female",
            "blood_group": "O+",
            "primary_condition": "Type 2 Diabetes Mellitus with Peripheral Neuropathy",
            "allergies": "None",
            "emergency_contact_name": "Suresh Nambiar (Husband)",
            "emergency_contact_phone": "+91-98840-22334",
            "assigned_doctor_id": "DOC_102",
            "risk_tier": "MODERATE"
        },
        {
            "patient_id": "PAT_003",
            "first_name": "Vikram",
            "last_name": "Singhania",
            "age": 44,
            "gender": "Male",
            "blood_group": "A+",
            "primary_condition": "Moderate Persistent Asthma & Allergic Rhinitis",
            "allergies": "Aspirin, Dust Mites",
            "emergency_contact_name": "Ananya Singhania (Sister)",
            "emergency_contact_phone": "+91-98840-33445",
            "assigned_doctor_id": "DOC_103",
            "risk_tier": "LOW"
        },
        {
            "patient_id": "PAT_004",
            "first_name": "Savitri",
            "last_name": "Devi",
            "age": 67,
            "gender": "Female",
            "blood_group": "AB+",
            "primary_condition": "Chronic Kidney Disease (Stage 3b) & Congestive Heart Failure",
            "allergies": "Ibuprofen, Contrast Dye",
            "emergency_contact_name": "Rohit Kumar (Son)",
            "emergency_contact_phone": "+91-98840-44556",
            "assigned_doctor_id": "DOC_101",
            "risk_tier": "CRITICAL"
        }
    ]
    with open("data/patient/patients.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=patients[0].keys())
        writer.writeheader()
        writer.writerows(patients)
    print("Generated patients.csv")

def generate_consultations():
    consultations = [
        {
            "consultation_id": "CON_1001",
            "patient_id": "PAT_001",
            "doctor_id": "DOC_101",
            "consultation_date": "2026-08-15 10:30:00",
            "chief_complaint": "Occipital morning headaches and bilateral ankle edema.",
            "clinical_notes": "Patient presented with uncontrolled hypertension. Baseline BP recorded at 160/98 mmHg. Resting ECG shows early Left Ventricular Hypertrophy (LVH). Recommended salt restriction, Telmisartan 40mg + Amlodipine 5mg titration, and bi-daily BP logging.",
            "primary_diagnosis": "Stage 2 Essential Hypertension with LVH",
            "icd10_code": "I10, I51.7",
            "follow_up_weeks": 4
        },
        {
            "consultation_id": "CON_1002",
            "patient_id": "PAT_002",
            "doctor_id": "DOC_102",
            "consultation_date": "2026-08-10 11:15:00",
            "chief_complaint": "Persistent fatigue, postprandial somnolence, and burning sensation in feet.",
            "clinical_notes": "Fasting blood sugar averaging 175 mg/dL; HbA1c at 8.4%. Mild distal symmetric sensory loss in lower extremities. Titrated Metformin to 1000mg BID and added Dapagliflozin 10mg once daily in morning. Advised foot care hygiene.",
            "primary_diagnosis": "Type 2 Diabetes Mellitus with Diabetic Neuropathy",
            "icd10_code": "E11.40",
            "follow_up_weeks": 6
        },
        {
            "consultation_id": "CON_1003",
            "patient_id": "PAT_003",
            "doctor_id": "DOC_103",
            "consultation_date": "2026-08-20 14:00:00",
            "chief_complaint": "Nocturnal cough and exertional wheezing after jogging.",
            "clinical_notes": "Spirometry reveals FEV1/FVC ratio of 68% with 15% bronchodilator reversibility. Prescribed Budesonide/Formoterol (160/4.5 mcg) DPI twice daily and Salbutamol inhaler PRN. Patient educated on inhaler spacer technique.",
            "primary_diagnosis": "Moderate Persistent Bronchial Asthma",
            "icd10_code": "J45.40",
            "follow_up_weeks": 8
        },
        {
            "consultation_id": "CON_1004",
            "patient_id": "PAT_004",
            "doctor_id": "DOC_101",
            "consultation_date": "2026-08-25 09:45:00",
            "chief_complaint": "Orthopnea, shortness of breath on walking 50 meters, severe pedal edema.",
            "clinical_notes": "Elevated JVP, bibasilar rales on chest auscultation. Serum creatinine 2.4 mg/dL (eGFR 24 mL/min/1.73m2), NT-proBNP 2400 pg/mL. Prescribed Torsemide 20mg morning, strict 1.2L fluid restriction, and urgent nephrology co-management.",
            "primary_diagnosis": "Congestive Heart Failure (NYHA Class III) with CKD Stage 3b",
            "icd10_code": "I50.9, N18.32",
            "follow_up_weeks": 2
        }
    ]
    with open("data/patient/consultations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=consultations[0].keys())
        writer.writeheader()
        writer.writerows(consultations)
    print("Generated consultations.csv")

def generate_vitals():
    vitals = []
    base_date = datetime(2026, 8, 25, 8, 0, 0)
    
    # PAT_001: Hypertension worsening to spike
    for day in range(15):
        dt = base_date + timedelta(days=day)
        systolic = 150 + day if day < 12 else 178 + (day - 12) * 5
        diastolic = 92 + (day // 2) if day < 12 else 105 + (day - 12) * 2
        vitals.append({
            "vital_id": f"VIT_{1000 + len(vitals)}",
            "patient_id": "PAT_001",
            "recorded_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "heart_rate": 78 + (day % 4),
            "spo2": 97,
            "temperature_c": 36.6,
            "blood_glucose_mg_dl": 108,
            "respiratory_rate": 16
        })

    # PAT_002: Diabetes glucose fluctuations
    for day in range(15):
        dt = base_date + timedelta(days=day)
        vitals.append({
            "vital_id": f"VIT_{1000 + len(vitals)}",
            "patient_id": "PAT_002",
            "recorded_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "systolic_bp": 126 + (day % 3),
            "diastolic_bp": 80,
            "heart_rate": 72,
            "spo2": 98,
            "temperature_c": 36.7,
            "blood_glucose_mg_dl": 165 + (day * 3) if day > 8 else 140 + day,
            "respiratory_rate": 15
        })

    # PAT_003: Stable Asthma
    for day in range(15):
        dt = base_date + timedelta(days=day)
        vitals.append({
            "vital_id": f"VIT_{1000 + len(vitals)}",
            "patient_id": "PAT_003",
            "recorded_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "systolic_bp": 118,
            "diastolic_bp": 76,
            "heart_rate": 74,
            "spo2": 98 - (1 if day % 5 == 0 else 0),
            "temperature_c": 36.6,
            "blood_glucose_mg_dl": 95,
            "respiratory_rate": 16
        })

    # PAT_004: Critical SpO2 desaturation and fluid overload
    for day in range(15):
        dt = base_date + timedelta(days=day)
        spo2_val = 94 - (day // 3) if day < 12 else 88
        vitals.append({
            "vital_id": f"VIT_{1000 + len(vitals)}",
            "patient_id": "PAT_004",
            "recorded_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "systolic_bp": 142 + (day % 5),
            "diastolic_bp": 88,
            "heart_rate": 96 + (day % 6),
            "spo2": spo2_val,
            "temperature_c": 37.1,
            "blood_glucose_mg_dl": 125,
            "respiratory_rate": 24 if spo2_val < 90 else 20
        })

    with open("data/patient/vitals.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=vitals[0].keys())
        writer.writeheader()
        writer.writerows(vitals)
    print("Generated vitals.csv")

def generate_lab_results():
    labs = [
        {
            "lab_id": "LAB_501",
            "patient_id": "PAT_001",
            "consultation_id": "CON_1001",
            "test_name": "Lipid Profile & Serum Electrolytes",
            "test_date": "2026-08-16 08:30:00",
            "biomarker": "Serum Potassium (K+)",
            "result_value": 4.6,
            "unit": "mEq/L",
            "reference_range": "3.5 - 5.0",
            "status": "NORMAL"
        },
        {
            "lab_id": "LAB_502",
            "patient_id": "PAT_001",
            "consultation_id": "CON_1001",
            "test_name": "Lipid Profile",
            "test_date": "2026-08-16 08:30:00",
            "biomarker": "LDL Cholesterol",
            "result_value": 158.0,
            "unit": "mg/dL",
            "reference_range": "< 100",
            "status": "ELEVATED"
        },
        {
            "lab_id": "LAB_503",
            "patient_id": "PAT_002",
            "consultation_id": "CON_1002",
            "test_name": "Glycemic Control Panel",
            "test_date": "2026-08-11 09:00:00",
            "biomarker": "HbA1c",
            "result_value": 8.4,
            "unit": "%",
            "reference_range": "< 5.7",
            "status": "HIGH"
        },
        {
            "lab_id": "LAB_504",
            "patient_id": "PAT_002",
            "consultation_id": "CON_1002",
            "test_name": "Renal Function Test",
            "test_date": "2026-08-11 09:00:00",
            "biomarker": "Microalbumin / Creatinine Ratio",
            "result_value": 45.0,
            "unit": "mg/g",
            "reference_range": "< 30",
            "status": "ELEVATED"
        },
        {
            "lab_id": "LAB_505",
            "patient_id": "PAT_004",
            "consultation_id": "CON_1004",
            "test_name": "Cardiac & Renal Biomarkers",
            "test_date": "2026-08-26 10:00:00",
            "biomarker": "NT-proBNP",
            "result_value": 2400.0,
            "unit": "pg/mL",
            "reference_range": "< 300",
            "status": "CRITICAL_HIGH"
        },
        {
            "lab_id": "LAB_506",
            "patient_id": "PAT_004",
            "consultation_id": "CON_1004",
            "test_name": "Renal Function Test",
            "test_date": "2026-08-26 10:00:00",
            "biomarker": "Serum Creatinine",
            "result_value": 2.4,
            "unit": "mg/dL",
            "reference_range": "0.6 - 1.2",
            "status": "HIGH"
        }
    ]
    with open("data/patient/lab_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=labs[0].keys())
        writer.writeheader()
        writer.writerows(labs)
    print("Generated lab_results.csv")

def generate_symptoms():
    symptoms = [
        {
            "symptom_id": "SYM_201",
            "patient_id": "PAT_001",
            "symptom_name": "Throbbing Occipital Headache & Dizziness",
            "severity": 8,
            "body_location": "Head / Neck",
            "onset_date": "2026-09-08 07:00:00",
            "reported_at": "2026-09-08 08:30:00",
            "notes": "Triggered upon waking up; accompanied by blurred vision sensation."
        },
        {
            "symptom_id": "SYM_202",
            "patient_id": "PAT_002",
            "symptom_name": "Tingling & Burning Dysesthesia in Toes",
            "severity": 6,
            "body_location": "Feet / Lower Extremities",
            "onset_date": "2026-09-05 21:00:00",
            "reported_at": "2026-09-06 09:15:00",
            "notes": "Worse at night, interfering with sleep cycle."
        },
        {
            "symptom_id": "SYM_203",
            "patient_id": "PAT_003",
            "symptom_name": "Mild Dry Cough after morning walk",
            "severity": 3,
            "body_location": "Chest / Throat",
            "onset_date": "2026-09-07 07:30:00",
            "reported_at": "2026-09-07 08:00:00",
            "notes": "Relieved after using Budesonide inhaler."
        },
        {
            "symptom_id": "SYM_204",
            "patient_id": "PAT_004",
            "symptom_name": "Severe Shortness of Breath at Rest & Orthopnea",
            "severity": 9,
            "body_location": "Chest",
            "onset_date": "2026-09-09 23:00:00",
            "reported_at": "2026-09-10 06:15:00",
            "notes": "Patient unable to lie flat, sleeping propped on 3 pillows."
        }
    ]
    with open("data/patient/symptoms.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=symptoms[0].keys())
        writer.writeheader()
        writer.writerows(symptoms)
    print("Generated symptoms.csv")

def generate_daily_checkins():
    checkins = []
    base_date = datetime(2026, 9, 1)
    for p_id, pain_b, sleep_b, mood in [
        ("PAT_001", 3, 6.0, "Anxious"),
        ("PAT_002", 4, 6.5, "Fatigued"),
        ("PAT_003", 1, 7.5, "Good"),
        ("PAT_004", 7, 4.0, "Distressed")
    ]:
        for day in range(10):
            dt = base_date + timedelta(days=day)
            checkins.append({
                "checkin_id": f"CHK_{100 + len(checkins)}",
                "patient_id": p_id,
                "checkin_date": dt.strftime("%Y-%m-%d"),
                "pain_score": min(10, max(0, pain_b + (1 if day > 7 else 0))),
                "sleep_hours": round(max(3.0, sleep_b - (0.5 if day > 7 else 0.0)), 1),
                "fatigue_level": "High" if p_id in ["PAT_001", "PAT_004"] and day > 6 else "Moderate",
                "mood": mood if day < 7 else ("Stressed" if p_id in ["PAT_001", "PAT_004"] else mood),
                "fluid_intake_liters": 1.2 if p_id == "PAT_004" else 2.2,
                "notes": "Followed prescribed diet." if day < 7 else "Experiencing increasing morning stiffness."
            })
    with open("data/patient/daily_checkins.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=checkins[0].keys())
        writer.writeheader()
        writer.writerows(checkins)
    print("Generated daily_checkins.csv")

def generate_monitoring_events():
    events = [
        {
            "event_id": "EVT_701",
            "patient_id": "PAT_001",
            "event_type": "HYPERTENSIVE_CRISIS_RISK",
            "severity": "CRITICAL",
            "detected_at": "2026-09-09 08:30:00",
            "description": "Systolic BP spiked to 188 mmHg (> 180 threshold) accompanied by severe occipital headache.",
            "status": "PENDING_DOCTOR_REVIEW"
        },
        {
            "event_id": "EVT_702",
            "patient_id": "PAT_002",
            "event_type": "MEDICATION_NON_ADHERENCE",
            "severity": "WARNING",
            "detected_at": "2026-09-08 20:00:00",
            "description": "Metformin missed for 3 consecutive evening doses. Adherence 30-day rate dropped to 68%.",
            "status": "ALERTED_PATIENT"
        },
        {
            "event_id": "EVT_703",
            "patient_id": "PAT_004",
            "event_type": "HYPOXEMIA_DESATURATION",
            "severity": "CRITICAL",
            "detected_at": "2026-09-10 06:20:00",
            "description": "SpO2 dropped to 88% (< 90% threshold) with resting respiratory rate 24 bpm.",
            "status": "ESCALATED_EMERGENCY"
        }
    ]
    with open("data/patient/monitoring_events.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=events[0].keys())
        writer.writeheader()
        writer.writerows(events)
    print("Generated monitoring_events.csv")

def generate_medications():
    medications = [
        {
            "medication_id": "MED_301",
            "patient_id": "PAT_001",
            "consultation_id": "CON_1001",
            "medication_name": "Telmisartan",
            "dosage": "40 mg",
            "route": "Oral",
            "frequency": "Once Daily (Morning)",
            "start_date": "2026-08-15",
            "end_date": "2026-11-15",
            "instructions": "Take with or without food. Monitor daily blood pressure."
        },
        {
            "medication_id": "MED_302",
            "patient_id": "PAT_001",
            "consultation_id": "CON_1001",
            "medication_name": "Amlodipine",
            "dosage": "5 mg",
            "route": "Oral",
            "frequency": "Once Daily (Evening)",
            "start_date": "2026-08-15",
            "end_date": "2026-11-15",
            "instructions": "Take after dinner. Watch for ankle swelling."
        },
        {
            "medication_id": "MED_303",
            "patient_id": "PAT_001",
            "consultation_id": "CON_1001",
            "medication_name": "Rosuvastatin",
            "dosage": "10 mg",
            "route": "Oral",
            "frequency": "Once Daily (Night)",
            "start_date": "2026-08-15",
            "end_date": "2026-11-15",
            "instructions": "Take at bedtime for lipid reduction."
        },
        {
            "medication_id": "MED_304",
            "patient_id": "PAT_002",
            "consultation_id": "CON_1002",
            "medication_name": "Metformin Hydrochloride",
            "dosage": "1000 mg",
            "route": "Oral",
            "frequency": "Twice Daily (Morning & Night)",
            "start_date": "2026-08-10",
            "end_date": "2026-11-10",
            "instructions": "Take with meals to minimize gastrointestinal discomfort."
        },
        {
            "medication_id": "MED_305",
            "patient_id": "PAT_002",
            "consultation_id": "CON_1002",
            "medication_name": "Dapagliflozin",
            "dosage": "10 mg",
            "route": "Oral",
            "frequency": "Once Daily (Morning)",
            "start_date": "2026-08-10",
            "end_date": "2026-11-10",
            "instructions": "Stay well hydrated throughout the day."
        },
        {
            "medication_id": "MED_306",
            "patient_id": "PAT_003",
            "consultation_id": "CON_1003",
            "medication_name": "Budesonide / Formoterol Inhaler",
            "dosage": "160/4.5 mcg",
            "route": "Inhalation (DPI)",
            "frequency": "2 Puffs Twice Daily",
            "start_date": "2026-08-20",
            "end_date": "2026-12-20",
            "instructions": "Rinse mouth thoroughly with water after each inhalation."
        },
        {
            "medication_id": "MED_307",
            "patient_id": "PAT_004",
            "consultation_id": "CON_1004",
            "medication_name": "Torsemide",
            "dosage": "20 mg",
            "route": "Oral",
            "frequency": "Once Daily (Morning)",
            "start_date": "2026-08-25",
            "end_date": "2026-10-25",
            "instructions": "Take early morning. Strict daily fluid balance log required."
        }
    ]
    with open("data/medication/medications.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=medications[0].keys())
        writer.writeheader()
        writer.writerows(medications)
    print("Generated medications.csv")

def generate_medication_adherence():
    adherence = [
        {
            "adherence_id": "ADH_401",
            "patient_id": "PAT_001",
            "medication_id": "MED_301",
            "total_doses_scheduled": 30,
            "doses_taken": 28,
            "missed_doses": 2,
            "adherence_rate": 93.3,
            "last_taken_at": "2026-09-09 08:15:00",
            "adherence_trend": "STABLE"
        },
        {
            "adherence_id": "ADH_402",
            "patient_id": "PAT_001",
            "medication_id": "MED_302",
            "total_doses_scheduled": 30,
            "doses_taken": 24,
            "missed_doses": 6,
            "adherence_rate": 80.0,
            "last_taken_at": "2026-09-07 20:30:00",
            "adherence_trend": "DECLINING"
        },
        {
            "adherence_id": "ADH_403",
            "patient_id": "PAT_002",
            "medication_id": "MED_304",
            "total_doses_scheduled": 60,
            "doses_taken": 41,
            "missed_doses": 19,
            "adherence_rate": 68.3,
            "last_taken_at": "2026-09-08 08:30:00",
            "adherence_trend": "CRITICAL_DROP"
        },
        {
            "adherence_id": "ADH_404",
            "patient_id": "PAT_003",
            "medication_id": "MED_306",
            "total_doses_scheduled": 60,
            "doses_taken": 58,
            "missed_doses": 2,
            "adherence_rate": 96.7,
            "last_taken_at": "2026-09-10 07:45:00",
            "adherence_trend": "EXCELLENT"
        },
        {
            "adherence_id": "ADH_405",
            "patient_id": "PAT_004",
            "medication_id": "MED_307",
            "total_doses_scheduled": 20,
            "doses_taken": 19,
            "missed_doses": 1,
            "adherence_rate": 95.0,
            "last_taken_at": "2026-09-09 07:00:00",
            "adherence_trend": "GOOD"
        }
    ]
    with open("data/medication/medication_adherence.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=adherence[0].keys())
        writer.writeheader()
        writer.writerows(adherence)
    print("Generated medication_adherence.csv")

def generate_appointments():
    appointments = [
        {
            "appointment_id": "APT_901",
            "patient_id": "PAT_001",
            "doctor_id": "DOC_101",
            "scheduled_datetime": "2026-09-12 11:00:00",
            "department": "Cardiology",
            "visit_type": "Follow-up",
            "status": "CONFIRMED",
            "notes": "Urgent BP titration review and 24h Holter assessment."
        },
        {
            "appointment_id": "APT_902",
            "patient_id": "PAT_002",
            "doctor_id": "DOC_102",
            "scheduled_datetime": "2026-09-22 14:30:00",
            "department": "Endocrinology",
            "visit_type": "Routine Review",
            "status": "SCHEDULED",
            "notes": "Review post-prandial spikes and neuropathy symptoms."
        },
        {
            "appointment_id": "APT_903",
            "patient_id": "PAT_003",
            "doctor_id": "DOC_103",
            "scheduled_datetime": "2026-10-15 10:00:00",
            "department": "Pulmonology",
            "visit_type": "Routine Review",
            "status": "SCHEDULED",
            "notes": "Repeat spirometry and inhaler adherence check."
        },
        {
            "appointment_id": "APT_904",
            "patient_id": "PAT_004",
            "doctor_id": "DOC_101",
            "scheduled_datetime": "2026-09-10 15:00:00",
            "department": "Cardiology / Heart Failure Clinic",
            "visit_type": "Emergency Escalation",
            "status": "URGENT_TODAY",
            "notes": "Decompensated heart failure and worsening SpO2 desaturation."
        }
    ]
    with open("data/appointment/appointments.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=appointments[0].keys())
        writer.writeheader()
        writer.writerows(appointments)
    print("Generated appointments.csv")

def generate_medical_research():
    research = [
        {
            "research_id": "RES_001",
            "title": "2024 AHA/ACC Guidelines for the Management of Elevated Blood Pressure and Hypertension",
            "journal": "Circulation - Journal of the American Heart Association",
            "publication_year": 2024,
            "doi": "10.1161/CIR.0000000000001201",
            "category": "Cardiology / Hypertension",
            "summary": "Recommends dual-therapy first line for Stage 2 hypertension with BP > 20/10 mmHg over goal. Demonstrates that combining ARBs (Telmisartan) with CCBs (Amlodipine) reduces cardiovascular events by 34% compared to monotherapy titration."
        },
        {
            "research_id": "RES_002",
            "title": "ADA Standards of Care in Diabetes — 2025: Pharmacologic Approaches to Glycemic Treatment",
            "journal": "Diabetes Care",
            "publication_year": 2025,
            "doi": "10.2337/dc25-S009",
            "category": "Endocrinology / Diabetes",
            "summary": "Early combination therapy of Metformin with SGLT2 inhibitors (Dapagliflozin) provides cardiorenal protection and superior glycemic durability in patients with elevated microalbuminuria."
        },
        {
            "research_id": "RES_003",
            "title": "Global Initiative for Asthma (GINA) 2025 Strategy Report: Stepwise Management of Asthma in Adults",
            "journal": "American Journal of Respiratory and Critical Care Medicine",
            "publication_year": 2025,
            "doi": "10.1164/rccm.202501-GINA",
            "category": "Pulmonology / Asthma",
            "summary": "Inhaled corticosteroid (ICS)-formoterol as both maintenance and reliever is the preferred track across Steps 3-4 to reduce severe exacerbation risks by 45% compared to SABA monotherapy."
        },
        {
            "research_id": "RES_004",
            "title": "Decompensated Heart Failure and Cardiorenal Syndrome: ESC Guidelines for Diagnosis and Treatment",
            "journal": "European Heart Journal",
            "publication_year": 2024,
            "doi": "10.1093/eurheartj/ehae332",
            "category": "Cardiology / Heart Failure",
            "summary": "In patients with acute heart failure exacerbation and CKD, aggressive loop diuretics combined with close electrolyte monitoring and non-invasive positive pressure ventilation are indicated if SpO2 drops below 90%."
        }
    ]
    with open("data/knowledge/medical_research.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=research[0].keys())
        writer.writeheader()
        writer.writerows(research)
    print("Generated medical_research.csv")

def generate_medical_research_chunks():
    chunks = [
        {
            "chunk_id": "CHK_RES_101",
            "research_id": "RES_001",
            "source_title": "AHA/ACC 2024 Hypertension Guidelines",
            "category": "Hypertension",
            "chunk_text": "In Stage 2 hypertension (Systolic BP >= 140 mmHg or Diastolic BP >= 90 mmHg), initiating prompt dual agent therapy with an ARB (such as Telmisartan 40-80mg) and a dihydropyridine CCB (such as Amlodipine 5-10mg) is superior in achieving target BP < 130/80 mmHg. Morning surges in systolic pressure above 180 mmHg represent a critical hypertensive urgency requiring immediate clinical assessment to exclude end-organ damage (stroke, encephalopathy, acute coronary syndrome)."
        },
        {
            "chunk_id": "CHK_RES_102",
            "research_id": "RES_001",
            "source_title": "AHA/ACC 2024 Hypertension Guidelines",
            "category": "Hypertension",
            "chunk_text": "Patient adherence to antihypertensive regimens is the single most controllable predictor of stroke reduction. Missed evening doses of calcium channel blockers cause rebound vasoconstriction and pronounced early morning BP surges, typically between 6 AM and 10 AM."
        },
        {
            "chunk_id": "CHK_RES_103",
            "research_id": "RES_002",
            "source_title": "ADA 2025 Diabetes Standards of Care",
            "category": "Diabetes",
            "chunk_text": "Patients with HbA1c > 8.0% and diabetic peripheral neuropathy require intensive glycemic stabilization. Metformin 1000mg twice daily with meals reduces hepatic gluconeogenesis without hypoglycemia risk. SGLT2 inhibitors like Dapagliflozin 10mg provide significant nephroprotection, reducing urinary albumin excretion rate by up to 35% in clinical trials."
        },
        {
            "chunk_id": "CHK_RES_104",
            "research_id": "RES_002",
            "source_title": "ADA 2025 Diabetes Standards of Care",
            "category": "Diabetes",
            "chunk_text": "Diabetic peripheral neuropathy presents as burning pain, tingling dysesthesia, or numbness in a stocking-glove distribution. Symptoms frequently exacerbate during nighttime. Strict glycemic control combined with alpha-lipoic acid, pregabalin, or duloxetine can alleviate neuropathic discomfort."
        },
        {
            "chunk_id": "CHK_RES_105",
            "research_id": "RES_003",
            "source_title": "GINA 2025 Asthma Guidelines",
            "category": "Asthma",
            "chunk_text": "The GINA 2025 report firmly recommends against SABA-only treatment. Using Budesonide/Formoterol combination as maintenance and reliever inhaler (SMART therapy) simultaneously addresses airway smooth muscle bronchoconstriction and mucosal eosinophilic inflammation, reducing emergency visits by 60%."
        },
        {
            "chunk_id": "CHK_RES_106",
            "research_id": "RES_004",
            "source_title": "ESC 2024 Heart Failure & Cardiorenal Guidelines",
            "category": "Heart Failure",
            "chunk_text": "Acute decompensated heart failure with elevated NT-proBNP (> 1000 pg/mL) and orthopnea requires urgent loop diuretic therapy (Torsemide or Furosemide). In concurrent Stage 3 CKD, monitor serum potassium and creatinine closely. An SpO2 drop below 90% or severe respiratory rate > 22 bpm signals pulmonary capillary congestion and mandates emergency oxygenation."
        }
    ]
    with open("data/knowledge/medical_research_chunks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=chunks[0].keys())
        writer.writeheader()
        writer.writerows(chunks)
    print("Generated medical_research_chunks.csv")

def generate_disease_knowledge():
    diseases = [
        {
            "disease_id": "DIS_001",
            "disease_name": "Essential Hypertension (Stage 2)",
            "icd10": "I10",
            "hallmark_symptoms": "Occipital headache, dizziness, visual disturbances, palpitations, fatigue",
            "risk_factors": "High sodium intake, obesity, sedentary lifestyle, chronic kidney disease, family history",
            "standard_of_care": "Dual therapy (ARB/ACEi + CCB or Thiazide), sodium restriction < 2g/day, daily home BP monitoring",
            "red_flags": "Systolic BP >= 180 mmHg, Diastolic BP >= 110 mmHg, chest pain, neurological deficit, severe headache",
            "lifestyle_precautions": "DASH diet, 30 mins moderate walking, stress reduction, avoid NSAIDs and excess caffeine"
        },
        {
            "disease_id": "DIS_002",
            "disease_name": "Type 2 Diabetes Mellitus with Neuropathy",
            "icd10": "E11.40",
            "hallmark_symptoms": "Polydipsia, polyuria, blurred vision, numbness/burning dysesthesia in lower limbs, slow healing wounds",
            "risk_factors": "Insulin resistance, BMI > 25, hyperlipidemia, hypertension, physical inactivity",
            "standard_of_care": "Metformin + SGLT2i / GLP-1 RA, target HbA1c < 7.0%, annual microalbuminuria screening, daily diabetic foot inspection",
            "red_flags": "Blood glucose > 250 mg/dL or < 70 mg/dL, foot ulceration, loss of sensation, ketonuria signs",
            "lifestyle_precautions": "Low glycemic index diet, regular meal timing, inspect feet daily with mirror, wear seamless diabetic socks"
        },
        {
            "disease_id": "DIS_003",
            "disease_name": "Bronchial Asthma (Moderate Persistent)",
            "icd10": "J45.40",
            "hallmark_symptoms": "Wheezing, nocturnal cough, dyspnea on exertion, chest tightness",
            "risk_factors": "Atopy, allergen exposure (dust, pollen, pet dander), air pollution, cold weather, viral infections",
            "standard_of_care": "Low-to-medium dose ICS-Formoterol inhaler twice daily, spacer device, annual influenza vaccine",
            "red_flags": "Peak expiratory flow < 60% of personal best, inability to speak in full sentences, SpO2 < 92%, silent chest",
            "lifestyle_precautions": "Avoid smoke exposure, dust mite proof mattress covers, rinse mouth after inhaler use to prevent oral thrush"
        },
        {
            "disease_id": "DIS_004",
            "disease_name": "Congestive Heart Failure with Cardiorenal Syndrome",
            "icd10": "I50.9",
            "hallmark_symptoms": "Orthopnea, paroxysmal nocturnal dyspnea, bilateral pitting ankle edema, exertional dyspnea, rapid weight gain",
            "risk_factors": "Coronary artery disease, long-standing hypertension, diabetes, cardiomyopathy, chronic kidney disease",
            "standard_of_care": "Guideline-directed medical therapy (GDMT: SGLT2i, ARNI/ARB, Beta-blocker, MRA), loop diuretic titration, fluid restriction <= 1.5L/day",
            "red_flags": "Weight gain > 2 kg in 48 hours, SpO2 < 90%, resting dyspnea, syncope, severe oliguria",
            "lifestyle_precautions": "Daily morning weight logging, strict sodium restriction (< 1.5g/day), elevate legs while sitting"
        }
    ]
    with open("data/knowledge/disease_knowledge.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=diseases[0].keys())
        writer.writeheader()
        writer.writerows(diseases)
    print("Generated disease_knowledge.csv")

def generate_escalation_rules():
    rules = [
        {
            "rule_id": "ESC_001",
            "rule_name": "Hypertensive Urgency / Crisis Spike",
            "metric_name": "systolic_bp",
            "operator": ">=",
            "threshold_value": 180.0,
            "severity_level": "CRITICAL",
            "escalation_action": "TRIGGER_EMERGENCY_DOCTOR_ALERT",
            "clinical_rationale": "Systolic BP >= 180 mmHg represents hypertensive urgency/crisis with immediate risk of cerebrovascular accident or acute heart failure.",
            "is_active": 1
        },
        {
            "rule_id": "ESC_002",
            "rule_name": "Severe Diastolic Hypertension",
            "metric_name": "diastolic_bp",
            "operator": ">=",
            "threshold_value": 110.0,
            "severity_level": "CRITICAL",
            "escalation_action": "TRIGGER_EMERGENCY_DOCTOR_ALERT",
            "clinical_rationale": "Diastolic pressure >= 110 mmHg causes severe end-organ vascular stress.",
            "is_active": 1
        },
        {
            "rule_id": "ESC_003",
            "rule_name": "Acute Hypoxemia Desaturation",
            "metric_name": "spo2",
            "operator": "<=",
            "threshold_value": 90.0,
            "severity_level": "CRITICAL",
            "escalation_action": "TRIGGER_EMERGENCY_AMBULANCE_OR_DOCTOR",
            "clinical_rationale": "Pulse oximetry SpO2 <= 90% indicates respiratory compromise, acute pulmonary edema, or severe asthma exacerbation.",
            "is_active": 1
        },
        {
            "rule_id": "ESC_004",
            "rule_name": "Marked Tachycardia at Rest",
            "metric_name": "heart_rate",
            "operator": ">=",
            "threshold_value": 115.0,
            "severity_level": "WARNING",
            "escalation_action": "PROMPT_PHYSICIAN_SAME_DAY_REVIEW",
            "clinical_rationale": "Resting heart rate >= 115 bpm may indicate decompensation, arrhythmia, sepsis, or severe pain.",
            "is_active": 1
        },
        {
            "rule_id": "ESC_005",
            "rule_name": "Severe Hyperglycemia Spike",
            "metric_name": "blood_glucose_mg_dl",
            "operator": ">=",
            "threshold_value": 250.0,
            "severity_level": "WARNING",
            "escalation_action": "ALERT_DOCTOR_GLYCEMIC_TITRATION",
            "clinical_rationale": "Blood glucose >= 250 mg/dL increases hyperosmolar and ketoacidosis risk.",
            "is_active": 1
        },
        {
            "rule_id": "ESC_006",
            "rule_name": "Severe Critical Pain Score",
            "metric_name": "pain_score",
            "operator": ">=",
            "threshold_value": 8.0,
            "severity_level": "WARNING",
            "escalation_action": "PROMPT_CLINICAL_NURSE_TRIAGE",
            "clinical_rationale": "Pain score >= 8/10 signals acute clinical decompensation or uncontrolled condition.",
            "is_active": 1
        },
        {
            "rule_id": "ESC_007",
            "rule_name": "Critical Medication Non-Adherence",
            "metric_name": "adherence_rate",
            "operator": "<=",
            "threshold_value": 70.0,
            "severity_level": "WARNING",
            "escalation_action": "NOTIFY_DOCTOR_MEDICATION_NONCOMPLIANCE",
            "clinical_rationale": "Adherence <= 70% precipitates disease recurrence, rebound hypertension, or loss of glycemic control.",
            "is_active": 1
        }
    ]
    with open("data/safety/escalation_rules.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rules[0].keys())
        writer.writeheader()
        writer.writerows(rules)
    print("Generated escalation_rules.csv")

if __name__ == "__main__":
    create_directories()
    generate_hospitals()
    generate_doctors()
    generate_patients()
    generate_consultations()
    generate_vitals()
    generate_lab_results()
    generate_symptoms()
    generate_daily_checkins()
    generate_monitoring_events()
    generate_medications()
    generate_medication_adherence()
    generate_appointments()
    generate_medical_research()
    generate_medical_research_chunks()
    generate_disease_knowledge()
    generate_escalation_rules()
    print("All 13 clinical datasets successfully generated!")
