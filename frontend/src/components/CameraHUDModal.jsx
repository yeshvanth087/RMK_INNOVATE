import React, { useState, useEffect } from 'react';
import { X, Video, ShieldAlert, AlertTriangle, Users, Eye } from 'lucide-react';

export default function CameraHUDModal({ isOpen, onClose }) {
  const [activeCam, setActiveCam] = useState('front');
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setPulse((p) => p + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-5xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* MODAL HEADER */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400">
              <Video className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                <span>Onboard Bus Edge-AI Vision Stream</span>
                <span className="text-[10px] bg-red-950 text-red-400 border border-red-800 px-2 py-0.5 rounded-full font-bold animate-pulse">
                  LIVE INFERENCE (Jetson Orin Nano)
                </span>
              </h2>
              <p className="text-xs text-slate-400">Bus Unit: BUS-BEL-104 • Model: YOLOv9 + ByteTrack + HSRP ANPR</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* CAMERA SELECTION TABS */}
        <div className="px-6 py-2.5 bg-slate-950/40 border-b border-slate-800 flex items-center space-x-2">
          {[
            { id: 'front', label: 'Front Cam: Road Defects & Traffic', icon: Eye },
            { id: 'rear', label: 'Rear/Side Cam: ANPR & Speeding', icon: ShieldAlert },
            { id: 'cabin', label: 'Cabin Cam: Passenger Crowding', icon: Users },
            { id: 'vru', label: 'Blindspot Cam: School VRU', icon: AlertTriangle }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveCam(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                  activeCam === tab.id
                    ? 'bg-cyan-600 text-white shadow-md'
                    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* LIVE SIMULATED VIDEO FEED CANVAS WITH HUD OVERLAYS */}
        <div className="p-6 flex-1 flex flex-col items-center justify-center bg-black relative min-h-[420px] overflow-hidden">
          {/* CAMERA HUD CORNERS */}
          <div className="absolute top-8 left-8 w-8 h-8 border-t-2 border-l-2 border-cyan-500"></div>
          <div className="absolute top-8 right-8 w-8 h-8 border-t-2 border-r-2 border-cyan-500"></div>
          <div className="absolute bottom-8 left-8 w-8 h-8 border-b-2 border-l-2 border-cyan-500"></div>
          <div className="absolute bottom-8 right-8 w-8 h-8 border-b-2 border-r-2 border-cyan-500"></div>

          {/* TOP METADATA HUD */}
          <div className="absolute top-10 left-12 right-12 flex items-center justify-between text-[11px] font-mono text-cyan-400 bg-slate-950/70 backdrop-blur px-4 py-1.5 rounded-lg border border-cyan-900/50">
            <span>CAM: 0{activeCam === 'front' ? '1' : activeCam === 'rear' ? '02' : activeCam === 'cabin' ? '03' : '04'}_HD</span>
            <span>FPS: 29.8 | LATENCY: 28ms</span>
            <span>TENSORRT ENGINE: ONNX_FP16</span>
            <span>GPS: 13.0827° N, 80.2707° E</span>
          </div>

          {/* VIEW 1: FRONT CAMERA (POTHOLES & VEHICLES) */}
          {activeCam === 'front' && (
            <div className="w-full h-full relative flex items-center justify-center">
              {/* Simulated Road Scene Background SVG */}
              <svg className="w-full h-80 rounded-xl" viewBox="0 0 800 400" fill="none">
                <rect width="800" height="400" fill="#0f172a" />
                {/* Road Perspective */}
                <polygon points="250,400 380,180 420,180 550,400" fill="#1e293b" />
                <line x1="400" y1="180" x2="400" y2="400" stroke="#facc15" strokeWidth="4" strokeDasharray="16, 16" />
                
                {/* Bounding Box 1: Pothole */}
                <rect x="340" y="270" width="120" height="60" stroke="#ef4444" strokeWidth="2.5" fill="#ef444420" />
                <text x="345" y="265" fill="#ef4444" fontSize="12" fontFamily="monospace" fontWeight="bold">⚠️ POTHOLE [HIGH] 94%</text>

                {/* Bounding Box 2: Car Ahead */}
                <rect x="370" y="190" width="90" height="60" stroke="#06b6d4" strokeWidth="2" fill="#06b6d415" />
                <text x="370" y="185" fill="#06b6d4" fontSize="11" fontFamily="monospace">Car [ID: 104] 97%</text>

                {/* Bounding Box 3: Auto Rickshaw */}
                <rect x="260" y="250" width="75" height="70" stroke="#06b6d4" strokeWidth="2" fill="#06b6d415" />
                <text x="260" y="245" fill="#06b6d4" fontSize="11" fontFamily="monospace">Auto-Rickshaw 92%</text>
              </svg>
            </div>
          )}

          {/* VIEW 2: REAR/SIDE CAMERA (ANPR & RASH DRIVING) */}
          {activeCam === 'rear' && (
            <div className="w-full h-full relative flex items-center justify-center">
              <svg className="w-full h-80 rounded-xl" viewBox="0 0 800 400" fill="none">
                <rect width="800" height="400" fill="#0f172a" />
                <polygon points="200,400 370,160 430,160 600,400" fill="#1e293b" />
                <line x1="400" y1="160" x2="400" y2="400" stroke="#facc15" strokeWidth="4" strokeDasharray="16, 16" />

                {/* Speeding Overtaking Vehicle Box */}
                <rect x="420" y="190" width="160" height="130" stroke="#ef4444" strokeWidth="3" fill="#ef444420" />
                <text x="420" y="180" fill="#ef4444" fontSize="13" fontFamily="monospace" fontWeight="bold">🚨 RASH OVERTAKE | SPEED: 84.5 km/h</text>
                
                {/* ANPR Zoom Plate Target */}
                <rect x="450" y="265" width="100" height="30" stroke="#38bdf8" strokeWidth="2" fill="#0284c740" />
                <text x="455" y="285" fill="#ffffff" fontSize="13" fontFamily="monospace" fontWeight="bold">TN 09 BK 4591</text>
                <text x="450" y="310" fill="#38bdf8" fontSize="10" fontFamily="monospace">OCR Conf: 96.4%</text>
              </svg>
            </div>
          )}

          {/* VIEW 3: PASSENGER CABIN CAMERA */}
          {activeCam === 'cabin' && (
            <div className="w-full h-full relative flex items-center justify-center">
              <svg className="w-full h-80 rounded-xl" viewBox="0 0 800 400" fill="none">
                <rect width="800" height="400" fill="#090d16" />
                <rect x="150" y="80" width="500" height="240" rx="12" fill="#1e293b" stroke="#334155" />
                <text x="400" y="130" fill="#38bdf8" fontSize="16" fontFamily="sans-serif" textAnchor="middle" fontWeight="bold">
                  PASSENGER OCCUPANCY ESTIMATION
                </text>
                <circle cx="280" cy="200" r="30" fill="#06b6d440" stroke="#06b6d4" strokeWidth="2" />
                <circle cx="360" cy="200" r="30" fill="#06b6d440" stroke="#06b6d4" strokeWidth="2" />
                <circle cx="440" cy="200" r="30" fill="#06b6d440" stroke="#06b6d4" strokeWidth="2" />
                <circle cx="520" cy="200" r="30" fill="#06b6d440" stroke="#06b6d4" strokeWidth="2" />
                <text x="400" y="275" fill="#e2e8f0" fontSize="14" fontFamily="sans-serif" textAnchor="middle">
                  Occupancy: 38 / 50 Seats (76% - HIGH CROWDING)
                </text>
              </svg>
            </div>
          )}

          {/* VIEW 4: SIDE/BLINDSPOT (VRU & SCHOOL CHILDREN) */}
          {activeCam === 'vru' && (
            <div className="w-full h-full relative flex items-center justify-center">
              <svg className="w-full h-80 rounded-xl" viewBox="0 0 800 400" fill="none">
                <rect width="800" height="400" fill="#0f172a" />
                <rect x="100" y="150" width="600" height="150" fill="#1e293b" />
                <rect x="250" y="150" width="300" height="150" fill="#facc1530" stroke="#facc15" strokeDasharray="12, 12" />
                <text x="400" y="140" fill="#facc15" fontSize="14" fontFamily="monospace" textAnchor="middle" fontWeight="bold">
                  🚸 SCHOOL CROSSING ZONE IDENTIFIED
                </text>
                <rect x="340" y="180" width="60" height="100" stroke="#a855f7" strokeWidth="2" fill="#a855f720" />
                <text x="340" y="175" fill="#a855f7" fontSize="11" fontFamily="monospace">Child Pedestrian 91%</text>
              </svg>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
