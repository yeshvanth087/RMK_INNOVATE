/**
 * NeuroNex UrbanSense AI - Frontend Controller
 * Handles Leaflet GIS map rendering, real-time telemetry polling,
 * role switching (PWD / Police / Transit), ML inference simulators, and AI Assistant chat.
 */

let map;
let busLayerGroup;
let hazardLayerGroup;
let incidentLayerGroup;
let detourPolylineGroup;

const API_BASE = "";

// Initialize App on DOM Load
document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  initMap();
  refreshAllData();
  
  // Continuous real-time polling every 3.5 seconds
  setInterval(refreshAllData, 3500);
});

// Initialize Leaflet Map
function initMap() {
  // Center on urban corridor (Chennai / Tamil Nadu metro coordinates)
  map = L.map('gis-map', {
    center: [13.0400, 80.2300],
    zoom: 12,
    zoomControl: true
  });

  // Dark theme CartoDB basemap tiles
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  busLayerGroup = L.layerGroup().addTo(map);
  hazardLayerGroup = L.layerGroup().addTo(map);
  incidentLayerGroup = L.layerGroup().addTo(map);
  detourPolylineGroup = L.layerGroup().addTo(map);
}

// Fetch and Refresh All Real-Time Data
async function refreshAllData() {
  try {
    await Promise.all([
      fetchKPIs(),
      fetchFleetLive(),
      fetchRoadDefects(),
      fetchPoliceIncidents(),
      fetchPWDTickets()
    ]);
    lucide.createIcons();
  } catch (err) {
    console.error("Data refresh error:", err);
  }
}

// 1. Fetch Summary KPIs
async function fetchKPIs() {
  const res = await fetch(`${API_BASE}/api/analytics/kpis`);
  const data = await res.json();
  
  document.getElementById("kpi-buses").innerText = `${data.active_sensing_buses} Online`;
  document.getElementById("kpi-defects").innerText = `${data.total_active_defects} Issues`;
  document.getElementById("kpi-incidents").innerText = `${data.active_police_incidents} Active`;
  document.getElementById("kpi-tickets").innerText = `${data.open_pwd_work_orders} Open`;
  document.getElementById("kpi-reliability").innerText = `${data.network_on_time_reliability_pct}%`;
  document.getElementById("kpi-roads").innerText = `${data.urban_roads_scanned_km} km`;
}

