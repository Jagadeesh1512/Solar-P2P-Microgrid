"""
Multi-Node Community Solar Microgrid Simulator
Simulates a neighborhood microgrid with multiple prosumer and consumer households,
battery storage units, weather variations, diurnal solar curves, and main grid interaction.
"""

import math
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

class HouseholdNode:
    def __init__(
        self,
        node_id: str,
        name: str,
        solar_capacity_kw: float,
        base_load_kw: float,
        battery_capacity_kwh: float = 0.0,
        initial_soc_pct: float = 50.0,
        has_ev: bool = False
    ):
        self.node_id = node_id
        self.name = name
        self.solar_capacity_kw = solar_capacity_kw
        self.base_load_kw = base_load_kw
        self.battery_capacity_kwh = battery_capacity_kwh
        self.battery_soc_pct = initial_soc_pct
        self.has_ev = has_ev
        
        # Live state
        self.current_solar_kw = 0.0
        self.current_load_kw = 0.0
        self.net_power_kw = 0.0 # Positive = Surplus, Negative = Deficit
        self.battery_power_kw = 0.0 # Positive = Charging, Negative = Discharging
        self.grid_relay_active = True
        self.wallet_balance_credits = 100.0 # Initial P2P token/currency balance
        self.total_solar_generated_kwh = 0.0
        self.total_consumed_kwh = 0.0
        self.total_p2p_exported_kwh = 0.0
        self.total_p2p_imported_kwh = 0.0
        self.is_hardware_linked = False
        self.last_hardware_telemetry_time = 0.0
        self.hardware_timeout_seconds = 90.0

    def update_physics(
        self,
        time_of_day_hours: float,
        weather_factor: float,
        dt_seconds: float
    ):
        """
        Updates generation, load, and local battery dynamics for this node.
        weather_factor: 1.0 (clear sky), 0.5 (cloudy), 0.1 (stormy)
        """
        dt_hours = dt_seconds / 3600.0

        # If connected to a live physical IoT node (e.g. Wokwi ESP32), sensor readings take precedence
        if self.is_hardware_linked:
            # 90-second heartbeat window: survives browser background tab throttling,
            # but gracefully resets when hardware is permanently powered down
            if time.time() - self.last_hardware_telemetry_time < self.hardware_timeout_seconds:
                self.net_power_kw = round(self.current_solar_kw - self.current_load_kw, 3)
                self.total_solar_generated_kwh += self.current_solar_kw * dt_hours
                self.total_consumed_kwh += self.current_load_kw * dt_hours
                return
            else:
                self.is_hardware_linked = False

        # 1. Solar Generation (Bell curve between 06:00 and 18:00)
        if 6.0 <= time_of_day_hours <= 18.0 and self.solar_capacity_kw > 0:
            sun_phase = math.sin((time_of_day_hours - 6.0) / 12.0 * math.pi)
            raw_gen = self.solar_capacity_kw * max(0.0, sun_phase) * weather_factor
            # Small random irradiance flutter
            gen_noise = random.uniform(0.95, 1.05)
            self.current_solar_kw = round(raw_gen * gen_noise, 3)
        else:
            self.current_solar_kw = 0.0

        # 2. Consumption / Household Load (Diurnal profile + appliance spikes)
        # Peak load in morning (7-9am) and evening (18-22pm)
        morning_peak = 1.6 * math.exp(-0.5 * ((time_of_day_hours - 8.0) / 1.5) ** 2)
        evening_peak = 2.2 * math.exp(-0.5 * ((time_of_day_hours - 20.0) / 2.0) ** 2)
        daily_multiplier = 0.7 + morning_peak + evening_peak
        
        # Base random jitter
        load_jitter = random.uniform(0.85, 1.25)
        load = self.base_load_kw * daily_multiplier * load_jitter

        # EV charging surge simulation (e.g. night or evening)
        if self.has_ev and 19.0 <= time_of_day_hours <= 23.0 and random.random() < 0.35:
            load += 3.3 # Level 2 EV charging boost
        
        self.current_load_kw = round(load, 3)

        # 3. Net household power before local battery
        raw_net = self.current_solar_kw - self.current_load_kw

        # 4. Local Battery Logic (Self-consumption priority)
        dt_hours = dt_seconds / 3600.0
        self.battery_power_kw = 0.0

        if self.battery_capacity_kwh > 0:
            if raw_net > 0:
                # Excess solar -> Charge local battery if not full (< 98%)
                charge_room_kwh = self.battery_capacity_kwh * (0.98 - (self.battery_soc_pct / 100.0))
                if charge_room_kwh > 0:
                    max_charge_rate_kw = min(raw_net, 3.0) # max 3kW charge rate
                    energy_to_add_kwh = min(max_charge_rate_kw * dt_hours, charge_room_kwh)
                    actual_charge_kw = energy_to_add_kwh / dt_hours
                    self.battery_soc_pct += (energy_to_add_kwh / self.battery_capacity_kwh) * 100.0
                    self.battery_power_kw = round(actual_charge_kw, 3)
                    raw_net -= actual_charge_kw
            elif raw_net < 0:
                # Deficit -> Discharge local battery if not depleted (> 15%)
                deficit_kw = abs(raw_net)
                available_energy_kwh = self.battery_capacity_kwh * ((self.battery_soc_pct - 15.0) / 100.0)
                if available_energy_kwh > 0:
                    max_discharge_rate_kw = min(deficit_kw, 3.0)
                    energy_to_draw_kwh = min(max_discharge_rate_kw * dt_hours, available_energy_kwh)
                    actual_discharge_kw = energy_to_draw_kwh / dt_hours
                    self.battery_soc_pct -= (energy_to_draw_kwh / self.battery_capacity_kwh) * 100.0
                    self.battery_power_kw = -round(actual_discharge_kw, 3)
                    raw_net += actual_discharge_kw

        self.battery_soc_pct = max(10.0, min(100.0, round(self.battery_soc_pct, 1)))
        self.net_power_kw = round(raw_net, 3)

        # Accumulators
        self.total_solar_generated_kwh += self.current_solar_kw * dt_hours
        self.total_consumed_kwh += self.current_load_kw * dt_hours

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "solar_capacity_kw": self.solar_capacity_kw,
            "current_solar_kw": self.current_solar_kw,
            "current_load_kw": self.current_load_kw,
            "net_power_kw": self.net_power_kw,
            "battery_capacity_kwh": self.battery_capacity_kwh,
            "battery_soc_pct": self.battery_soc_pct,
            "battery_power_kw": self.battery_power_kw,
            "grid_relay_active": self.grid_relay_active,
            "wallet_balance_credits": round(self.wallet_balance_credits, 2),
            "total_solar_kwh": round(self.total_solar_generated_kwh, 3),
            "total_consumed_kwh": round(self.total_consumed_kwh, 3),
            "is_hardware_linked": self.is_hardware_linked
        }


