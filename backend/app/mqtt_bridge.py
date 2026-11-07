import json
import logging
import os
import time
from typing import Optional

try:
    import paho.mqtt.client as mqtt
    from paho.mqtt.enums import CallbackAPIVersion
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False

logger = logging.getLogger("microgrid_mqtt")

class MQTTBridge:
    def __init__(
        self,
        broker_host: str = "broker.hivemq.com",
        broker_port: int = 1883,
        grid_service_ref=None
    ):
        self.broker_host = os.getenv("MQTT_BROKER_HOST", broker_host)
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", broker_port))
        self.grid_service = grid_service_ref
        self.client: Optional[mqtt.Client] = None
        self.connected = False

        if PAHO_AVAILABLE:
            try:
                self.client = mqtt.Client(
                    CallbackAPIVersion.VERSION2,
                    client_id=f"Microgrid-Backend-{int(time.time())}"
                )
                self.client.on_connect = self._on_connect
                self.client.on_disconnect = self._on_disconnect
                self.client.on_message = self._on_message
            except Exception as e:
                logger.warning(f"Failed to initialize MQTT Client: {e}")

    def set_grid_service(self, grid_service_ref):
        self.grid_service = grid_service_ref

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        logger.info(f"Connected to MQTT broker {self.broker_host}:{self.broker_port} with result code {rc}")
        self.connected = True
        client.subscribe("microgrid/telemetry/+")

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        logger.info(f"Disconnected from MQTT broker with code {rc}")
        self.connected = False

    def _on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
            node_id = data.get("household_id")

            if self.grid_service and node_id in self.grid_service.simulator.nodes:
                node = self.grid_service.simulator.nodes[node_id]
                node.is_hardware_linked = True
                node.last_hardware_telemetry_time = time.time()

                if "solar_kw" in data:
                    node.current_solar_kw = round(float(data["solar_kw"]), 3)
                if "load_kw" in data:
                    node.current_load_kw = round(float(data["load_kw"]), 3)
                if "battery_soc" in data:
                    node.battery_soc_pct = round(float(data["battery_soc"]), 1)
                if "net_kw" in data:
                    node.net_power_kw = round(float(data["net_kw"]), 3)
                else:
                    node.net_power_kw = round(node.current_solar_kw - node.current_load_kw, 3)
                if "grid_relay" in data:
                    node.grid_relay_active = bool(data["grid_relay"])

                logger.info(f"Updated node {node_id} from hardware MQTT: solar={node.current_solar_kw}kW, load={node.current_load_kw}kW, net={node.net_power_kw}kW")
        except Exception as e:
            logger.warning(f"Failed to process MQTT message on {msg.topic}: {e}")

    def publish_relay_command(self, node_id: str, relay_active: bool) -> bool:
        if not self.client or not self.connected:
            return False
        topic = f"microgrid/control/{node_id}"
        # Use compact JSON format (no spaces) for microcontroller compatibility
        payload = json.dumps({"grid_relay": relay_active}, separators=(',', ':'))
        try:
            res = self.client.publish(topic, payload)
            logger.info(f"Published control to {topic}: {payload}")
            return res.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.warning(f"Error publishing to {topic}: {e}")
            return False

    def start(self):
        if not self.client:
            logger.warning("MQTT client not available; running in simulation-only mode.")
            return

        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}...")
            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.warning(f"Could not connect to MQTT broker: {e}. Microgrid continues in simulated mode.")

    def stop(self):
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception as e:
                logger.warning(f"Error stopping MQTT client: {e}")

# Global singleton
mqtt_bridge = MQTTBridge()
