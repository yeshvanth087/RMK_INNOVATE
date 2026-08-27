// ==========================================================================
// NEURONEX URBANSENSE AI - ENHANCED MAP, ROAD RATINGS & COMMAND CENTER
// ==========================================================================

const API_BASE = window.location.origin;

// State Management
let map = null;
let busLayerGroup = null;
let hazardLayerGroup = null;
let incidentLayerGroup = null;
let roadQualityLayerGroup = null;
let detourLayerGroup = null;

let darkTileLayer = null;
let brightTileLayer = null;
let currentBasemap = "dark"; // "dark" or "bright"

let activePortal = "unified";
let mapViewMode = "fleet"; // "fleet" or "roads"
let activeSelectedRoadId = null;

let fleetData = [];
let roadRatingsData = [];

// Initialize Dashboard & Map on Load
document.addEventListener("DOMContentLoaded", () => {
  initLeafletMap();
  initLucideIcons();
  refreshAllData();
  selectHUDCam("front");

  // Real-time polling every 3.5 seconds
  setInterval(refreshAllData, 3500);
});

function initLucideIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// --------------------------------------------------------------------------
// Leaflet Map Initialization with High-Visibility Basemaps & Layers
// --------------------------------------------------------------------------
function initLeafletMap() {
  const mapElement = document.getElementById("gis-map");
  if (!mapElement) return;

  // Initialize Map centered on Chennai Urban Region
  map = L.map("gis-map", {
    center: [13.0450, 80.2450],
    zoom: 12,
    zoomControl: true
  });

  // 1. High-Contrast Cyber Dark Basemap
  darkTileLayer = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: "&copy; OpenStreetMap &copy; CARTO",
    subdomains: "abcd",
    maxZoom: 19
  });

  // 2. High-Contrast Bright Streets Basemap (Vibrant OSM / Voyager)
  brightTileLayer = L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
    attribution: "&copy; OpenStreetMap &copy; CARTO",
    subdomains: "abcd",
    maxZoom: 19
  });

  // Default to dark tiles
  darkTileLayer.addTo(map);

  // Initialize Layer Groups
  roadQualityLayerGroup = L.layerGroup().addTo(map);
  hazardLayerGroup = L.layerGroup().addTo(map);
  incidentLayerGroup = L.layerGroup().addTo(map);
  busLayerGroup = L.layerGroup().addTo(map);
  detourLayerGroup = L.layerGroup().addTo(map);
}

// Toggle Basemap (Dark vs High-Contrast Bright Streets)
function toggleMapBasemap() {
  const textEl = document.getElementById("basemap-mode-text");
  if (currentBasemap === "dark") {
    map.removeLayer(darkTileLayer);
    brightTileLayer.addTo(map);
    currentBasemap = "bright";
    if (textEl) textEl.innerText = "Cyber Dark Mode";
  } else {
    map.removeLayer(brightTileLayer);
    darkTileLayer.addTo(map);
    currentBasemap = "dark";
    if (textEl) textEl.innerText = "High-Contrast Bright Mode";
  }
  initLucideIcons();
}

// Toggle View Mode: Live Fleet vs Road Quality Ratings View
function setMapViewMode(mode) {
  mapViewMode = mode;
  const btnFleet = document.getElementById("map-mode-fleet");
  const btnRoads = document.getElementById("map-mode-roads");

  if (mode === "roads") {
    btnRoads.classList.add("bg-amber-500", "text-slate-950", "shadow-md");
    btnRoads.classList.remove("text-amber-300");
    btnFleet.classList.remove("bg-cyan-600", "text-white", "shadow-md");
    btnFleet.classList.add("text-cyan-400");
    
    // Dim hazard pins slightly to accentuate colored road ratings
    renderRoadQualityPolylines(roadRatingsData);
  } else {
    btnFleet.classList.add("bg-cyan-600", "text-white", "shadow-md");
    btnFleet.classList.remove("text-cyan-400");
    btnRoads.classList.remove("bg-amber-500", "text-slate-950", "shadow-md");
    btnRoads.classList.add("text-amber-300");
  }
}

