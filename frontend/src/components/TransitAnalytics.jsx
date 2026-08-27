import React, { useState } from 'react';
import { Clock, Route, Cpu, Navigation, AlertOctagon } from 'lucide-react';

export default function TransitAnalytics({ onSolveDetour, bottlenecks }) {
  const [routeId, setRouteId] = useState('RT-101');
  const [hour, setHour] = useState(18);
  const [weather, setWeather] = useState('HEAVY_RAIN');
  const [prediction, setPrediction] = useState(null);
  const [detourResult, setDetourResult] = useState(null);
  const [loadingPred, setLoadingPred] = useState(false);
  const [loadingDetour, setLoadingDetour] = useState(false);

  const handlePredictDelay = async () => {
    setLoadingPred(true);
    try {
      const res = await fetch('/api/analytics/predict-delay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          route_id: routeId,
          hour_of_day: hour,
          weather_condition: weather,
          current_crowding_pct: 65.0
        })
      });
      const data = await res.json();
      setPrediction(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingPred(false);
    }
  };

  const handleDetour = async () => {
    setLoadingDetour(true);
    try {
      const res = await fetch('/api/analytics/dynamic-route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: 'NODE_CENTRAL',
          destination: 'NODE_AIRPORT',
          avoid_hazards: true
        })
      });
      const data = await res.json();
      setDetourResult(data);
      if (onSolveDetour && data.route_waypoints) {
        onSolveDetour(data.route_waypoints.map((w) => [w.latitude, w.longitude]));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingDetour(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. ML DELAY & ETA PREDICTOR */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>Machine Learning Route Delay & ETA Predictor</span>
          </h3>
          <p className="text-xs text-slate-400">Random Forest regression fusing live vehicle PCU, weather & road defects</p>
        </div>

        <div className="grid grid-cols-3 gap-2 text-xs">
          <div>
            <label className="text-[11px] text-slate-400 block mb-1">Route</label>
            <select
              value={routeId}
              onChange={(e) => setRouteId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
            >
              <option value="RT-101">RT-101 (Central - Airport)</option>
              <option value="RT-204">RT-204 (Marina - OMR)</option>
              <option value="RT-305">RT-305 (Basin - Koyambedu)</option>
            </select>
          </div>
          <div>
            <label className="text-[11px] text-slate-400 block mb-1">Hour of Day</label>
            <select
              value={hour}
              onChange={(e) => setHour(parseInt(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
            >
              <option value={9}>09:00 AM (Morning Peak)</option>
              <option value={14}>02:00 PM (Off-Peak)</option>
              <option value={18}>06:00 PM (Evening Peak)</option>
              <option value={22}>10:00 PM (Night)</option>
            </select>
          </div>
          <div>
            <label className="text-[11px] text-slate-400 block mb-1">Weather Context</label>
            <select
              value={weather}
              onChange={(e) => setWeather(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
            >
              <option value="CLEAR">Clear Skies</option>
              <option value="RAIN">Moderate Rain</option>
              <option value="HEAVY_RAIN">Heavy Monsoon Rain</option>
            </select>
          </div>
        </div>

        <button
          onClick={handlePredictDelay}
          disabled={loadingPred}
          className="w-full py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 shadow-lg shadow-cyan-500/20 transition-all"
        >
          <Cpu className="w-4 h-4" />
          <span>{loadingPred ? 'Running Random Forest Model...' : 'Calculate Predicted Delay & ETA'}</span>
        </button>

        {prediction && (
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-cyan-400 text-sm">⏱️ ML Model Prediction Results</span>
              <span className="text-amber-400 font-bold text-sm">+{prediction.predicted_delay_minutes} min delay</span>
            </div>
            <div className="text-slate-300"><b>Category:</b> {prediction.delay_category}</div>
            <div className="text-slate-400 text-[11px] bg-slate-900/60 p-2 rounded">
              • Traffic Congestion Load: {prediction.delay_factors?.traffic_congestion_pct}%<br />
              • Weather Slowdown: +{prediction.delay_factors?.weather_impact_min} min<br />
              • Road Surface Hazards: +{prediction.delay_factors?.road_hazard_impact_min} min
            </div>
            <div className="text-emerald-400 text-[11px] font-semibold">
              💡 Actionable Dispatch: {prediction.recommendation}
            </div>
          </div>
        )}
      </div>

      {/* 2. DYNAMIC ROUTE DETOUR OPTIMIZER */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
            <Route className="w-4 h-4 text-emerald-400" />
            <span>Google OR-Tools Dynamic Hazard Detour Solver</span>
          </h3>
          <p className="text-xs text-slate-400">Recalculates transit network paths around high-severity potholes & floods</p>
        </div>

        <button
          onClick={handleDetour}
          disabled={loadingDetour}
          className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 shadow-lg shadow-emerald-500/20 transition-all"
        >
          <Navigation className="w-4 h-4" />
          <span>{loadingDetour ? 'Solving VRP Network Graph...' : 'Solve Dynamic Hazard Detour'}</span>
        </button>

        {detourResult && (
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-emerald-400">🛣️ Dynamic Detour Calculated</span>
              <span className="text-emerald-400 font-bold">Saved: {detourResult.estimated_time_saved_min} mins</span>
            </div>
            <div className="text-slate-300"><b>Status:</b> {detourResult.status}</div>
            <div className="text-slate-300"><b>Reason:</b> {detourResult.reason}</div>
            <div className="text-slate-400 text-[11px] bg-slate-900/60 p-2 rounded">
              Waypoints: {detourResult.route_waypoints?.map((w) => w.name).join(' ➔ ')}
            </div>
          </div>
        )}
      </div>

      {/* 3. GTFS CORRIDOR BOTTLENECK RANKING */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
        <h3 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
          <AlertOctagon className="w-4 h-4 text-amber-400" />
          <span>GTFS Corridor Bottleneck Ranking</span>
        </h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {bottlenecks.map((c) => (
            <div key={c.corridor_id} className="bg-slate-950 border border-slate-800 p-2.5 rounded-lg text-xs flex items-center justify-between">
              <div>
                <div className="font-semibold text-slate-200">{c.name}</div>
                <div className="text-[10px] text-slate-400">Scheduled: {c.scheduled_time_min}m | Actual: {c.actual_avg_time_min}m (+{c.delay_variance_pct}%)</div>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${c.bottleneck_severity === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}`}>
                {c.bottleneck_severity}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