// 2. Fetch & Render Live Fleet Markers
async function fetchFleetLive() {
  const res = await fetch(`${API_BASE}/api/gis/fleet-live`);
  const buses = await res.json();
  
  busLayerGroup.clearLayers();
  
  buses.forEach(b => {
    // Custom glowing bus SVG marker
    const busIcon = L.divIcon({
      className: 'bus-marker-icon',
      html: `
        <div class="relative flex items-center justify-center">
          <div class="w-8 h-8 rounded-full bg-cyan-500/20 border-2 border-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/50">
            <span class="text-white text-[10px] font-bold">🚍</span>
          </div>
          <span class="absolute -bottom-4 bg-slate-900/90 text-cyan-300 text-[9px] font-bold px-1.5 py-0.2 rounded border border-cyan-800 whitespace-nowrap">
            ${b.bus_id}
          </span>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    const marker = L.marker([b.latitude, b.longitude], { icon: busIcon });
    marker.bindPopup(`
      <div class="p-2 text-xs">
        <div class="font-bold text-cyan-400 text-sm mb-1">${b.bus_id} • ${b.route_id}</div>
        <div class="text-slate-300"><b>Speed:</b> ${b.speed_kmh} km/h</div>
        <div class="text-slate-300"><b>Heading:</b> ${Math.round(b.heading_deg)}°</div>
        <div class="text-slate-300"><b>Passenger Crowding:</b> ${b.crowding_pct}%</div>
        <div class="text-slate-400 text-[10px] mt-1">Edge Sensing AI Online</div>
      </div>
    `, { className: 'custom-popup' });
    
    busLayerGroup.addLayer(marker);
  });
}

// 3. Fetch & Render Road Defect Clusters
async function fetchRoadDefects() {
  const res = await fetch(`${API_BASE}/api/gis/road-defects-geojson`);
  const geojson = await res.json();
  
  hazardLayerGroup.clearLayers();
  const defectsContainer = document.getElementById("defects-feed-container");
  if (defectsContainer) defectsContainer.innerHTML = "";

  geojson.features.forEach(f => {
    const p = f.properties;
    const coords = f.geometry.coordinates; // [lng, lat]
    
    // Severity color
    let color = "#f59e0b"; // amber
    let iconEmoji = "⚠️";
    if (p.severity === "CRITICAL") { color = "#ef4444"; iconEmoji = "🚨"; }
    else if (p.hazard_type === "waterlogging") { color = "#3b82f6"; iconEmoji = "🌊"; }

    const hazardIcon = L.divIcon({
      className: 'hazard-marker-icon',
      html: `
        <div class="relative flex items-center justify-center">
          <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs shadow-lg" style="background-color: ${color}20; border: 2px solid ${color}">
            ${iconEmoji}
          </div>
          <span class="absolute -top-3 bg-slate-900/90 text-white text-[8px] font-bold px-1 rounded border border-slate-700">
            ${p.confirmation_count}x
          </span>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    const marker = L.marker([coords[1], coords[0]], { icon: hazardIcon });
    marker.bindPopup(`
      <div class="p-2 text-xs">
        <div class="font-bold text-amber-400 text-sm capitalize mb-1">${p.hazard_type.replace(/_/g, ' ')}</div>
        <div class="text-slate-300"><b>Severity:</b> <span class="text-red-400 font-bold">${p.severity}</span></div>
        <div class="text-slate-300"><b>AI Confidence:</b> ${Math.round(p.confidence * 100)}%</div>
        <div class="text-slate-300"><b>Confirmed by:</b> ${p.confirmation_count} Sensing Buses</div>
        <div class="text-slate-300"><b>Status:</b> ${p.status}</div>
        <div class="text-slate-400 text-[10px] mt-1">Ticket: ${p.ticket_id || 'Auto-Generating'}</div>
      </div>
    `, { className: 'custom-popup' });

    hazardLayerGroup.addLayer(marker);

    // Populate Sidebar Card
    if (defectsContainer) {
      const card = document.createElement("div");
      card.className = "bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-xs flex items-center justify-between hover:border-amber-500/50 transition-all";
      card.innerHTML = `
        <div class="flex items-center space-x-2.5">
          <div class="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 font-bold">${iconEmoji}</div>
          <div>
            <div class="font-semibold text-slate-200 capitalize">${p.hazard_type.replace(/_/g, ' ')}</div>
            <div class="text-[10px] text-slate-400">Position: ${p.relative_position || 'lane'} • Conf: ${Math.round(p.confidence*100)}%</div>
          </div>
        </div>
        <div class="text-right">
          <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${p.severity === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">
            ${p.severity}
          </span>
          <div class="text-[10px] text-slate-500 mt-1">${p.confirmation_count} buses confirmed</div>
        </div>
      `;
      defectsContainer.appendChild(card);
    }
  });
}

// 4. Fetch & Render Police Incidents & ANPR Feed
async function fetchPoliceIncidents() {
  const res = await fetch(`${API_BASE}/api/incidents/active`);
  const incidents = await res.json();

  incidentLayerGroup.clearLayers();
  const container = document.getElementById("incident-feed-container");
  const policeDetailContainer = document.getElementById("police-incident-detailed-container");
  
  if (container) container.innerHTML = "";
  if (policeDetailContainer) policeDetailContainer.innerHTML = "";

  incidents.forEach(inc => {
    // Map marker for incident
    const incIcon = L.divIcon({
      className: 'incident-marker-icon',
      html: `
        <div class="w-6 h-6 rounded-full bg-red-600/30 border-2 border-red-500 flex items-center justify-center text-xs animate-bounce shadow-lg shadow-red-500/50">
          🚨
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    const marker = L.marker([inc.latitude, inc.longitude], { icon: incIcon });
    marker.bindPopup(`
      <div class="p-2 text-xs">
        <div class="font-bold text-red-400 text-sm mb-1">🚨 ${inc.incident_type}</div>
        <div class="text-slate-200 font-mono text-sm bg-slate-900 p-1 rounded my-1 text-center font-bold border border-red-800">${inc.license_plate}</div>
        <div class="text-slate-300"><b>Plate Conf:</b> ${Math.round((inc.plate_confidence || 0.8)*100)}%</div>
        <div class="text-slate-300"><b>Speed:</b> ~${inc.estimated_speed} km/h</div>
        <div class="text-slate-400 text-[10px] mt-1">Bus: ${inc.reporting_bus_id}</div>
      </div>
    `, { className: 'custom-popup' });

    incidentLayerGroup.addLayer(marker);

    // Sidebar Summary Feed Card
    if (container) {
      const card = document.createElement("div");
      card.className = "bg-slate-950/90 border border-red-950 p-2.5 rounded-xl text-xs flex items-center justify-between hover:border-red-500/50 transition-all";
      card.innerHTML = `
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-red-400 font-bold">${inc.incident_type}</span>
            <span class="font-mono text-xs bg-slate-900 px-1.5 py-0.5 rounded text-slate-100 border border-slate-700">${inc.license_plate}</span>
          </div>
          <div class="text-[10px] text-slate-400 mt-1">Reported by ${inc.reporting_bus_id} • Speed: ${inc.estimated_speed} km/h</div>
        </div>
        <button onclick="dispatchPoliceInterceptor(${inc.id})" class="px-2.5 py-1 rounded bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white border border-red-800 text-[10px] font-bold transition-all">
          ${inc.status === 'DISPATCHED' ? 'Patrol Dispatched' : 'Dispatch'}
        </button>
      `;
      container.appendChild(card);
    }

    // Police Portal Detailed Card
    if (policeDetailContainer) {
      const pCard = document.createElement("div");
      pCard.className = "bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-3";
      pCard.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-red-400 uppercase tracking-wider">${inc.incident_type}</span>
          <span class="text-xs text-slate-400 font-mono">${inc.timestamp}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 bg-slate-900 p-2.5 rounded-lg text-xs">
          <div><span class="text-slate-400">License Plate:</span> <span class="font-mono font-bold text-slate-100">${inc.license_plate}</span></div>
          <div><span class="text-slate-400">OCR Confidence:</span> <span class="text-emerald-400 font-bold">${Math.round((inc.plate_confidence||0.8)*100)}%</span></div>
          <div><span class="text-slate-400">Estimated Speed:</span> <span class="text-amber-400 font-bold">${inc.estimated_speed} km/h</span></div>
          <div><span class="text-slate-400">Reporting Bus:</span> <span class="text-cyan-400">${inc.reporting_bus_id}</span></div>
        </div>
        ${inc.evidence_snapshot ? `<div class="rounded-lg overflow-hidden border border-slate-800">${inc.evidence_snapshot}</div>` : ''}
        <div class="flex items-center justify-end space-x-2 pt-1">
          <button onclick="dispatchPoliceInterceptor(${inc.id})" class="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold text-xs transition-all">
            ${inc.status === 'DISPATCHED' ? '✓ Patrol En Route' : 'Alert Nearest Traffic Patrol'}
          </button>
        </div>
      `;
      policeDetailContainer.appendChild(pCard);
    }
  });
}

// 5. Fetch & Render PWD Maintenance Tickets
async function fetchPWDTickets() {
  const res = await fetch(`${API_BASE}/api/tickets/`);
  const tickets = await res.json();
  const container = document.getElementById("pwd-tickets-container");
  if (!container) return;
  container.innerHTML = "";

  tickets.forEach(t => {
    const card = document.createElement("div");
    card.className = "bg-slate-950 border border-slate-800 p-3.5 rounded-xl space-y-2.5";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-mono font-bold text-purple-400">${t.ticket_id}</span>
          <span class="text-[10px] px-2 py-0.5 rounded-full font-bold ${t.priority === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">${t.priority}</span>
        </div>
        <span class="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 font-medium">${t.status}</span>
      </div>
      <div class="text-xs text-slate-200"><b>Issue:</b> <span class="capitalize">${t.defect_type.replace(/_/g, ' ')}</span> - ${t.location_desc}</div>
      <div class="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs">
        <span class="text-[11px] text-slate-400">${t.assigned_department}</span>
        <div class="flex items-center space-x-2">
          ${t.status === 'OPEN' ? `
            <button onclick="updateTicketStatus('${t.ticket_id}', 'IN_PROGRESS')" class="px-2.5 py-1 bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white rounded text-[11px] font-semibold transition-all">
              Issue Work Order
            </button>
          ` : ''}
          ${t.status === 'IN_PROGRESS' ? `
            <button onclick="updateTicketStatus('${t.ticket_id}', 'RESOLVED')" class="px-2.5 py-1 bg-amber-600/20 hover:bg-amber-600 text-amber-300 hover:text-white rounded text-[11px] font-semibold transition-all">
              Mark Repaired
            </button>
          ` : ''}
          ${t.status === 'RESOLVED' ? `
            <button onclick="verifyTicketAI('${t.ticket_id}')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-[11px] font-semibold transition-all flex items-center space-x-1">
              <span>🤖 Run Bus AI Audit</span>
            </button>
          ` : ''}
          ${t.status === 'AI_VERIFIED' ? `
            <span class="text-emerald-400 text-xs font-bold flex items-center space-x-1">
              <span>✓ Verified by Bus Fleet</span>
            </span>
          ` : ''}
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

// Dispatch Police Unit
async function dispatchPoliceInterceptor(incidentId) {
  await fetch(`${API_BASE}/api/incidents/${incidentId}/dispatch`, { method: "POST" });
  refreshAllData();
}

// Update PWD Ticket Status
async function updateTicketStatus(ticketId, newStatus) {
  await fetch(`${API_BASE}/api/tickets/${ticketId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus })
  });
  refreshAllData();
}

// AI Verification by Sensing Bus Pass
async function verifyTicketAI(ticketId) {
  const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/verify-repair`, { method: "POST" });
  const data = await res.json();
  alert(`🤖 AI Verification Success: ${data.verification_message}`);
  refreshAllData();
}

// Search ANPR License Plate
async function searchPlate() {
  const input = document.getElementById("plate-search-input").value;
  if (!input) return;
  const res = await fetch(`${API_BASE}/api/incidents/search?plate=${encodeURIComponent(input)}`);
  const results = await res.json();
  alert(`Found ${results.length} records matching plate query "${input}"`);
}

// Run ML Delay Prediction Simulator (PTOML / Chennai Analyzer)
async function runDelayPrediction() {
  const route = document.getElementById("sim-route").value;
  const hour = parseInt(document.getElementById("sim-hour").value);
  const weather = document.getElementById("sim-weather").value;

  const res = await fetch(`${API_BASE}/api/analytics/predict-delay`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      route_id: route,
      hour_of_day: hour,
      weather_condition: weather,
      current_crowding_pct: 60.0
    })
  });
  const data = await res.json();

  const box = document.getElementById("delay-prediction-result");
  box.classList.remove("hidden");
  box.innerHTML = `
    <div class="font-bold text-cyan-400 text-sm mb-1">⏱️ ML Model Prediction Results</div>
    <div class="text-slate-200"><b>Predicted Delay:</b> <span class="text-amber-400 font-bold text-sm">+${data.predicted_delay_minutes} minutes</span></div>
    <div class="text-slate-300"><b>Status:</b> ${data.delay_category}</div>
    <div class="text-slate-300 mt-1"><b>Contributing Factors:</b></div>
    <div class="text-slate-400 text-[11px] pl-2">
      • Traffic Volume Impact: ${data.delay_factors.traffic_congestion_pct}%<br>
      • Weather Impact: +${data.delay_factors.weather_impact_min} min<br>
      • Road Defect Slowdown: +${data.delay_factors.road_hazard_impact_min} min
    </div>
    <div class="text-emerald-400 text-[11px] mt-2 font-semibold">💡 Action: ${data.recommendation}</div>
  `;
}

// Solve Dynamic Hazard Detour (Pune OR-Tools Model)
async function solveDynamicRouteDetour() {
  const res = await fetch(`${API_BASE}/api/analytics/dynamic-route`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      origin: "NODE_CENTRAL",
      destination: "NODE_AIRPORT",
      avoid_hazards: true
    })
  });
  const data = await res.json();

  const box = document.getElementById("detour-result-box");
  box.classList.remove("hidden");
  box.innerHTML = `
    <div class="font-bold text-emerald-400 text-sm mb-1">🛣️ OR-Tools Dynamic Reroute Solved</div>
    <div class="text-slate-200"><b>Status:</b> ${data.status}</div>
    <div class="text-slate-300"><b>Reason:</b> ${data.reason}</div>
    <div class="text-slate-300"><b>Est. Time Saved:</b> <span class="text-emerald-400 font-bold">${data.estimated_time_saved_min} mins</span></div>
    <div class="text-slate-400 text-[11px] mt-1">Waypoints: ${data.route_waypoints.map(w => w.name).join(" ➔ ")}</div>
  `;

  // Draw Detour on Map
  detourPolylineGroup.clearLayers();
  const latlngs = data.route_waypoints.map(w => [w.latitude, w.longitude]);
  const polyline = L.polyline(latlngs, { color: '#10b981', weight: 4, dashArray: '6, 8' }).addTo(detourPolylineGroup);
  map.fitBounds(polyline.getBounds(), { padding: [40, 40] });
}

