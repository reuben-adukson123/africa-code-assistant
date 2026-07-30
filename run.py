#!/usr/bin/env python3
"""
Simple runner for Africa Code Assistant
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import and run
from src.main import main

if __name__ == "__main__":
    main()