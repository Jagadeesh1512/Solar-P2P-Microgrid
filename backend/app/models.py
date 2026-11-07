from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class TradeTransaction(BaseModel):
    id: Optional[int] = None
    timestamp: str
    seller_id: str
    seller_name: str
    buyer_id: str
    buyer_name: str
    energy_kwh: float
    clearing_price_usd: float
    total_cost_usd: float
    buyer_savings_usd: float
    seller_extra_profit_usd: float

class HouseholdState(BaseModel):
    node_id: str
    name: str
    solar_capacity_kw: float
    current_solar_kw: float
    current_load_kw: float
    net_power_kw: float
    battery_capacity_kwh: float
    battery_soc_pct: float
    battery_power_kw: float
    grid_relay_active: bool
    wallet_balance_credits: float
    total_solar_kwh: float
    total_consumed_kwh: float
    is_hardware_linked: bool = False

class CommunityBatteryState(BaseModel):
    capacity_kwh: float
    soc_pct: float
    power_kw: float

class GridSummary(BaseModel):
    total_generation_kw: float
    total_consumption_kw: float
    net_community_power_kw: float
    grid_import_kw: float
    grid_export_kw: float
    self_sufficiency_ratio_pct: float
    total_co2_offset_kg: float

class MicrogridStatePayload(BaseModel):
    timestamp: str
    simulated_time: str
    simulated_hour: float
    weather: str
    weather_factor: float
    is_grid_blackout: bool
    tariff_rates: Dict[str, float]
    community_battery: CommunityBatteryState
    summary: GridSummary
    nodes: Dict[str, HouseholdState]
    recent_trades: List[TradeTransaction]
    active_power_flows: List[Dict[str, Any]] = []

class ScenarioUpdateRequest(BaseModel):
    scenario: str = Field(..., description="peak_solar | cloudy_afternoon | night_blackout | morning_startup")

class SpeedUpdateRequest(BaseModel):
    multiplier: float = Field(..., ge=1.0, le=360.0)

class RelayControlRequest(BaseModel):
    node_id: str
    relay_active: bool
