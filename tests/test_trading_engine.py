import pytest
from backend.app.trading_engine import TradingEngine
from simulation.grid_simulator import HouseholdNode

def test_clearing_price_formula():
    """Verify Mid-Market clearing tariff formula: (P_utility + P_feedin) / 2."""
    engine = TradingEngine(utility_import_tariff=0.20, feed_in_export_tariff=0.06)
    assert engine.p2p_clearing_price == 0.13

    # Custom rates
    engine_custom = TradingEngine(utility_import_tariff=0.30, feed_in_export_tariff=0.10)
    assert engine_custom.p2p_clearing_price == 0.20

def test_p2p_matching_single_pair():
    """Verify bilateral matching between 1 prosumer and 1 consumer."""
    engine = TradingEngine(utility_import_tariff=0.20, feed_in_export_tariff=0.06)
    dt_seconds = 3600.0 # 1 hour for easy kWh verification

    seller = HouseholdNode("seller", "Seller Node", solar_capacity_kw=5.0, base_load_kw=1.0)
    seller.current_solar_kw = 4.0
    seller.current_load_kw = 1.0
    seller.net_power_kw = 3.0 # +3.0 kW surplus

    buyer = HouseholdNode("buyer", "Buyer Node", solar_capacity_kw=0.0, base_load_kw=2.0)
    buyer.current_solar_kw = 0.0
    buyer.current_load_kw = 2.0
    buyer.net_power_kw = -2.0 # -2.0 kW deficit

    nodes = {"seller": seller, "buyer": buyer}
    batt = {"capacity_kwh": 25.0, "soc_pct": 50.0, "power_kw": 0.0}

    trades, flows, summary = engine.match_interval(
        nodes=nodes,
        community_battery=batt,
        is_grid_blackout=False,
        dt_seconds=dt_seconds
    )

    # 1 trade executed matching 2.0 kWh
    assert len(trades) == 1
    t = trades[0]
    assert t["seller_id"] == "seller"
    assert t["buyer_id"] == "buyer"
    assert t["energy_kwh"] == 2.0
    assert t["clearing_price_usd"] == 0.13
    assert t["total_cost_usd"] == round(2.0 * 0.13, 4)
    # Buyer saved: 2.0 * (0.20 - 0.13) = 0.14
    assert t["buyer_savings_usd"] == 0.14
    # Seller extra profit: 2.0 * (0.13 - 0.06) = 0.14
    assert t["seller_extra_profit_usd"] == 0.14

    # Financial balances updated
    assert buyer.wallet_balance_credits == round(100.0 - 0.26, 2)
    assert seller.wallet_balance_credits == round(100.0 + 0.26, 2)

    # Unmatched surplus of 1.0 kW charges community battery
    assert batt["soc_pct"] > 50.0

def test_community_battery_storage_and_grid_export():
    """Verify leftover solar charges battery buffer first, then exports to utility."""
    engine = TradingEngine(utility_import_tariff=0.20, feed_in_export_tariff=0.06)
    dt_seconds = 3600.0

    # 10 kW surplus, no buyers
    seller = HouseholdNode("seller", "Seller Node", solar_capacity_kw=10.0, base_load_kw=0.0)
    seller.net_power_kw = 10.0

    nodes = {"seller": seller}
    # Community battery with only 2 kWh remaining capacity before 98%
    # capacity = 25 kWh, 98% = 24.5 kWh. At 90% SoC = 22.5 kWh. Room = 2.0 kWh.
    batt = {"capacity_kwh": 25.0, "soc_pct": 90.0, "power_kw": 0.0}

    trades, flows, summary = engine.match_interval(
        nodes=nodes,
        community_battery=batt,
        is_grid_blackout=False,
        dt_seconds=dt_seconds
    )

    assert len(trades) == 0
    # Battery absorbed 2.0 kWh
    assert round(batt["soc_pct"], 1) == 98.0
    # Leftover 8.0 kW exported to utility grid
    assert summary["grid_export_kw"] == 8.0
    assert summary["grid_import_kw"] == 0.0

def test_islanded_resilience_during_blackout():
    """Verify zero utility grid import/export during a grid blackout."""
    engine = TradingEngine()
    dt_seconds = 3600.0

    # Heavy deficit of 15 kW
    buyer = HouseholdNode("buyer", "Buyer Node", solar_capacity_kw=0.0, base_load_kw=15.0)
    buyer.net_power_kw = -15.0

    nodes = {"buyer": buyer}
    batt = {"capacity_kwh": 25.0, "soc_pct": 15.0, "power_kw": 0.0} # Depleted battery

    trades, flows, summary = engine.match_interval(
        nodes=nodes,
        community_battery=batt,
        is_grid_blackout=True, # Grid is down!
        dt_seconds=dt_seconds
    )

    # During blackout, grid cannot supply power
    assert summary["grid_import_kw"] == 0.0
    assert summary["grid_export_kw"] == 0.0

def test_disconnected_relay_node_excluded():
    """Verify disconnected/islanded household does not trade."""
    engine = TradingEngine()
    seller = HouseholdNode("seller", "Seller Node", solar_capacity_kw=5.0, base_load_kw=0.0)
    seller.net_power_kw = 5.0
    seller.grid_relay_active = False # Relay cut-off

    buyer = HouseholdNode("buyer", "Buyer Node", solar_capacity_kw=0.0, base_load_kw=3.0)
    buyer.net_power_kw = -3.0

    nodes = {"seller": seller, "buyer": buyer}
    batt = {"capacity_kwh": 25.0, "soc_pct": 50.0, "power_kw": 0.0}

    trades, flows, summary = engine.match_interval(
        nodes=nodes,
        community_battery=batt,
        is_grid_blackout=False,
        dt_seconds=60.0
    )

    # Seller is disconnected; no trade should occur
    assert len(trades) == 0
