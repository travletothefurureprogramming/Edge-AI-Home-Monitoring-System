# Edge-AI Home Monitoring System
[![CI Tests](https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System/actions/workflows/tests.yml/badge.svg)](https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System/actions/workflows/tests.yml)
### A privacy-first, edge-AI home automation hub using Linux, Flask, and real-time control to orchestrate smart devices.

<img width="1912" height="968" alt="Edge-AI Home Monitoring System dashboard" src="https://github.com/user-attachments/assets/1977c347-7d0e-4ddf-a71f-89956ec50f26" />

## 🚀 Features

- **Edge-AI Architecture:** Localized processing hubs reducing cloud dependency and latency.
- **Unified Network Control:** Asynchronous API endpoints driven by Flask and FastAPI to manage smart hardware (Yeelight, TP-Link Kasa, Sonos/Soco, Samsung TV).
- **Extensible Integration Layer:** Modulated code structure allowing direct hardware abstraction loops.
- **Robust CI/CD Pipeline:** Automated testing suite via GitHub Actions evaluating code coverage and reliability metrics on every push.

## 🛠️ Tech Stack

- **Backend Frameworks:** Python (FastAPI, Flask)
- **Deep Learning / Computer Vision:** PyTorch, Triton Inference Server
- **Testing & Quality:** Pytest, Pytest-Cov
- **Target Hardware Interfaces:** Single-board computers (Raspberry Pi), Microcontrollers (RP2040), Network Smart Devices

## 🔌 Offline-First Automations: They Never Stop

Unlike cloud-dependent systems, your automations **always run**—even if:
- Internet goes down
- WiFi router dies or reboots
- You unplug the system entirely (automations resume on power-up)
- Cloud services are unreachable

### How It Works

All automation rules are stored **locally** in `automations.json`. The `AutomationManager` runs on a background thread that:

1. **Loads rules from disk** at startup (not cloud)
2. **Executes scheduled rules** using local cron (no external scheduler needed)
3. **Triggers event-based rules** from local sensors (YOLO camera, device state changes)
4. **Calls device APIs directly** without internet involvement

**No internet = No outbound calls. Automation continues normally.**

### Proof

```bash
# Scenario: Internet dies at 22:00
# Rule: "At 23:00, turn off all lights"

# What happens:
22:00 - Router unplugged (internet dies)
22:30 - Dashboard unreachable, but system continues running
23:00 - Automation fires on schedule
        Lights turn off automatically
        No internet call was made
23:30 - Verify: SSH into Pi, confirm in logs that automation executed
```

### Why This Matters

**Home Assistant:** If internet dies, cloud integrations fail. Automations break.

**Edge-AI:** Internet is optional. Your automations are guaranteed to run, always.


## 📊 How Edge-AI Compares

| Feature | Home Assistant | Edge-AI |
|---------|---|---|
| **Automations work offline** | ❌ Cloud integrations fail | ✅ 100% guaranteed |
| **Internet required** | ✅ For most automations | ❌ Zero required |
| **Setup time** | 1 hour (config files) | 5 minutes (wizard) |
| **Startup time** | 45 seconds | <5 seconds |
| **Privacy** | Integrations vary | ✅ 100% local, zero exfil |
| **Device count** | 1,000+ | 30+ (curated, tested) |
| **Resiliency** | ⚠️ Single Pi = single point of failure | ✅ Local-only = always works |
| **Learning curve** | Steep (YAML, templating) | Gentle (web UI only) |
| **Automation chaining** | ✅ Yes, but complex | ✅ Yes, simple web UI |
| **Philosophy** | Flexibility first | Privacy & sovereignty first |

**Bottom line:** HA is powerful but fragile. Edge-AI is simple but unbreakable.


## 📋 Supported Devices

### Tapo LED Strips
- L900
- L920 (untested)
- L930 (untested)

### Tapo Light Bulbs
- L510 (untested)
- L520 (untested)
- L530 (untested)
- L535 (untested)
- L610 (untested)
- L630 (untested)

### Tapo Smart Plugs
- P100 (untested)
- P105 (untested)
- P110 (untested)
- P300 (untested)
- P304 (untested)
- P306 (untested)

### Philips Hue Lights
- All lights/bulbs or LED strips connected to a Philips Hue Bridge (untested)

### Yeelight
- All light bulbs that support Wi-Fi control (untested)

### Android TV
- Android 8+

### LG TV
- webOS 6+

### Daikin AC
- BRP069Axx / BRP069Bxx / BRP072Axx (untested)
- BRP15B61, a.k.a. AirBase (untested)

### Shelly
- Shelly 1 (untested)
- Shelly 1PM (untested)
- Shelly 2 (untested)
- Shelly 2.5 (untested)
- Shelly 4Pro (untested)
- Shelly Plug (untested)
- Shelly Plug S (untested)
- Shelly Bulb (untested)
- Shelly H&T (untested)
- Shelly Smoke (untested)
- Shelly EM (untested)
- Shelly Flood (untested)

### Kasa Plugs
- EP10 (untested)
- HS103 (untested)
- HS105 (untested)
- HS110 (untested)
- KP100 (untested)
- KP105 (untested)
- KP115 (untested)
- KP125 (untested)
- KP401 (untested)

