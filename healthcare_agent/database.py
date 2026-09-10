import os
import sqlite3
import pandas as pd
import glob
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "healthcare.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(data_dir: str = "data"):
    """
    Ingests all CSVs into SQLite relational database with proper indices.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    csv_files = glob.glob(f"{data_dir}/**/*.csv", recursive=True)
    loaded_tables = []

    for file_path in csv_files:
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            df = pd.read_csv(file_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            loaded_tables.append(table_name)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # Create indices for fast lookup across patient_id
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_patients_pid ON patients(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_consultations_pid ON consultations(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_vitals_pid ON vitals(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_lab_pid ON lab_results(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_symptoms_pid ON symptoms(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_checkins_pid ON daily_checkins(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_events_pid ON monitoring_events(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_meds_pid ON medications(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_adherence_pid ON medication_adherence(patient_id);",
        "CREATE INDEX IF NOT EXISTS idx_appts_pid ON appointments(patient_id);"
    ]
    for q in index_queries:
        try:
            cursor.execute(q)
        except Exception:
            pass

    conn.commit()
    conn.close()
    print(f"Database initialized with {len(loaded_tables)} tables at {DB_PATH}")

def get_patients_summary() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            p.patient_id, p.first_name, p.last_name, p.age, p.gender, p.blood_group,
            p.primary_condition, p.risk_tier,
            d.doctor_name, d.specialization,
            h.hospital_name
        FROM patients p
        LEFT JOIN doctors d ON p.assigned_doctor_id = d.doctor_id
        LEFT JOIN hospitals h ON d.hospital_id = h.hospital_id
    """
    rows = cursor.execute(query).fetchall()
    
    summaries = []
    for r in rows:
        p_dict = dict(r)
        # Fetch latest vital
        latest_vital = cursor.execute(
            "SELECT * FROM vitals WHERE patient_id = ? ORDER BY recorded_at DESC LIMIT 1",
            (p_dict["patient_id"],)
        ).fetchone()
        p_dict["latest_vital"] = dict(latest_vital) if latest_vital else None

        # Fetch latest event
        latest_event = cursor.execute(
            "SELECT * FROM monitoring_events WHERE patient_id = ? ORDER BY detected_at DESC LIMIT 1",
            (p_dict["patient_id"],)
        ).fetchone()
        p_dict["latest_event"] = dict(latest_event) if latest_event else None

        # Fetch overall adherence
        adh = cursor.execute(
            "SELECT AVG(adherence_rate) as avg_adh FROM medication_adherence WHERE patient_id = ?",
            (p_dict["patient_id"],)
        ).fetchone()
        p_dict["avg_adherence"] = round(adh["avg_adh"], 1) if adh and adh["avg_adh"] is not None else 100.0

        summaries.append(p_dict)

    conn.close()
    return summaries

def get_patient_360(patient_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Patient Profile
    p_row = cursor.execute("""
        SELECT p.*, d.doctor_name, d.specialization, d.phone as doctor_phone, h.hospital_name, h.emergency_contact
        FROM patients p
        LEFT JOIN doctors d ON p.assigned_doctor_id = d.doctor_id
        LEFT JOIN hospitals h ON d.hospital_id = h.hospital_id
        WHERE p.patient_id = ?
    """, (patient_id,)).fetchone()

    if not p_row:
        conn.close()
        return None

    patient_data = dict(p_row)

    # 2. Consultations
    consults = cursor.execute(
        "SELECT * FROM consultations WHERE patient_id = ? ORDER BY consultation_date DESC",
        (patient_id,)
    ).fetchall()
    patient_data["consultations"] = [dict(c) for c in consults]

    # 3. Vitals Time-Series
    vitals = cursor.execute(
        "SELECT * FROM vitals WHERE patient_id = ? ORDER BY recorded_at ASC",
        (patient_id,)
    ).fetchall()
    patient_data["vitals"] = [dict(v) for v in vitals]

    # 4. Lab Results
    labs = cursor.execute(
        "SELECT * FROM lab_results WHERE patient_id = ? ORDER BY test_date DESC",
        (patient_id,)
    ).fetchall()
    patient_data["lab_results"] = [dict(l) for l in labs]

    # 5. Symptoms
    symptoms = cursor.execute(
        "SELECT * FROM symptoms WHERE patient_id = ? ORDER BY reported_at DESC",
        (patient_id,)
    ).fetchall()
    patient_data["symptoms"] = [dict(s) for s in symptoms]

    # 6. Daily Check-ins
    checkins = cursor.execute(
        "SELECT * FROM daily_checkins WHERE patient_id = ? ORDER BY checkin_date DESC",
        (patient_id,)
    ).fetchall()
    patient_data["daily_checkins"] = [dict(chk) for chk in checkins]

    # 7. Medications & Adherence
    meds = cursor.execute("""
        SELECT m.*, a.adherence_rate, a.missed_doses, a.doses_taken, a.last_taken_at, a.adherence_trend
        FROM medications m
        LEFT JOIN medication_adherence a ON m.medication_id = a.medication_id
        WHERE m.patient_id = ?
    """, (patient_id,)).fetchall()
    patient_data["medications"] = [dict(m) for m in meds]

    # 8. Appointments
    appts = cursor.execute(
        "SELECT * FROM appointments WHERE patient_id = ? ORDER BY scheduled_datetime ASC",
        (patient_id,)
    ).fetchall()
    patient_data["appointments"] = [dict(a) for a in appts]

    # 9. Monitoring Events
    events = cursor.execute(
        "SELECT * FROM monitoring_events WHERE patient_id = ? ORDER BY detected_at DESC",
        (patient_id,)
    ).fetchall()
    patient_data["monitoring_events"] = [dict(e) for e in events]

    conn.close()
    return patient_data

def add_checkin_record(patient_id: str, pain_score: int, sleep_hours: float, fatigue: str, mood: str, fluid: float, notes: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
    chk_id = f"CHK_{int(pd.Timestamp.now().timestamp())}"
    cursor.execute("""
        INSERT INTO daily_checkins (checkin_id, patient_id, checkin_date, pain_score, sleep_hours, fatigue_level, mood, fluid_intake_liters, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (chk_id, patient_id, today_str, pain_score, sleep_hours, fatigue, mood, fluid, notes))
    conn.commit()
    conn.close()
    return chk_id

def log_med_intake(patient_id: str, medication_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE medication_adherence 
        SET doses_taken = doses_taken + 1, 
            last_taken_at = ?,
            adherence_rate = ROUND(CAST(doses_taken + 1 AS FLOAT) / CAST(total_doses_scheduled AS FLOAT) * 100.0, 1)
        WHERE patient_id = ? AND medication_id = ?
    """, (now_str, patient_id, medication_id))
    conn.commit()
    conn.close()
