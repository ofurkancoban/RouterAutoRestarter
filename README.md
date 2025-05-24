# RouterAutoRestarter

**RouterAutoRestarter** is a system tray application that automatically monitors your internet connection and restarts your TP-Link TL-WR940N modem if the connection is lost.

## Features

- 📡 Periodic internet connection checks
- ♻️ Automatic modem reboot if connection is lost
- 🖱️ Manual reboot from the system tray
- 📝 Log file viewer and configuration UI
- 🔒 Stores password and settings locally
- 🪟 Works in the background with a tray icon

## Requirements

- Python 3.8+
- TP-Link TL-WR940N router with web admin access
- `playwright`, `pystray`, `Pillow` installed
- `tkinter` available in your Python installation (standard library)

## Installation

1. Clone or download this repository.
2. Install dependencies:

```bash
pip install pystray pillow playwright
playwright install
python RouterAutoRestarter.py