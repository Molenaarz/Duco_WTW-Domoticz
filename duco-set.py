#!/usr/bin/env python3
import sys
import requests
import subprocess

# ==========================================
# CONFIGURATION: ADJUST TO YOUR LOCAL SETUP
# ==========================================
DUCO_IP = "192.168.1.150"
URL = f"http://{DUCO_IP}/action/nodes/1"

def stuur_stand_via_post(domoticz_level):
    if domoticz_level == 10:
        state_value = "CNT1"
    elif domoticz_level == 20:
        state_value = "CNT2"
    elif domoticz_level == 30:
        state_value = "CNT3"
    elif domoticz_level == 40 or domoticz_level == 0:
        state_value = "AUTO"
    else:
        sys.exit(1)

    payload = {"Action": "SetVentilationState", "Val": state_value}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            # Trigger background instant refresh after 3 seconds motor stabilization buffer
            cmd = "sleep 3 && /usr/bin/python3 /duco-script/duco-script.py"
            subprocess.Popen(["sh", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            level = int(sys.argv[1])
            stuur_stand_via_post(level)
        except ValueError:
            sys.exit(1)
    else:
        sys.exit(1)