// Role Portal Switcher
function switchPortal(portalName) {
  document.querySelectorAll(".portal-panel").forEach(p => p.classList.add("hidden"));
  document.querySelectorAll(".portal-btn").forEach(b => {
    b.classList.remove("bg-cyan-600", "text-white", "shadow-md");
    b.classList.add("text-slate-400");
  });

  const activeBtn = document.getElementById(`btn-portal-${portalName}`);
  if (activeBtn) {
    activeBtn.classList.add("bg-cyan-600", "text-white", "shadow-md");
    activeBtn.classList.remove("text-slate-400");
  }

  const targetView = document.getElementById(`portal-${portalName}-view`);
  if (targetView) targetView.classList.remove("hidden");
}

// Map Layer Toggles
function toggleMapLayers() {
  const showBuses = document.getElementById("layer-buses").checked;
  const showPotholes = document.getElementById("layer-potholes").checked;
  const showIncidents = document.getElementById("layer-incidents").checked;

  if (showBuses) map.addLayer(busLayerGroup); else map.removeLayer(busLayerGroup);
  if (showPotholes) map.addLayer(hazardLayerGroup); else map.removeLayer(hazardLayerGroup);
  if (showIncidents) map.addLayer(incidentLayerGroup); else map.removeLayer(incidentLayerGroup);
}

