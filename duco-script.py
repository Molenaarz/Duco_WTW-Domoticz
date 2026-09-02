#!/usr/bin/env python3
import json
import requests

# ==========================================
# CONFIGURATION: ADJUST TO YOUR LOCAL SETUP
# ==========================================
DUCO_IP = "192.168.1.150"
DOMOTICZ_IP = "127.0.0.1"
DOMOTICZ_PORT = "8080"

# Domoticz IDX placeholders - Replace with your own
IDX_TEMP_EHA     = 1001
IDX_TEMP_ETA     = 1002
IDX_TEMP_ODA     = 1003
IDX_TEMP_SUP     = 1004
IDX_FILTER       = 1005
IDX_SNELHEID     = 1006
IDX_STAND        = 1007
IDX_HUM          = 1008
IDX_RENDEMENT    = 1009
IDX_MODUS        = 1010
IDX_SELECTOR     = 1011  # Your selector switch IDX to keep it in sync


def send_to_domoticz(idx, value):
    if idx is None or value is None:
        return
    try:
        url = f"http://{DOMOTICZ_IP}:{DOMOTICZ_PORT}/json.htm?type=command&param=udevice&idx={idx}&svalue={value}"
        requests.get(url, timeout=3)
    except Exception as e:
        print(f"❌ Error updating Domoticz IDX {idx}: {str(e)}")


def send_humidity_to_domoticz(idx, humidity_value):
    if idx is None or humidity_value is None:
        return
    try:
        url = f"http://{DOMOTICZ_IP}:{DOMOTICZ_PORT}/json.htm?type=command&param=udevice&idx={idx}&nvalue={humidity_value}&svalue=0"
        requests.get(url, timeout=3)
    except Exception as e:
        print(f"❌ Error updating Humidity IDX {idx}: {str(e)}")


def vertaal_stand(status_code):
    vertalingen = {
        "CNT1": "Stand 1 (Laag)",
        "CNT2": "Stand 2 (Midden)",
        "CNT3": "Stand 3 (Hoog)",
        "AUTO": "Automatisch",
        "MANU": "Handmatig"
    }
    return vertalingen.get(status_code, status_code)


def vertaal_modus(mode_code):
    vertalingen = {
        "AUTO": "Automatisch",
        "MANU": "Handmatig",
        "OVER": "Overrule",
        "-": "Onbekend"
    }
    return vertalingen.get(mode_code, mode_code)


def main():
    try:
        res_info = requests.get(f"http://{DUCO_IP}/info", timeout=5)
        res_nodes = requests.get(f"http://{DUCO_IP}/info/nodes", timeout=5)
        
        if res_info.status_code != 200 or res_nodes.status_code != 200:
            return

        data_info = res_info.json()
        data_nodes = res_nodes.json()

        # Parse /info
        sensors = data_info.get("Ventilation", {}).get("Sensor", {})
        temp_oda = sensors.get("TempOda", {}).get("Val", 0) / 10.0
        temp_sup = sensors.get("TempSup", {}).get("Val", 0) / 10.0
        temp_eta = sensors.get("TempEta", {}).get("Val", 0) / 10.0
        temp_eha = sensors.get("TempEha", {}).get("Val", 0) / 10.0
        filter_days = data_info.get("HeatRecovery", {}).get("General", {}).get("TimeFilterRemain", {}).get("Val")

        # Parse /info/nodes (Node 1)
        box_node = next((node for node in data_nodes.get("Nodes", []) if node.get("Node") == 1), {})
        vent_data = box_node.get("Ventilation", {})
        node_sensors = box_node.get("Sensor", {})
        
        ruwe_stand = vent_data.get("State", {}).get("Val")
        ventilatiestand = vertaal_stand(ruwe_stand)
        ventilatiemodus = vertaal_modus(vent_data.get("Mode", {}).get("Val"))
        snelheid_pct = vent_data.get("FlowLvlTgt", {}).get("Val")
        humidity = node_sensors.get("Rh", {}).get("Val")
        iaq_rh = node_sensors.get("IaqRh", {}).get("Val")

        # Calculate efficiency
        if (temp_eta - temp_oda) != 0:
            rendement = max(0.0, min(100.0, round(((temp_sup - temp_oda) / (temp_eta - temp_oda)) * 100, 1)))
        else:
            rendement = 0.0

        # Push data
        send_to_domoticz(IDX_TEMP_EHA, temp_eha)
        send_to_domoticz(IDX_TEMP_ETA, temp_eta)
        send_to_domoticz(IDX_TEMP_ODA, temp_oda)
        send_to_domoticz(IDX_TEMP_SUP, temp_sup)
        send_to_domoticz(IDX_FILTER, filter_days)
        send_to_domoticz(IDX_SNELHEID, snelheid_pct)
        send_to_domoticz(IDX_STAND, ventilatiestand)
        send_to_domoticz(IDX_RENDEMENT, rendement)
        send_to_domoticz(IDX_MODUS, ventilatiemodus)
        send_to_domoticz(IDX_VOCHTDREMPEL, iaq_rh)
        send_humidity_to_domoticz(IDX_HUM, humidity)
        
        # Keep selector switch state in sync
        level_map = {"CNT1": 10, "CNT2": 20, "CNT3": 30, "AUTO": 40}
        if ruwe_stand in level_map:
            send_to_domoticz(IDX_SELECTOR, level_map[ruwe_stand])

    except Exception as e:
        print(f"💥 Main script error: {str(e)}")


if __name__ == "__main__":
    main()
