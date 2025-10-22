import os
import sys
import json
import time
import random
import argparse
import subprocess
from datetime import datetime
from utils.online_fetch import fetch_online_wallpaper
import os


# --- Fix imports when running from root or scripts directory ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.weather import get_weather_category
from utils.wallpaper_changer import set_wallpaper
from utils.online_fetch import fetch_online_wallpaper
from utils.category_builder import add_new_category

# --- Base directories ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")
CATEGORIES_PATH = os.path.join(BASE_DIR, "categories")


import os
import getpass

# Auto-fix for VS Code / cron where GNOME session vars are missing
if "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
    uid = os.getuid()
    possible_bus = f"/run/user/{uid}/bus"
    if os.path.exists(possible_bus):
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={possible_bus}"


if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
    try:
        pid = subprocess.check_output(["pgrep", "-u", os.getlogin(), "gnome-session"]).decode().split()[0]
        env_data = subprocess.check_output(["grep", "-z", "DBUS_SESSION_BUS_ADDRESS", f"/proc/{pid}/environ"])
        dbus_address = env_data.decode().split("=", 1)[1]
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = dbus_address
        print("🔗 Linked to GNOME DBus session for wallpaper control.")
    except Exception as e:
        print(f"⚠️ Could not link GNOME DBus session automatically: {e}")


# ---------------- CONFIG LOADER ----------------
def load_config():
    if not os.path.exists(CONFIG_PATH):
        print("No config.json found. Please create one before running.")
        exit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

# ---------------- THEME DETECTOR ----------------
def is_dark_mode():
    """Check if GNOME is currently using dark mode."""
    try:
        print("🧩 Checking GNOME color scheme...")
        schema_keys = subprocess.check_output(
            ["gsettings", "list-keys", "org.gnome.desktop.interface"],
            text=True
        )
        print("Available keys:", schema_keys)

        if "color-scheme" in schema_keys:
            mode = subprocess.check_output(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                text=True
            ).strip().lower()
            print(f"🌓 Detected color-scheme value: {mode}")
            return "dark" in mode
        else:
            print("⚠️ color-scheme key not found, checking gtk-theme instead...")
            gtk_theme = subprocess.check_output(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                text=True
            ).strip().lower()
            print(f"🎨 GTK theme: {gtk_theme}")
            return "dark" in gtk_theme

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running gsettings: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Unexpected error in dark mode detection: {e}")
        return False


# ---------------- TIME CATEGORY ----------------
def get_current_time_category(config):
    """Return category based on current system time."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return config["time_categories"].get("morning")
    elif 12 <= hour < 17:
        return config["time_categories"].get("afternoon")
    elif 17 <= hour < 21:
        return config["time_categories"].get("evening")
    else:
        return config["time_categories"].get("night")

# ---------------- WALLPAPER PICKER ----------------
def choose_wallpaper(base_cycle, category):
    """Randomly select a wallpaper from the given category."""
    folder = os.path.join(CATEGORIES_PATH, base_cycle, category)
    if not os.path.exists(folder):
        print(f"⚠️ Category folder '{folder}' not found.")
        return None

    wallpapers = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if not wallpapers:
        print(f"⚠️ No wallpapers found in '{folder}'.")
        return None

    return random.choice(wallpapers)

# ---------------- MAIN FUNCTION ----------------
def main():
    parser = argparse.ArgumentParser(description="🌄 Dynamic Wallpaper Manager for Linux (Ubuntu)")
    parser.add_argument("--category", help="Manually switch to a specific category (e.g. evening, night, cars)")
    parser.add_argument("--once", action="store_true", help="Change wallpaper once and exit")
    parser.add_argument("--add-category", help="Create a new category folder")
    args = parser.parse_args()

    # Load config
    config = load_config()
    base_cycle = config.get("base_cycle", "cycle24hour")
    mode = config.get("mode", "time")

    # Add new category
    if args.add_category:
        add_new_category(os.path.join(base_cycle, args.add_category))
        return

    # ✅ Determine starting category first
    if args.category:
        category = args.category
    elif mode == "weather" and config.get("use_weather"):
        category = get_weather_category(config.get("api_key")) or get_current_time_category(config)
    else:
        category = get_current_time_category(config)

    previous_category = None  # Track when category changes

    # ✅ Now handle online or local wallpaper after category is known
    if config.get("use_online_wallpapers", False):
        print(f"🌐 Fetching online wallpaper for category: {category}")
        wallpaper_path = fetch_online_wallpaper(category, os.path.join(os.getcwd(), "temp"), config.get("unsplash_access_key"))
        if wallpaper_path:
            set_wallpaper(wallpaper_path)
        else:
            print("⚠️ Failed to fetch online wallpaper.")
        if args.once:
            return
    else:
        # Main wallpaper loop for local wallpapers
        previous_category = None
        previous_dark_mode = None

        while True:
            current_category = get_current_time_category(config)
            dark = is_dark_mode()

            # Detect changes
            category_changed = current_category != previous_category
            theme_changed = dark != previous_dark_mode

            if category_changed or theme_changed:
                change_reason = []
                if category_changed:
                    change_reason.append(f"time → '{current_category}'")
                if theme_changed:
                    change_reason.append("theme change (Dark ↔ Light)")

                print(f"🔄 Change detected ({' & '.join(change_reason)}) — updating wallpaper...")

                wallpaper = choose_wallpaper(base_cycle, current_category)
                if wallpaper:
                    theme_text = "🌑 Dark mode" if dark else "☀️ Light mode"
                    print(f"{theme_text} — applying wallpaper: {os.path.basename(wallpaper)}")
                    set_wallpaper(wallpaper)
                else:
                    print("⚠️ Skipping wallpaper change...")

                previous_category = current_category
                previous_dark_mode = dark

            else:
                print("⏳ No change detected — waiting...")

            if args.once:
                break

            interval = config.get("interval_minutes", 15) * 60
            time.sleep(interval)

if __name__ == "__main__":
    main()
