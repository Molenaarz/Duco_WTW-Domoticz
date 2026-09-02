# DucoBox Energy Comfort (v2.7+) - Domoticz Integration

This repository contains two Python 3 scripts to achieve full bi-directional integration between a **DucoBox Energy Comfort** MVHR (WTW) unit (running PublicApiVersion 2.7+ with a Connectivity Board) and **Domoticz**.

## 💡 Why this project?
Starting from firmware v2.5/v2.7, Duco changed its Modbus TCP server logic. Traditional sequential register polling on the 4000-temperature range now results in a hard `Exception Response(131, 3, SlaveFailure)`. 

This project completely circumvents this limitation by utilizing the local **HTTP REST API (JSON)** for reading sensor data, while using targeted **HTTP POST JSON Payloads** to override and control the ventilation states.

---

## 📊 Supported Features & Sensors (10x)
The extraction script (`duco-script.py`) pulls live data every minute to update 10 different Domoticz sensors:
* **4x Temperatures:** Outdoor Air (`TempOda`), Supply Air (`TempSup`), Extract Air (`TempEta`), Exhaust Air (`TempEha`).
* **MVHR Efficiency / WTW Rendement (%):** Calculated on-the-fly using the thermodynamic formula.
* **Filter Status:** Remaining days until the next filter swap.
* **Ventilation Metrics:** Current speed (%), active state/fan speed level (Text), and ventilation mode (Text).
* **Humidity:** Relative Humidity (% Rh) and the internal Duco Air Quality Threshold index (`IaqRh`).

---

## 🛠️ Domoticz Setup
Create **10 virtual sensors** in Domoticz via **Setup -> Hardware -> Dummy -> Create Virtual Sensors**:

1. **Temperature** (4x) -> For the four temperature streams.
2. **Percentage** or **Custom Sensor** (1x) -> For the MVHR Efficiency (%).
3. **Custom Sensor** (1x, Axis Label: `Days`) -> For Filter Remaining.
4. **Text** (2x) -> For Ventilation State and Ventilation Mode.
5. **Humidity** (1x) -> For Indoor Humidity.
6. **Custom Sensor** (1x) -> For the Comfort Index Threshold (`IaqRh`).
7. **Selector Switch** (1x) -> For controlling the unit. Set the style to **Buttons** and check **Hide Off Level**. Add levels: `10` (Low), `20` (Medium), `30` (High), `40` (Auto).

---

## 🔧 Installation & Configuration

1. Clone or download these scripts to your Domoticz machine (e.g., `/duco-script/`).
2. Install the required Python 3 library:
   ```bash
   pip3 install requests
   ```
3. Open both Python files and adjust the configuration variables at the top (IP addresses and your unique Domoticz IDX numbers).
4. Make both files executable:
   ```bash
   chmod +x /duco-script/duco-script.py
   chmod +x /duco-script/duco-set.py
   ```

### Connecting the Selector Switch in Domoticz
Edit your Selector Switch and configure the **Selector Actions** using the following Linux shell wrappers to ensure clean background execution:
* Level 10 (Low): `script://sh -c "python3 /duco-script/duco-set.py 10"`
* Level 20 (Medium): `script://sh -c "python3 /duco-script/duco-set.py 20"`
* Level 30 (High): `script://sh -c "python3 /duco-script/duco-set.py 30"`
* Level 40 (Auto): `script://sh -c "python3 /duco-script/duco-set.py 40"`

---

## ⏱️ Automation (Crontab)
To poll the sensors automatically, add the script to your system's crontab (`crontab -e`):

```text
# Poll the DucoBox every minute
* * * * * /usr/bin/python3 /duco-script/duco-script.py > /dev/null 2>&1

# Optional: Poll once directly after server reboot (with a 30s network buffer)
@reboot sleep 30 && /usr/bin/python3 /duco-script/duco-script.py > /dev/null 2>&1
```
*Note: When you click a state button in Domoticz, `duco-set.py` will automatically trigger an instant refresh of `duco-script.py` after a 3-second motor buffer, giving you instantaneous dashboard updates.*
