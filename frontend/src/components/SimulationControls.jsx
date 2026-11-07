import React from 'react';
import { Sliders, Sun, Cloud, Moon, ZapOff, Play, FastForward, ShieldAlert } from 'lucide-react';

export default function SimulationControls({
  state,
  onSelectScenario,
  onToggleBlackout,
  onUpdateSpeed
}) {
  if (!state) return null;

  const scenarios = [
    { id: 'peak_solar', label: 'Peak Solar Noon', icon: Sun, color: 'text-amber-400 border-amber-500/30' },
    { id: 'cloudy_afternoon', label: 'Cloudy Afternoon', icon: Cloud, color: 'text-slate-300 border-slate-700' },
    { id: 'night_blackout', label: 'Night Grid Outage', icon: ZapOff, color: 'text-rose-400 border-rose-500/30' },
    { id: 'morning_startup', label: 'Morning Startup', icon: Moon, color: 'text-indigo-400 border-indigo-500/30' }
  ];

  const speeds = [1, 10, 60, 120];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <Sliders className="w-5 h-5 text-amber-400" />
        <h2 className="text-base font-bold text-slate-100">Microgrid Scenario & Simulation Controls</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Preset Scenarios */}
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Preset Test Scenarios
          </label>
          <div className="grid grid-cols-2 gap-2">
            {scenarios.map(s => {
              const Icon = s.icon;
              return (
                <button
                  key={s.id}
                  onClick={() => onSelectScenario(s.id)}
                  className={`flex items-center gap-2 p-2.5 rounded-xl border bg-slate-950/60 hover:bg-slate-800/80 text-xs font-medium transition text-left ${s.color}`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span className="leading-tight">{s.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Master Grid Outage Resilience Switch */}
        <div className="flex flex-col justify-between">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              National Grid Resilience
            </label>
            <p className="text-xs text-slate-400 mb-3">
              Simulate sudden blackout from utility grid. Microgrid automatically islands and preserves neighborhood power.
            </p>
          </div>
          <button
            onClick={() => onToggleBlackout(!state.is_grid_blackout)}
            className={`w-full py-2.5 px-4 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition ${
              state.is_grid_blackout
                ? 'bg-rose-500 text-white border-rose-400 shadow-lg shadow-rose-500/30 animate-pulse'
                : 'bg-slate-950/60 text-slate-300 border-slate-700 hover:border-slate-500'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            <span>
              {state.is_grid_blackout ? 'Utility Grid Down (Islanded Mode)' : 'Simulate Utility Blackout'}
            </span>
          </button>
        </div>

        {/* Time Speed Multiplier */}
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Simulation Clock Speed
          </label>
          <div className="grid grid-cols-4 gap-2 mb-2">
            {speeds.map(sp => (
              <button
                key={sp}
                onClick={() => onUpdateSpeed(sp)}
                className="py-2 rounded-xl border border-slate-700 bg-slate-950/60 hover:bg-slate-800 text-xs font-mono font-semibold text-slate-300 transition text-center"
              >
                {sp}x
              </button>
            ))}
          </div>
          <span className="text-[11px] text-slate-400 block text-center">
            60x: 1 real second = 1 simulation minute
          </span>
        </div>
      </div>
    </div>
  );
}
