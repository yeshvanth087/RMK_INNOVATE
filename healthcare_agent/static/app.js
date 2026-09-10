let currentPatientId = "PAT_001";
let currentPersona = "doctor";
let currentIntelData = null;
let vitalsChartInstance = null;

// Initialize on load
document.addEventListener("DOMContentLoaded", () => {
  loadPatientData(currentPatientId);
  // Initial search load
  executeRAGSearch("Hypertension Stage 2 Telmisartan Amlodipine combination");
});

function switchPersona(persona) {
  currentPersona = persona;
  document.getElementById("btn-doctor-mode").classList.toggle("active", persona === "doctor");
  document.getElementById("btn-patient-mode").classList.toggle("active", persona === "patient");

  document.getElementById("doctor-portal").classList.toggle("active", persona === "doctor");
  document.getElementById("patient-portal").classList.toggle("active", persona === "patient");
}

function onPatientChange() {
  const select = document.getElementById("patient-select");
  currentPatientId = select.value;
  loadPatientData(currentPatientId);
}

async function loadPatientData(patientId) {
  try {
    const res = await fetch(`/api/patients/${patientId}/intelligence`);
    const json = await res.json();
    if (!json.success) return;

    currentIntelData = json.data;
    renderAllViews(currentIntelData);
  } catch (err) {
    console.error("Error fetching patient intelligence:", err);
  }
}

