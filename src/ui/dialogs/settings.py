"""
Settings Dialog
"""

import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Use absolute import
from ui.themes import get_theme_names


class SettingsDialog(tb.Toplevel):
    """Settings dialog for the application."""
    
    def __init__(self, parent):
        """Initialize the settings dialog."""
        super().__init__(parent, title="Settings", themename=parent.style.theme.name)
        self.parent = parent
        self.geometry("500x450")
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
        """Build the settings UI."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # General tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        self.setup_general(general_frame)
        
        # Model tab
        model_frame = ttk.Frame(notebook)
        notebook.add(model_frame, text="Model")
        self.setup_model(model_frame)
        
        # RAG tab
        rag_frame = ttk.Frame(notebook)
        notebook.add(rag_frame, text="RAG")
        self.setup_rag(rag_frame)
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Save",
            bootstyle="success",
            command=self.save_settings
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            bootstyle="secondary",
            command=self.destroy
        ).pack(side=tk.RIGHT)
    
    def setup_general(self, frame):
        """Setup general settings tab."""
        # Theme
        ttk.Label(frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.theme_var = tk.StringVar(value=self.parent.style.theme.name)
        theme_combo = ttk.Combobox(
            frame,
            textvariable=self.theme_var,
            values=get_theme_names(),
            state="readonly",
            width=25
        )
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Language
        ttk.Label(frame, text="UI Language:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.lang_var = tk.StringVar(value=self.parent.current_language)
        lang_combo = ttk.Combobox(
            frame,
            textvariable=self.lang_var,
            values=["English", "Hausa", "Yoruba", "Igbo"],
            state="readonly",
            width=25
        )
        lang_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Threads
        ttk.Label(frame, text="CPU Threads:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.threads_var = tk.IntVar(value=self.parent.config.get('llm.threads', 4))
        spinbox = ttk.Spinbox(
            frame,
            from_=1,
            to=16,
            textvariable=self.threads_var,
            width=23
        )
        spinbox.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
    
    def setup_model(self, frame):
        """Setup model settings tab."""
        # Model path
        ttk.Label(frame, text="Model Path:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.model_path_var = tk.StringVar(value=self.parent.config.get('model_path', ''))
        entry = ttk.Entry(frame, textvariable=self.model_path_var, width=35)
        entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(0, 5))
        
        ttk.Button(
            frame,
            text="Browse",
            bootstyle="secondary",
            command=self.browse_model
        ).grid(row=0, column=2, pady=5)
        
        # Context length
        ttk.Label(frame, text="Context Length:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.context_var = tk.IntVar(value=self.parent.config.get('llm.context_length', 4096))
        spinbox = ttk.Spinbox(
            frame,
            from_=1024,
            to=8192,
            step=512,
            textvariable=self.context_var,
            width=23
        )
        spinbox.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Batch size
        ttk.Label(frame, text="Batch Size:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.batch_var = tk.IntVar(value=self.parent.config.get('llm.batch_size', 512))
        spinbox = ttk.Spinbox(
            frame,
            from_=64,
            to=2048,
            step=64,
            textvariable=self.batch_var,
            width=23
        )
        spinbox.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
    
    def setup_rag(self, frame):
        """Setup RAG settings tab."""
        # Docs path
        ttk.Label(frame, text="Docs Path:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.docs_path_var = tk.StringVar(value=self.parent.config.get('docs_path', ''))
        entry = ttk.Entry(frame, textvariable=self.docs_path_var, width=35)
        entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(0, 5))
        
        ttk.Button(
            frame,
            text="Browse",
            bootstyle="secondary",
            command=self.browse_docs
        ).grid(row=0, column=2, pady=5)
        
        # Chunk size
        ttk.Label(frame, text="Chunk Size:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.chunk_var = tk.IntVar(value=self.parent.config.get('rag.chunk_size', 512))
        spinbox = ttk.Spinbox(
            frame,
            from_=128,
            to=2048,
            step=64,
            textvariable=self.chunk_var,
            width=23
        )
        spinbox.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Overlap
        ttk.Label(frame, text="Chunk Overlap:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.overlap_var = tk.IntVar(value=self.parent.config.get('rag.overlap', 50))
        spinbox = ttk.Spinbox(
            frame,
            from_=0,
            to=200,
            step=10,
            textvariable=self.overlap_var,
            width=23
        )
        spinbox.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
    
    def browse_model(self):
        """Browse for model file."""
        path = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[("GGUF Model", "*.gguf")]
        )
        if path:
            self.model_path_var.set(path)
    
    def browse_docs(self):
        """Browse for documentation directory."""
        path = filedialog.askdirectory(
            title="Select Documentation Directory"
        )
        if path:
            self.docs_path_var.set(path)
    
    def save_settings(self):
        """Save settings and close dialog."""
        # General settings
        self.parent.config.set('ui.theme', self.theme_var.get())
        
        lang_map = {"English": "en", "Hausa": "ha", "Yoruba": "yo", "Igbo": "ig"}
        lang_code = lang_map.get(self.lang_var.get(), "en")
        self.parent.set_language_ui(lang_code)
        
        self.parent.config.set('llm.threads', self.threads_var.get())
        
        # Model settings
        self.parent.config.set('model_path', self.model_path_var.get())
        self.parent.config.set('llm.context_length', self.context_var.get())
        self.parent.config.set('llm.batch_size', self.batch_var.get())
        
        # RAG settings
        self.parent.config.set('docs_path', self.docs_path_var.get())
        self.parent.config.set('rag.chunk_size', self.chunk_var.get())
        self.parent.config.set('rag.overlap', self.overlap_var.get())
        
        # Save config
        self.parent.config.save()
        
        # Apply theme
        self.parent.update_theme(self.theme_var.get())
        
        # Close dialog
        self.destroy()