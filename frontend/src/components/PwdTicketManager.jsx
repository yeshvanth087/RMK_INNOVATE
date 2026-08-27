import React from 'react';
import { Wrench, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function PwdTicketManager({ tickets, onUpdateStatus, onVerifyAI }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Wrench className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Municipal PWD Work Order Management
          </h3>
        </div>
        <span className="text-[10px] bg-purple-950 text-purple-400 border border-purple-800 px-2 py-0.5 rounded-full font-bold">
          AUTO-TICKETING ACTIVE
        </span>
      </div>

      <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
        {tickets.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">No active PWD repair tickets.</div>
        ) : (
          tickets.map((t) => (
            <div
              key={t.ticket_id}
              className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2.5 hover:border-purple-500/40 transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold text-purple-400">{t.ticket_id}</span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                      t.priority === 'CRITICAL'
                        ? 'bg-red-950 text-red-400 border border-red-800'
                        : 'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}
                  >
                    {t.priority}
                  </span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 font-medium">
                  {t.status}
                </span>
              </div>

              <div className="text-xs text-slate-200">
                <b>Defect:</b> <span className="capitalize">{t.defect_type.replace(/_/g, ' ')}</span> — {t.location_desc}
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs">
                <span className="text-[11px] text-slate-400">{t.assigned_department}</span>

                <div className="flex items-center space-x-2">
                  {t.status === 'OPEN' && (
                    <button
                      onClick={() => onUpdateStatus(t.ticket_id, 'IN_PROGRESS')}
                      className="px-2.5 py-1 bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white rounded text-[11px] font-semibold transition-all"
                    >
                      Issue Work Order
                    </button>
                  )}
                  {t.status === 'IN_PROGRESS' && (
                    <button
                      onClick={() => onUpdateStatus(t.ticket_id, 'RESOLVED')}
                      className="px-2.5 py-1 bg-amber-600/20 hover:bg-amber-600 text-amber-300 hover:text-white rounded text-[11px] font-semibold transition-all"
                    >
                      Mark Repaired
                    </button>
                  )}
                  {t.status === 'RESOLVED' && (
                    <button
                      onClick={() => onVerifyAI(t.ticket_id)}
                      className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-[11px] font-semibold transition-all flex items-center space-x-1"
                    >
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>Run Bus Fleet AI Audit</span>
                    </button>
                  )}
                  {t.status === 'AI_VERIFIED' && (
                    <span className="text-emerald-400 text-xs font-bold flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Verified Repaired by Bus</span>
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