function renderAllViews(data) {
  const p = data.patient_profile;
  const doc = data.doctor_intelligence;
  const pat = data.patient_companion;

  // 1. Header Live Status & Alert Banner
  const statusPill = document.getElementById("live-status-pill");
  const statusText = document.getElementById("status-text");
  const alertBanner = document.getElementById("safety-alert-banner");

  if (doc.triage_status === "CONCERN") {
    statusPill.className = "status-badge-live status-concern";
    statusText.innerText = `🚨 ${doc.triage_level}`;
    alertBanner.style.display = "flex";
    
    if (doc.safety_alerts && doc.safety_alerts.length > 0) {
      const topAlert = doc.safety_alerts[0];
      document.getElementById("alert-title-text").innerText = `⚠️ CRITICAL SAFETY ALERT: ${topAlert.rule_name}`;
      document.getElementById("alert-desc-text").innerText = `Observed ${topAlert.metric}: ${topAlert.observed_value} (Threshold: ${topAlert.operator} ${topAlert.threshold}) — Required Action: ${topAlert.action}`;
    }
  } else {
    statusPill.className = "status-badge-live status-normal";
    statusText.innerText = "🟢 All Metrics Stable";
    alertBanner.style.display = "none";
  }

  // 2. Doctor Portal: Patient 360 Strip
  document.getElementById("doc-patient-name").innerText = `${p.first_name} ${p.last_name} (${p.patient_id})`;
  document.getElementById("doc-patient-demographics").innerText = `${p.age} Yrs • ${p.gender} • Blood ${p.blood_group}`;
  document.getElementById("doc-patient-condition").innerText = p.primary_condition;
  document.getElementById("doc-patient-allergies").innerText = p.allergies || "None";
  
  const riskTag = document.getElementById("doc-patient-risk");
  riskTag.className = `risk-tag risk-${p.risk_tier}`;
  riskTag.innerText = `${p.risk_tier} RISK`;

  // 3. Explanation Engine: What Changed & Why It Matters
  const changedList = document.getElementById("what-changed-list");
  changedList.innerHTML = doc.what_changed.map(c => `<li>${c}</li>`).join("");

  const mattersList = document.getElementById("why-it-matters-list");
  mattersList.innerHTML = doc.why_it_matters.map(m => `<li>${m}</li>`).join("");

  // 4. Vitals Time-Series Chart
  renderVitalsChart(p.vitals);

  // 5. Lab Biomarkers Grid
  const labGrid = document.getElementById("lab-biomarkers-grid");
  labGrid.innerHTML = p.lab_results.map(l => {
    const isElevated = l.status !== "NORMAL";
    return `
      <div class="vital-stat-box" style="border-left: 3px solid ${isElevated ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
        <div class="vital-stat-label">${l.biomarker}</div>
        <div class="vital-stat-value" style="font-size: 1.1rem;">${l.result_value} <span style="font-size: 0.75rem; color: var(--text-muted);">${l.unit}</span></div>
        <div class="vital-stat-delta" style="color: ${isElevated ? '#fb7185' : '#34d399'};">${l.status} (Ref: ${l.reference_range})</div>
      </div>
    `;
  }).join("");

  // Doctor Meds List
  const docMeds = document.getElementById("doctor-meds-list");
  docMeds.innerHTML = p.medications.map(m => `
    <div style="font-size: 0.82rem; color: #cbd5e1; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between;">
      <span><strong>${m.medication_name}</strong> ${m.dosage} (${m.frequency})</span>
      <span style="color: ${m.adherence_rate < 80 ? '#fb7185' : '#34d399'}; font-weight: 600;">Adherence: ${m.adherence_rate}%</span>
    </div>
  `).join("");

  // 6. Structured SOAP Note
  const soap = doc.soap_note.soap;
  document.getElementById("soap-s").innerHTML = `
    <p><strong>Chief Complaint:</strong> ${soap.S_Subjective.chief_complaint}</p>
    <p><strong>Severity:</strong> ${soap.S_Subjective.symptom_severity}</p>
    <p><strong>Pain Score:</strong> ${soap.S_Subjective.patient_reported_pain}</p>
    <p><strong>Sleep & Fatigue:</strong> ${soap.S_Subjective.sleep_quality}</p>
    <p><strong>Patient Note:</strong> ${soap.S_Subjective.patient_notes}</p>
  `;

  document.getElementById("soap-o").innerHTML = `
    <p><strong>Blood Pressure:</strong> ${soap.O_Objective.vital_signs.blood_pressure}</p>
    <p><strong>Heart Rate:</strong> ${soap.O_Objective.vital_signs.heart_rate} | <strong>SpO2:</strong> ${soap.O_Objective.vital_signs.spo2}</p>
    <p><strong>Blood Glucose:</strong> ${soap.O_Objective.vital_signs.blood_glucose} | <strong>Temp:</strong> ${soap.O_Objective.vital_signs.temperature}</p>
    <p style="margin-top: 6px;"><strong>Key Biomarkers:</strong> ${soap.O_Objective.recent_lab_biomarkers.join(", ")}</p>
  `;

  document.getElementById("soap-a").innerHTML = `
    <p><strong>Primary Diagnosis:</strong> ${soap.A_Assessment.primary_diagnosis} [${soap.A_Assessment.risk_tier}]</p>
    <p style="margin-top: 6px;"><strong>Change Deltas:</strong></p>
    <ul style="padding-left: 14px;">${soap.A_Assessment.what_changed.map(w => `<li>${w}</li>`).join("")}</ul>
  `;

  document.getElementById("soap-p").innerHTML = `
    <p><strong>Orders:</strong> ${soap.P_Plan.monitoring_orders.join("; ")}</p>
    <p style="margin-top: 6px;"><strong>Guidance:</strong> ${soap.P_Plan.patient_education_and_precautions.join("; ")}</p>
    <p style="margin-top: 6px; font-size: 0.75rem; color: var(--accent-blue);"><strong>Evidence Base:</strong> ${soap.P_Plan.evidence_base.join("<br>") || "Standard of care guidelines applied."}</p>
  `;

  // 7. Patient Companion View
  document.getElementById("patient-hero-greeting").innerText = `Good day, ${p.first_name}! 👋`;
  document.getElementById("patient-adherence-val").innerText = `${pat.overall_adherence}%`;

  // Patient Medication List with "Take Dose" buttons
  const patMedList = document.getElementById("patient-medication-list");
  patMedList.innerHTML = p.medications.map(m => `
    <div class="medication-card-item">
      <div>
        <div class="med-name">${m.medication_name} <span style="font-size: 0.8rem; color: var(--accent-blue); font-weight: normal;">(${m.dosage})</span></div>
        <div class="med-timing">⏰ ${m.frequency} • ${m.instructions}</div>
        <div style="font-size: 0.75rem; color: ${m.adherence_rate < 80 ? '#fb7185' : '#34d399'}; margin-top: 4px;">Compliance: ${m.adherence_rate}% (Last: ${m.last_taken_at || 'Today'})</div>
      </div>
      <button class="btn-take-dose" onclick="takeDose('${m.medication_id}')">✅ Log Taken</button>
    </div>
  `).join("");

  // Patient Precautions
  const precList = document.getElementById("patient-precautions-list");
  precList.innerHTML = pat.daily_precautions.map(pr => `<li>${pr}</li>`).join("");

  // Doctor Contact
  document.getElementById("patient-doc-name").innerText = `${p.doctor_name} (${p.specialization})`;
  document.getElementById("patient-hosp-name").innerText = `${p.hospital_name}`;
  document.getElementById("patient-emerg-contact").innerText = `Emergency: ${p.emergency_contact || p.doctor_phone}`;
}

