import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import keyboard
import time
import pygetwindow as gw
from sys import platform
import pystray
from pystray import MenuItem as item, Icon as icon, Menu as menu
from PIL import Image

class AntiAFKApp:
    def __init__(self, master):
        self.master = master
        master.title("\033[1;31mGelvey's FiveM Anti-AFK Script\033[0m")

        # Set default values
        self.application_focus_enabled = True
        self.auto_afk_enabled = False
        self.key_interval = 2
        self.countdown_interval = 3 * 60
        self.mute_game_on_enable = False
        self.last_input_time = time.time()
        self.idle_threshold = 120  # 2 minutes
        self.script_running = False

        self.create_widgets()

    def create_widgets(self):
        # GUI Elements
        self.enable_afk_var = tk.IntVar()
        self.enable_focus_var = tk.IntVar()
        self.mute_game_var = tk.IntVar()

        ttk.Label(self.master, text="Options:").grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        # Enable AFK Checkbox
        ttk.Checkbutton(self.master, text="Enable Anti-AFK", variable=self.enable_afk_var).grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

        # Enable Focus Checkbox
        ttk.Checkbutton(self.master, text="Enable Application Focus", variable=self.enable_focus_var, command=self.toggle_focus).grid(row=2, column=0, columnspan=2, pady=5, sticky="w")

        # Mute Game Checkbox
        ttk.Checkbutton(self.master, text="Mute Game on Enable", variable=self.mute_game_var).grid(row=3, column=0, columnspan=2, pady=5, sticky="w")

        # Key Interval Entry
        ttk.Label(self.master, text="Key Press Interval (seconds):").grid(row=4, column=0, columnspan=2, pady=5, sticky="w")
        self.key_interval_entry = ttk.Entry(self.master)
        self.key_interval_entry.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

        # Countdown Interval Entry
        ttk.Label(self.master, text="Countdown Interval (seconds):").grid(row=6, column=0, columnspan=2, pady=5, sticky="w")
        self.countdown_interval_entry = ttk.Entry(self.master)
        self.countdown_interval_entry.grid(row=7, column=0, columnspan=2, pady=5, sticky="w")

        # Start Button
        ttk.Button(self.master, text="Start Script", command=self.start_script).grid(row=8, column=0, pady=10, sticky="w")

        # Stop Button
        ttk.Button(self.master, text="Stop Script", command=self.stop_script).grid(row=8, column=1, pady=10, sticky="e")
        
        # Test Button
        ttk.Button(self.master, text="Test Console Output", command=self.print_test_message).grid(row=10, column=0, pady=10, sticky="w")
        
        # Minimize to Tray Button
        ttk.Button(self.master, text="Minimize to Tray", command=self.minimize_to_tray).grid(row=10, column=1, pady=10, sticky="e")
        
        # Set the icon for the main window
        self.master.iconbitmap(default='icon.ico')  # Replace 'your_icon.ico' with the path to your icon file
        
        # Initialize system tray icon
        self.icon = None

        # Console Output
        self.console_output = tk.Text(self.master, height=10, width=60)
        self.console_output.grid(row=9, column=0, columnspan=2, pady=10, sticky="w")
        
    def minimize_to_tray(self):
        self.master.withdraw()  # Hide the main window
        image = Image.open('icon.ico')  # Replace 'your_icon.ico' with the path to your icon file
        menu = (item('Open', self.restore_from_tray), item('Exit', self.on_closing))
        self.icon = pystray.Icon("test_icon", image)
        self.icon.menu = menu
        self.icon.run()

    def restore_from_tray(self, icon, item):
        icon.stop()
        self.master.attributes("-topmost", True)  # Bring the window to the top
        self.master.deiconify()  # Restore the main window from the tray if it was hidden
        self.master.lift()  # Bring the main window to the front

    def on_closing(self):
        if self.icon:
            self.icon.stop()  # Stop the system tray icon
        if not hasattr(self, '_destroyed'):
            self.master.destroy()
            self._destroyed = True
        
    def print_test_message(self):
        self.print_to_console("This is a test message.")
        
    def print_to_console(self, text):
        self.console_output.config(state=tk.NORMAL)
        self.console_output.insert(tk.END, text + "\n")
        self.console_output.config(state=tk.DISABLED)
        self.console_output.see(tk.END)  # Scroll to the end

    def toggle_focus(self):
        self.application_focus_enabled = not self.application_focus_enabled

    def start_script(self):
        try:
            self.auto_afk_enabled = self.enable_afk_var.get()
            self.application_focus_enabled = self.enable_focus_var.get()
            self.mute_game_on_enable = self.mute_game_var.get()
            self.key_interval = int(self.key_interval_entry.get()) if self.key_interval_entry.get() else 2
            self.countdown_interval = int(self.countdown_interval_entry.get()) if self.countdown_interval_entry.get() else 180

            if self.mute_game_on_enable:
                self.mute_game()

                self.master.iconify()  # Minimize to tray
                self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)  # Handle window close

                self.run_script()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for intervals.")

    def stop_script(self):
        self.script_running = False

    def mute_game(self):
        # Implement game muting logic here
        pass

    def run_script(self):
        self.script_running = True
        try:
            while self.script_running:
                self.check_input_idle()

                if self.auto_afk_enabled and self.is_application_focused():
                    self.perform_afk_actions()

                time.sleep(1)

        except KeyboardInterrupt:
            self.on_closing()

    def check_input_idle(self):
        if not keyboard.is_pressed():
            # No key is currently pressed, consider the keyboard as idle
            if time.time() - self.last_input_time > self.idle_threshold:
                self.last_input_time = time.time()

    def is_application_focused(self):
        if not self.application_focus_enabled:
            return True

        active_window = gw.getActiveWindow()
        focused_title = active_window.title.lower() if active_window else None
        return focused_title and "fivem" in focused_title and "fat duck gaming" in focused_title

    def perform_afk_actions(self):
        self.print_to_console("Pressing 'w' key for 2 seconds...")
        keyboard.press('w')
        time.sleep(self.key_interval)
        keyboard.release('w')

        self.print_to_console("Pressing 's' key for 2 seconds...")
        keyboard.press('s')
        time.sleep(self.key_interval)
        keyboard.release('s')

        self.countdown_timer(self.countdown_interval)
        self.print_to_console("Waiting for the next interval...\n")

    def countdown_timer(self, seconds):
        for remaining in range(seconds, 0, -1):
            minutes, secs = divmod(remaining, 60)
            time.sleep(1)
            print(f"\rCountdown: {minutes} minute{'s' if minutes != 1 else ''} {secs} second{'s' if secs != 1 else ''}", end='', flush=True)
        print("\nCountdown: 0 minutes 0 seconds")

# Main
if __name__ == "__main__":
    root = tk.Tk()

    app = AntiAFKApp(root)

    root.mainloop()