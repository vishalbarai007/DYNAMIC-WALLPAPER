# import os
# import subprocess

# def set_wallpaper(image_path):
#     """Set wallpaper with compatibility for all GNOME versions."""
#     print(f"🖼️ Changing wallpaper to: {image_path}")
#     try:
#         # Try standard GNOME key first
#         subprocess.run(
#             ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{image_path}"],
#             check=True
#         )
#     except subprocess.CalledProcessError:
#         print("⚠️ Failed to set using 'picture-uri' key")

#     # Try dark mode key (optional)
#     try:
#         subprocess.run(
#             ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", f"file://{image_path}"],
#             check=True
#         )
#     except subprocess.CalledProcessError:
#         print("⚠️ Your GNOME version might not support 'picture-uri-dark' key. Using standard one instead.")
import subprocess
import os

def detect_color_scheme():
    """Detects GNOME dark/light mode safely."""
    try:
        # Try GNOME's newer color-scheme key (GNOME 42+)
        result = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip().replace("'", "").lower()

        if "dark" in result:
            return "dark"
        else:
            return "light"

    except subprocess.CalledProcessError:
        # Fallback: Try GTK theme name for older GNOME/X11
        try:
            theme = subprocess.check_output(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip().replace("'", "").lower()

            if "dark" in theme:
                return "dark"
            else:
                return "light"
        except Exception:
            # Default fallback
            return "light"


def set_wallpaper(image_path: str):
    """Set wallpaper for GNOME light/dark mode dynamically."""
    if not os.path.exists(image_path):
        print(f"⚠️ Wallpaper file not found: {image_path}")
        return

    color_mode = detect_color_scheme()

    try:
        if color_mode == "dark":
            print("🌙 Dark mode detected — using picture-uri-dark key")
            subprocess.run([
                "gsettings", "set",
                "org.gnome.desktop.background", "picture-uri-dark",
                f"file://{image_path}"
            ], check=False)
        else:
            print("🌞 Light mode detected — using picture-uri key")
            subprocess.run([
                "gsettings", "set",
                "org.gnome.desktop.background", "picture-uri",
                f"file://{image_path}"
            ], check=False)

        print(f"✅ Wallpaper set successfully: {image_path}")

    except Exception as e:
        print(f"⚠️ Error while setting wallpaper: {e}")
