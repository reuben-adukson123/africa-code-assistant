"""
Chat Interface Widget
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime

# Use absolute import
from ui.themes import get_theme


class ChatPanel(ttk.Frame):
    """Chat interface for interacting with the AI assistant."""
    
    # Mode flags for different chat modes
    MODE_NORMAL = "normal"
    MODE_DOCS = "docs"
    MODE_QUIZ = "quiz"
    MODE_PROJECT = "project"
    MODE_HELP = "help"
    
    def __init__(self, parent, height: int = 400, **kwargs):
        """Initialize the chat panel."""
        super().__init__(parent, **kwargs)
        
        self.theme = get_theme('darkly')
        self.llm_engine = None
        self.rag_engine = None
        self.is_processing = False
        self.current_mode = self.MODE_NORMAL
        
        # Store height
        self.chat_height = height
        
        # Setup UI
        self.setup_ui()
        
        # Load initial state
        self.load_state()
    
    def setup_ui(self):
        """Build the chat interface."""
        # Create a main container frame with grid layout
        self.grid_rowconfigure(0, weight=1)  # Chat display takes remaining space
        self.grid_rowconfigure(1, weight=0)  # Input area fixed height
        self.grid_columnconfigure(0, weight=1)
        
        # === CHAT DISPLAY AREA ===
        self.chat_display = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg=self.theme['input_bg'],
            fg=self.theme['input_fg'],
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        # Configure message tags
        self.chat_display.tag_configure(
            'user',
            foreground='#00ff00',
            font=('Segoe UI', 11, 'bold')
        )
        self.chat_display.tag_configure(
            'assistant',
            foreground='#00bfff',
            font=('Segoe UI', 11, 'bold')
        )
        self.chat_display.tag_configure(
            'system',
            foreground='#ff8800',
            font=('Segoe UI', 10, 'italic')
        )
        self.chat_display.tag_configure(
            'time',
            foreground='#666666',
            font=('Segoe UI', 8)
        )
        
        # === INPUT AREA ===
        self.input_container = ttk.Frame(self)
        self.input_container.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.input_container.grid_columnconfigure(0, weight=1)
        
        # Top row: Mode indicator and RAG toggle
        self.top_row = ttk.Frame(self.input_container)
        self.top_row.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.top_row.grid_columnconfigure(0, weight=1)
        
        # Mode indicator (left)
        self.mode_label = ttk.Label(
            self.top_row,
            text="💬 Chat Mode",
            font=('Segoe UI', 9, 'bold'),
            bootstyle="info"
        )
        self.mode_label.grid(row=0, column=0, sticky="w")
        
        # RAG toggle (right)
        self.rag_var = tk.BooleanVar(value=True)
        self.rag_check = ttk.Checkbutton(
            self.top_row,
            text="🔍 RAG",
            variable=self.rag_var,
            bootstyle="success-round-toggle"
        )
        self.rag_check.grid(row=0, column=1, sticky="e")
        
        # Bottom row: Input field and Send button
        self.bottom_row = ttk.Frame(self.input_container)
        self.bottom_row.grid(row=1, column=0, sticky="ew")
        self.bottom_row.grid_columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = ttk.Entry(
            self.bottom_row,
            font=('Segoe UI', 11)
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_field.bind('<Return>', self.send_message)
        
        # Send button
        self.send_btn = ttk.Button(
            self.bottom_row,
            text="➤ Send",
            bootstyle="primary",
            command=self.send_message
        )
        self.send_btn.grid(row=0, column=1, sticky="e")
        
        # Set initial placeholder text
        self._set_placeholder("Type your message here...")
        
        # Bind focus events for placeholder
        self.input_field.bind('<FocusIn>', self._on_entry_focus)
        self.input_field.bind('<FocusOut>', self._on_entry_blur)
        
        # Force update
        self.update_idletasks()
    
    def _set_placeholder(self, text: str):
        """Set placeholder text in entry."""
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, text)
        self.input_field.config(foreground='#666666')
    
    def _on_entry_focus(self, event):
        """Clear placeholder text when focus gained."""
        if self.input_field.get() in [
            "Type your message here...",
            "Ask about Python, Pandas, NumPy...",
            "Generate a quiz on...",
            "Create a project for...",
            "Ask how to use a feature..."
        ]:
            self.input_field.delete(0, tk.END)
            self.input_field.config(foreground='#ffffff')
    
    def _on_entry_blur(self, event):
        """Restore placeholder text when focus lost."""
        if not self.input_field.get().strip():
            self._set_placeholder("Type your message here...")
    
    def set_llm_engine(self, engine):
        """Set the LLM engine."""
        self.llm_engine = engine
    
    def set_rag_engine(self, engine):
        """Set the RAG engine."""
        self.rag_engine = engine
    
    def set_mode(self, mode: str, mode_name: str = "💬 Chat Mode"):
        """Set the current chat mode."""
        self.current_mode = mode
        self.mode_label.config(text=mode_name)
        
        # Change input placeholder based on mode
        if mode == self.MODE_DOCS:
            self.input_field.config(foreground='#00bfff')
            self._set_placeholder("Ask about Python, Pandas, NumPy...")
            self.add_message('system', 
                f"📚 **Documentation Mode Active**\n\n"
                f"Ask me about:\n"
                f"• Python Standard Library\n"
                f"• Pandas Data Analysis\n"
                f"• NumPy Numerical Computing\n\n"
                f"💡 Example: 'How do I use pandas groupby?'"
            )
        elif mode == self.MODE_QUIZ:
            self.input_field.config(foreground='#ff8800')
            self._set_placeholder("Generate a quiz on...")
            self.add_message('system',
                f"🎯 **Quiz Mode Active**\n\n"
                f"I'll generate coding questions for you!\n"
                f"💡 Example: 'Generate a Python quiz on functions'"
            )
        elif mode == self.MODE_PROJECT:
            self.input_field.config(foreground='#00bc8c')
            self._set_placeholder("Create a project for...")
            self.add_message('system',
                f"📁 **Project Assistant Mode Active**\n\n"
                f"I can help you with:\n"
                f"• Creating a project structure\n"
                f"• Generating boilerplate code\n"
                f"• Setting up files and folders\n"
                f"• Adding dependencies\n\n"
                f"💡 Example: 'Create a Python project for a web scraper'"
            )
        elif mode == self.MODE_HELP:
            self.input_field.config(foreground='#3498db')
            self._set_placeholder("Ask how to use a feature...")
            self.add_message('system',
                f"❓ **Help Mode Active**\n\n"
                f"Ask me anything about using Africa Code Assistant!\n"
                f"💡 Example: 'How do I use the translate feature?'"
            )
        else:
            # Normal mode
            self.input_field.config(foreground='#ffffff')
            self._set_placeholder("Type your message here...")
    
    def reset_mode(self):
        """Reset to normal chat mode."""
        self.current_mode = self.MODE_NORMAL
        self.mode_label.config(text="💬 Chat Mode")
        self.input_field.config(foreground='#ffffff')
        self._set_placeholder("Type your message here...")
    
    def add_message(self, role: str, content: str, show_time: bool = True):
        """Add a message to the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        if show_time:
            timestamp = datetime.now().strftime("%H:%M")
            self.chat_display.insert(
                tk.END,
                f" {timestamp} ",
                'time'
            )
        
        # Add role label
        role_label = {
            'user': '👤 You',
            'assistant': '🤖 AI',
            'system': '⚙️ System'
        }.get(role, role)
        
        self.chat_display.insert(
            tk.END,
            f"\n{role_label}:\n",
            role
        )
        
        # Add content
        self.chat_display.insert(tk.END, f"{content}\n\n")
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Send a message to the AI with context-aware processing."""
        if self.is_processing:
            return
        
        message = self.input_field.get().strip()
        
        # Ignore placeholder text
        placeholder_texts = [
            "Type your message here...",
            "Ask about Python, Pandas, NumPy...",
            "Generate a quiz on...",
            "Create a project for...",
            "Ask how to use a feature..."
        ]
        if not message or message in placeholder_texts:
            return
        
        # Clear input
        self.input_field.delete(0, tk.END)
        
        # Show user message
        self.add_message('user', message)
        
        # Start processing
        self.is_processing = True
        self.send_btn.config(state=tk.DISABLED)
        self.input_field.config(state=tk.DISABLED)
        
        # Add status message
        self.add_message('system', "⏳ Thinking...", show_time=False)
        
        # Process in background with current mode
        threading.Thread(
            target=self._process_message_with_mode,
            args=(message, self.current_mode),
            daemon=True
        ).start()
    
    def _process_message_with_mode(self, message: str, mode: str):
        """Process message based on current mode."""
        try:
            if mode == self.MODE_DOCS:
                response = self._process_docs_query(message)
            elif mode == self.MODE_QUIZ:
                response = self._process_quiz_request(message)
            elif mode == self.MODE_PROJECT:
                response = self._process_project_request(message)
            elif mode == self.MODE_HELP:
                response = self._process_help_request(message)
            else:
                response = self._process_normal_query(message)
            
            # Update UI
            self.after(0, self._display_response, response)
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.after(0, self._display_response, error_msg)
    
    def _process_normal_query(self, message: str) -> str:
        """Process normal chat query with optional RAG."""
        # Check if RAG should be used
        use_rag = self.rag_var.get()
        
        # Get response
        if use_rag and self.rag_engine:
            # Search RAG for relevant context
            context = self.rag_engine.query(message)
            if context:
                enhanced_message = f"Context: {context}\n\nQuestion: {message}"
                response = self.llm_engine.chat(enhanced_message)
            else:
                response = self.llm_engine.chat(message)
        else:
            response = self.llm_engine.chat(message)
        
        return response
    
    def _process_docs_query(self, message: str) -> str:
        """Process documentation search query."""
        # Force RAG on for docs mode
        if self.rag_engine:
            context = self.rag_engine.query(message)
            if context:
                prompt = f"You are a documentation expert. Use the following context to answer the question.\n\nContext: {context}\n\nQuestion: {message}\n\nAnswer:"
                response = self.llm_engine.generate(prompt, max_tokens=1024, temperature=0.3)
                
                # Add source reference
                return f"📚 **Documentation Response**\n\n{response}\n\n---\n*Source: Offline Documentation (RAG)*"
            else:
                prompt = f"You are a documentation expert. The question is about {message}. Provide a helpful explanation from your knowledge."
                response = self.llm_engine.generate(prompt, max_tokens=1024, temperature=0.3)
                return f"📚 **Documentation Response**\n\n{response}\n\n---\n*Note: No specific documentation found. Based on general knowledge.*"
        else:
            return "❌ RAG engine is not available. Please check your documentation setup."
    
    def _process_quiz_request(self, message: str) -> str:
        """Process quiz generation request."""
        prompt = f"""
