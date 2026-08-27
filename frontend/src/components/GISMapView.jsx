import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function GISMapView({ fleet, defects, incidents, detourPath }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const busGroup = useRef(null);
  const defectGroup = useRef(null);
  const incidentGroup = useRef(null);
  const detourGroup = useRef(null);

  useEffect(() => {
    if (!mapInstance.current && mapRef.current) {
      mapInstance.current = L.map(mapRef.current, {
        center: [13.0400, 80.2300],
        zoom: 12,
        zoomControl: true
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(mapInstance.current);

      busGroup.current = L.layerGroup().addTo(mapInstance.current);
      defectGroup.current = L.layerGroup().addTo(mapInstance.current);
      incidentGroup.current = L.layerGroup().addTo(mapInstance.current);
      detourGroup.current = L.layerGroup().addTo(mapInstance.current);
    }
  }, []);

  // Update Bus Markers
  useEffect(() => {
    if (!busGroup.current) return;
    busGroup.current.clearLayers();

    fleet.forEach((b) => {
      const busIcon = L.divIcon({
        className: 'bus-marker-icon',
        html: `
          <div class="relative flex items-center justify-center">
            <div class="w-8 h-8 rounded-full bg-cyan-500/20 border-2 border-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/50">
              <span class="text-white text-[10px] font-bold">🚍</span>
            </div>
            <span class="absolute -bottom-4 bg-slate-900/90 text-cyan-300 text-[9px] font-bold px-1 rounded border border-cyan-800 whitespace-nowrap">
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

      busGroup.current.addLayer(marker);
    });
  }, [fleet]);

  // Update Road Defects
  useEffect(() => {
    if (!defectGroup.current) return;
    defectGroup.current.clearLayers();

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
            <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs shadow-lg" style="background-color: ${color}20; border: 2px solid ${color}">
              ${emoji}
            </div>
            <span class="absolute -top-3 bg-slate-900/90 text-white text-[8px] font-bold px-1 rounded border border-slate-700">
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
          <div class="text-slate-300"><b>Severity:</b> <span class="text-red-400 font-bold">${p.severity}</span></div>
          <div class="text-slate-300"><b>AI Confidence:</b> ${Math.round((p.confidence || 0.9) * 100)}%</div>
          <div class="text-slate-300"><b>Confirmed by:</b> ${p.confirmation_count || 1} Sensing Buses</div>
          <div class="text-slate-400 text-[10px] mt-1">Ticket: ${p.ticket_id || 'Auto-Generating'}</div>
        </div>
      `, { className: 'custom-popup' });

      defectGroup.current.addLayer(marker);
    });
  }, [defects]);

  // Update Police Incidents
  useEffect(() => {
    if (!incidentGroup.current) return;
    incidentGroup.current.clearLayers();

    incidents.forEach((inc) => {
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
          <div class="text-slate-300"><b>Speed:</b> ~${inc.estimated_speed} km/h</div>
          <div class="text-slate-400 text-[10px] mt-1">Reporting Bus: ${inc.reporting_bus_id}</div>
        </div>
      `, { className: 'custom-popup' });

      incidentGroup.current.addLayer(marker);
    });
  }, [incidents]);

  // Update Dynamic Detour Polyline
  useEffect(() => {
    if (!detourGroup.current) return;
    detourGroup.current.clearLayers();

    if (detourPath && detourPath.length > 0) {
      const polyline = L.polyline(detourPath, { color: '#10b981', weight: 4, dashArray: '6, 8' });
      detourGroup.current.addLayer(polyline);
      if (mapInstance.current) {
        mapInstance.current.fitBounds(polyline.getBounds(), { padding: [40, 40] });
      }
    }
  }, [detourPath]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex-1 flex flex-col relative shadow-xl overflow-hidden min-h-[520px]">
      <div className="flex items-center justify-between mb-3 z-10">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
          <span>Live Fleet GIS Map & Dynamic Hazard Layer</span>
        </span>
        <div className="flex items-center space-x-3 text-xs bg-slate-950/80 px-3 py-1 rounded-lg border border-slate-800">
          <span className="text-slate-300">Active Sensors: {fleet.length}</span>
        </div>
      </div>

      <div ref={mapRef} className="flex-1 w-full rounded-xl z-0 overflow-hidden border border-slate-800 min-h-[440px]"></div>

      <div className="mt-3 flex flex-wrap items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-400"></span><span>Sensing Bus</span></span>
          <span className="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span><span>Pothole / Crack</span></span>
          <span className="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span><span>Waterlogging</span></span>
          <span className="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 rounded-full bg-red-500"></span><span>Hit & Run / ANPR</span></span>
        </div>
      </div>
    </div>
  );
}
