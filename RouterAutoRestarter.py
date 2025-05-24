import threading
import logging
import json
import os
import time
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import socket
import winreg

APP_NAME = "RouterAutoRestarter"
SETTINGS_FILE = Path.home() / ".router_restarter_config.json"
LOG_FILE = Path.home() / "router_restarter.log"
ICON_PATH = Path(getattr(sys, '_MEIPASS', Path(__file__).parent)) / "router.ico"
EXECUTABLE_PATH = sys.executable
CHECK_INTERVAL = 60
REBOOT_WAIT = 180
settings = {"password": "", "auto_reboot": True, "auto_start": False}
last_reboot_time = None
is_running = True

def generate_default_icon():
    image = Image.new("RGB", (64, 64), (0, 128, 255))
    draw = ImageDraw.Draw(image)
    draw.text((18, 20), "M", fill="white")
    return image

def load_settings():
    global settings
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings.update(json.load(f))
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def set_autostart(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{EXECUTABLE_PATH}"')
        else:
            winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except Exception as e:
        logging.error(f"Autostart error: {e}")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def notify(icon, title, message):
    try:
        if icon:
            icon.notify(message, title=title)
        logging.info(f"[Notify] {title}: {message}")
    except Exception as e:
        logging.error(f"Notification failed: {e}")

def internet_ok():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def reboot_modem(triggered_by_user=False, icon=None):
    global last_reboot_time
    logging.info("Rebooting router...")
    notify(icon, "RouterAutoRestarter", "Router is being rebooted...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("http://192.168.0.1")
            page.fill('input[type="password"]', settings.get("password", ""))
            page.click('label.loginBtn')
            page.wait_for_timeout(3000)
            menu_frame = page.frame(name="bottomLeftFrame")
            main_frame = page.frame(name="mainFrame")
            if not menu_frame or not main_frame:
                raise Exception("Frames not found")
            menu_frame.click('xpath=/html/body/menu/ol[49]/li/a')
            page.wait_for_timeout(1000)
            menu_frame.click('xpath=/html/body/menu/ol[56]/li/a')
            page.wait_for_timeout(1000)
            main_frame.evaluate("window.confirm = () => true; window.alert = () => {};")
            main_frame.click('input[name="Reboot"]')
            page.wait_for_timeout(2000)
            browser.close()
        last_reboot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info("Reboot triggered successfully")
    except Exception as e:
        logging.error(f"Router reboot failed: {e}")
        notify(icon, "Router Restarter", f"Reboot failed: {e}")
    return True

def monitor(icon):
    global is_running
    internet_was_down = False
    while is_running:
        if not internet_ok():
            logging.info("Internet down")
            if settings.get("auto_reboot", True) and not internet_was_down:
                reboot_modem(icon=icon)
                internet_was_down = True
        else:
            if internet_was_down:
                logging.info("Internet restored")
                notify(icon, "RouterAutoRestarter", "Internet connection restored.")
            internet_was_down = False
        time.sleep(CHECK_INTERVAL)

def show_settings_ui():
    def on_save():
        settings["password"] = password_var.get()
        save_settings()
        messagebox.showinfo("Settings", "Settings saved successfully.")

    win = tk.Tk()
    win.title("Settings")
    if ICON_PATH.exists():
        try:
            win.iconbitmap(default=str(ICON_PATH))
        except Exception as e:
            logging.warning(f"Failed to set window icon: {e}")
    win.geometry("220x180+1600+600")
    win.resizable(False, False)

    ttk.Label(win, text="Router Password:").pack(pady=(10, 0))
    password_var = tk.StringVar(value=settings.get("password", ""))
    ttk.Entry(win, textvariable=password_var, show="*").pack(fill="x", padx=10)

    ttk.Button(win, text="Save", command=on_save).pack(pady=5)
    ttk.Button(win, text="Open Log", command=lambda: os.startfile(LOG_FILE)).pack(pady=2)
    ttk.Button(win, text="GitHub", command=lambda: os.system("start https://github.com/ofurkancoban/RouterAutoRestarter")).pack(pady=2)
    ttk.Button(win, text="Close", command=win.destroy).pack(pady=(2, 10))

    win.mainloop()
    return True

def toggle_auto_reboot(icon):
    settings["auto_reboot"] = not settings.get("auto_reboot", True)
    save_settings()
    icon.menu = build_menu(icon)
    return True

def toggle_auto_start(icon):
    settings["auto_start"] = not settings.get("auto_start", False)
    save_settings()
    set_autostart(settings["auto_start"])
    icon.menu = build_menu(icon)
    return True

def on_quit(icon, item=None):
    global is_running
    is_running = False
    icon.stop()
    return True

def build_menu(icon):
    return Menu(
        Item("Restart Router Now", lambda icon, item: reboot_modem(triggered_by_user=True, icon=icon)),
        Item("Auto Reboot", lambda icon, item: toggle_auto_reboot(icon), checked=lambda item: settings.get("auto_reboot", True)),
        Item("Auto Start with Windows", lambda icon, item: toggle_auto_start(icon), checked=lambda item: settings.get("auto_start", False)),
        Item(f"Last Reboot: {last_reboot_time or 'N/A'}", None, enabled=False),
        Item("Settings", lambda icon, item: show_settings_ui()),
        Item("Open Log File", lambda icon, item: os.startfile(LOG_FILE) or True),
        Item("Quit", lambda icon, item: on_quit(icon))
    )

def run_tray():
    icon = Icon(APP_NAME)
    try:
        icon.icon = Image.open(ICON_PATH)
    except Exception as e:
        logging.warning(f"Tray icon fallback used: {e}")
        icon.icon = generate_default_icon()
    icon.menu = build_menu(icon)
    threading.Thread(target=monitor, args=(icon,), daemon=True).start()
    icon.run()

if __name__ == "__main__":
    load_settings()
    if settings.get("auto_start"):
        set_autostart(True)
    run_tray()
