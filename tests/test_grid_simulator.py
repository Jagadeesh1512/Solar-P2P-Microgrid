import pytest
import time
from simulation.grid_simulator import HouseholdNode, MicrogridEnvironment

def test_diurnal_solar_generation():
    """Verify solar generation peaks at mid-day and is 0 at night."""
    node = HouseholdNode("solar_home", "Solar Home", solar_capacity_kw=6.0, base_load_kw=1.0)

    # Night time (22:00)
    node.update_physics(time_of_day_hours=22.0, weather_factor=1.0, dt_seconds=60.0)
    assert node.current_solar_kw == 0.0

    # Early morning (04:00)
    node.update_physics(time_of_day_hours=4.0, weather_factor=1.0, dt_seconds=60.0)
    assert node.current_solar_kw == 0.0

    # Noon (12:00) with clear sky
    node.update_physics(time_of_day_hours=12.0, weather_factor=1.0, dt_seconds=60.0)
    assert node.current_solar_kw > 5.0 # Close to 6.0 kW capacity

def test_local_battery_dynamics():
    """Verify local home battery charges during surplus and discharges during deficit."""
    # Prosumer with 10 kWh battery, 50% SoC
    node = HouseholdNode(
        "home_batt", "Battery Home",
        solar_capacity_kw=6.0,
        base_load_kw=1.0,
        battery_capacity_kwh=10.0,
        initial_soc_pct=50.0
    )

    # 1. Solar peak at 12:00 -> excess solar should charge local battery
    node.update_physics(time_of_day_hours=12.0, weather_factor=1.0, dt_seconds=1800.0)
    assert node.battery_soc_pct > 50.0
    assert node.battery_power_kw > 0 # Positive = charging

    # 2. Night at 21:00 -> zero solar + load -> battery should discharge
    soc_before = node.battery_soc_pct
    node.update_physics(time_of_day_hours=21.0, weather_factor=0.0, dt_seconds=1800.0)
    assert node.battery_soc_pct < soc_before
    assert node.battery_power_kw < 0 # Negative = discharging

def test_hardware_linked_telemetry_precedence():
    """Verify physical/Wokwi hardware readings take precedence over simulation."""
    node = HouseholdNode("house_alpha", "Alpha Villa", solar_capacity_kw=6.0, base_load_kw=1.0)
    
    # Simulate MQTT hardware update
    node.is_hardware_linked = True
    node.last_hardware_telemetry_time = time.time()
    node.current_solar_kw = 2.45
    node.current_load_kw = 1.15

    # Run update_physics at night (which would normally produce 0.0 kW)
    node.update_physics(time_of_day_hours=23.0, weather_factor=0.0, dt_seconds=60.0)

    # Physical reading should be preserved!
    assert node.current_solar_kw == 2.45
    assert node.current_load_kw == 1.15
    assert node.net_power_kw == round(2.45 - 1.15, 3)

def test_hardware_timeout_fallback():
    """Verify when hardware telemetry times out (>90s), physics resumes automatically."""
    node = HouseholdNode("house_alpha", "Alpha Villa", solar_capacity_kw=6.0, base_load_kw=1.0)
    node.is_hardware_linked = True
    node.last_hardware_telemetry_time = time.time() - (node.hardware_timeout_seconds + 10.0) # Timed out

    # Run physics at midnight
    node.update_physics(time_of_day_hours=0.0, weather_factor=1.0, dt_seconds=60.0)

    # Hardware link dropped, physics resumed
    assert node.is_hardware_linked is False
    assert node.current_solar_kw == 0.0

def test_scenarios():
    """Verify test scenarios set correct hours and environmental flags."""
    env = MicrogridEnvironment()

    env.set_scenario("peak_solar")
    assert env.simulated_hour == 12.5
    assert env.weather_condition == "Sunny"
    assert env.is_grid_blackout is False

    env.set_scenario("night_blackout")
    assert env.simulated_hour == 21.0
    assert env.is_grid_blackout is True

    env.set_scenario("cloudy_afternoon")
    assert env.simulated_hour == 15.0
    assert env.weather_factor == 0.45
