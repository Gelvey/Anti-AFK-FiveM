import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import keyboard
import time
import pygetwindow as gw
import pystray
from PIL import Image

class AntiAFKApp:
    ICON_PATH = 'icon.ico'
    IDLE_THRESHOLD = 120
    DEFAULT_KEY_INTERVAL = 2
    DEFAULT_COUNTDOWN_INTERVAL = 180

    def __init__(self, master):
        self.master = master
        master.title("\033[1;31mGelvey's FiveM Anti-AFK Script\033[0m")
        self.create_widgets()

    def create_widgets(self):
        self.create_gui_elements()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.iconbitmap(default=self.ICON_PATH)
        self.icon = None

    def create_gui_elements(self):
        self.enable_afk_var = tk.IntVar()
        self.enable_focus_var = tk.IntVar()
        self.mute_game_var = tk.IntVar()

        ttk.Label(self.master, text="Options:").grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Checkbutton(self.master, text="Enable Anti-AFK", variable=self.enable_afk_var).grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Checkbutton(self.master, text="Enable Application Focus", variable=self.enable_focus_var, command=self.toggle_focus).grid(row=2, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Checkbutton(self.master, text="Mute Game on Enable", variable=self.mute_game_var).grid(row=3, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Label(self.master, text="Key Press Interval (seconds):").grid(row=4, column=0, columnspan=2, pady=5, sticky="w")
        self.key_interval_entry = ttk.Entry(self.master)
        self.key_interval_entry.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Label(self.master, text="Countdown Interval (seconds):").grid(row=6, column=0, columnspan=2, pady=5, sticky="w")
        self.countdown_interval_entry = ttk.Entry(self.master)
        self.countdown_interval_entry.grid(row=7, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Button(self.master, text="Start Script", command=self.start_script).grid(row=8, column=0, pady=10, sticky="w")
        ttk.Button(self.master, text="Stop Script", command=self.stop_script).grid(row=8, column=1, pady=10, sticky="e")
        ttk.Button(self.master, text="Test Console Output", command=self.print_test_message).grid(row=10, column=0, pady=10, sticky="w")
        ttk.Button(self.master, text="Minimize to Tray", command=self.minimize_to_tray).grid(row=10, column=1, pady=10, sticky="e")
        self.console_output = tk.Text(self.master, height=10, width=60)
        self.console_output.grid(row=9, column=0, columnspan=2, pady=10, sticky="w")

    def minimize_to_tray(self):
        self.master.withdraw()
        image = Image.open(self.ICON_PATH)
        menu = (pystray.MenuItem('Open', self.restore_from_tray), pystray.MenuItem('Exit', self.on_closing))
        self.icon = pystray.Icon("test_icon", image)
        self.icon.menu = menu
        self.icon.run()

    def restore_from_tray(self, icon, item):
        icon.stop()
        self.master.attributes("-topmost", True)
        self.master.deiconify()
        self.master.lift()

    def on_closing(self):
        if self.icon:
            self.icon.stop()
        if not hasattr(self, '_destroyed'):
            self.master.destroy()
            self._destroyed = True

    def print_test_message(self):
        self.print_to_console("This is a test message.")

    def print_to_console(self, text):
        self.console_output.config(state=tk.NORMAL)
        self.console_output.insert(tk.END, text + "\n")
        self.console_output.config(state=tk.DISABLED)
        self.console_output.see(tk.END)

    def toggle_focus(self):
        self.application_focus_enabled = not self.application_focus_enabled

    def start_script(self):
        try:
            self.auto_afk_enabled = self.enable_afk_var.get()
            self.application_focus_enabled = self.enable_focus_var.get()
            self.mute_game_on_enable = self.mute_game_var.get()
            self.key_interval = int(self.key_interval_entry.get()) if self.key_interval_entry.get() else self.DEFAULT_KEY_INTERVAL
            self.countdown_interval = int(self.countdown_interval_entry.get()) if self.countdown_interval_entry.get() else self.DEFAULT_COUNTDOWN_INTERVAL

            if self.mute_game_on_enable:
                self.mute_game()

                self.master.iconify()
                self.run_script()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for intervals.")

    def stop_script(self):
        self.script_running = False

    def mute_game(self):
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
            if time.time() - self.last_input_time > self.IDLE_THRESHOLD:
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