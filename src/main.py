#!/usr/bin/env python3
"""
Africa Code Assistant - Main Entry Point
ADTC 2026 Submission
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Now imports will work
from ui.app import CodeAssistantApp
from utils.logger import setup_logging
from utils.config import load_config


def main():
    """Main entry point for the application."""
    # Setup logging
    setup_logging()
    
    # Load configuration
    config = load_config()
    
    # Create and run the application
    app = CodeAssistantApp(config)
    app.mainloop()


if __name__ == "__main__":
    main()