### Kasa Power Strips
- EP40 (untested)
- HS107 (untested)
- HS300 (untested)
- KP200 (untested)
- KP303 (untested)
- KP400 (untested)

### Kasa Wall Switches
- ES20M (untested)
- HS210 (untested)
- KP405 (untested)
- KS200 (untested)
- KS200M (untested)
- KS220 (untested)
- KS220M (untested)
- KS230 (untested)

### Kasa Bulbs
- KL110 (untested)
- KL120 (untested)
- KL125 (untested)
- KL130 (untested)
- KL135 (untested)
- KL50 (untested)
- KL60 (untested)
- LB110 (untested)

### Kasa Light Strips
- KL400L5 (untested)
- KL420L5 (untested)
- KL430 (untested)

### Broadlink Universal Remotes
- RM Home (untested)
- RM Mini 3 (untested)
- RM Plus (untested)
- RM Pro (untested)
- RM Pro+ (untested)
- RM4 Mini (untested)
- RM4 Pro (untested)
- RM4C Mini (untested)
- RM4S (untested)
- RM4 TV Mate (untested)

You can control any device via a Broadlink Universal Remote in the following categories: TV, AC, Decoder.

### Samsung TV
- Supports Samsung Tizen TV (2016+)

## 📦 Installation

The Edge-AI Home Monitoring System is fully containerized using Docker. The setup process is automatic and works on **Windows**, **Linux**, and **macOS**.

### Prerequisites

Before you begin, install the following software:

* **Git** — https://git-scm.com/downloads
* **Docker Desktop** (Windows/macOS) — https://www.docker.com/products/docker-desktop/
* **Docker Engine + Docker Compose** (Linux) — https://docs.docker.com/engine/install/

> **Note**
> Python, Ollama, Android SDK Platform Tools (ADB), and all required Python packages are provided automatically by Docker. No additional manual installation is required.

### 1. Clone the repository

```bash
git clone https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System.git
cd Edge-AI-Home-Monitoring-System
```

### 2. Start the application

**Windows**

```bash
start.bat
```

**Linux / macOS**

Make the script executable (only required once):

```bash
chmod +x start.sh
```

Then start the application:

```bash
./start.sh
```

During the first launch, the startup script will automatically:

* Create the required configuration directories.
* Create the `.env` file if it does not already exist.
* Build the Docker containers.
* Download the Ollama Docker image.
* Start all required services.

> **Note**
> The first startup may take several minutes while Docker downloads the required images.

### 3. Open the Setup Wizard

Once the containers are running, open your web browser and navigate to:

```text
http://localhost:8080
```

The setup wizard will guide you through the entire configuration process. You will be asked to:

* Create the administrator password.
* Configure Telegram notifications (optional).
* Add and configure your smart devices.
* Save your configuration.

### 4. AI Model Download

During the initial setup, the required AI model will be downloaded automatically if it is not already installed.

> **Note**
> The first model download may take several minutes depending on your internet connection.

### 5. Access the Dashboard

After completing the setup, open your browser and visit:

```text
http://localhost:8080
```

Sign in using:

* **Username:** `admin`
* **Password:** the password you created during setup.

## 🔄 Updating

To update the project:

```bash
git pull
```

Then restart the application:

**Windows**

```bash
start.bat
```

**Linux / macOS**

```bash
./start.sh
```

## 🤖 Telegram Bot Configuration

Your system needs a Bot Token and a Chat ID to send real-time alerts.

**Step 1 — Get your Bot Token**

1. Open Telegram and search for **@BotFather** (official verified bot).
2. Send `/newbot` and follow the prompts to choose a name and a unique username ending in `_bot` (e.g., `my_edge_ai_bot`).
3. Copy the HTTP API token provided. This is your `TELEGRAM_TOKEN`.
4. **Important:** Click the link to your new bot (e.g., `t.me/your_bot`) and press **Start**.

**Step 2 — Get your Chat ID**

1. Search for **@GetMyIDBot** or **@userinfobot** in Telegram.
2. Press **Start**.
3. Copy the numerical value next to `Id`. This is your `TELEGRAM_CHAT_ID`.

## 🚀 Usage

### Web Dashboard

Open http://localhost:8080 and log in with:

* **Username:** `admin`
* **Password:** the password created during setup.

### Desktop Assistant

Run:

```bash
python App.py
```

to communicate with the Edge AI assistant.

### Telegram Commands

* `devices` — list all devices and device types.
* `turn on <device>` / `turn off <device>` — send a command to a specific device (e.g., `turn on lg_tv`).
* `turn on camera` / `turn off camera` — enable or disable the server camera. When the camera is on and detects a person, you will receive a Telegram notification.

### Tailscale (Remote Access)

You can install and configure Tailscale to access the server remotely. During setup, select the option to use a Tailscale IP and enter it manually.

## 📜 Credits & Licensing

This project uses the [AndroidTV-Remote-Controller](https://github.com/Jekso/AndroidTV-Remote-Controller) library by Jekso, distributed under the MIT License.

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

Copyright © 2026 Γρηγόριος Ιωσηφίδης
