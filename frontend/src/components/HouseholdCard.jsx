import React, { useState } from 'react';
import { Sun, Home, Battery, Power, Wallet, ArrowUpRight, ArrowDownLeft, Radio } from 'lucide-react';

export default function HouseholdCard({ node, onToggleRelay }) {
  const [loadingRelay, setLoadingRelay] = useState(false);

  if (!node) return null;

  const handleRelayClick = async () => {
    try {
      setLoadingRelay(true);
      await onToggleRelay(node.node_id, !node.grid_relay_active);
    } finally {
      setLoadingRelay(false);
    }
  };

  const isProsumer = node.solar_capacity_kw > 0;
  const isSurplus = node.net_power_kw >= 0;

  return (
    <div className={`rounded-2xl border transition-all duration-300 p-5 ${
      !node.grid_relay_active
        ? 'bg-slate-950/40 border-rose-900/50 opacity-75'
        : isProsumer
        ? 'bg-slate-900/90 border-slate-800 hover:border-amber-500/40 shadow-lg'
        : 'bg-slate-900/90 border-slate-800 hover:border-sky-500/40 shadow-lg'
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-bold text-slate-100 text-sm">{node.name}</h3>
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
              isProsumer
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
            }`}>
              {isProsumer ? `${node.solar_capacity_kw} kW Solar` : 'Consumer'}
            </span>
            {node.is_hardware_linked && (
              <span className="text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-1.5 py-0.5 rounded-full flex items-center gap-1">
                <Radio className="w-2.5 h-2.5 animate-pulse text-purple-400" />
                <span>IoT Node (ESP32)</span>
              </span>
            )}
          </div>
          <span className="text-xs text-slate-400 font-mono">ID: {node.node_id}</span>
        </div>

        {/* Smart Meter Cut-Off Relay Button */}
        <button
          onClick={handleRelayClick}
          disabled={loadingRelay}
          title={node.grid_relay_active ? "Disconnect from Community Bus" : "Reconnect to Community Bus"}
          className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
            node.grid_relay_active
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20'
          }`}
        >
          <Power className="w-3 h-3" />
          <span>{node.grid_relay_active ? 'Online' : 'Cutoff'}</span>
        </button>
      </div>

      {/* Main Gauges */}
      <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-800/80 mb-4 text-center">
        <div>
          <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
            <Sun className="w-3 h-3 text-amber-400" /> Gen
          </div>
          <div className="text-sm font-bold font-mono text-amber-400 mt-0.5">
            {node.current_solar_kw.toFixed(2)}
          </div>
          <div className="text-[9px] text-slate-400">kW</div>
        </div>

        <div>
          <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
            <Home className="w-3 h-3 text-slate-400" /> Load
          </div>
          <div className="text-sm font-bold font-mono text-slate-200 mt-0.5">
            {node.current_load_kw.toFixed(2)}
          </div>
          <div className="text-[9px] text-slate-400">kW</div>
        </div>

        <div>
          <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
            {isSurplus ? (
              <ArrowUpRight className="w-3 h-3 text-emerald-400" />
            ) : (
              <ArrowDownLeft className="w-3 h-3 text-rose-400" />
            )}
            Net
          </div>
          <div className={`text-sm font-bold font-mono mt-0.5 ${isSurplus ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isSurplus ? `+${node.net_power_kw.toFixed(2)}` : node.net_power_kw.toFixed(2)}
          </div>
          <div className="text-[9px] text-slate-400">kW</div>
        </div>
      </div>

      {/* Local Battery (if installed) */}
      {node.battery_capacity_kwh > 0 && (
        <div className="mb-4 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
          <div className="flex justify-between items-center text-xs mb-1.5">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Battery className="w-3.5 h-3.5 text-sky-400" />
              Home Battery ({node.battery_capacity_kwh} kWh)
            </span>
            <span className="font-mono font-bold text-sky-400">{node.battery_soc_pct}%</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className="bg-sky-400 h-full transition-all duration-300"
              style={{ width: `${node.battery_soc_pct}%` }}
            />
          </div>
        </div>
      )}

      {/* Wallet Balance & Cumulative Metrics */}
      <div className="flex items-center justify-between text-xs pt-1">
        <div className="flex items-center gap-1.5 text-slate-300">
          <Wallet className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-slate-400">Credits:</span>
          <span className="font-mono font-bold text-amber-400">${node.wallet_balance_credits.toFixed(2)}</span>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">
          Gen: {node.total_solar_kwh.toFixed(1)} kWh
        </div>
      </div>
    </div>
  );
}
