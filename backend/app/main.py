from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.app.database import init_db, get_recent_trades
from backend.app.grid_service import grid_service
from backend.app.mqtt_bridge import mqtt_bridge
from backend.app.models import ScenarioUpdateRequest, SpeedUpdateRequest, RelayControlRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("microgrid_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and Start Physics/Market Loop
    logger.info("Initializing Microgrid SQLite database...")
    await init_db()
    
    # Load recent trades into memory cache
    recent = await get_recent_trades(30)
    grid_service.recent_trades_cache = recent
    
    logger.info("Starting simulation and trading engine...")
    grid_service.start()

    logger.info("Starting MQTT hardware bridge...")
    mqtt_bridge.set_grid_service(grid_service)
    mqtt_bridge.start()

    yield

    # Shutdown
    logger.info("Stopping MQTT bridge...")
    mqtt_bridge.stop()
    logger.info("Stopping simulation...")
    grid_service.stop()

app = FastAPI(
    title="Decentralized Solar Microgrid & P2P Energy API",
    description="Backend engine and hardware simulation bridge for community solar sharing",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "system": "Decentralized Solar Microgrid P2P Trading Platform",
        "status": "online",
        "version": "1.0.0",
        "ws_url": "/ws"
    }

@app.get("/api/state")
async def get_state():
    """Retrieve full snapshot of the community microgrid."""
    return await grid_service.get_current_full_state()

@app.get("/api/trades")
async def list_trades(limit: int = 50):
    """Retrieve historical P2P trading ledger."""
    return await get_recent_trades(limit)

@app.post("/api/scenario")
async def trigger_scenario(req: ScenarioUpdateRequest):
    """Switch simulation scenario: peak_solar, cloudy_afternoon, night_blackout, morning_startup."""
    valid_scenarios = ["peak_solar", "cloudy_afternoon", "night_blackout", "morning_startup"]
    if req.scenario not in valid_scenarios:
        raise HTTPException(status_code=400, detail=f"Invalid scenario. Choose from {valid_scenarios}")
    
    grid_service.simulator.set_scenario(req.scenario)
    return {"message": f"Scenario '{req.scenario}' activated successfully."}

@app.post("/api/speed")
async def update_speed(req: SpeedUpdateRequest):
    """Update simulation time speed multiplier."""
    grid_service.simulator.time_speed_multiplier = req.multiplier
    return {"message": f"Speed multiplier set to {req.multiplier}x"}

@app.post("/api/blackout")
async def toggle_blackout(active: bool):
    """Toggle utility grid blackout (forcing neighborhood into 100% islanded microgrid mode)."""
    grid_service.simulator.is_grid_blackout = active
    return {"message": f"Grid blackout state set to: {active}"}

@app.post("/api/relay")
async def toggle_relay(req: RelayControlRequest):
    """Island or reconnect an individual household smart meter."""
    if req.node_id not in grid_service.simulator.nodes:
        raise HTTPException(status_code=404, detail=f"Node {req.node_id} not found.")
    
    node = grid_service.simulator.nodes[req.node_id]
    node.grid_relay_active = req.relay_active
    
    # Forward relay command to hardware IoT nodes via MQTT
    mqtt_forwarded = mqtt_bridge.publish_relay_command(req.node_id, req.relay_active)
    
    return {
        "node_id": req.node_id,
        "grid_relay_active": node.grid_relay_active,
        "status": "CONNECTED" if node.grid_relay_active else "ISLANDED",
        "mqtt_forwarded": mqtt_forwarded
    }

@app.get("/api/mqtt/status")
def mqtt_status():
    """Retrieve connection status of the MQTT hardware bridge."""
    return {
        "enabled": mqtt_bridge.client is not None,
        "connected": mqtt_bridge.connected,
        "broker": f"{mqtt_bridge.broker_host}:{mqtt_bridge.broker_port}"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await grid_service.connect_client(websocket)
        while True:
            # Keep alive and listen for any client messages
            msg = await websocket.receive_text()
            # Can support direct websocket command injections
            logger.debug(f"Received WS command: {msg}")
    except WebSocketDisconnect:
        grid_service.disconnect_client(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        grid_service.disconnect_client(websocket)
