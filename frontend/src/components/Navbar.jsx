import React from 'react';
import { LayoutDashboard, Route, Wrench, ShieldAlert, Navigation, Sparkles, Video } from 'lucide-react';

export default function Navbar({ activePortal, setActivePortal, toggleAI, toggleCameraHUD, fleetCount }) {
  const portals = [
    { id: 'unified', label: 'Command Center', icon: LayoutDashboard },
    { id: 'road-ratings', label: 'Road Ratings', icon: Route },
    { id: 'pwd', label: 'Municipal PWD', icon: Wrench },
    { id: 'police', label: 'Traffic Police', icon: ShieldAlert },
    { id: 'transit', label: 'Transit Ops', icon: Navigation }
  ];

  return (
    <header className="bg-slate-900/95 backdrop-blur-md border-b border-cyan-500/30 px-6 py-3 sticky top-0 z-50 flex items-center justify-between shadow-lg shadow-cyan-500/10">
      {/* BRAND & UPLOADED LOGO */}
      <div className="flex items-center space-x-3.5">
        <div className="w-12 h-12 rounded-2xl overflow-hidden bg-slate-950 p-1 border border-cyan-500/40 shadow-lg shadow-cyan-500/30 flex items-center justify-center">
          <img src="/logo.png" alt="NeuroNex UrbanSense AI Logo" className="w-full h-full object-contain rounded-xl" />
        </div>
        <div>
          <h1 className="text-xl font-black tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-amber-400 drop-shadow-md">
            NeuroNex UrbanSense AI
          </h1>
          <p className="text-xs text-slate-300 font-medium tracking-wide">
            AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet
          </p>
        </div>
      </div>

      {/* ROLE SWITCHER BUTTONS */}
      <div className="flex items-center space-x-1.5 bg-slate-950/90 p-1.5 rounded-2xl border border-cyan-500/30 shadow-inner">
        {portals.map((p) => {
          const Icon = p.icon;
          const isActive = activePortal === p.id;
          return (
            <button
              key={p.id}
              onClick={() => setActivePortal(p.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
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
          className="px-3.5 py-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-cyan-300 border border-cyan-500/40 text-xs font-bold flex items-center space-x-1.5 shadow-md transition-all"
        >
          <Video className="w-4 h-4 text-cyan-400" />
          <span>Camera AI HUD</span>
        </button>

        <div className="flex items-center space-x-2 text-xs bg-slate-950/80 px-3 py-1.5 rounded-xl border border-cyan-500/30">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="text-slate-200 font-bold">Fleet: {fleetCount || 8} Buses</span>
        </div>

        <button
          onClick={toggleAI}
          className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white text-xs font-bold flex items-center space-x-2 shadow-lg shadow-cyan-500/30 transition-all transform hover:scale-105"
        >
          <Sparkles className="w-4 h-4" />
          <span>AI Assistant</span>
        </button>
      </div>
    </header>
  );
}