// Trigger Simulated Edge Ping manually from UI
async function triggerSimulatedPing() {
  refreshAllData();
}

// AI Assistant Chat Toggle & Queries
function toggleAIAssistant() {
  const drawer = document.getElementById("ai-assistant-drawer");
  drawer.classList.toggle("translate-x-full");
}

async function sendAIChatQuery() {
  const input = document.getElementById("ai-chat-input");
  const text = input.value.trim();
  if (!text) return;

  const chatLog = document.getElementById("ai-chat-log");
  
  // User bubble
  const userMsg = document.createElement("div");
  userMsg.className = "bg-cyan-950/60 border border-cyan-800 p-2.5 rounded-xl ml-4";
  userMsg.innerHTML = `<span class="text-cyan-300 font-semibold block mb-0.5">👤 You</span>${text}`;
  chatLog.appendChild(userMsg);
  input.value = "";

  // Call backend assistant API
  try {
    const res = await fetch(`${API_BASE}/api/assistant/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text })
    });
    const data = await res.json();

    const botMsg = document.createElement("div");
    botMsg.className = "bg-slate-950 border border-slate-800 p-3 rounded-xl mr-4 space-y-1.5";
    botMsg.innerHTML = `
      <span class="text-cyan-400 font-semibold block">🤖 Assistant (${data.domain})</span>
      <div class="text-slate-200 font-medium">${data.summary}</div>
      <pre class="text-slate-400 text-[11px] whitespace-pre-wrap font-sans bg-slate-900/80 p-2 rounded">${data.insights}</pre>
      <div class="text-emerald-400 text-[11px] font-semibold">💡 Recommendation: ${data.actionable_recommendation}</div>
    `;
    chatLog.appendChild(botMsg);
    chatLog.scrollTop = chatLog.scrollHeight;
  } catch (e) {
    console.error("AI chat error:", e);
  }
}
