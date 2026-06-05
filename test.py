import asyncio
import serial
import json
import websockets
from bleak import BleakScanner
import time

ARDUINO_PORT = 'COM4'
WS_HOST = '127.0.0.1' 
WS_PORT = 8765
IDLE_TIMEOUT = 10.0

try:
    ser = serial.Serial(ARDUINO_PORT, 115200, timeout=0.1)
    print(f"✅ Arduino successfully connected on {ARDUINO_PORT}")
except Exception as e:
    ser = None
    print(f"⚠️ Arduino not connected ({e}). Running in UI-Only Demo Mode.")

is_light_on = False
last_trigger_time = time.time()
websocket_clients = set()
total_carbon_saved = 14.250  # 累计减碳基础值

def get_mock_metrics(state):
    global total_carbon_saved
    timestamp = time.strftime('%H:%M:%S')
    if state == "ON":
        return {
            "state": "ON",
            "time": timestamp,
            "hvac": "Active Mode (22.5°C) - High Efficiency",
            "plug_load": "Desks 1-8: ENGAGED (320W Total Load)",
            "utilisation": "84% (Spatial Peak Level)",
            "anomaly": "NILM Scan: Device Overload Shield Active",
            "inclusive": "Pedestrian / Mobility Aid Detected",
            "carbon_saved": f"{total_carbon_saved:.3f} kg CO2"
        }
    else:
        return {
            "state": "OFF",
            "time": timestamp,
            "hvac": "Eco Saving Mode (26.0°C) - Active",
            "plug_load": "Plug Load Kill-Switch: ACTIVATED (0W Leakage)",
            "utilisation": "12% (Standby Level)",
            "anomaly": "Circuit Waste Audit: Zero Leakage Secured",
            "inclusive": "Zone Vacant",
            "carbon_saved": f"{total_carbon_saved:.3f} kg CO2"
        }

async def broadcast(msg):
    if websocket_clients:
        payload = json.dumps(msg)
        # 使用 asyncio.gather 确保并发安全送达
        await asyncio.gather(*[ws.send(payload) for ws in websocket_clients], return_exceptions=True)

def send_command(cmd):
    if ser:
        try:
            ser.write(f"{cmd}\n".encode())
            ser.flush()
        except Exception as e:
            print(f"❌ Serial Write Error: {e}")
    print(f" >> [Hardware Relay] Executed Command: {cmd}")

async def callback(device, adv_data):
    global is_light_on, last_trigger_time
    
    if device.name == "BM-Sensor":
        # 抓踩踏信号
        if not adv_data.manufacturer_data:
            return  

        last_trigger_time = time.time()
        timestamp = time.strftime('%H:%M:%S')
        
        await broadcast({'event': 'footstep', 'time': timestamp, 'rssi': adv_data.rssi})
        
        if not is_light_on:
            send_command("ON")
            is_light_on = True
            metrics = get_mock_metrics("ON")
            await broadcast(metrics)
            print(f"[{timestamp}] BLE Interrupt Caught -> System ACTIVE")

async def idle_checker():
    global is_light_on, total_carbon_saved
    while True:
        await asyncio.sleep(1)
        
        if not is_light_on:
            total_carbon_saved += 0.003
            await broadcast({"carbon_update": f"{total_carbon_saved:.3f} kg CO2"})
            
        if is_light_on and (time.time() - last_trigger_time > IDLE_TIMEOUT):
            timestamp = time.strftime('%H:%M:%S')  
            send_command("OFF")
            is_light_on = False
            metrics = get_mock_metrics("OFF")
            await broadcast(metrics)
            print(f"[{timestamp}] Spatial Idle Timeout -> System STANDBY")

async def ws_handler(ws):
    websocket_clients.add(ws)
    await ws.send(json.dumps(get_mock_metrics("ON" if is_light_on else "OFF")))
    try:
        await ws.wait_closed()
    finally:
        websocket_clients.remove(ws)

async def main():
    scanner = BleakScanner(callback, scanning_mode="active")
    await scanner.start()
    print(" BLE Gateway Core initialized. Scanning for Hardware Interrupts...")
    
    asyncio.create_task(idle_checker())
    
    async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
        print(f"🌐 Building Mind Engine Layer active on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Core Engine Shutdown Safely.")