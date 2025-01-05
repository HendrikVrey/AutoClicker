import customtkinter as ctk
import pyautogui
import time
import threading
from pynput import keyboard

class AutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        #Configure window
        self.title("AutoClicker")
        self.geometry("400x375")
        self.configure(fg_color=("#ffffff", "#333333"))
        
        #Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        
        #Initialize variables
        self.stop_event = threading.Event()
        self.click_thread = None
        
        self.create_widgets()
        self.start_hotkey_listener()

    #UI  
    def create_widgets(self):       
        #Settings frame
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
        
        #Control buttons frame
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        #Start button
        self.start_button = ctk.CTkButton(
            button_frame,
            font=ctk.CTkFont(size=14, weight="bold"),
            text="Start Clicking",
            command=self.start_clicking,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        #Stop button
        self.stop_button = ctk.CTkButton(
            button_frame,
            font=ctk.CTkFont(size=14, weight="bold"),
            text="Stop Clicking",
            command=self.stop_clicking,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        #Status frame
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        #Hotkey information
        hotkey_label = ctk.CTkLabel(
            status_frame,
            text="Hotkeys:\nF8 - Start Clicking\nF9 - Stop Clicking",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        )
        hotkey_label.pack(padx=20, pady=20)
        
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
            self.interval_entry.configure(border_color = "red")
            self.interval_entry.configure(placeholder_text_color = "red")
            self.interval_entry.configure(placeholder_text="Please enter valid numbers for interval...")
            
    def stop_clicking(self):
        self.stop_event.set()
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join()

        #Reset interval color
        self.interval_entry.configure(border_color=("#979DA2", "#565B5E")) 

        #Reset button states
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
    
    def on_hotkey_press(self, key):
        try:
            if key == keyboard.Key.f8:
                self.start_clicking()
            elif key == keyboard.Key.f9:
                self.stop_clicking()
        except Exception as e:
            print(f"Error: {e}")
    
    def start_hotkey_listener(self):
        listener = keyboard.Listener(on_press=self.on_hotkey_press)
        listener.start()

if __name__ == "__main__":
    #Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    
    app = AutoClicker()
    app.mainloop()