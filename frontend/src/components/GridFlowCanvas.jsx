import React from 'react';
import { Zap, BatteryCharging, Home, ArrowRight, ShieldAlert, Cpu } from 'lucide-react';

export default function GridFlowCanvas({ state }) {
  if (!state) return null;

  const {
    nodes,
    community_battery,
    active_power_flows,
    summary,
    is_grid_blackout
  } = state;

  const alpha = nodes?.house_alpha;
  const beta = nodes?.house_beta;
  const gamma = nodes?.house_gamma;
  const delta = nodes?.house_delta;
  const epsilon = nodes?.house_epsilon;

  // Determine flow speeds or active classes
  const isP2PActive = active_power_flows && active_power_flows.some(f => f.flow_type === 'p2p_share');
  const isBatteryCharging = community_battery?.power_kw > 0.05;
  const isBatteryDischarging = community_battery?.power_kw < -0.05;
  const isGridImporting = summary?.grid_import_kw > 0.05;
  const isGridExporting = summary?.grid_export_kw > 0.05;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-bold text-slate-100">Live Microgrid Power Distribution Topology (5 Households)</h2>
        </div>
        <div className="flex items-center gap-4 text-xs font-medium text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping inline-block" />
            P2P Solar Share
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 inline-block" />
            Storage Flow
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
            Utility Grid
          </span>
        </div>
      </div>

      {/* SVG Canvas for Topology and Animated Power Flows */}
      <div className="relative w-full h-[460px] bg-slate-950/70 border border-slate-800/80 rounded-xl flex items-center justify-center p-4 select-none">
        <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            {/* Animated dash patterns */}
            <pattern id="grid-pattern" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(51, 65, 85, 0.15)" strokeWidth="1" />
            </pattern>
          </defs>

          <rect width="100%" height="100%" fill="url(#grid-pattern)" />

          {/* Wire: Utility Grid -> Central Bus */}
          <line
            x1="50%" y1="10%"
            x2="50%" y2="50%"
            stroke={is_grid_blackout ? "#e11d48" : isGridImporting ? "#f59e0b" : isGridExporting ? "#0ea5e9" : "#334155"}
            strokeWidth={isGridImporting || isGridExporting ? "3" : "2"}
            strokeDasharray={isGridImporting || isGridExporting ? "6 6" : "none"}
            className={isGridImporting || isGridExporting ? "animate-flow" : ""}
          />

          {/* Wire: Alpha Villa (Top-Left) -> Central Bus */}
          <line
            x1="20%" y1="18%"
            x2="50%" y2="50%"
            stroke={alpha?.net_power_kw > 0.05 ? "#10b981" : "#334155"}
            strokeWidth={alpha?.net_power_kw > 0.05 ? "3" : "2"}
            strokeDasharray={alpha?.net_power_kw > 0.05 ? "6 6" : "none"}
            className={alpha?.net_power_kw > 0.05 ? "animate-flow" : ""}
          />

          {/* Wire: Beta Eco-Home (Mid-Left) -> Central Bus */}
          <line
            x1="20%" y1="50%"
            x2="50%" y2="50%"
            stroke={beta?.net_power_kw > 0.05 ? "#10b981" : "#334155"}
            strokeWidth={beta?.net_power_kw > 0.05 ? "3" : "2"}
            strokeDasharray={beta?.net_power_kw > 0.05 ? "6 6" : "none"}
            className={beta?.net_power_kw > 0.05 ? "animate-flow" : ""}
          />

          {/* Wire: Epsilon Smart-Home (Bottom-Left) -> Central Bus */}
          <line
            x1="20%" y1="82%"
            x2="50%" y2="50%"
            stroke={epsilon?.net_power_kw > 0.05 ? "#10b981" : "#334155"}
            strokeWidth={epsilon?.net_power_kw > 0.05 ? "3" : "2"}
            strokeDasharray={epsilon?.net_power_kw > 0.05 ? "6 6" : "none"}
            className={epsilon?.net_power_kw > 0.05 ? "animate-flow" : ""}
          />

          {/* Wire: Central Bus -> Gamma Residence (Top-Right) */}
          <line
            x1="50%" y1="50%"
            x2="80%" y2="28%"
            stroke={gamma?.current_load_kw > 0 ? "#10b981" : "#334155"}
            strokeWidth="3"
            strokeDasharray="6 6"
            className="animate-flow"
          />

          {/* Wire: Central Bus -> Delta Family (Bottom-Right) */}
          <line
            x1="50%" y1="50%"
            x2="80%" y2="72%"
            stroke={delta?.current_load_kw > 0 ? "#10b981" : "#334155"}
            strokeWidth="3"
            strokeDasharray="6 6"
            className="animate-flow"
          />

          {/* Wire: Central Bus -> Community Battery (Bottom Center) */}
          <line
            x1="50%" y1="50%"
            x2="50%" y2="88%"
            stroke={isBatteryCharging ? "#0ea5e9" : isBatteryDischarging ? "#10b981" : "#334155"}
            strokeWidth={isBatteryCharging || isBatteryDischarging ? "3" : "2"}
            strokeDasharray={isBatteryCharging || isBatteryDischarging ? "6 6" : "none"}
            className={isBatteryCharging || isBatteryDischarging ? "animate-flow" : ""}
          />
        </svg>

        {/* Top: Utility Grid Node */}
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center">
          <div className={`px-4 py-2 rounded-xl border flex items-center gap-2 shadow-lg transition-all ${
            is_grid_blackout
              ? 'bg-rose-950/80 border-rose-600/80 text-rose-300'
              : 'bg-slate-900 border-slate-700 text-slate-200'
          }`}>
            <Zap className={`w-4 h-4 ${is_grid_blackout ? 'text-rose-400' : 'text-amber-400'}`} />
            <div className="text-left">
              <div className="text-xs font-bold leading-tight">National Utility Grid</div>
              <div className="text-[10px] font-mono text-slate-400">
                {is_grid_blackout ? 'BLACKOUT / OFFLINE' : `$${state.tariff_rates?.utility_import_usd}/kWh`}
              </div>
            </div>
          </div>
        </div>

        {/* Top-Left: Alpha Villa */}
        <div className="absolute top-[10%] left-[4%] md:left-[8%] z-10 flex flex-col items-center">
          <div className="p-3 bg-slate-900/95 border border-slate-700 rounded-xl shadow-lg w-40 md:w-44 hover:border-amber-400/50 transition">
            <div className="flex items-center justify-between text-xs font-bold text-amber-400 mb-1">
              <span className="truncate">{alpha?.name || 'Alpha Villa'}</span>
              <span className="text-[10px] bg-amber-500/20 px-1.5 py-0.5 rounded text-amber-300 shrink-0 ml-1">Prosumer</span>
            </div>
            <div className="text-[11px] font-mono text-slate-300 space-y-0.5">
              <div className="flex justify-between"><span>Solar:</span> <span className="text-amber-400 font-bold">{alpha?.current_solar_kw.toFixed(2)} kW</span></div>
              <div className="flex justify-between"><span>Load:</span> <span>{alpha?.current_load_kw.toFixed(2)} kW</span></div>
              {Math.abs(alpha?.battery_power_kw || 0) > 0.05 && (
                <div className="flex justify-between text-sky-400">
                  <span>Battery:</span>
                  <span>{alpha.battery_power_kw > 0 ? `+${alpha.battery_power_kw.toFixed(2)} (Chg)` : `${alpha.battery_power_kw.toFixed(2)} (Dis)`}</span>
                </div>
              )}
              <div className="flex justify-between font-bold">
                <span>Net:</span>
                <span className={alpha?.net_power_kw >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                  {alpha?.net_power_kw >= 0 ? `+${alpha?.net_power_kw.toFixed(2)}` : alpha?.net_power_kw.toFixed(2)} kW
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Mid-Left: Beta Eco-Home */}
        <div className="absolute top-[42%] left-[4%] md:left-[8%] z-10 flex flex-col items-center">
          <div className="p-3 bg-slate-900/95 border border-slate-700 rounded-xl shadow-lg w-40 md:w-44 hover:border-amber-400/50 transition">
            <div className="flex items-center justify-between text-xs font-bold text-amber-400 mb-1">
              <span className="truncate">{beta?.name || 'Beta Eco-Home'}</span>
              <span className="text-[10px] bg-amber-500/20 px-1.5 py-0.5 rounded text-amber-300 shrink-0 ml-1">Prosumer</span>
            </div>
            <div className="text-[11px] font-mono text-slate-300 space-y-0.5">
              <div className="flex justify-between"><span>Solar:</span> <span className="text-amber-400 font-bold">{beta?.current_solar_kw.toFixed(2)} kW</span></div>
              <div className="flex justify-between"><span>Load:</span> <span>{beta?.current_load_kw.toFixed(2)} kW</span></div>
              {Math.abs(beta?.battery_power_kw || 0) > 0.05 && (
                <div className="flex justify-between text-sky-400">
                  <span>Battery:</span>
                  <span>{beta.battery_power_kw > 0 ? `+${beta.battery_power_kw.toFixed(2)} (Chg)` : `${beta.battery_power_kw.toFixed(2)} (Dis)`}</span>
                </div>
              )}
              <div className="flex justify-between font-bold">
                <span>Net:</span>
                <span className={beta?.net_power_kw >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                  {beta?.net_power_kw >= 0 ? `+${beta?.net_power_kw.toFixed(2)}` : beta?.net_power_kw.toFixed(2)} kW
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom-Left: Epsilon Smart-Home */}
        <div className="absolute top-[74%] left-[4%] md:left-[8%] z-10 flex flex-col items-center">
          <div className="p-3 bg-slate-900/95 border border-slate-700 rounded-xl shadow-lg w-40 md:w-44 hover:border-amber-400/50 transition">
            <div className="flex items-center justify-between text-xs font-bold text-amber-400 mb-1">
              <span className="truncate">{epsilon?.name || 'Epsilon Smart-Home'}</span>
              <span className="text-[10px] bg-amber-500/20 px-1.5 py-0.5 rounded text-amber-300 shrink-0 ml-1">Prosumer</span>
            </div>
            <div className="text-[11px] font-mono text-slate-300 space-y-0.5">
              <div className="flex justify-between"><span>Solar:</span> <span className="text-amber-400 font-bold">{epsilon?.current_solar_kw.toFixed(2)} kW</span></div>
              <div className="flex justify-between"><span>Load:</span> <span>{epsilon?.current_load_kw.toFixed(2)} kW</span></div>
              {Math.abs(epsilon?.battery_power_kw || 0) > 0.05 && (
                <div className="flex justify-between text-sky-400">
                  <span>Battery:</span>
                  <span>{epsilon.battery_power_kw > 0 ? `+${epsilon.battery_power_kw.toFixed(2)} (Chg)` : `${epsilon.battery_power_kw.toFixed(2)} (Dis)`}</span>
                </div>
              )}
              <div className="flex justify-between font-bold">
                <span>Net:</span>
                <span className={epsilon?.net_power_kw >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                  {epsilon?.net_power_kw >= 0 ? `+${epsilon?.net_power_kw.toFixed(2)}` : epsilon?.net_power_kw.toFixed(2)} kW
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Center: Community AC Distribution Bus */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
          <div className="w-28 h-28 rounded-full bg-slate-900/95 border-2 border-emerald-400/80 shadow-2xl shadow-emerald-500/20 flex flex-col items-center justify-center p-2 text-center backdrop-blur-md">
            <Zap className="w-5 h-5 text-emerald-400 mb-0.5 animate-pulse" />
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-300 leading-tight">Microgrid Bus</div>
            <div className="text-xs font-mono font-bold text-emerald-400">
              {summary?.total_generation_kw?.toFixed(1)} kW
            </div>
            <div className="text-[9px] text-slate-400">Shared Pool</div>
          </div>
        </div>

        {/* Top-Right: Gamma Residence */}
        <div className="absolute top-[20%] right-[8%] md:right-[12%] z-10 flex flex-col items-center">
          <div className="p-3 bg-slate-900/95 border border-slate-700 rounded-xl shadow-lg w-44 hover:border-sky-400/50 transition">
            <div className="flex items-center justify-between text-xs font-bold text-sky-400 mb-1">
              <span>{gamma?.name || 'Gamma Residence'}</span>
              <span className="text-[10px] bg-sky-500/20 px-1.5 py-0.5 rounded text-sky-300">Consumer</span>
            </div>
            <div className="text-[11px] font-mono text-slate-300 space-y-0.5">
              <div className="flex justify-between"><span>Solar:</span> <span className="text-slate-400">0.00 kW</span></div>
              <div className="flex justify-between"><span>Load:</span> <span>{gamma?.current_load_kw.toFixed(2)} kW</span></div>
              <div className="flex justify-between font-bold">
                <span>P2P In:</span>
                <span className="text-emerald-400 font-bold">
                  {Math.abs(gamma?.net_power_kw || 0).toFixed(2)} kW
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom-Right: Delta Family (EV) */}
        <div className="absolute top-[65%] right-[8%] md:right-[12%] z-10 flex flex-col items-center">
          <div className="p-3 bg-slate-900/95 border border-slate-700 rounded-xl shadow-lg w-44 hover:border-sky-400/50 transition">
            <div className="flex items-center justify-between text-xs font-bold text-sky-400 mb-1">
              <span>{delta?.name || 'Delta Family (EV)'}</span>
              <span className="text-[10px] bg-sky-500/20 px-1.5 py-0.5 rounded text-sky-300">High Load</span>
            </div>
            <div className="text-[11px] font-mono text-slate-300 space-y-0.5">
              <div className="flex justify-between"><span>Solar:</span> <span className="text-slate-400">0.00 kW</span></div>
              <div className="flex justify-between"><span>Load:</span> <span className="text-rose-300">{delta?.current_load_kw.toFixed(2)} kW</span></div>
              <div className="flex justify-between font-bold">
                <span>P2P In:</span>
                <span className="text-emerald-400 font-bold">
                  {Math.abs(delta?.net_power_kw || 0).toFixed(2)} kW
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom-Center: Shared Community Battery Hub */}
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center">
          <div className="px-4 py-2 bg-slate-900/95 border border-sky-500/40 rounded-xl shadow-lg flex items-center gap-3">
            <BatteryCharging className="w-5 h-5 text-sky-400" />
            <div className="text-left">
              <div className="text-xs font-bold text-slate-200">Community Battery Buffer (25 kWh)</div>
              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="text-sky-400 font-bold">{community_battery?.soc_pct}% SoC</span>
                <span className="text-slate-400">
                  {isBatteryCharging ? `+${community_battery?.power_kw.toFixed(1)} kW (Charging)` :
                   isBatteryDischarging ? `${community_battery?.power_kw.toFixed(1)} kW (Discharging)` : 'Standby'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
