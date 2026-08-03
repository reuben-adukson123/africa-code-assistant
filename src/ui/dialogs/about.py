"""
About Dialog
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class AboutDialog(tb.Toplevel):
    """About dialog for the application."""
    
    def __init__(self, parent):
        """Initialize the about dialog."""
        super().__init__(parent, title="About", themename=parent.style.theme.name)
        self.parent = parent
        self.geometry("450x350")
        self.resizable(False, False)
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Build the about UI."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES, padx=30, pady=30)
        
        # App icon
        ttk.Label(
            main_frame,
            text="🤖",
            font=('Segoe UI', 48)
        ).pack(pady=(0, 10))
        
        # App name
        ttk.Label(
            main_frame,
            text="Africa Code Assistant",
            font=('Segoe UI', 18, 'bold')
        ).pack()
        
        # Version
        ttk.Label(
            main_frame,
            text="Version 1.0.0",
            font=('Segoe UI', 10)
        ).pack(pady=(0, 10))
        
        # Separator
        ttk.Separator(main_frame).pack(fill=tk.X, pady=10)
        
        # Description
        ttk.Label(
            main_frame,
            text="Offline AI Coding Assistant for African Developers",
            font=('Segoe UI', 10),
            wraplength=350
        ).pack()
        
        ttk.Label(
            main_frame,
            text="Built for the Africa Deep Tech Challenge 2026",
            font=('Segoe UI', 9, 'italic')
        ).pack(pady=(5, 10))
        
        # Flag emojis
        ttk.Label(
            main_frame,
            text="🇳🇬 🇰🇪 🇿🇦 🇬🇭 🇹🇿 🇷🇼",
            font=('Segoe UI', 14)
        ).pack()
        
        ttk.Separator(main_frame).pack(fill=tk.X, pady=10)
        
        # Features
        features_frame = ttk.Frame(main_frame)
        features_frame.pack(pady=(0, 10))
        
        features = [
            "💻 Code Generation",
            "📖 Code Explanation",
            "🐛 Debugging",
            "⚡ Optimization",
            "🔄 Code Translation",
            "📚 RAG Documentation",
            "🌍 African Languages"
        ]
        
        for i, feature in enumerate(features):
            ttk.Label(
                features_frame,
                text=feature,
                font=('Segoe UI', 9)
            ).grid(row=i // 3, column=i % 3, padx=10, pady=2, sticky=tk.W)
        
        ttk.Separator(main_frame).pack(fill=tk.X, pady=10)
        
        # Copyright
        ttk.Label(
            main_frame,
            text="© 2026 Your Team Name",
            font=('Segoe UI', 8)
        ).pack()
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            bootstyle="secondary",
            command=self.destroy
        ).pack(pady=15)