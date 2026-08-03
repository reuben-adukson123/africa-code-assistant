"""
Status Bar Widget
"""

import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from ui.themes import get_theme


class StatusBar(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = get_theme('darkly')
        self.is_running = True
        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self):
        self.status_label = ttk.Label(self, text="Ready", font=('Segoe UI', 9), bootstyle="info")
        self.status_label.pack(side=tk.LEFT, padx=10)
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.model_label = ttk.Label(self, text="Model: None", font=('Segoe UI', 9), bootstyle="secondary")
        self.model_label.pack(side=tk.LEFT, padx=10)
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.memory_label = ttk.Label(self, text="RAM: 0 MB", font=('Segoe UI', 9), bootstyle="secondary")
        self.memory_label.pack(side=tk.LEFT, padx=10)
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.gpu_label = ttk.Label(self, text="GPU: N/A", font=('Segoe UI', 9), bootstyle="secondary")
        self.gpu_label.pack(side=tk.LEFT, padx=10)
        self.progress = ttk.Progressbar(self, bootstyle="success-striped", mode='indeterminate', length=100)
        self.progress.pack(side=tk.RIGHT, padx=10)
        self.progress.pack_forget()

    def set_status(self, message: str, style: str = "info"):
        self.status_label.config(text=message, bootstyle=style)

    def set_model_status(self, model: str):
        self.model_label.config(text=f"Model: {model}")

    def set_memory_usage(self):
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        memory_gb = memory_mb / 1024
        self.memory_label.config(text=f"RAM: {memory_gb:.1f} GB")
        
        # WARNING if approaching 7GB
        if memory_gb > 6.5:
            self.memory_label.config(bootstyle="danger")
            self.set_status("⚠️ MEMORY HIGH - Close other apps", "danger")
        else:
            self.memory_label.config(bootstyle="secondary")
        
        if hasattr(self.master, 'sidebar'):
            self.master.sidebar.update_memory_usage(memory_mb)

    def show_progress(self):
        self.progress.pack(side=tk.RIGHT, padx=10)
        self.progress.start()

    def hide_progress(self):
        self.progress.stop()
        self.progress.pack_forget()

    def start_monitoring(self):
        def monitor():
            while self.is_running:
                try:
                    self.after(0, self.set_memory_usage)
                    if hasattr(self.master, 'llm_engine'):
                        if getattr(self.master.llm_engine, 'is_processing', False):
                            self.after(0, self.show_progress)
                        else:
                            self.after(0, self.hide_progress)
                    time.sleep(2)
                except Exception:
                    break
        threading.Thread(target=monitor, daemon=True).start()

    def destroy(self):
        self.is_running = False
        super().destroy()