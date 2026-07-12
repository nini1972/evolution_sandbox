import os
import time

def monitor_system_health():
    # Detect if components are still running.
    files = os.listdir('.')
    if 'master_controller.py' in files:
        print("Diagnostic: Master Controller present.")
    
    # Analyze the complexity score log for growth
    try:
        with open('analyzer/adaptation_tracker/evolution_history.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) > 5:
                print("Diagnostic: Evolution history active and growing.")
    except Exception as e:
        print(f"Diagnostic Warning: {e}")

if __name__ == "__main__":
    monitor_system_health()
