"""
Peer-to-Peer Energy Matching and Settlement Engine
Implements dynamic double-sided matching between localized solar prosumers and consumers.
"""

from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any

class TradingEngine:
    def __init__(
        self,
        utility_import_tariff: float = 0.20, # $/kWh to buy from utility
        feed_in_export_tariff: float = 0.06  # $/kWh to sell to utility
    ):
        self.utility_import_tariff = utility_import_tariff
        self.feed_in_export_tariff = feed_in_export_tariff
        # P2P Mid-Market clearing price provides economic incentive for both parties
        self.p2p_clearing_price = round(
            (self.utility_import_tariff + self.feed_in_export_tariff) / 2.0, 3
        )
        self.total_co2_offset_kg = 0.0 # Standard grid emission factor: ~0.4 kg CO2 / kWh solar used

    def match_interval(
        self,
        nodes: Dict[str, Any],
        community_battery: Dict[str, Any],
        is_grid_blackout: bool,
        dt_seconds: float
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, float]]:
        """
        Executes P2P matching for a simulation interval.
        Returns:
            - new_trades: List of executed trades to record in DB
            - active_flows: Visual flow links (source, target, power_kw, type)
            - grid_metrics: Grid import/export and community battery updates
        """
        dt_hours = dt_seconds / 3600.0
        new_trades: List[Dict[str, Any]] = []
        active_flows: List[Dict[str, Any]] = []

        # 1. Identify sellers (surplus) and buyers (deficit)
        sellers = []
        buyers = []

        for nid, node in nodes.items():
            if not node.grid_relay_active:
                continue # Node is disconnected / islanded
            
            if node.net_power_kw > 0.05:
                sellers.append({
                    "id": nid,
                    "name": node.name,
                    "surplus_kw": node.net_power_kw,
                    "avail_kwh": node.net_power_kw * dt_hours
                })
            elif node.net_power_kw < -0.05:
                deficit_kw = abs(node.net_power_kw)
                buyers.append({
                    "id": nid,
                    "name": node.name,
                    "deficit_kw": deficit_kw,
                    "demand_kwh": deficit_kw * dt_hours
                })

        # 2. P2P Direct Matching (Pro-rata / Merit Order)
        total_p2p_traded_kw = 0.0
        
        for seller in sellers:
            if seller["avail_kwh"] <= 0.0001:
                continue

            for buyer in buyers:
                if buyer["demand_kwh"] <= 0.0001:
                    continue

                # Energy matched in this transaction
                matched_kwh = min(seller["avail_kwh"], buyer["demand_kwh"])
                if matched_kwh <= 0.00001:
                    continue

                matched_kw = matched_kwh / dt_hours
                seller["avail_kwh"] -= matched_kwh
                buyer["demand_kwh"] -= matched_kwh
                total_p2p_traded_kw += matched_kw

                # Financial Calculations
                total_cost = round(matched_kwh * self.p2p_clearing_price, 4)
                buyer_savings = round(matched_kwh * (self.utility_import_tariff - self.p2p_clearing_price), 4)
                seller_profit = round(matched_kwh * (self.p2p_clearing_price - self.feed_in_export_tariff), 4)

                # Update wallet balances
                nodes[buyer["id"]].wallet_balance_credits -= total_cost
                nodes[seller["id"]].wallet_balance_credits += total_cost
                nodes[seller["id"]].total_p2p_exported_kwh += matched_kwh
                nodes[buyer["id"]].total_p2p_imported_kwh += matched_kwh

                now_iso = datetime.now(timezone.utc).isoformat()
                trade_record = {
                    "timestamp": now_iso,
                    "seller_id": seller["id"],
                    "seller_name": seller["name"],
                    "buyer_id": buyer["id"],
                    "buyer_name": buyer["name"],
                    "energy_kwh": round(matched_kwh, 4),
                    "clearing_price_usd": self.p2p_clearing_price,
                    "total_cost_usd": total_cost,
                    "buyer_savings_usd": buyer_savings,
                    "seller_extra_profit_usd": seller_profit
                }
                new_trades.append(trade_record)

                # Record live visual flow
                active_flows.append({
                    "source": seller["id"],
                    "target": buyer["id"],
                    "power_kw": round(matched_kw, 2),
                    "flow_type": "p2p_share"
                })

        # 3. Community Central Battery Charging / Discharging
        unmatched_surplus_kwh = sum(s["avail_kwh"] for s in sellers if s["avail_kwh"] > 0)
        unmatched_deficit_kwh = sum(b["demand_kwh"] for b in buyers if b["demand_kwh"] > 0)
        
        community_batt_capacity = community_battery["capacity_kwh"]
        community_batt_soc = community_battery["soc_pct"]
        comm_batt_power_kw = 0.0

        if unmatched_surplus_kwh > 0:
            # Store leftover solar into community shared battery
            room_kwh = community_batt_capacity * (0.98 - (community_batt_soc / 100.0))
            if room_kwh > 0:
                stored_kwh = min(unmatched_surplus_kwh, room_kwh)
                community_batt_soc += (stored_kwh / community_batt_capacity) * 100.0
                unmatched_surplus_kwh -= stored_kwh
                comm_batt_power_kw = stored_kwh / dt_hours
                active_flows.append({
                    "source": "solar_surplus",
                    "target": "community_battery",
                    "power_kw": round(comm_batt_power_kw, 2),
                    "flow_type": "storage_charge"
                })

        elif unmatched_deficit_kwh > 0:
            # Discharge community shared battery to cover neighborhood deficit
            available_batt_kwh = community_batt_capacity * ((community_batt_soc - 15.0) / 100.0)
            if available_batt_kwh > 0:
                discharged_kwh = min(unmatched_deficit_kwh, available_batt_kwh)
                community_batt_soc -= (discharged_kwh / community_batt_capacity) * 100.0
                unmatched_deficit_kwh -= discharged_kwh
                comm_batt_power_kw = -(discharged_kwh / dt_hours)
                active_flows.append({
                    "source": "community_battery",
                    "target": "neighborhood_load",
                    "power_kw": round(abs(comm_batt_power_kw), 2),
                    "flow_type": "storage_discharge"
                })

        community_battery["soc_pct"] = max(10.0, min(100.0, community_batt_soc))
        community_battery["power_kw"] = comm_batt_power_kw

        # 4. Main Utility Grid Interaction (Export or Import)
        grid_export_kw = 0.0
        grid_import_kw = 0.0

        if not is_grid_blackout:
            if unmatched_surplus_kwh > 0:
                grid_export_kw = unmatched_surplus_kwh / dt_hours
                active_flows.append({
                    "source": "microgrid",
                    "target": "utility_grid",
                    "power_kw": round(grid_export_kw, 2),
                    "flow_type": "grid_export"
                })
            elif unmatched_deficit_kwh > 0:
                grid_import_kw = unmatched_deficit_kwh / dt_hours
                active_flows.append({
                    "source": "utility_grid",
                    "target": "microgrid",
                    "power_kw": round(grid_import_kw, 2),
                    "flow_type": "grid_import"
                })

        # 5. CO2 and Sustainability Metrics
        total_gen_kw = sum(n.current_solar_kw for n in nodes.values())
        total_load_kw = sum(n.current_load_kw for n in nodes.values())
        solar_consumed_locally_kwh = max(0.0, (total_load_kw - grid_import_kw)) * dt_hours
        self.total_co2_offset_kg += solar_consumed_locally_kwh * 0.42 # 0.42 kg CO2 per kWh solar

        self_sufficiency = 100.0
        if total_load_kw > 0:
            self_sufficiency = max(0.0, min(100.0, ((total_load_kw - grid_import_kw) / total_load_kw) * 100.0))

        grid_summary = {
            "total_generation_kw": round(total_gen_kw, 2),
            "total_consumption_kw": round(total_load_kw, 2),
            "net_community_power_kw": round(total_gen_kw - total_load_kw, 2),
            "grid_import_kw": round(grid_import_kw, 2),
            "grid_export_kw": round(grid_export_kw, 2),
            "self_sufficiency_ratio_pct": round(self_sufficiency, 1),
            "total_co2_offset_kg": round(self.total_co2_offset_kg, 2)
        }

        return new_trades, active_flows, grid_summary
