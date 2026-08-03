"""
Main Tkinter Application with Modern UI
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from pathlib import Path
import threading
import sys

# Use absolute imports
from ui.widgets.code_editor import CodeEditorWidget
from ui.widgets.chat_panel import ChatPanel
from ui.widgets.sidebar import Sidebar
from ui.widgets.status_bar import StatusBar
from ui.dialogs.settings import SettingsDialog
from ui.dialogs.about import AboutDialog
from ui.themes import THEMES, get_theme
from core.llm_engine import LLMEngine
from core.rag_engine import RAGEngine
from core.localizer import Localizer
from utils.config import AppConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class CodeAssistantApp(tb.Window):
    """Main application window with modern UI."""
    
    def __init__(self, config: AppConfig):
        """Initialize the main application."""
        # Setup themed window
        theme = config.get('ui.theme', 'darkly')
        super().__init__(themename=theme, title="Africa Code Assistant")
        
        self.config = config
        self.logger = logger
        
        # Application state
        self.current_language = config.get('language', 'en')
        self.current_model = config.get('model_path', 'model-q4_0.gguf')
        self.is_processing = False
        
        # Initialize core components
        self.llm_engine = None
        self.rag_engine = None
        self.localizer = None
        
        # Build UI first (so the window shows)
        self.setup_ui()
        
        # Then initialize core components (may take time)
        self.after(100, self.setup_core_components)
        
        # Setup window properties
        self.setup_window()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_core_components(self):
        """Initialize core backend components."""
        try:
            # Model path
            model_path = self.config.get('model_path')
            if not model_path:
                model_path = './models/qwen-coder-3b-q4/model-q4_0.gguf'
            
            print(f"📥 Loading model from: {model_path}")
            
            # LLM Engine
            self.llm_engine = LLMEngine(model_path, self.config)
            
            # RAG Engine
            docs_path = self.config.get('docs_path', './resources/docs')
            self.rag_engine = RAGEngine(docs_path, self.config)
            
            # Localizer (African languages)
            self.localizer = Localizer(self.config)
            
            # Update chat panel with engines
            if hasattr(self, 'chat_panel'):
                self.chat_panel.set_llm_engine(self.llm_engine)
                self.chat_panel.set_rag_engine(self.rag_engine)
            
            # Load welcome message
            if self.localizer and hasattr(self, 'chat_panel'):
                welcome = self.localizer.get_welcome_message(self.current_language)
                self.chat_panel.add_message("assistant", welcome)
            
            # Update status
            self.status_bar.set_status("Ready", "info")
            self.status_bar.set_model_status(self.current_model)
            
            self.logger.info("Core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize core components: {e}")
            self.status_bar.set_status(f"Error: {str(e)[:50]}...", "danger")
            # Show error in chat
            if hasattr(self, 'chat_panel'):
                self.chat_panel.add_message(
                    "system", 
                    f"❌ Error loading AI model: {e}\n\n"
                    f"Please check that:\n"
                    f"1. The model exists at: {self.config.get('model_path')}\n"
                    f"2. You have enough RAM (8GB+)\n"
                    f"3. All dependencies are installed"
                )
    
    def setup_ui(self):
        """Build the user interface."""
        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Configure grid for main_container
        self.main_container.grid_columnconfigure(0, weight=0, minsize=220)  # Sidebar
        self.main_container.grid_columnconfigure(1, weight=1)  # Main content
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=0)  # Status bar
        
        # Sidebar
        self.sidebar = Sidebar(
            self.main_container,
            self,
            width=220,
            padding=(10, 10)
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Main content area - Using Notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=0, column=1, sticky="nsew")
        
        # Code Editor Tab
        self.code_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.code_tab, text="✏️ Code Editor")
        self.setup_code_editor()
        
        # Chat Tab
        self.chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_tab, text="💬 Chat")
        self.setup_chat_panel()
        
        # Status Bar
        self.status_bar = StatusBar(self.main_container)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Bind events
        self.bind_events()
    
    def setup_code_editor(self):
        """Setup the code editor tab."""
        # Top toolbar
        toolbar = ttk.Frame(self.code_tab)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # Language selector
        ttk.Label(toolbar, text="Language:").pack(side=LEFT, padx=(0, 5))
        self.lang_var = tk.StringVar(value="python")
        lang_combo = ttk.Combobox(
            toolbar,
            textvariable=self.lang_var,
            values=["python", "java", "javascript", "cpp", "sql", "html", "css"],
            width=15,
            state="readonly"
        )
        lang_combo.pack(side=LEFT, padx=(0, 10))
        lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Action buttons
        btn_style = "outline-primary"
        ttk.Button(toolbar, text="▶ Generate", bootstyle=btn_style, 
                   command=self.generate_code).pack(side=LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="📝 Explain", bootstyle=btn_style,
                   command=self.explain_code).pack(side=LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🐛 Debug", bootstyle=btn_style,
                   command=self.debug_code).pack(side=LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="⚡ Optimize", bootstyle=btn_style,
                   command=self.optimize_code).pack(side=LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔄 Translate", bootstyle=btn_style,
                   command=self.translate_code).pack(side=LEFT, padx=(0, 5))
        
        # Code Editor Widget
        self.code_editor = CodeEditorWidget(
            self.code_tab,
            language="python",
            height=500
        )
        self.code_editor.pack(fill=BOTH, expand=YES)
    
    def setup_chat_panel(self):
        """Setup the chat panel."""
        # Create chat panel with proper height
        self.chat_panel = ChatPanel(
            self.chat_tab,
            height=400
        )
        # Use pack with fill and expand
        self.chat_panel.pack(fill=BOTH, expand=YES)
        
        # Add initial message
        self.chat_panel.add_message(
            "system",
            "🤖 Africa Code Assistant is loading...\n"
            "Please wait while the AI model loads.\n\n"
            "💡 **How to use:**\n"
            "• Write code in the Editor tab\n"
            "• Ask questions in this Chat tab\n"
            "• Click buttons to Generate, Explain, Debug, Optimize, or Translate"
        )
        
        # Force UI update
        self.chat_panel.update_idletasks()
    
    def bind_events(self):
        """Bind application-wide events."""
        self.bind('<Control-n>', lambda e: self.new_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-q>', lambda e: self.quit())
    
    def setup_window(self):
        """Setup window properties and position."""
        # Set window size and position
        window_width = 1200
        window_height = 800
        
        # Center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(800, 600)
    
    # ===== Action Methods =====
    
    def generate_code(self):
        if not self.llm_engine:
            self.show_error("Not Ready", "AI model is still loading. Please wait...")
            return
        self._execute_action("generate", self.code_editor.get_selected_or_all())
    
    def explain_code(self):
        if not self.llm_engine:
            self.show_error("Not Ready", "AI model is still loading. Please wait...")
            return
        self._execute_action("explain", self.code_editor.get_selected_or_all())
    
    def debug_code(self):
        if not self.llm_engine:
            self.show_error("Not Ready", "AI model is still loading. Please wait...")
            return
        self._execute_action("debug", self.code_editor.get_selected_or_all())
    
    def optimize_code(self):
        if not self.llm_engine:
            self.show_error("Not Ready", "AI model is still loading. Please wait...")
            return
        self._execute_action("optimize", self.code_editor.get_selected_or_all())
    
    def translate_code(self):
        """Translate code to another programming language."""
        if not self.llm_engine:
            self.show_error("Not Ready", "AI model is still loading. Please wait...")
            return
        
        code = self.code_editor.get_selected_or_all()
        if not code:
            self.show_error("No Code", "Please select or enter code first.")
            return
        
        # Create translation dialog
        self.show_translation_dialog(code)
    
    def show_translation_dialog(self, code: str):
        """Show translation language selection dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("🔄 Translate Code")
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 225
        y = (dialog.winfo_screenheight() // 2) - 150
        dialog.geometry(f"+{x}+{y}")
        
        # UI Elements
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text="🔄 Translate Code",
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=(0, 10))
        
        ttk.Label(
            main_frame,
            text="Select the target programming language:",
            font=('Segoe UI', 10)
        ).pack(pady=(0, 15))
        
        # Language selection
        self.translate_lang_var = tk.StringVar(value="javascript")
        
        # Create a frame for the combobox
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(pady=(0, 15))
        
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.translate_lang_var,
            values=[
                "python", "java", "javascript", "cpp", "csharp",
                "php", "ruby", "go", "rust", "sql"
            ],
            state="readonly",
            width=30,
            font=('Segoe UI', 11)
        )
        lang_combo.pack()
        
        # Show current language
        current_lang = self.lang_var.get()
        ttk.Label(
            main_frame,
            text=f"📝 Translating from: {current_lang}",
            font=('Segoe UI', 9),
            bootstyle="secondary"
        ).pack(pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def do_translation():
            target = self.translate_lang_var.get()
            dialog.destroy()
            
            self.is_processing = True
            self.status_bar.set_status(f"Translating to {target}...", "warning")
            
            threading.Thread(
                target=self._process_translation,
                args=(code, target),
                daemon=True
            ).start()
        
        ttk.Button(
            btn_frame,
            text="🔄 Translate",
            bootstyle="primary",
            command=do_translation
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❌ Cancel",
            bootstyle="secondary",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Info label
        ttk.Label(
            main_frame,
            text="💡 The translated code will replace your selected code",
            font=('Segoe UI', 9, 'italic'),
            bootstyle="secondary"
        ).pack(pady=(10, 0))
    
    def _process_translation(self, code: str, target_lang: str):
        """Process translation in background thread."""
        try:
            # Force garbage collection before heavy operation
            import gc
            gc.collect()
            
            result = self.llm_engine.translate_code("", code, target_lang)
            self.after(0, self._update_translation_result, result)
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            self.after(0, self.show_error, "Translation Error", str(e))
        finally:
            self.after(0, self._reset_processing)
    
    def _update_translation_result(self, result: str):
        """Update UI with translation result."""
        self.code_editor.set_text(result)
        self.status_bar.set_status("Translation completed successfully", "success")
        self.show_info("✅ Translation Complete", "Code has been translated successfully!")
    
    def _execute_action(self, action: str, code: str):
        if not code:
            self.show_error("No Code", "Please select or enter code first.")
            return
        
        if self.is_processing:
            self.show_info("Processing", "Please wait for current operation to complete.")
            return
        
        self.is_processing = True
        self.status_bar.set_status(f"Processing: {action}...", "warning")
        
        threading.Thread(
            target=self._process_action,
            args=(action, code),
            daemon=True
        ).start()
    
    def _process_action(self, action: str, code: str):
        try:
            language = self.lang_var.get()
            
            if action == "generate":
                result = self.llm_engine.generate_code(code, language)
            elif action == "explain":
                result = self.llm_engine.explain_code("", code)
            elif action == "debug":
                result = self.llm_engine.debug_code("", code)
            elif action == "optimize":
                result = self.llm_engine.optimize_code("", code)
            else:
                result = "Unknown action"
            
            self.after(0, self._update_result, action, result)
            
        except Exception as e:
            self.logger.error(f"Action {action} failed: {e}")
            self.after(0, self.show_error, "Error", str(e))
        finally:
            self.after(0, self._reset_processing)
    
    def _update_result(self, action: str, result: str):
        """Update UI with action result."""
        if action == "generate":
            self.code_editor.set_text(result)
            self.status_bar.set_status("Code generated successfully", "success")
        else:
            # Add message to chat
            self.chat_panel.add_message("assistant", result)
            self.status_bar.set_status(f"{action.capitalize()} completed", "success")
            
            # Switch to chat tab to show the result
            self.notebook.select(self.chat_tab)
            
            # Show a notification
            self.show_info(
                "💬 Result in Chat", 
                f"Your {action} result has been displayed in the Chat tab."
            )
    
    def _reset_processing(self):
        self.is_processing = False
    
    # ===== File Operations =====
    
    def new_file(self):
        self.code_editor.set_text("")
        self.status_bar.set_status("New file created", "info")
    
    def open_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Open Code File",
            filetypes=[("Code Files", "*.py *.java *.js *.cpp *.sql"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.set_text(content)
                self.status_bar.set_status(f"Opened: {file_path}", "success")
            except Exception as e:
                self.show_error("Open Error", f"Failed to open file: {e}")
    
    def save_file(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Save Code File",
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                content = self.code_editor.get_text()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.set_status(f"Saved: {file_path}", "success")
            except Exception as e:
                self.show_error("Save Error", f"Failed to save file: {e}")
    
    # ===== UI Helpers =====
    
    def show_error(self, title: str, message: str):
        from tkinter import messagebox
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    def on_language_change(self, event):
        lang = self.lang_var.get()
        self.code_editor.set_language(lang)
        self.status_bar.set_status(f"Language: {lang}", "info")
    
    def update_theme(self, theme_name: str):
        self.style.theme_use(theme_name)
        self.status_bar.set_status(f"Theme updated: {theme_name}", "info")
    
    def set_language_ui(self, language: str):
        self.current_language = language
        if self.localizer:
            self.localizer.set_language(language)
        self.status_bar.set_status(f"UI Language: {language}", "info")
    
    def update_model(self, model_path: str):
        if self.llm_engine:
            self.llm_engine.load_model(model_path)
            self.current_model = model_path
            self.status_bar.set_model_status(model_path)
    
    def on_closing(self):
        self.config.save()
        if self.llm_engine:
            self.llm_engine.cleanup()
        if self.rag_engine:
            self.rag_engine.cleanup()
        self.destroy()
    
    def quit(self, event=None):
        self.on_closing()


if __name__ == "__main__":
    from utils.config import load_config
    config = load_config()
    app = CodeAssistantApp(config)
    app.mainloop()