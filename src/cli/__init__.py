"""
CLI package for IELTS Practice CLI application.

This package contains all command-line interface components including:
- Commands: Typer-based CLI commands
- Interface: Rich-based UI components
- Input Handler: Multi-line input handling with markdown support
"""

from .commands import app as cli_app
from .interface import IELTSInterface
from .input_handler import InputHandler

__all__ = [
    'cli_app',
    'IELTSInterface', 
    'InputHandler'
]
