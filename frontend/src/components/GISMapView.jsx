import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function GISMapView({ fleet, defects, incidents, roads, detourPath, onSelectRoad }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const busGroup = useRef(null);
  const defectGroup = useRef(null);
  const incidentGroup = useRef(null);
  const roadQualityGroup = useRef(null);
  const detourGroup = useRef(null);

  useEffect(() => {
    if (!mapInstance.current && mapRef.current) {
      mapInstance.current = L.map(mapRef.current, {
        center: [13.0450, 80.2450],
        zoom: 12,
        zoomControl: true
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(mapInstance.current);

      roadQualityGroup.current = L.layerGroup().addTo(mapInstance.current);
      hazardGroup.current = L.layerGroup().addTo(mapInstance.current);
      incidentGroup.current = L.layerGroup().addTo(mapInstance.current);
      busGroup.current = L.layerGroup().addTo(mapInstance.current);
      detourGroup.current = L.layerGroup().addTo(mapInstance.current);
    }
  }, []);

  // Update Road Quality Polylines
  useEffect(() => {
    if (!roadQualityGroup.current || !roads) return;
    roadQualityGroup.current.clearLayers();

    roads.forEach((r) => {
      const polyline = L.polyline(r.coordinates, {
        color: r.color_hex,
        weight: 6,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round'
      });

      polyline.bindTooltip(`
        <div class="p-1 text-xs font-sans">
          <span class="font-bold text-slate-950">${r.name}</span><br>
          <span class="font-bold" style="color: ${r.color_hex}">★ ${r.star_rating} | Score: ${r.quality_score}/100 (${r.grade})</span>
        </div>
      `, { sticky: true });

      polyline.on('click', () => {
        if (onSelectRoad) onSelectRoad(r);
      });

      roadQualityGroup.current.addLayer(polyline);
    });
  }, [roads, onSelectRoad]);

  // Update Bus Markers
  useEffect(() => {
    if (!busGroup.current || !fleet) return;
    busGroup.current.clearLayers();

    fleet.forEach((b) => {
      const busIcon = L.divIcon({
        className: 'bus-marker-icon',
        html: `
          <div class="relative flex items-center justify-center">
            <div class="w-8 h-8 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 border-2 border-white flex items-center justify-center shadow-lg shadow-cyan-500/80">
              <span class="text-white text-xs font-bold">🚍</span>
            </div>
            <span class="absolute -bottom-4 bg-slate-950/95 text-cyan-300 font-mono text-[9px] font-bold px-1.5 py-0.5 rounded border border-cyan-500/50 whitespace-nowrap shadow-md">
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
          <div class="text-slate-200"><b>Speed:</b> ${b.speed_kmh} km/h</div>
          <div class="text-slate-200"><b>Heading:</b> ${Math.round(b.heading_deg)}°</div>
          <div class="text-slate-200"><b>Passenger Crowding:</b> ${b.crowding_pct}%</div>
          <div class="text-emerald-400 text-[10px] mt-1 font-bold">Edge Sensing AI Online</div>
        </div>
      `, { className: 'custom-popup' });

      busGroup.current.addLayer(marker);
    });
  }, [fleet]);

  // Update Road Defects
  useEffect(() => {
    if (!hazardGroup.current || !defects) return;
    hazardGroup.current.clearLayers();

    defects.forEach((f) => {
      const p = f.properties || f;
      const coords = f.geometry ? [f.geometry.coordinates[1], f.geometry.coordinates[0]] : [p.latitude, p.longitude];
      if (!coords[0] || !coords[1]) return;

      const isCritical = p.severity === 'CRITICAL';
      const isWater = p.hazard_type === 'waterlogging';
      const color = isCritical ? '#ef4444' : (isWater ? '#3b82f6' : '#f59e0b');
      const emoji = isCritical ? '🚨' : (isWater ? '🌊' : '⚠️');

      const icon = L.divIcon({
        className: 'hazard-marker-icon',
        html: `
          <div class="relative flex items-center justify-center">
            <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs shadow-lg" style="background-color: ${color}30; border: 2px solid ${color}">
              ${emoji}
            </div>
            <span class="absolute -top-3 bg-slate-950/90 text-white text-[8px] font-bold px-1 rounded border border-slate-700">
              ${p.confirmation_count || 1}x
            </span>
          </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      });

      const marker = L.marker(coords, { icon });
      marker.bindPopup(`
        <div class="p-2 text-xs">
          <div class="font-bold text-amber-400 text-sm capitalize mb-1">${(p.hazard_type || '').replace(/_/g, ' ')}</div>
          <div class="text-slate-200"><b>Severity:</b> <span class="text-red-400 font-bold">${p.severity}</span></div>
          <div class="text-slate-200"><b>AI Confidence:</b> ${Math.round((p.confidence || 0.9) * 100)}%</div>
          <div class="text-slate-200"><b>Confirmed by:</b> ${p.confirmation_count || 1} Buses</div>
        </div>
      `, { className: 'custom-popup' });

      hazardGroup.current.addLayer(marker);
    });
  }, [defects]);

  // Update Police Incidents
  useEffect(() => {
    if (!incidentGroup.current || !incidents) return;
    incidentGroup.current.clearLayers();

    incidents.forEach((inc) => {
      const incIcon = L.divIcon({
        className: 'incident-marker-icon',
        html: `
          <div class="w-6 h-6 rounded-full bg-red-600/40 border-2 border-red-500 flex items-center justify-center text-xs animate-bounce shadow-lg shadow-red-500/80">
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
          <div class="text-white font-mono text-sm bg-slate-950 p-1 rounded my-1 text-center font-bold border border-red-800">${inc.license_plate}</div>
          <div class="text-slate-200"><b>Speed:</b> ~${inc.estimated_speed} km/h</div>
        </div>
      `, { className: 'custom-popup' });

      incidentGroup.current.addLayer(marker);
    });
  }, [incidents]);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex-1 flex flex-col relative shadow-2xl overflow-hidden min-h-[540px]">
      <div className="flex items-center justify-between mb-3 z-10">
        <span className="text-xs font-bold uppercase tracking-wider text-cyan-300 flex items-center space-x-1.5">
          <span>Live Fleet GIS Map & Color-Coded Road Quality Polylines</span>
        </span>
        <div className="flex items-center space-x-3 text-xs bg-slate-950/80 px-3 py-1 rounded-xl border border-slate-800">
          <span className="text-slate-200 font-bold">Active Sensors: {fleet.length}</span>
        </div>
      </div>

      <div ref={mapRef} className="flex-1 w-full rounded-xl z-0 overflow-hidden border border-slate-700 min-h-[440px]"></div>

      <div className="mt-3 flex flex-wrap items-center justify-between text-xs text-slate-300 pt-2 border-t border-slate-800">
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span><span>Grade A (Smooth)</span></span>
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span><span>Grade B (Good)</span></span>
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-yellow-400"></span><span>Grade C (Fair)</span></span>
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-orange-400"></span><span>Grade D (Poor)</span></span>
          <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>Grade F (Hazardous)</span></span>
        </div>
      </div>
    </div>
  );
}
