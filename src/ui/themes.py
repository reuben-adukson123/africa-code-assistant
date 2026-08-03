"""
Modern UI Theme Configuration
"""

THEMES = {
    'darkly': {
        'background': '#222222',
        'foreground': '#ffffff',
        'primary': '#375a7f',
        'secondary': '#444444',
        'success': '#00bc8c',
        'info': '#3498db',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'light': '#ecf0f1',
        'dark': '#222222',
        'input_bg': '#2b2b2b',
        'input_fg': '#ffffff',
        'select_bg': '#375a7f',
        'select_fg': '#ffffff',
        'scrollbar_bg': '#2b2b2b',
        'scrollbar_trough': '#3d3d3d',
        'border': '#444444'
    },
    'superhero': {
        'background': '#1e2a36',
        'foreground': '#ffffff',
        'primary': '#2c3e50',
        'secondary': '#34495e',
        'success': '#18bc9c',
        'info': '#3498db',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'light': '#ecf0f1',
        'dark': '#1e2a36',
        'input_bg': '#2c3e50',
        'input_fg': '#ffffff',
        'select_bg': '#3498db',
        'select_fg': '#ffffff',
        'scrollbar_bg': '#2c3e50',
        'scrollbar_trough': '#1e2a36',
        'border': '#34495e'
    },
    'cyborg': {
        'background': '#060606',
        'foreground': '#ffffff',
        'primary': '#2a2a2a',
        'secondary': '#333333',
        'success': '#00ff41',
        'info': '#007bff',
        'warning': '#ff8800',
        'danger': '#ff0044',
        'light': '#aaaaaa',
        'dark': '#060606',
        'input_bg': '#1a1a1a',
        'input_fg': '#00ff41',
        'select_bg': '#00ff41',
        'select_fg': '#060606',
        'scrollbar_bg': '#1a1a1a',
        'scrollbar_trough': '#2a2a2a',
        'border': '#333333'
    },
    'solar': {
        'background': '#fdf6e3',
        'foreground': '#073642',
        'primary': '#268bd2',
        'secondary': '#93a1a1',
        'success': '#2aa198',
        'info': '#268bd2',
        'warning': '#b58900',
        'danger': '#dc322f',
        'light': '#eee8d5',
        'dark': '#073642',
        'input_bg': '#eee8d5',
        'input_fg': '#073642',
        'select_bg': '#268bd2',
        'select_fg': '#fdf6e3',
        'scrollbar_bg': '#eee8d5',
        'scrollbar_trough': '#fdf6e3',
        'border': '#93a1a1'
    },
    'flatly': {
        'background': '#ecf0f1',
        'foreground': '#2c3e50',
        'primary': '#2c3e50',
        'secondary': '#95a5a6',
        'success': '#18bc9c',
        'info': '#3498db',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'light': '#ecf0f1',
        'dark': '#2c3e50',
        'input_bg': '#ffffff',
        'input_fg': '#2c3e50',
        'select_bg': '#2c3e50',
        'select_fg': '#ffffff',
        'scrollbar_bg': '#ffffff',
        'scrollbar_trough': '#ecf0f1',
        'border': '#bdc3c7'
    }
}


def get_theme(theme_name: str = 'darkly'):
    """Get theme configuration."""
    return THEMES.get(theme_name, THEMES['darkly'])


def get_theme_names():
    """Get list of available theme names."""
    return list(THEMES.keys())