import React, { useState } from 'react';
import { Route, Star, AlertTriangle, ShieldCheck, Send } from 'lucide-react';

export default function RoadRatingsPortal({ roads, onRateRoad, onSelectRoad }) {
  const [selectedRoad, setSelectedRoad] = useState(roads[0] || null);
  const [userRating, setUserRating] = useState(4);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (roadId) => {
    setIsSubmitting(true);
    try {
      await onRateRoad(roadId, userRating);
      alert('⭐ Road Quality Rating recorded successfully!');
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. ROAD QUALITY LEADERBOARD */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 border-l-4 border-l-amber-400">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-black text-amber-300 flex items-center space-x-2">
              <Route className="w-5 h-5 text-amber-400" />
              <span>Urban Road Quality & Safety Rating Index</span>
            </h3>
            <p className="text-xs text-slate-300">Multi-factor health scores computed by mobile bus sensors</p>
          </div>
          <span className="text-[11px] bg-amber-950 text-amber-400 border border-amber-800 px-2.5 py-1 rounded-full font-bold">
            {roads.length} Corridors
          </span>
        </div>

        <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
          {roads.map((r) => (
            <div
              key={r.road_id}
              onClick={() => {
                setSelectedRoad(r);
                if (onSelectRoad) onSelectRoad(r);
              }}
              className={`bg-slate-950 border p-3.5 rounded-xl space-y-2 cursor-pointer transition-all ${
                selectedRoad?.road_id === r.road_id
                  ? 'border-amber-400 shadow-lg shadow-amber-400/10'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: r.color_hex, boxShadow: `0 0 8px ${r.color_hex}` }}
                  ></span>
                  <span className="font-bold text-sm text-slate-100">{r.name}</span>
                </div>
                <span
                  className="text-xs font-black px-2.5 py-0.5 rounded-lg border font-mono"
                  style={{ backgroundColor: `${r.color_hex}20`, color: r.color_hex, borderColor: r.color_hex }}
                >
                  Grade {r.grade} ({r.quality_score}/100)
                </span>
              </div>

              <div className="text-xs text-slate-400">{r.segment} • <b>{r.length_km} km</b></div>

              <div className="grid grid-cols-3 gap-2 bg-slate-900/80 p-2 rounded-lg text-[11px]">
                <div><span className="text-slate-400">Stars:</span> <span className="font-bold text-amber-400">★ {r.star_rating}</span></div>
                <div><span className="text-slate-400">Potholes:</span> <span className="font-bold text-amber-300">{r.potholes_count}</span></div>
                <div><span className="text-slate-400">Water Risk:</span> <span className="font-bold text-blue-400">{r.waterlogging_risk}</span></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. ROAD QUALITY INSPECTION & RATING SUBMISSION CARD */}
      {selectedRoad && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3 border-l-4 border-l-cyan-400">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
              <Star className="w-4 h-4 text-amber-400" />
              <span>Inspector / Citizen Rating: {selectedRoad.name}</span>
            </h4>
            <span className="text-xs font-bold text-amber-400">{userRating} / 5 Stars</span>
          </div>

          <div className="space-y-2">
            <input
              type="range"
              min="1"
              max="5"
              step="0.5"
              value={userRating}
              onChange={(e) => setUserRating(parseFloat(e.target.value))}
              className="w-full accent-amber-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>1.0 (Hazardous)</span>
              <span>3.0 (Moderate)</span>
              <span>5.0 (Flawless)</span>
            </div>
          </div>

          <div className="text-[11px] text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
            <b>PWD Action:</b> {selectedRoad.pwd_action}
          </div>

          <button
            onClick={() => handleSubmit(selectedRoad.road_id)}
            disabled={isSubmitting}
            className="w-full py-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 rounded-xl font-bold text-xs flex items-center justify-center space-x-1.5 shadow-lg shadow-amber-500/20 transition-all"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSubmitting ? 'Recording Rating...' : 'Submit Road Quality Score'}</span>
          </button>
        </div>
      )}
    </div>
  );
}
