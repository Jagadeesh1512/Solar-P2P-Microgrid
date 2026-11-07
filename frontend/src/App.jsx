import React, { useState, useEffect, useRef } from 'react';
import MetricsHeader from './components/MetricsHeader';
import GridFlowCanvas from './components/GridFlowCanvas';
import HouseholdCard from './components/HouseholdCard';
import LedgerTable from './components/LedgerTable';
import SimulationControls from './components/SimulationControls';
import { Sparkles, Globe, Shield, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

export default function App() {
  const [state, setState] = useState(null);
  const [connected, setConnected] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          setConnected(true);
          setErrorMsg(null);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setState(data);
          } catch (e) {
            console.error("Failed to parse WS state", e);
          }
        };

        ws.onerror = (err) => {
          console.warn("WebSocket error, retrying...", err);
        };

        ws.onclose = () => {
          setConnected(false);
          // Try reconnect after 2 seconds
          reconnectTimeout = setTimeout(connectWebSocket, 2000);
        };
      } catch (err) {
        console.error("Connection failed", err);
        reconnectTimeout = setTimeout(connectWebSocket, 2000);
      }
    };

    connectWebSocket();

    // Fallback initial poll
    fetch(`${API_BASE}/api/state`)
      .then(res => res.json())
      .then(data => setState(data))
      .catch(err => console.log("Initial state fetch waiting for server...", err));

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  const handleSelectScenario = async (scenario) => {
    try {
      await fetch(`${API_BASE}/api/scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario })
      });
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleBlackout = async (active) => {
    try {
      await fetch(`${API_BASE}/api/blackout?active=${active}`, {
        method: 'POST'
      });
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpdateSpeed = async (multiplier) => {
    try {
      await fetch(`${API_BASE}/api/speed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ multiplier })
      });
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleRelay = async (node_id, relay_active) => {
    try {
      await fetch(`${API_BASE}/api/relay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_id, relay_active })
      });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Header & Metrics Bar */}
      <MetricsHeader state={state} />

      {/* Connection Indicator banner if offline */}
      {!connected && (
        <div className="bg-amber-500/10 border-b border-amber-500/30 text-amber-400 text-xs px-4 py-2 text-center flex items-center justify-center gap-2">
          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          <span>Connecting to backend microgrid engine at {API_BASE}...</span>
        </div>
      )}

      {/* Main Grid Workspace */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-6 space-y-6">
        {/* Topology Power Flow Canvas */}
        <GridFlowCanvas state={state} />

        {/* Community Households Grid */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-200">Community Smart Meter Nodes</h2>
            <span className="text-xs text-slate-400">
              Interactive relays & individual prosumer telemetry
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {state?.nodes &&
              Object.values(state.nodes).map((node) => (
                <HouseholdCard
                  key={node.node_id}
                  node={node}
                  onToggleRelay={handleToggleRelay}
                />
              ))}
          </div>
        </div>

        {/* Simulation Controls Panel */}
        <SimulationControls
          state={state}
          onSelectScenario={handleSelectScenario}
          onToggleBlackout={handleToggleBlackout}
          onUpdateSpeed={handleUpdateSpeed}
        />

        {/* Immutable Trading Ledger */}
        <LedgerTable trades={state?.recent_trades} />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/60 px-6 py-6 mt-12 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>
              Decentralized Community Solar Microgrid with P2P Automated Clearing
            </span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              UN SDG 7: Clean Energy
            </span>
            <span className="px-2.5 py-1 rounded-md bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium">
              UN SDG 11: Sustainable Cities
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
