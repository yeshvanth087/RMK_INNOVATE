import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import KpiRibbon from './components/KpiRibbon';
import GISMapView from './components/GISMapView';
import IncidentFeed from './components/IncidentFeed';
import PwdTicketManager from './components/PwdTicketManager';
import TransitAnalytics from './components/TransitAnalytics';
import AIAssistantChat from './components/AIAssistantChat';
import CameraHUDModal from './components/CameraHUDModal';
import RoadRatingsPortal from './components/RoadRatingsPortal';
import { AlertTriangle } from 'lucide-react';

export default function App() {
  const [activePortal, setActivePortal] = useState('unified');
  const [isAIOpen, setIsAIOpen] = useState(false);
  const [isCameraHUDOpen, setIsCameraHUDOpen] = useState(false);

  // Real-time State
  const [fleet, setFleet] = useState([]);
  const [defects, setDefects] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [kpis, setKpis] = useState({});
  const [bottlenecks, setBottlenecks] = useState([]);
  const [roads, setRoads] = useState([]);
  const [detourPath, setDetourPath] = useState(null);

  // Polling Real-Time Data from Backend
  const refreshData = async () => {
    try {
      const [fRes, dRes, iRes, tRes, kRes, bRes, rRes] = await Promise.all([
        fetch('/api/gis/fleet-live').then((r) => r.json()),
        fetch('/api/gis/road-defects-geojson').then((r) => r.json()),
        fetch('/api/incidents/active').then((r) => r.json()),
        fetch('/api/tickets/').then((r) => r.json()),
        fetch('/api/analytics/kpis').then((r) => r.json()),
        fetch('/api/analytics/bottlenecks').then((r) => r.json()),
        fetch('/api/roads/ratings').then((r) => r.json())
      ]);

      setFleet(fRes || []);
      setDefects(dRes.features || []);
      setIncidents(iRes || []);
      setTickets(tRes || []);
      setKpis(kRes || {});
      setBottlenecks(bRes || []);
      setRoads(rRes || []);
    } catch (err) {
      console.error('Error refreshing live data:', err);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 3500);
    return () => clearInterval(interval);
  }, []);

  // Handlers
  const handleDispatchPolice = async (id) => {
    await fetch(`/api/incidents/${id}/dispatch`, { method: 'POST' });
    refreshData();
  };

  const handleUpdateTicketStatus = async (ticketId, status) => {
    await fetch(`/api/tickets/${ticketId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    refreshData();
  };

  const handleVerifyAI = async (ticketId) => {
    const res = await fetch(`/api/tickets/${ticketId}/verify-repair`, { method: 'POST' });
    const data = await res.json();
    alert(`🤖 AI Verification Success: ${data.verification_message}`);
    refreshData();
  };

  const handleRateRoad = async (roadId, rating) => {
    await fetch('/api/roads/rate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ road_id: roadId, rating })
    });
    refreshData();
  };

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans antialiased selection:bg-cyan-500 selection:text-black">
      {/* 1. TOP NAVBAR */}
      <Navbar
        activePortal={activePortal}
        setActivePortal={setActivePortal}
        toggleAI={() => setIsAIOpen(!isAIOpen)}
        toggleCameraHUD={() => setIsCameraHUDOpen(true)}
        fleetCount={fleet.length}
      />

      {/* 2. KPI RIBBON */}
      <KpiRibbon kpis={kpis} />

      {/* 3. MAIN DASHBOARD CONTENT */}
      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">
        {/* LEFT COLUMN: INTERACTIVE GIS MAP (7 COLS) */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          <GISMapView
            fleet={fleet}
            defects={defects}
            incidents={incidents}
            roads={roads}
            detourPath={detourPath}
          />
        </div>

        {/* RIGHT COLUMN: PORTAL SPECIFIC PANELS (5 COLS) */}
        <div className="lg:col-span-5 flex flex-col space-y-6 overflow-y-auto max-h-[85vh] pr-1">
          {/* PORTAL 1: UNIFIED COMMAND CENTER (DEFAULT) */}
          {activePortal === 'unified' && (
            <div className="space-y-6">
              <IncidentFeed
                incidents={incidents}
                onDispatch={handleDispatchPolice}
                isDetailedView={false}
              />

              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3 border-l-4 border-l-amber-400">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                    <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                      Detected Road Defects & Hazards
                    </h3>
                  </div>
                  <span className="text-[11px] text-slate-300 font-semibold">Deduplicated (15m Radius)</span>
                </div>

                <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                  {defects.map((f, idx) => {
                    const p = f.properties || f;
                    const isCritical = p.severity === 'CRITICAL';
                    return (
                      <div
                        key={idx}
                        className="bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-xs flex items-center justify-between hover:border-amber-500/40 transition-all"
                      >
                        <div className="flex items-center space-x-2.5">
                          <span className="text-base">{isCritical ? '🚨' : '⚠️'}</span>
                          <div>
                            <div className="font-semibold text-slate-200 capitalize">
                              {(p.hazard_type || '').replace(/_/g, ' ')}
                            </div>
                            <div className="text-[10px] text-slate-400">
                              Pos: {p.relative_position || 'lane'} • Conf: {Math.round((p.confidence || 0.9) * 100)}%
                            </div>
                          </div>
                        </div>

                        <div className="text-right">
                          <span
                            className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                              isCritical
                                ? 'bg-red-950 text-red-400 border border-red-800'
                                : 'bg-amber-950 text-amber-400 border border-amber-800'
                            }`}
                          >
                            {p.severity}
                          </span>
                          <div className="text-[10px] text-slate-400 mt-1">
                            {p.confirmation_count || 1} buses confirmed
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* PORTAL: ROAD QUALITY RATINGS MODULE */}
          {activePortal === 'road-ratings' && (
            <RoadRatingsPortal
              roads={roads}
              onRateRoad={handleRateRoad}
            />
          )}

          {/* PORTAL 2: MUNICIPAL PWD */}
          {activePortal === 'pwd' && (
            <PwdTicketManager
              tickets={tickets}
              onUpdateStatus={handleUpdateTicketStatus}
              onVerifyAI={handleVerifyAI}
            />
          )}

          {/* PORTAL 3: TRAFFIC POLICE */}
          {activePortal === 'police' && (
            <IncidentFeed
              incidents={incidents}
              onDispatch={handleDispatchPolice}
              isDetailedView={true}
            />
          )}

          {/* PORTAL 4: TRANSIT OPS */}
          {activePortal === 'transit' && (
            <TransitAnalytics
              onSolveDetour={(path) => setDetourPath(path)}
              bottlenecks={bottlenecks}
            />
          )}
        </div>
      </main>

      {/* 4. MODALS & DRAWERS */}
      <CameraHUDModal
        isOpen={isCameraHUDOpen}
        onClose={() => setIsCameraHUDOpen(false)}
      />

      <AIAssistantChat
        isOpen={isAIOpen}
        onClose={() => setIsAIOpen(false)}
      />
    </div>
  );
}
