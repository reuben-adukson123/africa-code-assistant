"""
Syntax-highlighted Code Editor Widget
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from pygments.styles import get_style_by_name

# Use absolute import
from ui.themes import get_theme


class CodeEditorWidget(ttk.Frame):
    """Enhanced code editor with syntax highlighting."""
    
    LANGUAGE_MAP = {
        'python': 'python3',
        'java': 'java',
        'javascript': 'javascript',
        'cpp': 'cpp',
        'sql': 'sql',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'xml': 'xml',
        'yaml': 'yaml',
        'markdown': 'markdown'
    }
    
    # Define colors for syntax highlighting
    STYLE_COLORS = {
        'keyword': {'foreground': '#f92672'},
        'function': {'foreground': '#a6e22e'},
        'class': {'foreground': '#66d9ef'},
        'string': {'foreground': '#e6db74'},
        'comment': {'foreground': '#75715e'},
        'number': {'foreground': '#ae81ff'},
        'operator': {'foreground': '#f92672'},
        'builtin': {'foreground': '#66d9ef'},
        'variable': {'foreground': '#f8f8f2'},
        'decorator': {'foreground': '#a6e22e'},
        'error': {'foreground': '#ff0000'},
        'text': {'foreground': '#f8f8f2'},
    }

    def __init__(self, parent, language: str = 'python', height: int = 400, **kwargs):
        """Initialize the code editor."""
        super().__init__(parent, **kwargs)
        
        self.language = language
        self.theme = get_theme('darkly')
        
        # Create the text widget with scrollbar
        self.text = scrolledtext.ScrolledText(
            self,
            wrap=tk.NONE,  # No wrap for code
            font=('Consolas', 11),
            bg='#1e1e1e',  # Dark background like VS Code
            fg='#d4d4d4',  # Light text
            insertbackground='#ffffff',
            selectbackground='#264f78',
            selectforeground='#ffffff',
            height=height,
            padx=10,
            pady=10
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for syntax highlighting
        self.setup_tags()
        
        # Bind events
        self.text.bind('<KeyRelease>', self.on_text_change)
        self.text.bind('<FocusIn>', self.on_focus_in)
        
        # Auto-indent
        self.text.bind('<Return>', self.on_return)
        self.text.bind('<Tab>', self.on_tab)
        self.text.bind('<Shift-Tab>', self.on_shift_tab)
    
    def setup_tags(self):
        """Setup text tags for syntax highlighting."""
        # Configure tags with colors
        for tag_name, colors in self.STYLE_COLORS.items():
            self.text.tag_configure(tag_name, **colors)
    
    def set_language(self, language: str):
        """Set the language for syntax highlighting."""
        self.language = language
        self.highlight()
    
    def set_text(self, text: str):
        """Set the text content."""
        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, text)
        self.highlight()
    
    def get_text(self) -> str:
        """Get the text content."""
        return self.text.get(1.0, tk.END).rstrip('\n')
    
    def get_selected_or_all(self) -> str:
        """Get selected text or all text if nothing selected."""
        try:
            selected = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected:
                return selected
        except tk.TclError:
            pass
        return self.get_text()
    
    def highlight(self, event=None):
        """Apply syntax highlighting to the current text."""
        # Get current text
        text = self.get_text()
        if not text:
            return
        
        # Clear all existing tags except 'sel' (selection)
        for tag in self.text.tag_names():
            if tag != 'sel':
                self.text.tag_delete(tag)
        
        # Setup tags again
        self.setup_tags()
        
        # Apply highlighting
        try:
            lexer = get_lexer_by_name(
                self.LANGUAGE_MAP.get(self.language, self.language)
            )
            tokens = list(lexer.get_tokens(text))
            
            # Highlight tokens
            start_pos = 1.0
            current_char = 1
            
            for token_type, token_text in tokens:
                if token_text:
                    tag_name = self._token_to_tag(token_type)
                    if tag_name:
                        # Calculate position
                        start = f"{start_pos:.0f}.{current_char}"
                        end_char = current_char + len(token_text)
                        self.text.tag_add(
                            tag_name,
                            start,
                            f"{start_pos:.0f}.{end_char}"
                        )
                    
                    # Update position
                    lines = token_text.count('\n')
                    if lines > 0:
                        start_pos += lines
                        current_char = len(token_text.split('\n')[-1]) + 1
                    else:
                        current_char += len(token_text)
        except Exception as e:
            # If highlighting fails, just skip
            pass
    
    def _token_to_tag(self, token_type):
        """Convert Pygments token to tag name."""
        if token_type in Token.Keyword:
            return 'keyword'
        elif token_type in Token.Name.Function:
            return 'function'
        elif token_type in Token.Name.Class:
            return 'class'
        elif token_type in Token.String:
            return 'string'
        elif token_type in Token.Comment:
            return 'comment'
        elif token_type in Token.Number:
            return 'number'
        elif token_type in Token.Operator:
            return 'operator'
        elif token_type in Token.Name.Builtin:
            return 'builtin'
        elif token_type in Token.Name.Variable:
            return 'variable'
        elif token_type in Token.Name.Decorator:
            return 'decorator'
        return None
    
    def on_text_change(self, event=None):
        """Handle text changes."""
        # Schedule highlighting after a short delay
        self.after(300, self.highlight)
    
    def on_focus_in(self, event=None):
        """Handle focus in event."""
        self.text.config(insertbackground='#ffffff')
    
    def on_return(self, event=None):
        """Handle return key - auto-indent."""
        # Get current line
        cursor_pos = self.text.index(tk.INSERT)
        line_start = self.text.index(f"{cursor_pos} linestart")
        line_text = self.text.get(line_start, cursor_pos)
        
        # Calculate indentation
        indent = ''
        for char in line_text:
            if char in (' ', '\t'):
                indent += char
            else:
                break
        
        # Insert newline with indent
        self.text.insert(cursor_pos, '\n' + indent)
        return 'break'
    
    def on_tab(self, event=None):
        """Handle tab key."""
        try:
            # Check if there's a selection
            start = self.text.index(tk.SEL_FIRST)
            end = self.text.index(tk.SEL_LAST)
            
            # If multiple lines selected, indent all
            if start != end and '\n' in self.text.get(start, end):
                lines = self.text.get(start, end).split('\n')
                indented = '\n'.join('    ' + line if line.strip() else '' for line in lines)
                self.text.delete(start, end)
                self.text.insert(start, indented)
                return 'break'
        except tk.TclError:
            pass
        
        # Insert tab
        self.text.insert(tk.INSERT, '    ')
        return 'break'
    
    def on_shift_tab(self, event=None):
        """Handle shift+tab - unindent."""
        try:
            start = self.text.index(tk.SEL_FIRST)
            end = self.text.index(tk.SEL_LAST)
            
            if start != end:
                lines = self.text.get(start, end).split('\n')
                unindented = []
                for line in lines:
                    if line.startswith('    '):
                        unindented.append(line[4:])
                    elif line.startswith('\t'):
                        unindented.append(line[1:])
                    else:
                        unindented.append(line)
                self.text.delete(start, end)
                self.text.insert(start, '\n'.join(unindented))
                return 'break'
        except tk.TclError:
            pass
        
        return 'break'