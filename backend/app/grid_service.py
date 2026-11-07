import asyncio
import json
import logging
import os
import sys
from typing import Set, Dict, Any, List
from fastapi import WebSocket

# Ensure simulation module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from simulation.grid_simulator import MicrogridEnvironment
from backend.app.trading_engine import TradingEngine
from backend.app.database import record_trade, get_recent_trades

logger = logging.getLogger("microgrid_service")

class GridService:
    def __init__(self):
        self.simulator = MicrogridEnvironment()
        self.engine = TradingEngine()
        self.active_connections: Set[WebSocket] = set()
        self.running = False
        self.task: asyncio.Task = None
        self.recent_trades_cache: List[Dict[str, Any]] = []

    async def connect_client(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        # Send immediate initial state
        initial_state = await self.get_current_full_state()
        await websocket.send_text(json.dumps(initial_state))

    def disconnect_client(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        if not self.active_connections:
            return
        payload = json.dumps(data)
        stale_connections = set()
        for ws in self.active_connections:
            try:
                await ws.send_text(payload)
            except Exception:
                stale_connections.add(ws)
        for dead_ws in stale_connections:
            self.active_connections.discard(dead_ws)

    async def get_current_full_state(self) -> Dict[str, Any]:
        sim_state = self.simulator.get_state()
        total_load = sum(n.current_load_kw for n in self.simulator.nodes.values())
        grid_import = self.simulator.grid_import_kw
        self_sufficiency = 100.0
        if total_load > 0:
            self_sufficiency = max(0.0, min(100.0, ((total_load - grid_import) / total_load) * 100.0))

        return {
            "timestamp": sim_state["timestamp"],
            "simulated_time": sim_state["simulated_time"],
            "simulated_hour": sim_state["simulated_hour"],
            "weather": sim_state["weather"],
            "weather_factor": sim_state["weather_factor"],
            "is_grid_blackout": sim_state["is_grid_blackout"],
            "tariff_rates": {
                "utility_import_usd": self.engine.utility_import_tariff,
                "feed_in_export_usd": self.engine.feed_in_export_tariff,
                "p2p_clearing_usd": self.engine.p2p_clearing_price
            },
            "community_battery": sim_state["community_battery"],
            "summary": {
                **sim_state["summary"],
                "grid_import_kw": self.simulator.grid_import_kw,
                "grid_export_kw": self.simulator.grid_export_kw,
                "self_sufficiency_ratio_pct": round(self_sufficiency, 1),
                "total_co2_offset_kg": round(self.engine.total_co2_offset_kg, 2)
            },
            "nodes": sim_state["nodes"],
            "recent_trades": self.recent_trades_cache[:15],
            "active_power_flows": []
        }

    async def simulation_loop(self):
        logger.info("Microgrid simulation loop started.")
        while self.running:
            try:
                step_dt = 1.0 # 1 real-time second
                # 1. Advance physics simulation
                self.simulator.step(step_dt)

                # 2. Run P2P Market Matching
                new_trades, active_flows, grid_summary = self._do_match(step_dt)

                # Record any new trades to SQLite and memory cache
                for trade in new_trades:
                    await record_trade(trade)
                    self.recent_trades_cache.insert(0, trade)
                if len(self.recent_trades_cache) > 50:
                    self.recent_trades_cache = self.recent_trades_cache[:50]

                # 3. Assemble complete live state
                sim_state = self.simulator.get_state()
                full_payload = {
                    "timestamp": sim_state["timestamp"],
                    "simulated_time": sim_state["simulated_time"],
                    "simulated_hour": sim_state["simulated_hour"],
                    "weather": sim_state["weather"],
                    "weather_factor": sim_state["weather_factor"],
                    "is_grid_blackout": sim_state["is_grid_blackout"],
                    "tariff_rates": {
                        "utility_import_usd": self.engine.utility_import_tariff,
                        "feed_in_export_usd": self.engine.feed_in_export_tariff,
                        "p2p_clearing_usd": self.engine.p2p_clearing_price
                    },
                    "community_battery": {
                        "capacity_kwh": self.simulator.community_battery_kwh,
                        "soc_pct": round(self.simulator.community_battery_soc, 1),
                        "power_kw": round(self.simulator.community_battery_flow_kw, 2)
                    },
                    "summary": grid_summary,
                    "nodes": sim_state["nodes"],
                    "recent_trades": self.recent_trades_cache[:15],
                    "active_power_flows": active_flows
                }

                # 4. Broadcast to WebSockets
                await self.broadcast(full_payload)

            except Exception as e:
                logger.error(f"Error in simulation loop: {e}", exc_info=True)

            await asyncio.sleep(1.0)

    def _do_match(self, step_dt: float):
        batt_dict = {
            "capacity_kwh": self.simulator.community_battery_kwh,
            "soc_pct": self.simulator.community_battery_soc,
            "power_kw": self.simulator.community_battery_flow_kw
        }
        effective_dt = step_dt * self.simulator.time_speed_multiplier
        trades, flows, summary = self.engine.match_interval(
            nodes=self.simulator.nodes,
            community_battery=batt_dict,
            is_grid_blackout=self.simulator.is_grid_blackout,
            dt_seconds=effective_dt
        )
        self.simulator.community_battery_soc = batt_dict["soc_pct"]
        self.simulator.community_battery_flow_kw = batt_dict.get("power_kw", 0.0)
        self.simulator.grid_import_kw = summary["grid_import_kw"]
        self.simulator.grid_export_kw = summary["grid_export_kw"]
        return trades, flows, summary

    def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self.simulation_loop())

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()

# Global singleton
grid_service = GridService()
