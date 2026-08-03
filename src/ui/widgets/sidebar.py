"""
Sidebar Navigation Widget
"""

import tkinter as tk
from tkinter import ttk

# Use absolute imports
from ui.themes import get_theme
from ui.dialogs.settings import SettingsDialog
from ui.dialogs.about import AboutDialog


class Sidebar(ttk.Frame):
    """Sidebar with navigation and features."""
    
    FEATURES = [
        ('📝 Code Generation', 'generate'),
        ('📖 Code Explanation', 'explain'),
        ('🐛 Debugging', 'debug'),
        ('⚡ Optimization', 'optimize'),
        ('🔄 Translation', 'translate'),
        ('📚 Documentation', 'docs'),
        ('🎯 Quiz Mode', 'quiz'),
        ('📁 Project Assistant', 'project'),
        ('❓ Help & Guide', 'help')
    ]
    
    LANGUAGES = ['English', 'Hausa', 'Yoruba', 'Igbo']
    
    def __init__(self, parent, app, width: int = 220, padding: tuple = (10, 10)):
        """Initialize the sidebar."""
        super().__init__(parent, width=width)
        
        self.app = app
        self.theme = get_theme('darkly')
        self.padding = padding
        
        self.setup_ui()
    
    def setup_ui(self):
        """Build the sidebar UI."""
        # Application Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="🤖 Africa Code",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="inverse-primary"
        ).pack()
        
        ttk.Label(
            title_frame,
            text="Assistant",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="inverse-secondary"
        ).pack()
        
        # Separator
        ttk.Separator(self).pack(fill=tk.X, pady=10)
        
        # Feature buttons
        ttk.Label(
            self,
            text="Features",
            font=('Segoe UI', 10, 'bold'),
            bootstyle="inverse-secondary"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        for label, action in self.FEATURES:
            btn = ttk.Button(
                self,
                text=label,
                bootstyle="outline-primary",
                command=lambda a=action: self.on_feature_click(a)
            )
            btn.pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(self).pack(fill=tk.X, pady=10)
        
        # Language selector
        ttk.Label(
            self,
            text="🌍 Language",
            font=('Segoe UI', 10, 'bold'),
            bootstyle="inverse-secondary"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.lang_var = tk.StringVar(value='English')
        lang_combo = ttk.Combobox(
            self,
            textvariable=self.lang_var,
            values=self.LANGUAGES,
            state='readonly',
            width=15
        )
        lang_combo.pack(fill=tk.X, pady=(0, 10))
        lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Theme selector
        ttk.Label(
            self,
            text="🎨 Theme",
            font=('Segoe UI', 10, 'bold'),
            bootstyle="inverse-secondary"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        themes = ['darkly', 'superhero', 'cyborg', 'solar', 'flatly']
        self.theme_var = tk.StringVar(value='darkly')
        theme_combo = ttk.Combobox(
            self,
            textvariable=self.theme_var,
            values=themes,
            state='readonly',
            width=15
        )
        theme_combo.pack(fill=tk.X, pady=(0, 10))
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
        
        # Separator
        ttk.Separator(self).pack(fill=tk.X, pady=10)
        
        # Model status
        ttk.Label(
            self,
            text="🧠 Model",
            font=('Segoe UI', 10, 'bold'),
            bootstyle="inverse-secondary"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.model_label = ttk.Label(
            self,
            text="Qwen 3B",
            font=('Segoe UI', 9),
            bootstyle="info"
        )
        self.model_label.pack(anchor=tk.W)
        
        # Memory status
        ttk.Label(
            self,
            text="💾 Memory",
            font=('Segoe UI', 10, 'bold'),
            bootstyle="inverse-secondary"
        ).pack(anchor=tk.W, pady=(5, 0))
        
        self.memory_label = ttk.Label(
            self,
            text="0 MB / 7 GB",
            font=('Segoe UI', 9),
            bootstyle="info"
        )
        self.memory_label.pack(anchor=tk.W)
        
        # Progress bar placeholder
        self.progress = ttk.Progressbar(
            self,
            bootstyle="success-striped",
            mode='determinate',
            maximum=100,
            value=0
        )
        self.progress.pack(fill=tk.X, pady=10)
        
        # Bottom buttons - Settings, About, Quit
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            bottom_frame,
            text="⚙️ Settings",
            bootstyle="outline-secondary",
            command=self.open_settings
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            bottom_frame,
            text="ℹ️ About",
            bootstyle="outline-secondary",
            command=self.open_about
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            bottom_frame,
            text="🚪 Quit",
            bootstyle="outline-danger",
            command=self.quit_app
        ).pack(fill=tk.X, pady=2)
    
    def on_feature_click(self, action: str):
        """Handle feature button click."""
        # Map action to app method
        action_map = {
            'generate': self.app.generate_code,
            'explain': self.app.explain_code,
            'debug': self.app.debug_code,
            'optimize': self.app.optimize_code,
            'translate': self.app.translate_code,
            'docs': self.open_documentation,
            'quiz': self.open_quiz,
            'project': self.open_project_assistant,
            'help': self.open_help
        }
        
        if action in action_map:
            action_map[action]()
    
    def on_language_change(self, event=None):
        """Handle language selection change."""
        language = self.lang_var.get()
        language_code = {
            'English': 'en',
            'Hausa': 'ha',
            'Yoruba': 'yo',
            'Igbo': 'ig'
        }.get(language, 'en')
        
        self.app.set_language_ui(language_code)
    
    def on_theme_change(self, event=None):
        """Handle theme selection change."""
        theme = self.theme_var.get()
        self.app.update_theme(theme)
    
    def open_settings(self):
        """Open settings dialog."""
        SettingsDialog(self.app)
    
    def open_about(self):
        """Open about dialog."""
        AboutDialog(self.app)
    
    def open_documentation(self):
        """Open documentation feature."""
        self.app.chat_panel.set_mode(
            self.app.chat_panel.MODE_DOCS,
            "📚 Documentation"
        )
        self.app.notebook.select(self.app.chat_tab)
    
    def open_quiz(self):
        """Open quiz mode."""
        self.app.chat_panel.set_mode(
            self.app.chat_panel.MODE_QUIZ,
            "🎯 Quiz Mode"
        )
        self.app.notebook.select(self.app.chat_tab)
    
    def open_project_assistant(self):
        """Open project assistant."""
        self.app.chat_panel.set_mode(
            self.app.chat_panel.MODE_PROJECT,
            "📁 Project Assistant"
        )
        self.app.notebook.select(self.app.chat_tab)
    
    def open_help(self):
        """Open help guide."""
        self.app.chat_panel.set_mode(
            self.app.chat_panel.MODE_HELP,
            "❓ Help"
        )
        self.app.notebook.select(self.app.chat_tab)
    
    def quit_app(self):
        """Quit the application."""
        self.app.quit()
    
    def update_model_status(self, model_name: str):
        """Update model status label."""
        self.model_label.config(text=model_name)
    
    def update_memory_usage(self, memory_mb: int):
        """Update memory usage label."""
        memory_gb = memory_mb / 1024
        self.memory_label.config(text=f"{memory_gb:.1f} GB / 7 GB")
        
        # Update progress bar
        progress = (memory_mb / (7 * 1024)) * 100
        self.progress.config(value=min(progress, 100))
        
        # Change color based on usage
        if progress > 80:
            self.progress.config(bootstyle="danger-striped")
        elif progress > 60:
            self.progress.config(bootstyle="warning-striped")
        else:
            self.progress.config(bootstyle="success-striped")