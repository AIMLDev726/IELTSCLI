"""
Main entry point for IELTS Practice CLI application - Root level.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run main application
from src.main import main

if __name__ == "__main__":
    main()