function renderVitalsChart(vitals) {
  if (!vitals || vitals.length === 0) return;
  const ctx = document.getElementById("vitalsChart").getContext("2d");

  const labels = vitals.map(v => v.recorded_at.split(" ")[0].slice(5));
  const sbp = vitals.map(v => v.systolic_bp);
  const dbp = vitals.map(v => v.diastolic_bp);
  const spo2 = vitals.map(v => v.spo2);
  const hr = vitals.map(v => v.heart_rate);

  if (vitalsChartInstance) {
    vitalsChartInstance.destroy();
  }

  vitalsChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Systolic BP (mmHg)",
          data: sbp,
          borderColor: "#f43f5e",
          backgroundColor: "rgba(244, 63, 94, 0.1)",
          borderWidth: 2,
          tension: 0.3
        },
        {
          label: "Diastolic BP (mmHg)",
          data: dbp,
          borderColor: "#f59e0b",
          borderWidth: 1.5,
          tension: 0.3
        },
        {
          label: "SpO2 (%)",
          data: spo2,
          borderColor: "#38bdf8",
          borderWidth: 2,
          borderDash: [4, 4],
          tension: 0.3
        },
        {
          label: "Heart Rate (bpm)",
          data: hr,
          borderColor: "#10b981",
          borderWidth: 1.5,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          labels: { color: "#94a3b8", font: { size: 11 } }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#64748b" }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#64748b" }
        }
      }
    }
  });
}

// Interactive API Handlers
async function takeDose(medicationId) {
  try {
    const res = await fetch(`/api/patients/${currentPatientId}/medication/take`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ medication_id: medicationId })
    });
    const json = await res.json();
    if (json.success) {
      alert("✅ Dose recorded! Adherence rate updated.");
      loadPatientData(currentPatientId);
    }
  } catch (err) {
    console.error("Error taking dose:", err);
  }
}

