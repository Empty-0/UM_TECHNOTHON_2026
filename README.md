# TEAM NEW SPACE - UM TECHNOTHON 2026

## BuildingMind AI OS · Digital Prototype

### System Architecture
- **dashboard.html** — Real-time ESG & PropTech intelligent dashboard (WebSocket client)
- **gateway.py** — BLE sensor gateway + WebSocket server + serial relay control

### Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run gateway: `python test.py`
3. Open `test.html` in any modern browser
4. Trigger footstep via BLE sensor or press 'F' key

### Key Features Demonstrated
- Layer 1: Real-time automation (lighting, HVAC, plug kill-switch)
- Layer 2: Space intelligence (heatmap, utilisation ring, dwell time)
- Layer 3: Equipment health (predictive maintenance, NILM breakdown)
- Layer 4: Safety & compliance (fire fail-safe, camera-free alerts)
- Layer 5: Long-term platform (carbon tracking, tenant billing, federated learning)

### Technical Stack
- Frontend: Vanilla HTML/CSS/JS with WebSocket real-time communication
- Backend: Python asyncio + Bleak BLE scanner + WebSocket server
- Hardware: Arduino relay control via serial, BLE sensor nodes
