# Edge-AI Home Monitoring System

### A privacy-first, edge-AI home automation hub using Linux, Flask, and real-time control to orchestrate smart devices.

<img width="1912" height="968" alt="Screenshot 2026-06-03 172605" src="https://github.com/user-attachments/assets/1977c347-7d0e-4ddf-a71f-89956ec50f26" />

## 🚀 Features
* Control devices seamlessly via dashboard remotely without port forwarding.
* Real time control using a smart assistant
* Edge AI for communication and commands.

## Suppourted Devices

* Tapo Led Strips: 
- L900
- L920
- L930

* Tapo Light Bulbs:
- L510
- L520
- L530
- L535
- L610
- L630

* Tapo Smart Plugs:
- P100
- P105
- P110
- P300
- P304
- P306

* Android Tv
* Android Tv:
- Android 8+

* LG TV:
- WEB OS 6+
(Coming Soon)

## 🛠 Tech Stack

* **Language:** Python 3.11
* **Core Library:** [AndroidTV-Remote-Controller](https://github.com/Jekso/AndroidTV-Remote-Controller)
* **Interface Tool:** Android Debug Bridge (ADB)
* **Environment:** Designed for Linux (Raspberry Pi compatible) / Windows / macOS
* **Main Hardware:** An old laptop


## 📦 Installation
### Clone the repository:

Bash
git clone https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System/

### Install the required dependencies:
1. Download and Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Download and Install [Python 3.11](https://www.python.org/downloads/)
4. Download and Install [Download SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools). Then follow the steps below to add it to path.
5. Install Telegram, Create an account and then create a bot [Download here](https://telegram.org/) and learn more below
5. Open setup.bat if you are in windows or setup.sh if you are in linux or mac
6. Press "Install Dependencies" to install all the requirement python packages and ollama if you dont have it already.
7. Press "Download AI Model (Phi3).
8. Press "Next".
9. Add your telegram bot token and chat id.
10. Press "Next"
11. Add your devices (For LG TV you must have powered on the tv and press yes)
12. Close the window.


### Install Android SDK platform tools

* **Find it here:** [Download SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools)

* **Add to PATH:**
  1. **Download and Extract:** Download the zip file and extract it to a permanent folder on your machine (e.g., `/opt/platform-tools` or `C:\tools\platform-tools`).
  2. **Linux / macOS:** Add the following line to your `~/.bashrc` or `~/.zshrc` file:
     ```bash
     export PATH=$PATH:/your/extracted/path/platform-tools
     ```
     Then run `source ~/.bashrc` to apply the changes.
  3. **Windows:** Search for "Edit the system environment variables" in the Start menu, go to **Environment Variables**, select **Path**, click **Edit**, and add the full path to your extracted `platform-tools` folder.
  4. **Verify:** Open a new terminal and type `adb version` to confirm the installation.

### 🤖 Telegram Bot Configuration
Your system needs a Bot Token and a Chat ID to send real-time alerts.

1. Step 1: Get your Bot Token
* Open Telegram and search for @BotFather (official verified bot).

* Send /newbot and follow the prompts to choose a Name and a unique Username ending in _bot (e.g., my_edge_ai_bot).

* Copy the HTTP API Token provided. This is your TELEGRAM_TOKEN.

* Crucial: Click the link to your new bot (e.g., t.me/your_bot) and press START.

2. Step 2: Get your Chat ID
* Search for @GetMyIDBot or @userinfobot in Telegram.

* Press START.

* Copy the numerical value next to Id. This is your TELEGRAM_CHAT_ID.

## 🏃 How to Run

Once the installation and setup are complete, you can start the Edge-AI hub using the automated execution scripts.

### 🪟 On Windows
Navigate to the project directory open .bin folder double-click the execution script run.bat

### 🐧 On Linux or Mac
Cooming soon!

## How to use it

### On web browser
Open the adress of the server on port 8080.

### Via app
Open the App.py to communicate with the chatbot from your computer.

### Using Telegram
You can use the following commands: 

* To give you a list of devices and dev types: devices.
* To send a command for device: [command] [device]. For example: Turn on lg_tv.
* To turn on/off camera: turn on/off camera.(Server camera, If the camera is on and it see a person, you will receive notifications in telegram).

### Tailscale
You can download and setup tailscale to have remote access on the server:

* You must select to use tailscale ip on setup and type the ip manualy

## 📜 Credits & Licensing
This project utilizes the AndroidTV-Remote-Controller library by Jekso, which is distributed under the MIT License.

## 📝 License
This project is licensed under the MIT License. See the LICENSE file for more details.
Copyright (c) 2026 Γρηγόριος Ιωσηφίδης