async function submitPatientCheckin(e) {
  e.preventDefault();
  const payload = {
    pain_score: parseInt(document.getElementById("chk-pain").value),
    sleep_hours: parseFloat(document.getElementById("chk-sleep").value),
    fatigue_level: document.getElementById("chk-fatigue").value,
    mood: document.getElementById("chk-mood").value,
    fluid_intake_liters: parseFloat(document.getElementById("chk-fluid").value),
    notes: document.getElementById("chk-notes").value
  };

  try {
    const res = await fetch(`/api/patients/${currentPatientId}/checkin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.success) {
      alert("✨ Daily check-in logged! The AI Agent has updated your care plan.");
      document.getElementById("chk-notes").value = "";
      loadPatientData(currentPatientId);
    }
  } catch (err) {
    console.error("Error submitting checkin:", err);
  }
}

async function executeRAGSearch(queryOverride) {
  const query = queryOverride || document.getElementById("rag-query-input").value;
  if (!query) return;

  const container = document.getElementById("rag-evidence-container");
  container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem;'>Querying peer-reviewed literature & guidelines...</p>";

  try {
    const res = await fetch(`/api/research/search?query=${encodeURIComponent(query)}&top_k=3`);
    const json = await res.json();
    if (!json.success || json.results.length === 0) {
      container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem;'>No specific research matches found.</p>";
      return;
    }

    container.innerHTML = json.results.map(r => `
      <div class="evidence-card">
        <div class="evidence-title">📄 ${r.title}</div>
        <div class="evidence-meta"><strong>Journal:</strong> ${r.journal} (${r.publication_year}) • <strong>DOI:</strong> ${r.doi} • <strong>Relevance:</strong> ${(r.relevance_score * 100).toFixed(1)}%</div>
        <div class="evidence-text">${r.document_text}</div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error executing RAG search:", err);
  }
}

// Chat Handlers
function handlePatientChatEnter(e) {
  if (e.key === "Enter") sendPatientMessage();
}

async function sendPatientMessage() {
  const input = document.getElementById("patient-chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById("patient-chat-box");
  chatBox.innerHTML += `<div class="chat-bubble user">${escapeHtml(msg)}</div>`;
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch("/api/chat/patient", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patient_id: currentPatientId, message: msg })
    });
    const json = await res.json();
    if (json.success) {
      chatBox.innerHTML += `<div class="chat-bubble bot">${escapeHtml(json.data.reply)}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (err) {
    console.error("Chat error:", err);
  }
}

function quickPatientChat(text) {
  document.getElementById("patient-chat-input").value = text;
  sendPatientMessage();
}

function handleDoctorChatEnter(e) {
  if (e.key === "Enter") sendDoctorMessage();
}

async function sendDoctorMessage() {
  const input = document.getElementById("doctor-chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById("doctor-chat-box");
  chatBox.innerHTML += `<div class="chat-bubble user">${escapeHtml(msg)}</div>`;
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch("/api/chat/doctor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patient_id: currentPatientId, message: msg })
    });
    const json = await res.json();
    if (json.success) {
      chatBox.innerHTML += `<div class="chat-bubble bot" style="white-space: pre-wrap;">${escapeHtml(json.data.reply)}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  } catch (err) {
    console.error("Doctor chat error:", err);
  }
}

function copySOAPNote() {
  if (!currentIntelData) return;
  const soap = currentIntelData.doctor_intelligence.soap_note.soap;
  const text = `
CLINICAL SOAP NOTE — ${currentIntelData.patient_profile.first_name} ${currentIntelData.patient_profile.last_name} (${currentPatientId})
Date: ${new Date().toISOString()}

[S] SUBJECTIVE:
- Chief Complaint: ${soap.S_Subjective.chief_complaint}
- Severity: ${soap.S_Subjective.symptom_severity}
- Pain: ${soap.S_Subjective.patient_reported_pain} | Sleep: ${soap.S_Subjective.sleep_quality}

[O] OBJECTIVE:
- Vitals: BP ${soap.O_Objective.vital_signs.blood_pressure}, HR ${soap.O_Objective.vital_signs.heart_rate}, SpO2 ${soap.O_Objective.vital_signs.spo2}, Glucose ${soap.O_Objective.vital_signs.blood_glucose}
- Labs: ${soap.O_Objective.recent_lab_biomarkers.join("; ")}
- Current Meds: ${soap.O_Objective.current_medications.join("; ")}

[A] ASSESSMENT:
- Diagnosis: ${soap.A_Assessment.primary_diagnosis}
- What Changed: ${soap.A_Assessment.what_changed.join("; ")}

[P] PLAN:
- Orders: ${soap.P_Plan.monitoring_orders.join("; ")}
- Education: ${soap.P_Plan.patient_education_and_precautions.join("; ")}
- Evidence Base: ${soap.P_Plan.evidence_base.join("; ")}
  `.trim();

  navigator.clipboard.writeText(text).then(() => {
    alert("📋 Structured SOAP note copied to clipboard!");
  });
}

function acknowledgeAlert() {
  alert("🚨 Doctor has acknowledged emergency escalation alert for this patient.");
  document.getElementById("safety-alert-banner").style.display = "none";
}

function triggerPatientSOS() {
  alert("🚨 EMERGENCY SOS DISPATCHED!\n\nYour assigned hospital (Apollo Super Specialty) and Dr. Arvind Ramanathan have been notified with your live GPS location and health metrics.");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}
