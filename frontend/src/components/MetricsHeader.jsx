import React from 'react';
import { Sun, Cloud, Moon, Zap, ShieldCheck, AlertTriangle, Leaf, DollarSign } from 'lucide-react';

export default function MetricsHeader({ state }) {
  if (!state) return null;

  const {
    simulated_time,
    weather,
    is_grid_blackout,
    tariff_rates,
    summary,
    nodes
  } = state;

  const getWeatherIcon = () => {
    if (is_grid_blackout) return <AlertTriangle className="w-5 h-5 text-rose-400 animate-bounce" />;
    if (weather === "Sunny") return <Sun className="w-5 h-5 text-amber-400 animate-spin-slow" />;
    if (weather === "Partly Cloudy") return <Cloud className="w-5 h-5 text-slate-300" />;
    return <Moon className="w-5 h-5 text-indigo-400" />;
  };

  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50 px-6 py-4 shadow-xl">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Brand & Subtitle */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-amber-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Zap className="w-6 h-6 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">
                EcoGrid P2P
              </h1>
              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-1 ${
                is_grid_blackout
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}>
                {is_grid_blackout ? '⚠️ Islanded (Grid Outage)' : '● Microgrid Active'}
              </span>
            </div>
            <p className="text-xs text-slate-400">Decentralized Solar Sharing & Automated Energy Ledger</p>
          </div>
        </div>

        {/* Live Simulation Clock & Weather */}
        <div className="flex items-center gap-3 bg-slate-950/60 border border-slate-800/80 rounded-xl px-4 py-2">
          <div className="p-2 bg-slate-800/80 rounded-lg">
            {getWeatherIcon()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-400 uppercase">Sim Time</span>
              <span className="text-sm font-mono font-bold text-amber-400">{simulated_time}</span>
            </div>
            <div className="text-xs text-slate-300 font-medium">
              {is_grid_blackout ? 'Utility Blackout' : weather}
            </div>
          </div>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-4">
        {/* KPI 1: Solar Gen */}
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Solar Generation</span>
            <Sun className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-lg font-bold text-amber-400 font-mono">
            {summary?.total_generation_kw?.toFixed(2) || '0.00'}{' '}
            <span className="text-xs font-normal text-slate-400">kW</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Load: {summary?.total_consumption_kw?.toFixed(2)} kW
          </div>
        </div>

        {/* KPI 2: Self-Sufficiency */}
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Self-Sufficiency</span>
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-lg font-bold text-emerald-400 font-mono">
            {summary?.self_sufficiency_ratio_pct?.toFixed(1) || '100.0'}%
          </div>
          <div className="w-full bg-slate-800 h-1 rounded-full mt-1.5 overflow-hidden">
            <div
              className="bg-emerald-400 h-full transition-all duration-500"
              style={{ width: `${Math.min(100, summary?.self_sufficiency_ratio_pct || 100)}%` }}
            />
          </div>
        </div>

        {/* KPI 3: Utility Grid Exchange */}
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Utility Grid Flow</span>
            <Zap className="w-3.5 h-3.5 text-sky-400" />
          </div>
          <div className="text-lg font-bold font-mono">
            {summary?.grid_import_kw > 0 ? (
              <span className="text-rose-400">+{summary.grid_import_kw.toFixed(2)} kW</span>
            ) : summary?.grid_export_kw > 0 ? (
              <span className="text-sky-400">-{summary.grid_export_kw.toFixed(2)} kW</span>
            ) : (
              <span className="text-slate-400">0.00 kW</span>
            )}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            {summary?.grid_import_kw > 0 ? 'Importing from Grid' : summary?.grid_export_kw > 0 ? 'Exporting Surplus' : 'Zero Net Grid Dependency'}
          </div>
        </div>

        {/* KPI 4: CO2 Offset */}
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Community CO₂ Offset</span>
            <Leaf className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-lg font-bold text-emerald-400 font-mono">
            {summary?.total_co2_offset_kg?.toFixed(1) || '0.0'}{' '}
            <span className="text-xs font-normal text-slate-400">kg</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Clean Solar Footprint
          </div>
        </div>

        {/* KPI 5: Market Clearing Price */}
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3 col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">P2P Tariff Rate</span>
            <DollarSign className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-lg font-bold text-amber-400 font-mono">
            ${tariff_rates?.p2p_clearing_usd?.toFixed(3)}{' '}
            <span className="text-xs font-normal text-slate-400">/kWh</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            vs Utility ${tariff_rates?.utility_import_usd?.toFixed(2)}/kWh
          </div>
        </div>
      </div>
    </header>
  );
}
