# Edge-AI Home Monitoring System

[![CI Tests](https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System/actions/workflows/tests.yml/badge.svg)](https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System/actions/workflows/tests.yml)

A local-first home monitoring and automation system built with Python, Flask/FastAPI, Docker, and edge AI.

<img width="1912" height="968" alt="Edge-AI Home Monitoring System dashboard" src="https://github.com/user-attachments/assets/1977c347-7d0e-4ddf-a71f-89956ec50f26" />

## Overview

The goal of this project is to control smart-home devices locally and keep automation logic on the user's own hardware.

The system can handle device control, automation rules, notifications, camera-based detection, and an AI assistant from a single dashboard.

The main idea is simple:

* Automations are stored locally.
* Device commands are sent over the local network whenever possible.
* The system can continue working when there is no internet connection.
* Different device ecosystems can be managed from the same interface.

The project is still under development, so some integrations are tested while others are currently listed as untested.

## Features

* Local-first home automation
* Smart-device control from a web dashboard
* Flask and FastAPI services
* Local automation manager
* Camera-based person detection
* YOLO-based computer vision
* Telegram notifications
* AI assistant integration
* Docker-based deployment
* GitHub Actions CI tests
* Optional remote access through Tailscale

## Tech Stack

### Backend

* Python
* Flask
* FastAPI

### AI / Computer Vision

* PyTorch
* YOLO
* Triton Inference Server

### Testing

* Pytest
* Pytest-Cov
* GitHub Actions

### Deployment

* Docker
* Docker Compose

### Hardware

* Raspberry Pi and other single-board computers
* RP2040-based microcontrollers
* Network-connected smart-home devices

## Offline Operation

One of the main design goals is to keep automation independent of cloud services.

Automation rules are stored locally in `automations.json` and managed by the `AutomationManager`.

At startup, the system loads the rules from disk and continues running them locally. Depending on the automation, rules can be triggered by schedules, device state changes, or local sensor events.

For example:

```text
22:00 - Internet connection goes down

23:00 - Scheduled automation runs
        Lights are turned off

23:30 - The automation can be verified locally
```

The exact behavior depends on the devices involved. Some devices may still require an internet connection for features that are provided by their manufacturer.

## Automation System

Automation rules are handled locally by the automation manager.

The general flow is:

1. Load automation rules from disk.
2. Check scheduled rules.
3. React to supported local events.
4. Send commands to the relevant devices.
5. Record the result in the local logs.

This means the automation engine itself does not need an external scheduling service.

## Network and Privacy

The project is designed around local processing and local device communication.

Automation data and configuration are stored on the machine running the system. Device commands are sent directly to supported devices or their local APIs.

The project does not require a central cloud backend for its core automation functionality.

Some optional features, such as Telegram notifications, obviously require access to their respective external services.

You can inspect network activity yourself with tools such as `tcpdump`:

```bash
tcpdump -i any 'not (dst 192.168.0.0/16 or dst 10.0.0.0/8 or dst 127.0.0.1)'
```

The result will depend on which features are enabled and which devices or services are being used.

## Supported Devices

### Tapo LED Strips

* L900
* L920 (untested)
* L930 (untested)

### Tapo Light Bulbs

* L510 (untested)
* L520 (untested)
* L530 (untested)
* L535 (untested)
* L610 (untested)
* L630 (untested)

### Tapo Smart Plugs

* P100 (untested)
* P105 (untested)
* P110 (untested)
* P300 (untested)
* P304 (untested)
* P306 (untested)

### Philips Hue

* Lights, bulbs, and LED strips connected through a Philips Hue Bridge (untested)

### Yeelight

* Wi-Fi-enabled light bulbs (untested)

### Android TV

* Android 8+

### LG TV

* webOS 6+

### Daikin AC

* BRP069Axx / BRP069Bxx / BRP072Axx (untested)
* BRP15B61 / AirBase (untested)

### Shelly

* Shelly 1 (untested)
* Shelly 1PM (untested)
* Shelly 2 (untested)
* Shelly 2.5 (untested)
* Shelly 4Pro (untested)
* Shelly Plug (untested)
* Shelly Plug S (untested)
* Shelly Bulb (untested)
* Shelly H&T (untested)
* Shelly Smoke (untested)
* Shelly EM (untested)
* Shelly Flood (untested)

### Kasa Plugs

* EP10 (untested)
* HS103 (untested)
* HS105 (untested)
* HS110 (untested)
* KP100 (untested)
* KP105 (untested)
* KP115 (untested)
* KP125 (untested)
* KP401 (untested)

