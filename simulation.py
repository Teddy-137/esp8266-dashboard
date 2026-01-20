import time
import threading
from mqtt_client import latest_data, state_lock

def simulate_battery():
    battery_level = 74
    while True:
        with state_lock:
            latest_data["battery"] = battery_level
        
        time.sleep(64) # Decrease every 5 seconds
        battery_level -= 1
        
        if battery_level < 0:
            battery_level = 100 # Reset to 100 for continuous demo

def start_battery_simulation():
    thread = threading.Thread(target=simulate_battery, daemon=True)
    thread.start()
