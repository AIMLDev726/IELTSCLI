"""
Core utilities and helper functions for IELTS CLI application.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def get_app_data_dir() -> Path:
    """
    Get the application data directory.
    
    Returns:
        Path: The application data directory path
    """
    if os.name == 'nt':  # Windows
        app_data = os.getenv('APPDATA', os.path.expanduser('~'))
        return Path(app_data) / 'ieltscli'
    else:  # Unix-like systems
        return Path.home() / '.ieltscli'


def ensure_app_data_dir() -> Path:
    """
    Ensure the application data directory exists.
    
    Returns:
        Path: The application data directory path
    """
    app_dir = get_app_data_dir()
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def safe_import(module_name: str, package: Optional[str] = None) -> Optional[Any]:
    """
    Safely import a module with error handling.
    
    Args:
        module_name: Name of the module to import
        package: Package name for relative imports
        
    Returns:
        The imported module or None if import fails
    """
    try:
        if package:
            return __import__(module_name, fromlist=[package])
        return __import__(module_name)
    except ImportError as e:
        console.print(f"[red]Failed to import {module_name}: {e}[/red]")
        return None


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format an error message for display.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        str: Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"{context}: {error_type} - {error_msg}"
    return f"{error_type}: {error_msg}"


def display_error(error: Exception, context: str = "", exit_app: bool = False) -> None:
    """
    Display an error message using Rich formatting.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        exit_app: Whether to exit the application after displaying the error
    """
    error_msg = format_error_message(error, context)
    
    panel = Panel(
        Text(error_msg, style="bold red"),
        title="[red]Error[/red]",
        border_style="red"
    )
    
    console.print(panel)
    
    if exit_app:
        sys.exit(1)


def display_success(message: str, title: str = "Success") -> None:
    """
    Display a success message using Rich formatting.
    
    Args:
        message: The success message to display
        title: The title for the success panel
    """
    panel = Panel(
        Text(message, style="bold green"),
        title=f"[green]{title}[/green]",
        border_style="green"
    )
    
    console.print(panel)


def display_info(message: str, title: str = "Info") -> None:
    """
    Display an informational message using Rich formatting.
    
    Args:
        message: The info message to display
        title: The title for the info panel
    """
    panel = Panel(
        Text(message, style="bold blue"),
        title=f"[blue]{title}[/blue]",
        border_style="blue"
    )
    
    console.print(panel)


def display_warning(message: str, title: str = "Warning") -> None:
    """
    Display a warning message using Rich formatting.
    
    Args:
        message: The warning message to display
        title: The title for the warning panel
    """
    panel = Panel(
        Text(message, style="bold yellow"),
        title=f"[yellow]{title}[/yellow]",
        border_style="yellow"
    )
    
    console.print(panel)


def run_async(coro) -> Any:
    """
    Run an async function in a sync context.
    
    Args:
        coro: The coroutine to run
        
    Returns:
        The result of the coroutine
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, we need to run in a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop exists, create a new one
        return asyncio.run(coro)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the text
        suffix: Suffix to add when truncating
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_file_path(file_path: str) -> bool:
    """
    Validate if a file path is valid and accessible.
    
    Args:
        file_path: The file path to validate
        
    Returns:
        bool: True if the path is valid and accessible
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except (OSError, ValueError):
        return False


def validate_directory_path(dir_path: str) -> bool:
    """
    Validate if a directory path is valid and accessible.
    
    Args:
        dir_path: The directory path to validate
        
    Returns:
        bool: True if the path is valid and accessible
    """
    try:
        path = Path(dir_path)
        return path.exists() and path.is_dir()
    except (OSError, ValueError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters for filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure the filename is not empty
    if not filename:
        filename = "untitled"
        
    return filename


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_file_size_mb(file_path: str) -> float:
    """
    Get the size of a file in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: File size in megabytes
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except (OSError, ValueError):
        return 0.0