// --------------------------------------------------------------------------
// Data Refresh & Polling Engine
// --------------------------------------------------------------------------
async function refreshAllData() {
  try {
    const [fleetRes, defectsRes, incidentsRes, ticketsRes, kpisRes, roadsRes] = await Promise.all([
      fetch(`${API_BASE}/api/gis/fleet-live`).then(r => r.json()),
      fetch(`${API_BASE}/api/gis/road-defects-geojson`).then(r => r.json()),
      fetch(`${API_BASE}/api/incidents/active`).then(r => r.json()),
      fetch(`${API_BASE}/api/tickets/`).then(r => r.json()),
      fetch(`${API_BASE}/api/analytics/kpis`).then(r => r.json()),
      fetch(`${API_BASE}/api/roads/ratings`).then(r => r.json())
    ]);

    fleetData = fleetRes || [];
    roadRatingsData = roadsRes || [];

    updateKpiRibbon(kpisRes);
    renderBusMarkers(fleetData);
    renderHazardMarkers(defectsRes);
    renderIncidentMarkers(incidentsRes);
    renderRoadQualityPolylines(roadRatingsData);

    renderIncidentFeed(incidentsRes);
    renderDefectsFeed(defectsRes);
    renderPwdTickets(ticketsRes);
    renderPoliceIncidentsDetailed(incidentsRes);
    renderRoadRatingsLeaderboard(roadRatingsData);

    initLucideIcons();
  } catch (error) {
    console.error("Data refresh error:", error);
  }
}

// --------------------------------------------------------------------------
// KPI Metric Ribbon
// --------------------------------------------------------------------------
function updateKpiRibbon(kpis) {
  if (!kpis) return;
  document.getElementById("kpi-buses").innerText = `${kpis.active_sensing_buses || 8} Online`;
  document.getElementById("kpi-defects").innerText = `${kpis.total_active_defects || 0} Issues`;
  document.getElementById("kpi-incidents").innerText = `${kpis.active_police_incidents || 0} Active`;
  document.getElementById("kpi-tickets").innerText = `${kpis.open_pwd_work_orders || 0} Open`;
  document.getElementById("kpi-reliability").innerText = `${kpis.network_on_time_reliability_pct || 86.4}%`;
  document.getElementById("kpi-roads").innerText = `${kpis.urban_roads_scanned_km || 428.5} km`;
}

