"""
NeuroNex UrbanSense AI Platform - Unified System Runner
Launches the FastAPI Cloud Server and initializes the Multi-Bus Edge Sensing Simulator.
Accessible locally and across local Wi-Fi / LAN network.
"""
import uvicorn
import threading
import time
import sys
import os
import socket

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from edge_ai.fleet_simulator import BusFleetSimulator

def get_local_ip():
    """Gets local LAN IP address for cross-device access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def find_available_port(preferred_port=8000):
    """Finds available port if preferred is already in use."""
    for port in [preferred_port, 8001, 8080, 8888, 5000]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    return preferred_port

def start_edge_fleet_simulator(port=8000):
    """Background worker thread simulating multi-bus edge telemetry pings."""
    time.sleep(2.5)  # Wait for FastAPI server to boot
    simulator = BusFleetSimulator(num_buses=8, backend_url=f"http://127.0.0.1:{port}/api/telemetry/ping")
    simulator.run_continuous_stream(interval_seconds=3.0)

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = find_available_port(8000)
    
    print("=" * 75)
    print(" [*] NEURONEX URBANSENSE AI - MOBILE URBAN INTELLIGENCE PLATFORM")
    print(" [*] Problem Statement: SIH26124 | Bharat Electronics Limited (BEL)")
    print("=" * 75)
    print(f"[+] Access on THIS laptop:     http://localhost:{port}")
    print(f"[+] Access on FRIEND'S laptop: http://{local_ip}:{port}")
    print(f"[+] API Documentation (Swagger): http://localhost:{port}/docs")
    print("=" * 75)
    print(" (Make sure both laptops are connected to the same Wi-Fi / Mobile Hotspot)")
    print("=" * 75)

    # Launch edge simulator in background thread
    sim_thread = threading.Thread(target=start_edge_fleet_simulator, args=(port,), daemon=True)
    sim_thread.start()

    # Start FastAPI Web Server on 0.0.0.0 (Accessible across local network)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
