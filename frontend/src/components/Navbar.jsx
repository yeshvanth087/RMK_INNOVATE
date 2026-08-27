import React from 'react';
import { Bus, LayoutDashboard, Wrench, ShieldAlert, Navigation, Sparkles, Video } from 'lucide-react';

export default function Navbar({ activePortal, setActivePortal, toggleAI, toggleCameraHUD, fleetCount }) {
  const portals = [
    { id: 'unified', label: 'Command Center', icon: LayoutDashboard },
    { id: 'pwd', label: 'Municipal PWD', icon: Wrench },
    { id: 'police', label: 'Traffic Police', icon: ShieldAlert },
    { id: 'transit', label: 'Transit Ops', icon: Navigation }
  ];

  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-3 sticky top-0 z-50 flex items-center justify-between">
      {/* BRAND & LOGO */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Bus className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-400">
              NeuroNex UrbanSense AI
            </h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800">
              SIH26124 • BEL
            </span>
          </div>
          <p className="text-xs text-slate-400">Mobile Urban Intelligence Platform Using Public Transport Fleet</p>
        </div>
      </div>

      {/* ROLE SWITCHER BUTTONS */}
      <div className="flex items-center space-x-1.5 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800">
        {portals.map((p) => {
          const Icon = p.icon;
          const isActive = activePortal === p.id;
          return (
            <button
              key={p.id}
              onClick={() => setActivePortal(p.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                isActive
                  ? 'bg-cyan-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{p.label}</span>
            </button>
          );
        })}
      </div>

      {/* QUICK ACTIONS */}
      <div className="flex items-center space-x-3">
        <button
          onClick={toggleCameraHUD}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 text-xs font-semibold flex items-center space-x-1.5 transition-all"
        >
          <Video className="w-4 h-4 text-cyan-400" />
          <span>Live Camera AI HUD</span>
        </button>

        <div className="flex items-center space-x-2 text-xs bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-slate-300 font-medium">Fleet: {fleetCount || 8} Buses</span>
        </div>

        <button
          onClick={toggleAI}
          className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20 transition-all"
        >
          <Sparkles className="w-4 h-4" />
          <span>AI Assistant</span>
        </button>
      </div>
    </header>
  );
}
