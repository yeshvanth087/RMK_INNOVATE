import React from 'react';
import { Radio, AlertTriangle, ShieldAlert, FileCheck2, Clock, Map } from 'lucide-react';

export default function KpiRibbon({ kpis }) {
  return (
    <section className="bg-slate-900/40 border-b border-slate-800/80 px-6 py-2.5 grid grid-cols-2 md:grid-cols-6 gap-3">
      <div className="bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
          <Radio className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Sensing Buses</div>
          <div className="text-base font-bold text-slate-100">{kpis.active_sensing_buses || 8} Online</div>
        </div>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Active Defects</div>
          <div className="text-base font-bold text-amber-400">{kpis.total_active_defects ?? '--'} Issues</div>
        </div>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-red-500/10 text-red-400">
          <ShieldAlert className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Police Alerts</div>
          <div className="text-base font-bold text-red-400">{kpis.active_police_incidents ?? '--'} Active</div>
        </div>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
          <FileCheck2 className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Open Work Orders</div>
          <div className="text-base font-bold text-purple-300">{kpis.open_pwd_work_orders ?? '--'} Open</div>
        </div>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
          <Clock className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs text-slate-400">On-Time Score</div>
          <div className="text-base font-bold text-emerald-400">{kpis.network_on_time_reliability_pct || '86.4'}%</div>
        </div>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-lg flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
          <Map className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Roads Scanned</div>
          <div className="text-base font-bold text-cyan-300">{kpis.urban_roads_scanned_km || '428.5'} km</div>
        </div>
      </div>
    </section>
  );
}
