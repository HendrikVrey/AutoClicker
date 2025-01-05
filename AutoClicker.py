import customtkinter as ctk
import pyautogui
import time
import threading
from pynput import keyboard
from pynput import mouse

class AutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        #Configure window
        self.title("AutoClicker")
        self.geometry("420x480")
        
        #Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        
        #Initialize variables
        self.stop_event = threading.Event()
        self.click_thread = None
        
        #Default hotkeys (if user doesn't define any)
        self.default_start_key = keyboard.Key.f8
        self.default_stop_key  = keyboard.Key.f9
        
        #Current user-defined hotkeys
        self.start_key = None
        self.stop_key  = None

        #Create UI
        self.create_widgets()
        
        #Start a global listener that checks for start/stop press
        self.global_listener = keyboard.Listener(on_press=self.on_hotkey_press)
        self.global_listener.start()

    #UI
    def create_widgets(self):       
        #Row 1: Interval/Count Fields
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure(0, weight=1)
        
        #Interval input
        interval_label = ctk.CTkLabel(
            settings_frame,
            text="Interval (seconds):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        interval_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.interval_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="Enter interval..."
        )
        self.interval_entry.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        #Count input
        count_label = ctk.CTkLabel(
            settings_frame,
            text="Number of clicks (leave blank for infinite):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        count_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.count_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="Enter click count..."
        )
        self.count_entry.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        #Row 2: Start/Stop Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0,1), weight=1)
        
        #Start button
        self.start_button = ctk.CTkButton(
            button_frame,
            font=ctk.CTkFont(size=14, weight="bold"),
            text="Start Clicking",
            command=self.start_clicking,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        #Stop button
        self.stop_button = ctk.CTkButton(
            button_frame,
            font=ctk.CTkFont(size=14, weight="bold"),
            text="Stop Clicking",
            command=self.stop_clicking,
            fg_color="#e74c3c",
            hover_color="#8B0000"
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        #Row 3: Set Hotkey Buttons
        hotkey_frame = ctk.CTkFrame(self)
        hotkey_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        hotkey_frame.grid_columnconfigure((0,1), weight=1)
        
        #Set Start Key
        self.set_start_btn = ctk.CTkButton(
            hotkey_frame,
            font=ctk.CTkFont(size=14, weight="bold"),
            text="Set Start Hotkey",
            command=self.set_start_hotkey
        )
        self.set_start_btn.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        #Set Stop Key
        self.set_stop_btn = ctk.CTkButton(
            hotkey_frame,
            font=ctk.CTkFont(size=14, weight="bold"),
            text="Set Stop Hotkey",
            command=self.set_stop_hotkey
        )
        self.set_stop_btn.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        #Row 4: Status/Hotkeys & Clear
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        #Label to display current hotkeys
        self.hotkey_label = ctk.CTkLabel(
            status_frame,
            text=self.get_current_hotkeys_text(),
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        )
        self.hotkey_label.pack(padx=20, pady=10)

        #Button to clear hotkeys
        self.clear_hotkeys_btn = ctk.CTkButton(
            status_frame,
            font=ctk.CTkFont(size=14, weight="bold"),
            text="Clear Hotkeys (Revert to F8 / F9)",
            command=self.clear_hotkeys
        )
        self.clear_hotkeys_btn.pack(padx=5, pady=10)

    #Update the bottom label
    def update_hotkey_label(self):
        self.hotkey_label.configure(text=self.get_current_hotkeys_text())

    def get_current_hotkeys_text(self):
        start_str = self.format_key(self.start_key) or "F8 (default)"
        stop_str  = self.format_key(self.stop_key)  or "F9 (default)"

        return (
            f"Current Hotkeys:\n\n"
            f"START: {start_str}\n"
            f"STOP : {stop_str}"
        )

    #Clicking Logic
    def start_clicking(self):
        try:
            interval = float(self.interval_entry.get())
            count = int(self.count_entry.get()) if self.count_entry.get() else None

            self.interval_entry.configure(border_color="green")

            def clicker():
                clicks = 0
                while not self.stop_event.is_set():
                    if count and clicks >= count:
                        break
                    pyautogui.click()
                    clicks += 1
                    time.sleep(interval)
            
            self.stop_event.clear()
            self.click_thread = threading.Thread(target=clicker)
            self.click_thread.start()
            
            #Update button states
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
        except ValueError:
            self.interval_entry.configure(border_color="red")
            self.interval_entry.configure(placeholder_text_color="red")
            self.interval_entry.configure(
                placeholder_text="Please enter valid numbers for interval..."
            )
            
    def stop_clicking(self):
        self.stop_event.set()
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join()

        #Reset interval color
        self.interval_entry.configure(border_color=("#979DA2", "#565B5E")) 

        #Reset button states
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    #Hotkey Selection Logic
    def set_start_hotkey(self):
        self.set_start_btn.configure(state="disabled")

        def on_press(key):
            #As soon as the user presses a key, store it
            self.start_key = key
            #Update label so user sees the new hotkey
            self.update_hotkey_label()
            #Re-enable button
            self.set_start_btn.configure(state="normal")
            #Stop this one-time listener
            listener.stop()

        #Create a one-time listener that captures exactly one key press
        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def set_stop_hotkey(self):
        self.set_stop_btn.configure(state="disabled")

        def on_press(key):
            self.stop_key = key
            self.update_hotkey_label()
            self.set_stop_btn.configure(state="normal")
            listener.stop()

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def clear_hotkeys(self):
        self.start_key = None
        self.stop_key = None
        self.update_hotkey_label()

    #Global Hotkey Check
    def on_hotkey_press(self, key):
        #If the user hasn't set one, use default
        actual_start_key = self.start_key if self.start_key else self.default_start_key
        actual_stop_key  = self.stop_key  if self.stop_key  else self.default_stop_key
        
        if key == actual_start_key:
            self.start_clicking()
        elif key == actual_stop_key:
            self.stop_clicking()

    #Utility
    def format_key(self, key):
        if key is None:
            return None
        
        #Special keys come through as keyboard.Key.xxx
        if isinstance(key, keyboard.Key):
            return str(key).replace("Key.", "").upper()

        #Character keys come through as keyboard.KeyCode, e.g. KeyCode(char='a')
        if hasattr(key, 'char') and key.char is not None:
            return key.char.upper()

        #Fallback
        return str(key)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = AutoClicker()
    app.mainloop()
