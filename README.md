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

* Android Tv

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

1. Open setup.bat if you are in windows or setup.sh if you are in linux or mac
2. Press "Install Dependencies" to install all the requirement python packages
3. Go to ollama.com and download it.
4. Press "Download AI Model (Phi3).
5. Press "Next".
6. Add your devices(For now it is only suppourt android tv and tapo L900 led strip)
7. Close the window.


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

## 🏃 How to Run

Once the installation and setup are complete, you can start the Edge-AI hub using the automated execution scripts.

### 🪟 On Windows
Navigate to the project directory and double-click the execution script, or run it via terminal:
run.bat

### 🐧 On Linux or Mac
Navigate to the project directory and double-click the execution script, or run it via terminal:
run.sh

## How to use it

### On web browser
Open the adress of the server on port 8080.

### Via app
Open the App.py to communicate with the chatbot from your computer.

## 📜 Credits & Licensing
This project utilizes the AndroidTV-Remote-Controller library by Jekso, which is distributed under the MIT License.

## 📝 License
This project is licensed under the MIT License. See the LICENSE file for more details.
Copyright (c) 2026 Γρηγόριος Ιωσηφίδης
