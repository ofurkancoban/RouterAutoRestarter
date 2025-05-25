# 🚀 RouterAutoRestarter

**RouterAutoRestarter** is a lightweight system tray application that monitors your internet connection and automatically reboots your **TP-Link TL-WR940N** modem if the connection is lost. It works silently in the background and notifies you through native Windows toast notifications.

---

## ✅ Features

- 📡 Checks internet connection every 60 seconds
- ♻️ Automatically reboots modem via headless Chromium + Playwright
- 🖱️ Manual reboot from tray menu
- ⚙️ Settings UI with:
  - Router password input
  - View logs
  - Delete/Reinstall Chromium
  - GitHub link
- 📝 Logs saved to:
  ```
  C:\Users\<username>\AppData\Local\RouterAutoRestarter\router_restarter.log
  ```
- 🛠 Auto-start with Windows
- 🔔 Native toast notifications
- 🧩 Chromium bundled as zip and auto-extracted on first run

---

## 💻 Run as Python Script (Developer Mode)

### ✅ Requirements

- Windows 10 or later
- Python 3.11+
- TP-Link TL-WR940N router with iframe-based admin panel

### 📦 Install Dependencies

```bash
pip install playwright pystray pillow win10toast-click
playwright install chromium
```

### ▶️ Run the app

```bash
python RouterAutoRestarter.py
```

---

## 📦 Run as Standalone Executable (.exe)

### 🗂 Included Files

- `RouterAutoRestarter.exe` – Main application
- `chromium.zip` – Chromium for Playwright (auto-extracted on first run)
- `router.ico` – App icon

### ▶️ How to Use

1. Download the latest `.zip` from [Releases](https://github.com/ofurkancoban/RouterAutoRestarter/releases)
2. Extract to a folder, e.g. `C:\Tools\RouterAutoRestarter`
3. Run `RouterAutoRestarter.exe`
4. The tray icon will appear in the bottom-right corner
5. Right-click the icon to open Settings or trigger a manual reboot
6. Chromium will be auto-extracted silently (if not already installed)

---

## 🧪 Tested On

- ✅ Windows 10, 11 (x64)
- ✅ TP-Link TL-WR940N
- ❌ Not tested on other routers (may not work with non-iframe UIs)

---

## 🔐 Data & Privacy

- No data leaves your device.
- All settings, password and logs are stored locally.
- No telemetry, no internet usage beyond router interaction.

---

## 🧰 Advanced: Build Your Own `.exe`

If you'd like to build a custom standalone binary:

### 🧩 Requirements

- `chromium.zip` (create by zipping the Playwright Chromium folder)
- `router.ico`

### ⚙️ Build Command

```bash
pyinstaller --noconsole --onefile RouterAutoRestarter.py --icon=router.ico --add-data "chromium.zip;." --add-data "router.ico;."
```

Output `.exe` will be in the `dist/` folder.

---
