# Edge-AI Home Monitoring System

### A privacy-first, edge-AI home automation hub using Linux, Flask, and real-time computer vision to orchestrate smart devices.

<img width="1919" height="1019" alt="Screenshot 2026-06-02 161514" src="https://github.com/user-attachments/assets/7124a22d-f178-4773-baee-44437cc92437" />


## 🚀 Features
* Control devices seamlessly via dashboard remotely without port forwarding.
* Real time control using a camera and a smart assistant/
* Edge AI for basic communication and commands.


## 🛠 Tech Stack

* **Language:** Python 3.11
* **Core Library:** [AndroidTV-Remote-Controller](https://github.com/Jekso/AndroidTV-Remote-Controller)
* **Interface Tool:** Android Debug Bridge (ADB)
* **Environment:** Designed for Linux (Raspberry Pi compatible) / Windows / macOS
* **Main Hardware:** A old laptop


## 📦 Installation
### Clone the repository:

Bash
git clone https://github.com/travletothefurureprogramming/Edge-AI-Home-Monitoring-System/

### Install the required dependencies:

Bash
pip install -r requirements.txt

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

## 📜 Credits & Licensing
This project utilizes the AndroidTV-Remote-Controller library by Jekso, which is distributed under the MIT License.

## 📝 License
This project is licensed under the MIT License. See the LICENSE file for more details.
Copyright (c) 2026 Γρηγόριος Ιωσηφίδης