### Kasa Power Strips

* EP40 (untested)
* HS107 (untested)
* HS300 (untested)
* KP200 (untested)
* KP303 (untested)
* KP400 (untested)

### Kasa Wall Switches

* ES20M (untested)
* HS210 (untested)
* KP405 (untested)
* KS200 (untested)
* KS200M (untested)
* KS220 (untested)
* KS220M (untested)
* KS230 (untested)

### Kasa Bulbs

* KL110 (untested)
* KL120 (untested)
* KL125 (untested)
* KL130 (untested)
* KL135 (untested)
* KL50 (untested)
* KL60 (untested)
* LB110 (untested)

### Kasa Light Strips

* KL400L5 (untested)
* KL420L5 (untested)
* KL430 (untested)

### Broadlink

* RM Home (untested)
* RM Mini 3 (untested)
* RM Plus (untested)
* RM Pro (untested)
* RM Pro+ (untested)
* RM4 Mini (untested)
* RM4 Pro (untested)
* RM4C Mini (untested)
* RM4S (untested)
* RM4 TV Mate (untested)

Broadlink remotes can be used to control compatible infrared devices such as TVs, air conditioners, and decoders.

### Samsung TV

* Samsung Tizen TVs (2016+)

## Installation

The project runs inside Docker containers and is intended to work on Windows, Linux, and macOS.

### Requirements

Install:

* [Git](https://git-scm.com/downloads)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) on Windows/macOS
* Docker Engine and Docker Compose on Linux

Python and the required Python packages are installed inside the containers.

### 1. Clone the repository

```bash
git clone https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System.git
cd Edge-AI-Home-Monitoring-System
```

### 2. Start the application

#### Windows

```bat
start.bat
```

#### Linux / macOS

Make the script executable:

```bash
chmod +x start.sh
```

Then run:

```bash
./start.sh
```

The startup script takes care of the initial setup, including:

* Creating required directories
* Creating the `.env` file when needed
* Building the Docker containers
* Pulling the required Docker images
* Starting the application services

The first startup can take a few minutes because Docker may need to download several images.

### 3. Open the Setup Wizard

Open:

```text
http://localhost:8080
```

The setup wizard will guide you through the initial configuration.

You can configure:

* Administrator password
* Telegram notifications
* Smart devices
* Other system settings

### 4. AI Model

The required AI model is downloaded during the initial setup when it is not already available.

The download time depends on your internet connection and the model size.

### 5. Dashboard

After setup, open:

```text
http://localhost:8080
```

Default username:

```text
admin
```

The password is the one created during the setup process.

## Updating

Pull the latest changes:

```bash
git pull
```

Then restart the application.

### Windows

```bat
start.bat
```

### Linux / macOS

```bash
./start.sh
```

## Telegram Bot

Telegram can be used for notifications and remote commands.

### Get a Bot Token

1. Open Telegram.
2. Search for `@BotFather`.
3. Run `/newbot`.
4. Follow the instructions.
5. Copy the token provided by BotFather.
6. Open the new bot and press **Start**.

The token is used as:

```text
TELEGRAM_TOKEN
```

### Get a Chat ID

You can use bots such as:

* `@GetMyIDBot`
* `@userinfobot`

Start the bot and copy the numerical ID.

This is used as:

```text
TELEGRAM_CHAT_ID
```

## Usage

### Web Dashboard

Open:

```text
http://localhost:8080
```

and log in with the administrator account created during setup.

### Desktop Assistant

Run:

```bash
python App.py
```

to start the desktop assistant.

### Telegram Commands

Some available commands include:

```text
devices
turn on <device>
turn off <device>
turn on camera
turn off camera
```

For example:

```text
turn on lg_tv
```

The camera commands enable or disable the server camera. When person detection is enabled, the system can send a Telegram notification when a person is detected.

### Tailscale

Tailscale can be used for remote access to the system.

During setup, configure the system with the Tailscale IP address when remote access is required.

## Project Status

This project is currently under active development.

Some integrations have been tested with real hardware, while others are included based on compatibility and still need testing.

Expect configuration changes, new integrations, and other changes as the project develops.

## Credits

This project uses the [AndroidTV-Remote-Controller](https://github.com/Jekso/AndroidTV-Remote-Controller) library by Jekso.

The library is distributed under the MIT License.

## License

This project is licensed under the MIT License.

See the [`LICENSE`](LICENSE) file for the full license text.

Copyright © 2026 Γρηγόριος Ιωσηφίδης
