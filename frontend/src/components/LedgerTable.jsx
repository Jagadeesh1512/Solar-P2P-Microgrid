import React from 'react';
import { History, ArrowRight, CheckCircle2, TrendingUp, PiggyBank } from 'lucide-react';

export default function LedgerTable({ trades }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-bold text-slate-100">P2P Smart Energy Trading Ledger</h2>
        </div>
        <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full font-mono flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5" /> Real-time Clearing
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/60 text-slate-400 uppercase font-mono text-[10px] tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3">Time</th>
              <th className="py-2.5 px-3">Seller (Prosumer)</th>
              <th className="py-2.5 px-3 text-center">Flow</th>
              <th className="py-2.5 px-3">Buyer (Consumer)</th>
              <th className="py-2.5 px-3 text-right">Energy (kWh)</th>
              <th className="py-2.5 px-3 text-right">Tariff ($/kWh)</th>
              <th className="py-2.5 px-3 text-right">Settled Amount</th>
              <th className="py-2.5 px-3 text-right">Mutual Benefit</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {(!trades || trades.length === 0) ? (
              <tr>
                <td colSpan="8" className="py-8 text-center text-slate-500">
                  Waiting for active generation and trade matching...
                </td>
              </tr>
            ) : (
              trades.slice(0, 10).map((t, index) => {
                const timeStr = t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : '--:--:--';
                return (
                  <tr key={t.id || index} className="hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-3 text-slate-400">{timeStr}</td>
                    <td className="py-2.5 px-3 font-semibold text-amber-400">
                      {t.seller_name || t.seller_id}
                    </td>
                    <td className="py-2.5 px-3 text-center text-slate-500">
                      <ArrowRight className="w-3.5 h-3.5 inline text-emerald-400" />
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-sky-400">
                      {t.buyer_name || t.buyer_id}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-slate-100">
                      {t.energy_kwh.toFixed(4)}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-300">
                      ${t.clearing_price_usd.toFixed(3)}
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-amber-300">
                      ${t.total_cost_usd.toFixed(4)}
                    </td>
                    <td className="py-2.5 px-3 text-right text-emerald-400 font-sans text-[11px]">
                      <span title={`Buyer saved $${t.buyer_savings_usd.toFixed(4)}, Seller made +$${t.seller_extra_profit_usd.toFixed(4)} extra`}>
                        +${(t.buyer_savings_usd + t.seller_extra_profit_usd).toFixed(4)} saved
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
