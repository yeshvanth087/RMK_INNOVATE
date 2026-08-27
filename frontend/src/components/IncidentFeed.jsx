import React, { useState } from 'react';
import { ShieldAlert, Search, Send } from 'lucide-react';

export default function IncidentFeed({ incidents, onDispatch, isDetailedView }) {
  const [searchPlate, setSearchPlate] = useState('');

  const filtered = searchPlate.trim()
    ? incidents.filter((i) =>
        (i.license_plate || '').toLowerCase().includes(searchPlate.toLowerCase())
      )
    : incidents;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-red-400" />
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Traffic Police ANPR & Incident Stream
          </h3>
        </div>
        <span className="text-[10px] bg-red-950 text-red-400 border border-red-800 px-2 py-0.5 rounded-full font-bold animate-pulse">
          LIVE ENFORCEMENT
        </span>
      </div>

      {/* SEARCH BAR FOR DETAILED VIEW */}
      {isDetailedView && (
        <div className="flex items-center space-x-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              value={searchPlate}
              onChange={(e) => setSearchPlate(e.target.value)}
              placeholder="Search Vehicle Registration (e.g. TN 09 BK 4591)..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>
      )}

      {/* LIST OF INCIDENT CARDS */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
        {filtered.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">No active incidents matching query.</div>
        ) : (
          filtered.map((inc) => (
            <div
              key={inc.id}
              className="bg-slate-950 border border-red-950/80 p-3.5 rounded-xl space-y-2.5 hover:border-red-500/50 transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-red-400 flex items-center space-x-1.5">
                  <span>🚨 {inc.incident_type}</span>
                </span>
                <span className="text-xs font-mono bg-slate-900 px-2 py-0.5 rounded font-bold text-slate-100 border border-slate-800">
                  {inc.license_plate}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 bg-slate-900/60 p-2 rounded-lg text-xs">
                <div>
                  <span className="text-slate-400">OCR Conf:</span>{' '}
                  <span className="text-emerald-400 font-bold">
                    {Math.round((inc.plate_confidence || 0.85) * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Speed:</span>{' '}
                  <span className="text-amber-400 font-bold">~{inc.estimated_speed} km/h</span>
                </div>
                <div>
                  <span className="text-slate-400">Reporting Bus:</span>{' '}
                  <span className="text-cyan-400">{inc.reporting_bus_id}</span>
                </div>
                <div>
                  <span className="text-slate-400">Status:</span>{' '}
                  <span className="text-slate-200 font-medium">{inc.status}</span>
                </div>
              </div>

              {inc.evidence_snapshot && isDetailedView && (
                <div
                  className="rounded-lg overflow-hidden border border-slate-800"
                  dangerouslySetInnerHTML={{ __html: inc.evidence_snapshot }}
                />
              )}

              <div className="flex items-center justify-end pt-1">
                <button
                  onClick={() => onDispatch(inc.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition-all ${
                    inc.status === 'DISPATCHED'
                      ? 'bg-slate-800 text-slate-400 cursor-default'
                      : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/20'
                  }`}
                >
                  <Send className="w-3 h-3" />
                  <span>{inc.status === 'DISPATCHED' ? 'Patrol Dispatched' : 'Alert Nearest Traffic Patrol'}</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