class MicrogridEnvironment:
    """
    Coordinates all nodes, weather simulation, and grid interaction.
    """
    def __init__(self):
        self.simulated_hour = 12.0 # Starts at 12:00 PM (Peak solar)
        self.time_speed_multiplier = 60.0 # 1 real second = 60 simulation seconds (1 min)
        self.weather_condition = "Sunny" # "Sunny", "Partly Cloudy", "Rainy"
        self.weather_factor = 1.0
        self.is_grid_blackout = False # Grid resilience scenario
        
        # Community Hub Shared Battery (25 kWh storage buffer)
        self.community_battery_kwh = 25.0
        self.community_battery_soc = 65.0 # %
        self.community_battery_flow_kw = 0.0
        
        # Grid connection metrics
        self.grid_import_kw = 0.0
        self.grid_export_kw = 0.0

        # Initialize standard community neighborhood nodes
        self.nodes: Dict[str, HouseholdNode] = {
            "house_alpha": HouseholdNode(
                node_id="house_alpha",
                name="Alpha Villa (Solar + Storage)",
                solar_capacity_kw=6.0,
                base_load_kw=1.4,
                battery_capacity_kwh=10.0,
                initial_soc_pct=70.0
            ),
            "house_beta": HouseholdNode(
                node_id="house_beta",
                name="Beta Eco-Home (Solar Only)",
                solar_capacity_kw=4.0,
                base_load_kw=1.1,
                battery_capacity_kwh=0.0
            ),
            "house_gamma": HouseholdNode(
                node_id="house_gamma",
                name="Gamma Residence (Consumer)",
                solar_capacity_kw=0.0,
                base_load_kw=1.8,
                battery_capacity_kwh=0.0
            ),
            "house_delta": HouseholdNode(
                node_id="house_delta",
                name="Delta Family (EV Charging)",
                solar_capacity_kw=0.0,
                base_load_kw=2.2,
                battery_capacity_kwh=0.0,
                has_ev=True
            ),
            "house_epsilon": HouseholdNode(
                node_id="house_epsilon",
                name="Epsilon Smart-Home (Solar + Storage)",
                solar_capacity_kw=3.5,
                base_load_kw=1.5,
                battery_capacity_kwh=5.0,
                initial_soc_pct=65.0
            )
        }

    def set_scenario(self, scenario: str):
        """Apply test scenarios for live demonstrations."""
        if scenario == "peak_solar":
            self.simulated_hour = 12.5
            self.weather_condition = "Sunny"
            self.weather_factor = 1.0
            self.is_grid_blackout = False
        elif scenario == "cloudy_afternoon":
            self.simulated_hour = 15.0
            self.weather_condition = "Partly Cloudy"
            self.weather_factor = 0.45
            self.is_grid_blackout = False
        elif scenario == "night_blackout":
            self.simulated_hour = 21.0
            self.weather_condition = "Clear Night"
            self.weather_factor = 0.0
            self.is_grid_blackout = True
        elif scenario == "morning_startup":
            self.simulated_hour = 7.5
            self.weather_condition = "Sunny"
            self.weather_factor = 0.85
            self.is_grid_blackout = False

    def step(self, real_dt_seconds: float = 1.0) -> Dict[str, Any]:
        """
        Advances the microgrid simulation by one time step.
        """
        # Advance simulation clock
        sim_dt_seconds = real_dt_seconds * self.time_speed_multiplier
        self.simulated_hour = (self.simulated_hour + (sim_dt_seconds / 3600.0)) % 24.0

        # Adjust weather factor
        if self.weather_condition == "Sunny":
            self.weather_factor = 1.0
        elif self.weather_condition == "Partly Cloudy":
            self.weather_factor = 0.5 + 0.2 * math.sin(self.simulated_hour * 4.0)
        elif self.weather_condition == "Rainy":
            self.weather_factor = 0.15

        # Update each node
        for node in self.nodes.values():
            node.update_physics(self.simulated_hour, self.weather_factor, sim_dt_seconds)

        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        total_gen = sum(n.current_solar_kw for n in self.nodes.values())
        total_load = sum(n.current_load_kw for n in self.nodes.values())
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulated_time": f"{int(self.simulated_hour):02d}:{int((self.simulated_hour % 1) * 60):02d}",
            "simulated_hour": round(self.simulated_hour, 2),
            "weather": self.weather_condition,
            "weather_factor": round(self.weather_factor, 2),
            "is_grid_blackout": self.is_grid_blackout,
            "community_battery": {
                "capacity_kwh": self.community_battery_kwh,
                "soc_pct": round(self.community_battery_soc, 1),
                "power_kw": round(self.community_battery_flow_kw, 2)
            },
            "summary": {
                "total_generation_kw": round(total_gen, 3),
                "total_consumption_kw": round(total_load, 3),
                "net_community_power_kw": round(total_gen - total_load, 3)
            },
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()}
        }