// --------------------------------------------------------------------------
// Render Bus Markers on Leaflet Map
// --------------------------------------------------------------------------
function renderBusMarkers(buses) {
  if (!busLayerGroup) return;
  busLayerGroup.clearLayers();

  const isBusesChecked = document.getElementById("layer-buses").checked;
  if (!isBusesChecked) return;

  buses.forEach(b => {
    const iconHtml = `
      <div class="relative flex items-center justify-center">
        <div class="w-9 h-9 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 border-2 border-white flex items-center justify-center shadow-lg shadow-cyan-500/80 animate-neon-pulse">
          <span class="text-white text-xs font-black">🚍</span>
        </div>
        <span class="absolute -bottom-4 bg-slate-950/95 text-cyan-300 font-mono text-[9px] font-black px-1.5 py-0.5 rounded-md border border-cyan-500/50 whitespace-nowrap shadow-md">
          ${b.bus_id}
        </span>
      </div>
    `;

    const icon = L.divIcon({
      className: "bus-marker-icon",
      html: iconHtml,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    const marker = L.marker([b.latitude, b.longitude], { icon: icon });
    marker.bindPopup(`
      <div class="p-2.5 text-xs font-sans space-y-1">
        <div class="font-black text-cyan-400 text-sm border-b border-slate-700 pb-1">${b.bus_id} (${b.route_id})</div>
        <div class="text-slate-200"><b>Speed:</b> <span class="text-cyan-300 font-bold">${b.speed_kmh} km/h</span></div>
        <div class="text-slate-200"><b>Heading:</b> ${Math.round(b.heading_deg)}°</div>
        <div class="text-slate-200"><b>Passenger Crowding:</b> <span class="text-amber-400 font-bold">${b.crowding_pct}%</span></div>
        <div class="text-[10px] text-emerald-400 font-bold pt-1">✅ Onboard Edge AI Sensors Active</div>
      </div>
    `, { className: "custom-popup" });

    busLayerGroup.addLayer(marker);
  });
}

// --------------------------------------------------------------------------
// Render Road Quality Rating Polylines with Color-Coded Health Tints
// --------------------------------------------------------------------------
function renderRoadQualityPolylines(roads) {
  if (!roadQualityLayerGroup || !roads) return;
  roadQualityLayerGroup.clearLayers();

  roads.forEach(r => {
    const isSelected = activeSelectedRoadId === r.road_id;
    const polylineWeight = isSelected ? 9 : (mapViewMode === "roads" ? 7 : 4.5);
    const polylineOpacity = isSelected ? 1.0 : (mapViewMode === "roads" ? 0.9 : 0.65);

    // Glowing polyline
    const polyline = L.polyline(r.coordinates, {
      color: r.color_hex,
      weight: polylineWeight,
      opacity: polylineOpacity,
      dashArray: r.grade === "F" ? "6, 8" : null,
      lineCap: "round",
      lineJoin: "round"
    });

    polyline.bindTooltip(`
      <div class="p-1 text-xs font-sans">
        <span class="font-bold text-slate-950">${r.name}</span><br>
        <span class="font-bold" style="color: ${r.color_hex}">★ ${r.star_rating} | Score: ${r.quality_score}/100 (${r.grade})</span>
      </div>
    `, { sticky: true, opacity: 0.95 });

    polyline.on("click", () => {
      openRoadInspectorModal(r);
    });

    roadQualityLayerGroup.addLayer(polyline);
  });
}

// --------------------------------------------------------------------------
// Render Road Defects & Hazard Markers
// --------------------------------------------------------------------------
function renderHazardMarkers(defectsGeoJson) {
  if (!hazardLayerGroup || !defectsGeoJson.features) return;
  hazardLayerGroup.clearLayers();

  const isChecked = document.getElementById("layer-potholes").checked;
  if (!isChecked) return;

  defectsGeoJson.features.forEach(f => {
    const props = f.properties;
    const [lng, lat] = f.geometry.coordinates;

    const isCritical = props.severity === "CRITICAL";
    const isWater = props.hazard_type === "waterlogging";
    const color = isCritical ? "#ef4444" : (isWater ? "#3b82f6" : "#f59e0b");
    const emoji = isCritical ? "🚨" : (isWater ? "🌊" : "⚠️");

    const icon = L.divIcon({
      className: "hazard-marker-icon",
      html: `
        <div class="relative flex items-center justify-center">
          <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs shadow-lg transform hover:scale-125 transition-transform" style="background-color: ${color}30; border: 2px solid ${color};">
            ${emoji}
          </div>
          <span class="absolute -top-3 bg-slate-950/90 text-white font-bold text-[8px] px-1 rounded border border-slate-700">
            ${props.confirmation_count}x
          </span>
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });

    const marker = L.marker([lat, lng], { icon: icon });
    marker.bindPopup(`
      <div class="p-2 text-xs font-sans space-y-1">
        <div class="font-black text-amber-400 text-sm uppercase">${props.hazard_type.replace(/_/g, " ")}</div>
        <div class="text-slate-200"><b>Severity:</b> <span class="text-red-400 font-bold">${props.severity}</span></div>
        <div class="text-slate-200"><b>AI Confidence:</b> <span class="text-emerald-400 font-bold">${Math.round(props.confidence * 100)}%</span></div>
        <div class="text-slate-200"><b>Confirmed by:</b> ${props.confirmation_count} Fleet Buses</div>
        <div class="text-[10px] text-purple-300 font-mono pt-1">Ticket: ${props.ticket_id || "Auto-Generating"}</div>
      </div>
    `, { className: "custom-popup" });

    hazardLayerGroup.addLayer(marker);
  });
}

// --------------------------------------------------------------------------
// Render Police Incident Markers
// --------------------------------------------------------------------------
function renderIncidentMarkers(incidents) {
  if (!incidentLayerGroup || !incidents) return;
  incidentLayerGroup.clearLayers();

  const isChecked = document.getElementById("layer-incidents").checked;
  if (!isChecked) return;

  incidents.forEach(inc => {
    const icon = L.divIcon({
      className: "incident-marker-icon",
      html: `
        <div class="w-7 h-7 rounded-full bg-red-600/40 border-2 border-red-500 flex items-center justify-center text-xs animate-bounce shadow-lg shadow-red-500/80">
          🚨
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });

    const marker = L.marker([inc.latitude, inc.longitude], { icon: icon });
    marker.bindPopup(`
      <div class="p-2 text-xs font-sans space-y-1">
        <div class="font-black text-red-400 text-sm">🚨 ${inc.incident_type}</div>
        <div class="font-mono text-sm bg-slate-950 p-1.5 rounded font-black text-white text-center border border-red-800">${inc.license_plate}</div>
        <div class="text-slate-200"><b>Speed:</b> <span class="text-amber-400 font-bold">~${inc.estimated_speed} km/h</span></div>
        <div class="text-[10px] text-slate-400 pt-1">Flagged by ${inc.reporting_bus_id}</div>
      </div>
    `, { className: "custom-popup" });

    incidentLayerGroup.addLayer(marker);
  });
}

// --------------------------------------------------------------------------
// Road Quality Ratings Leaderboard & Inspector
// --------------------------------------------------------------------------
function renderRoadRatingsLeaderboard(roads) {
  const container = document.getElementById("road-ratings-list-container");
  if (!container || !roads) return;

  container.innerHTML = roads.map(r => {
    return `
      <div onclick="openRoadInspectorModalById('${r.road_id}')" class="bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl space-y-2 hover:border-amber-500/50 cursor-pointer transition-all">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="w-3 h-3 rounded-full" style="background-color: ${r.color_hex}; box-shadow: 0 0 8px ${r.color_hex};"></span>
            <span class="font-black text-sm text-slate-100">${r.name}</span>
          </div>
          <span class="text-xs font-black px-2.5 py-0.5 rounded-lg border font-mono" style="background-color: ${r.color_hex}20; color: ${r.color_hex}; border-color: ${r.color_hex};">
            ${r.grade} (${r.quality_score}/100)
          </span>
        </div>

        <div class="text-xs text-slate-400">${r.segment} • <b>${r.length_km} km</b></div>

        <div class="grid grid-cols-3 gap-2 bg-slate-900/90 p-2 rounded-lg text-[11px]">
          <div><span class="text-slate-400">Stars:</span> <span class="font-bold text-amber-400">★ ${r.star_rating}</span></div>
          <div><span class="text-slate-400">Potholes:</span> <span class="font-bold text-amber-300">${r.potholes_count} (${r.potholes_per_km}/km)</span></div>
          <div><span class="text-slate-400">Water Risk:</span> <span class="font-bold ${r.waterlogging_risk === 'HIGH' ? 'text-red-400' : 'text-blue-400'}">${r.waterlogging_risk}</span></div>
        </div>

        <div class="text-[11px] font-semibold text-emerald-400">
          💡 ${r.pwd_action}
        </div>
      </div>
    `;
  }).join("");
}

function openRoadInspectorModalById(roadId) {
  const road = roadRatingsData.find(r => r.road_id === roadId);
  if (road) openRoadInspectorModal(road);
}

function openRoadInspectorModal(road) {
  activeSelectedRoadId = road.road_id;
  renderRoadQualityPolylines(roadRatingsData);

  document.getElementById("modal-road-name").innerText = road.name;
  document.getElementById("modal-road-segment").innerText = `${road.segment} (${road.length_km} km)`;
  document.getElementById("modal-quality-score").innerText = `${road.quality_score}/100`;
  
  const gradeEl = document.getElementById("modal-grade");
  gradeEl.innerText = `Grade ${road.grade}`;
  gradeEl.style.backgroundColor = `${road.color_hex}30`;
  gradeEl.style.color = road.color_hex;

  document.getElementById("modal-potholes-km").innerText = `${road.potholes_per_km} per km (${road.potholes_count} total)`;
  document.getElementById("modal-water-risk").innerText = road.waterlogging_risk;
  document.getElementById("modal-speed").innerText = `${road.avg_speed_kmh} km/h (Limit: ${road.speed_limit_kmh})`;
  document.getElementById("modal-length").innerText = `${road.length_km} km (${road.lane_count} lanes)`;
  document.getElementById("modal-pwd-action").innerText = `PWD Recommendation: ${road.pwd_action}`;

  document.getElementById("rate-slider").value = Math.min(5, Math.max(1, road.star_rating || 4));
  document.getElementById("rate-val-display").innerText = `${document.getElementById("rate-slider").value} Stars`;

  document.getElementById("road-inspector-modal").classList.remove("hidden");
}

function closeRoadModal() {
  document.getElementById("road-inspector-modal").classList.add("hidden");
  activeSelectedRoadId = null;
  renderRoadQualityPolylines(roadRatingsData);
}

async function submitUserRoadRating() {
  if (!activeSelectedRoadId) return;
  const ratingVal = parseFloat(document.getElementById("rate-slider").value);

  try {
    const res = await fetch(`${API_BASE}/api/roads/rate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        road_id: activeSelectedRoadId,
        rating: ratingVal,
        feedback_notes: "Submitted via UrbanSense Dashboard"
      })
    });
    const data = await res.json();
    alert(`⭐ ${data.message}`);
    closeRoadModal();
    refreshAllData();
  } catch (err) {
    console.error("Error submitting rating:", err);
  }
}

// --------------------------------------------------------------------------
// Incident & Defect Feeds
// --------------------------------------------------------------------------
function renderIncidentFeed(incidents) {
  const container = document.getElementById("incident-feed-container");
  if (!container || !incidents) return;

  if (incidents.length === 0) {
    container.innerHTML = `<div class="text-slate-400 text-xs text-center py-4">No active police incidents.</div>`;
    return;
  }

  container.innerHTML = incidents.slice(0, 3).map(inc => `
    <div class="bg-slate-950/80 border border-red-950 p-2.5 rounded-xl space-y-1.5 hover:border-red-500/40 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-black text-red-400">🚨 ${inc.incident_type}</span>
        <span class="text-xs font-mono font-black bg-slate-900 px-1.5 py-0.5 rounded text-white border border-slate-800">${inc.license_plate}</span>
      </div>
      <div class="flex items-center justify-between text-[11px] text-slate-300">
        <span>Speed: <b class="text-amber-400">~${inc.estimated_speed} km/h</b></span>
        <span>Bus: <b class="text-cyan-400">${inc.reporting_bus_id}</b></span>
      </div>
    </div>
  `).join("");
}

function renderDefectsFeed(defectsGeoJson) {
  const container = document.getElementById("defects-feed-container");
  if (!container || !defectsGeoJson.features) return;

  container.innerHTML = defectsGeoJson.features.slice(0, 4).map(f => {
    const p = f.properties;
    const isCrit = p.severity === "CRITICAL";
    return `
      <div class="bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-xs flex items-center justify-between hover:border-amber-500/40 transition-all">
        <div class="flex items-center space-x-2.5">
          <span class="text-base">${isCrit ? "🚨" : "⚠️"}</span>
          <div>
            <div class="font-bold text-slate-200 uppercase">${p.hazard_type.replace(/_/g, " ")}</div>
            <div class="text-[10px] text-slate-400">Pos: ${p.relative_position || "lane"} • Conf: ${Math.round(p.confidence * 100)}%</div>
          </div>
        </div>
        <div class="text-right">
          <span class="text-[10px] font-black px-1.5 py-0.5 rounded ${isCrit ? 'bg-red-950 text-red-400 border border-red-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">${p.severity}</span>
          <div class="text-[10px] text-slate-400 mt-1">${p.confirmation_count} buses confirmed</div>
        </div>
      </div>
    `;
  }).join("");
}

// --------------------------------------------------------------------------
// Municipal PWD & Traffic Police Portals
// --------------------------------------------------------------------------
function renderPwdTickets(tickets) {
  const container = document.getElementById("pwd-tickets-container");
  if (!container || !tickets) return;

  container.innerHTML = tickets.map(t => `
    <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2.5 hover:border-purple-500/40 transition-all">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-mono font-black text-purple-400">${t.ticket_id}</span>
          <span class="text-[10px] px-2 py-0.5 rounded-full font-bold ${t.priority === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">${t.priority}</span>
        </div>
        <span class="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 font-bold">${t.status}</span>
      </div>
      <div class="text-xs text-slate-200"><b>Defect:</b> <span class="capitalize">${t.defect_type.replace(/_/g, " ")}</span> — ${t.location_desc}</div>
      <div class="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
        <span class="text-[11px] text-slate-400">${t.assigned_department}</span>
        <div class="flex items-center space-x-2">
          ${t.status === 'OPEN' ? `<button onclick="updateTicketStatus('${t.ticket_id}', 'IN_PROGRESS')" class="px-2.5 py-1 bg-blue-600/30 hover:bg-blue-600 text-blue-300 hover:text-white rounded-lg text-[11px] font-bold">Issue Work Order</button>` : ''}
          ${t.status === 'IN_PROGRESS' ? `<button onclick="updateTicketStatus('${t.ticket_id}', 'RESOLVED')" class="px-2.5 py-1 bg-amber-600/30 hover:bg-amber-600 text-amber-300 hover:text-white rounded-lg text-[11px] font-bold">Mark Repaired</button>` : ''}
          ${t.status === 'RESOLVED' ? `<button onclick="verifyTicketAI('${t.ticket_id}')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-[11px] font-bold flex items-center space-x-1"><span>🤖 Run Bus AI Audit</span></button>` : ''}
          ${t.status === 'AI_VERIFIED' ? `<span class="text-emerald-400 text-xs font-black">✅ Repaired & Bus Verified</span>` : ''}
        </div>
      </div>
    </div>
  `).join("");
}

function renderPoliceIncidentsDetailed(incidents) {
  const container = document.getElementById("police-incident-detailed-container");
  if (!container || !incidents) return;

  container.innerHTML = incidents.map(inc => `
    <div class="bg-slate-950 border border-red-950 p-4 rounded-xl space-y-3 hover:border-red-500/60 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-black text-red-400">🚨 ${inc.incident_type}</span>
        <span class="text-sm font-mono font-black text-white bg-slate-900 px-2 py-0.5 rounded border border-slate-700">${inc.license_plate}</span>
      </div>
      <div class="grid grid-cols-2 gap-2 bg-slate-900/80 p-2.5 rounded-lg text-xs">
        <div><span class="text-slate-400">OCR Conf:</span> <span class="text-emerald-400 font-bold">${Math.round(inc.plate_confidence * 100)}%</span></div>
        <div><span class="text-slate-400">Speed:</span> <span class="text-amber-400 font-bold">~${inc.estimated_speed} km/h</span></div>
        <div><span class="text-slate-400">Reporting Bus:</span> <span class="text-cyan-400 font-bold">${inc.reporting_bus_id}</span></div>
        <div><span class="text-slate-400">Status:</span> <span class="text-white font-bold">${inc.status}</span></div>
      </div>
      ${inc.evidence_snapshot ? `<div class="rounded-lg overflow-hidden border border-slate-800">${inc.evidence_snapshot}</div>` : ''}
      <div class="flex justify-end pt-1">
        <button onclick="dispatchPolice('${inc.id}')" class="px-3.5 py-1.5 rounded-xl text-xs font-bold ${inc.status === 'DISPATCHED' ? 'bg-slate-800 text-slate-400' : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/30'}">
          ${inc.status === 'DISPATCHED' ? 'Patrol Dispatched' : 'Alert Nearest Traffic Patrol'}
        </button>
      </div>
    </div>
  `).join("");
}

// --------------------------------------------------------------------------
// Navigation & Portal Switching
// --------------------------------------------------------------------------
function switchPortal(portalId) {
  activePortal = portalId;
  document.querySelectorAll(".portal-btn").forEach(b => {
    b.classList.remove("bg-gradient-to-r", "from-cyan-500", "to-blue-600", "text-white", "shadow-lg", "shadow-cyan-500/30");
    b.classList.add("text-slate-400");
  });

  const activeBtn = document.getElementById(`btn-portal-${portalId}`);
  if (activeBtn) {
    activeBtn.classList.remove("text-slate-400", "text-amber-300", "text-purple-300", "text-red-300", "text-emerald-300");
    activeBtn.classList.add("bg-gradient-to-r", "from-cyan-500", "to-blue-600", "text-white", "shadow-lg", "shadow-cyan-500/30");
  }

  document.querySelectorAll(".portal-panel").forEach(p => p.classList.add("hidden"));
  const targetPanel = document.getElementById(`portal-${portalId}-view`);
  if (targetPanel) targetPanel.classList.remove("hidden");

  // Automatically switch map view mode when clicking Road Ratings
  if (portalId === "road-ratings") {
    setMapViewMode("roads");
  }

  initLucideIcons();
}

function toggleMapLayers() {
  renderBusMarkers(fleetData);
  renderHazardMarkers({ features: [] });
  refreshAllData();
}

// --------------------------------------------------------------------------
// Live Onboard Camera AI HUD Controller
// --------------------------------------------------------------------------
let currentHudCam = "front";
function selectHUDCam(camId) {
  currentHudCam = camId;
  document.querySelectorAll(".hud-tab-btn").forEach(b => {
    b.classList.remove("bg-cyan-600", "text-white", "shadow-md");
    b.classList.add("text-slate-300");
  });
  const activeTab = document.getElementById(`dash-cam-${camId}`);
  if (activeTab) {
    activeTab.classList.add("bg-cyan-600", "text-white", "shadow-md");
    activeTab.classList.remove("text-slate-300");
  }

  const streamContainer = document.getElementById("dash-camera-stream");
  if (!streamContainer) return;

  if (camId === "front") {
    streamContainer.innerHTML = `
      <svg class="w-full h-64 rounded-xl" viewBox="0 0 800 400" fill="none">
        <rect width="800" height="400" fill="#0f172a"/>
        <polygon points="250,400 380,180 420,180 550,400" fill="#1e293b"/>
        <line x1="400" y1="180" x2="400" y2="400" stroke="#facc15" stroke-width="4" stroke-dasharray="16, 16"/>
        <rect x="340" y="270" width="120" height="60" stroke="#ef4444" stroke-width="3" fill="#ef444425"/>
        <text x="345" y="265" fill="#ef4444" font-size="14" font-family="monospace" font-weight="bold">⚠️ POTHOLE [HIGH] 94%</text>
        <rect x="370" y="190" width="90" height="60" stroke="#00f2fe" stroke-width="2" fill="#00f2fe15"/>
        <text x="370" y="185" fill="#00f2fe" font-size="12" font-family="monospace">Car [ID: 104] 97%</text>
        <rect x="260" y="250" width="75" height="70" stroke="#00f2fe" stroke-width="2" fill="#00f2fe15"/>
        <text x="260" y="245" fill="#00f2fe" font-size="12" font-family="monospace">Auto-Rickshaw 92%</text>
      </svg>
    `;
  } else if (camId === "rear") {
    streamContainer.innerHTML = `
      <svg class="w-full h-64 rounded-xl" viewBox="0 0 800 400" fill="none">
        <rect width="800" height="400" fill="#0f172a"/>
        <polygon points="200,400 370,160 430,160 600,400" fill="#1e293b"/>
        <line x1="400" y1="160" x2="400" y2="400" stroke="#facc15" stroke-width="4" stroke-dasharray="16, 16"/>
        <rect x="420" y="190" width="160" height="130" stroke="#ef4444" stroke-width="3" fill="#ef444425"/>
        <text x="420" y="180" fill="#ef4444" font-size="13" font-family="monospace" font-weight="bold">🚨 RASH OVERTAKE | SPEED: 84.5 km/h</text>
        <rect x="450" y="265" width="100" height="30" stroke="#38bdf8" stroke-width="2" fill="#0284c750"/>
        <text x="455" y="285" fill="#ffffff" font-size="13" font-family="monospace" font-weight="bold">TN 09 BK 4591</text>
        <text x="450" y="310" fill="#38bdf8" font-size="10" font-family="monospace">OCR Conf: 96.4%</text>
      </svg>
    `;
  } else if (camId === "cabin") {
    streamContainer.innerHTML = `
      <svg class="w-full h-64 rounded-xl" viewBox="0 0 800 400" fill="none">
        <rect width="800" height="400" fill="#090d16"/>
        <rect x="150" y="60" width="500" height="260" rx="16" fill="#1e293b" stroke="#334155"/>
        <text x="400" y="110" fill="#00f2fe" font-size="16" font-family="sans-serif" text-anchor="middle" font-weight="bold">PASSENGER OCCUPANCY ESTIMATION</text>
        <circle cx="280" cy="180" r="30" fill="#00f2fe30" stroke="#00f2fe" stroke-width="2"/>
        <circle cx="360" cy="180" r="30" fill="#00f2fe30" stroke="#00f2fe" stroke-width="2"/>
        <circle cx="440" cy="180" r="30" fill="#00f2fe30" stroke="#00f2fe" stroke-width="2"/>
        <circle cx="520" cy="180" r="30" fill="#00f2fe30" stroke="#00f2fe" stroke-width="2"/>
        <text x="400" y="260" fill="#e2e8f0" font-size="14" font-family="sans-serif" text-anchor="middle" font-weight="bold">Occupancy: 38 / 50 Seats (76% - HIGH CROWDING)</text>
      </svg>
    `;
  } else if (camId === "vru") {
    streamContainer.innerHTML = `
      <svg class="w-full h-64 rounded-xl" viewBox="0 0 800 400" fill="none">
        <rect width="800" height="400" fill="#0f172a"/>
        <rect x="100" y="150" width="600" height="150" fill="#1e293b"/>
        <rect x="250" y="150" width="300" height="150" fill="#facc1530" stroke="#facc15" stroke-dasharray="12, 12"/>
        <text x="400" y="140" fill="#facc15" font-size="14" font-family="monospace" text-anchor="middle" font-weight="bold">🚸 SCHOOL CROSSING ZONE IDENTIFIED</text>
        <rect x="340" y="180" width="60" height="100" stroke="#a855f7" stroke-width="2" fill="#a855f725"/>
        <text x="340" y="175" fill="#a855f7" font-size="11" font-family="monospace">Child Pedestrian 91%</text>
      </svg>
    `;
  }
}

// --------------------------------------------------------------------------
// Actions & Dispatch Handlers
// --------------------------------------------------------------------------
async function triggerSimulatedPing() {
  await fetch(`${API_BASE}/api/telemetry/simulate-step`, { method: "POST" });
  refreshAllData();
}

async function dispatchPolice(incidentId) {
  await fetch(`${API_BASE}/api/incidents/${incidentId}/dispatch`, { method: "POST" });
  refreshAllData();
}

async function updateTicketStatus(ticketId, newStatus) {
  await fetch(`${API_BASE}/api/tickets/${ticketId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus })
  });
  refreshAllData();
}

async function verifyTicketAI(ticketId) {
  const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/verify-repair`, { method: "POST" });
  const data = await res.json();
  alert(`🤖 AI Verification Success: ${data.verification_message}`);
  refreshAllData();
}

async function searchPlate() {
  const input = document.getElementById("plate-search-input").value;
  if (!input) return;
  const res = await fetch(`${API_BASE}/api/incidents/search?plate=${encodeURIComponent(input)}`);
  const results = await res.json();
  renderPoliceIncidentsDetailed(results);
  alert(`Found ${results.length} records matching plate query "${input}"`);
}

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
    <div class="text-slate-400 text-[11px] bg-slate-900/80 p-2 rounded mt-1">
      • Traffic Load: ${data.delay_factors.traffic_congestion_pct}%<br>
      • Weather Slowdown: +${data.delay_factors.weather_impact_min} min<br>
      • Road Hazards: +${data.delay_factors.road_hazard_impact_min} min
    </div>
    <div class="text-emerald-400 text-[11px] font-bold mt-1">💡 Actionable Dispatch: ${data.recommendation}</div>
  `;
}

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
    <div class="font-bold text-emerald-400 text-sm mb-1">🛣️ Dynamic Detour Calculated</div>
    <div class="text-slate-200"><b>Detour Status:</b> ${data.status}</div>
    <div class="text-slate-200"><b>Reason:</b> ${data.reason}</div>
    <div class="text-emerald-300 font-bold">Estimated Time Saved: +${data.estimated_time_saved_min} mins</div>
  `;

  if (detourLayerGroup && data.route_waypoints) {
    detourLayerGroup.clearLayers();
    const latLngs = data.route_waypoints.map(w => [w.latitude, w.longitude]);
    const polyline = L.polyline(latLngs, { color: "#10b981", weight: 5, dashArray: "6, 8" });
    detourLayerGroup.addLayer(polyline);
    map.fitBounds(polyline.getBounds(), { padding: [30, 30] });
  }
}

// --------------------------------------------------------------------------
// AI Assistant NLP Chat
// --------------------------------------------------------------------------
function toggleAIAssistant() {
  const drawer = document.getElementById("ai-assistant-drawer");
  drawer.classList.toggle("translate-x-full");
}

async function sendAIChatQuery() {
  const input = document.getElementById("ai-chat-input");
  const text = input.value.trim();
  if (!text) return;

  const chatLog = document.getElementById("ai-chat-log");
  const userMsg = document.createElement("div");
  userMsg.className = "bg-cyan-950/80 border border-cyan-700 p-2.5 rounded-xl ml-4";
  userMsg.innerHTML = `<span class="text-cyan-300 font-bold block mb-0.5">👤 You</span>${text}`;
  chatLog.appendChild(userMsg);
  input.value = "";

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
      <span class="text-cyan-400 font-bold block">🤖 Assistant (${data.domain})</span>
      <div class="text-slate-200 font-medium">${data.summary}</div>
      <pre class="text-slate-400 text-[11px] whitespace-pre-wrap font-sans bg-slate-900/90 p-2 rounded">${data.insights}</pre>
      <div class="text-emerald-400 text-[11px] font-bold">💡 Recommendation: ${data.actionable_recommendation}</div>
    `;
    chatLog.appendChild(botMsg);
    chatLog.scrollTop = chatLog.scrollHeight;
  } catch (e) {
    console.error("AI chat error:", e);
  }
}