You are a coding quiz generator. Generate a quiz based on this request: "{message}"

Format your response as:
1. Quiz Title
2. 3-5 questions with multiple choice options
3. Answers and explanations at the end

Make it educational and fun!
"""
        response = self.llm_engine.generate(prompt, max_tokens=1024, temperature=0.7)
        return f"🎯 **Quiz Generated**\n\n{response}"
    
    def _process_project_request(self, message: str) -> str:
        """Process project assistant request."""
        prompt = f"""
You are a project structure expert. Help with this project request: "{message}"

Provide:
1. Project structure (folders and files)
2. Recommended dependencies
3. Setup instructions
4. Key components

Make it practical and well-organized.
"""
        response = self.llm_engine.generate(prompt, max_tokens=1024, temperature=0.4)
        return f"📁 **Project Structure**\n\n{response}"
    
    def _process_help_request(self, message: str) -> str:
        """Process help request."""
        prompt = f"""
You are a helpful assistant for the Africa Code Assistant app. Answer this question: "{message}"

Provide clear, concise instructions on how to use the feature or solve the problem.
"""
        response = self.llm_engine.generate(prompt, max_tokens=1024, temperature=0.5)
        return f"❓ **Help Response**\n\n{response}"
    
    def _display_response(self, response: str):
        """Display the AI response."""
        # Remove status message
        self.chat_display.config(state=tk.NORMAL)
        
        # Find and delete the status message
        content = self.chat_display.get(1.0, tk.END)
        if "⏳ Thinking..." in content:
            # Find the line with "⏳ Thinking..."
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "⏳ Thinking..." in line:
                    # Try to delete from this line
                    try:
                        start_idx = f"{i+1}.0"
                        # Find where this message ends
                        end_line = i + 3
                        end_idx = f"{end_line}.0"
                        self.chat_display.delete(start_idx, end_idx)
                    except:
                        pass
                    break
        
        self.chat_display.config(state=tk.DISABLED)
        
        # Add response
        self.add_message('assistant', response)
        
        # Reset UI
        self.is_processing = False
        self.send_btn.config(state=tk.NORMAL)
        self.input_field.config(state=tk.NORMAL)
        self.input_field.focus()
        
        # Reset placeholder if empty
        if not self.input_field.get().strip():
            self.input_field.config(foreground='#666666')
            self.input_field.insert(0, "Type your message here...")
    
    def load_state(self):
        """Load previous chat history if any."""
        pass
    
    def clear_history(self):
        """Clear chat history."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.reset_mode()
