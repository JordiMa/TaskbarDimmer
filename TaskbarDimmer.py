import pyautogui
import time
import tkinter as tk
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import threading
import queue
import json
import os
import platform
import subprocess
import ctypes
from ctypes import wintypes

# Global declaration for icon
tray_icon = None


def get_documents_folder():
    if platform.system() == "Windows":
        csidl_personal = 5  # My Documents
        shgfp_type_current = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, csidl_personal, None, shgfp_type_current, buf)
        return buf.value
    else:
        return os.path.expanduser("~/Documents")


def load_config():
    default_config = {
        "taskbar_height": 60,
        "base_opacity_percent": 70,  # Default value in percentage
        "taskbar_detection_height": 60
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                # Ensure all default config keys are present and converted to integers
                config["base_opacity_percent"] = int(
                    config.get("base_opacity_percent", default_config["base_opacity_percent"]))
                config["taskbar_height"] = int(config.get("taskbar_height", default_config["taskbar_height"]))
                config["taskbar_detection_height"] = int(
                    config.get("taskbar_detection_height", default_config["taskbar_detection_height"]))
                return config
        except json.JSONDecodeError:
            return default_config
    return default_config


def save_config(config):
    try:
        # Convert values to integers before saving
        config["base_opacity_percent"] = int(config["base_opacity_percent"])
        config["taskbar_height"] = int(config["taskbar_height"])
        config["taskbar_detection_height"] = int(config["taskbar_detection_height"])
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file)
    except IOError as e:
        print(f"Error saving configuration: {e}")


def create_black_overlay():
    overlay = tk.Toplevel()
    overlay.overrideredirect(True)
    overlay.geometry(f"{screen_width}x{config['taskbar_height']}+0+{screen_height - config['taskbar_height']}")
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", config["base_opacity_percent"] / 100)
    overlay.configure(bg='black')
    overlay.bind("<Button-1>", lambda e: "break")

    # Make the window click-through on Linux
    if platform.system() == "Linux":
        overlay.update_idletasks()
        window_id = overlay.winfo_id()
        set_clickthrough_linux(window_id)

    return overlay


def set_clickthrough_linux(window_id):
    script = f'''
    xprop -id {window_id} -f _NET_WM_WINDOW_TYPE 32a -set _NET_WM_WINDOW_TYPE _NET_WM_WINDOW_TYPE_DOCK
    xprop -id {window_id} -f _NET_WM_STATE 32a -set _NET_WM_STATE _NET_WM_STATE_BELOW
    xprop -id {window_id} -remove _NET_WM_WINDOW_OPACITY
    '''
    subprocess.run(script, shell=True, check=True)


def create_default_icon():
    width = 64
    height = 64
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((width * 0.2, height * 0.2, width * 0.8, height * 0.8), fill="black")
    return image


def quit_app():
    global tray_icon
    tray_icon.stop()  # Stop the system tray icon
    global running
    running = False  # Set the global flag to stop the main loop
    root.quit()  # Close the Tkinter main window


def open_config_window():
    config_window = tk.Toplevel(root)
    config_window.title("Configuration")
    config_window.geometry("300x300")

    tk.Label(config_window, text="Taskbar Height:").pack(pady=5)
    taskbar_height_entry = tk.Entry(config_window)
    taskbar_height_entry.pack(pady=5)
    taskbar_height_entry.insert(0, config["taskbar_height"])

    tk.Label(config_window, text="Taskbar Detection Height:").pack(pady=5)
    taskbar_detection_height_entry = tk.Entry(config_window)
    taskbar_detection_height_entry.pack(pady=5)
    taskbar_detection_height_entry.insert(0, config["taskbar_detection_height"])

    tk.Label(config_window, text="Base Opacity (%):").pack(pady=5)
    base_opacity_entry = tk.Entry(config_window)
    base_opacity_entry.pack(pady=5)
    base_opacity_entry.insert(0, config["base_opacity_percent"])

    def save_config_window():
        try:
            config["taskbar_height"] = int(taskbar_height_entry.get())
            config["base_opacity_percent"] = int(float(base_opacity_entry.get()))  # Convert to integer
            config["taskbar_detection_height"] = int(taskbar_detection_height_entry.get())
            save_config(config)
            overlay.geometry(f"{screen_width}x{config['taskbar_height']}+0+{screen_height - config['taskbar_height']}")
            overlay.attributes("-alpha", config["base_opacity_percent"] / 100)
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid values.")
        config_window.destroy()

    tk.Button(config_window, text="Save", command=save_config_window).pack(pady=20)


def show_config_window():
    q.put(open_config_window)


def create_system_tray_icon():
    global tray_icon
    icon_image = create_default_icon()
    icon_menu = Menu(
        MenuItem('Configuration', show_config_window),
        MenuItem('Quit', quit_app)
    )
    tray_icon = Icon("Taskbar Dimmer", icon_image, "Taskbar Dimmer", icon_menu)
    tray_icon.run()


def smooth_transition(overlay, start_opacity, end_opacity, duration=0.1, steps=30):
    step_duration = duration / steps
    step_opacity = (end_opacity - start_opacity) / steps
    for step in range(steps):
        current_opacity = start_opacity + step * step_opacity
        overlay.attributes("-alpha", current_opacity)
        overlay.update()
        time.sleep(step_duration)
    overlay.attributes("-alpha", end_opacity)


def keep_overlay_on_top(overlay):
    overlay.attributes("-topmost", True)
    overlay.lift()


def process_queue():
    try:
        task = q.get_nowait()
        task()
    except queue.Empty:
        pass
    root.after(100, process_queue)


# Initialization
user_documents = get_documents_folder()
app_folder = os.path.join(user_documents, "JordiMA", "TaskbarDimmer")
CONFIG_FILE = os.path.join(app_folder, "config.json")
os.makedirs(app_folder, exist_ok=True)
config = load_config()

screen_width, screen_height = pyautogui.size()
root = tk.Tk()
root.withdraw()
q = queue.Queue()

overlay = create_black_overlay()
overlay.attributes("-alpha", config["base_opacity_percent"] / 100)

# Declaration of taskbar_dimmed
taskbar_dimmed = False

running = True
icon_thread = threading.Thread(target=create_system_tray_icon)
icon_thread.start()

root.after(100, process_queue)

try:
    while running:
        x, y = pyautogui.position()
        keep_overlay_on_top(overlay)
        if y >= screen_height - config["taskbar_detection_height"]:
            if not taskbar_dimmed:
                smooth_transition(overlay, config["base_opacity_percent"] / 100, 0.0)
                overlay.withdraw()  # Hide the overlay to allow clicks to pass through
                taskbar_dimmed = True
        else:
            if taskbar_dimmed:
                overlay.deiconify()  # Show the overlay again
                smooth_transition(overlay, 0.0, config["base_opacity_percent"] / 100)
                taskbar_dimmed = False
        overlay.update()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting Taskbar Dimmer...")
finally:
    quit_app()
