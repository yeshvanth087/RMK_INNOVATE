import uvicorn
import os
import sys

def main():
    print("=" * 70)
    print("🩺 NeuroNex MediSense AI — Healthcare Research & Patient Support Agent")
    print("=" * 70)
    print("🚀 Initializing Clinical Database & Multi-Agent Engines...")
    
    # Ensure working directory is workspace root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Ensure datasets exist
    if not os.path.exists("data/patient/patients.csv"):
        print("Generating clinical CSV datasets...")
        import generate_datasets
        generate_datasets.create_directories()
        generate_datasets.generate_hospitals()
        generate_datasets.generate_doctors()
        generate_datasets.generate_patients()
        generate_datasets.generate_consultations()
        generate_datasets.generate_vitals()
        generate_datasets.generate_lab_results()
        generate_datasets.generate_symptoms()
        generate_datasets.generate_daily_checkins()
        generate_datasets.generate_monitoring_events()
        generate_datasets.generate_medications()
        generate_datasets.generate_medication_adherence()
        generate_datasets.generate_appointments()
        generate_datasets.generate_medical_research()
        generate_datasets.generate_medical_research_chunks()
        generate_datasets.generate_disease_knowledge()
        generate_datasets.generate_escalation_rules()

    from healthcare_agent.database import init_db
    init_db()

    print("\n✅ Platform Ready!")
    print("🌐 Open Unified Command Center: http://127.0.0.1:8000")
    print("📖 Open Interactive API Docs:   http://127.0.0.1:8000/docs\n")

    uvicorn.run("healthcare_agent.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
