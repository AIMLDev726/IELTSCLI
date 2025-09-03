"""
Main entry point for IELTS Practice CLI application.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional

# Add src to Python path for development
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

import typer
from rich.console import Console
from rich.traceback import install

# Install rich traceback handler for better error display
install(show_locals=True)

# Import CLI components
from src.cli import cli_app, IELTSInterface
from src.core.config import ConfigManager
from src.storage.database import db_manager
from src.utils import get_app_data_dir, display_error, display_success, display_warning, display_info

# Initialize console
console = Console()

# Global exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for better error reporting."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle graceful shutdown on Ctrl+C
        console.print("\n[yellow]Application interrupted by user[/yellow]")
        return
    
    # Log the full exception
    logger = logging.getLogger(__name__)
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Display user-friendly error message
    display_error(f"An unexpected error occurred: {exc_value}")
    display_info("Please check the logs for more details.")

# Set the global exception handler
sys.excepthook = handle_exception


def setup_logging(verbose: bool = False) -> None:
    """
    Setup application logging.
    
    Args:
        verbose: Enable verbose logging
    """
    app_dir = get_app_data_dir()
    log_dir = app_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "ieltscli.log"
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler() if verbose else logging.NullHandler()
        ]
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)


def check_first_run() -> bool:
    """
    Check if this is the first run of the application.
    
    Returns:
        True if first run, False otherwise
    """
    app_dir = get_app_data_dir()
    config_file = app_dir / "config.json"
    
    return not config_file.exists()


def initialize_application() -> None:
    """Initialize application on first run."""
    interface = IELTSInterface(console)
    config_manager = ConfigManager()
    
    try:
        # Display welcome message
        interface.display_welcome()
        
        console.print("[bold]🚀 Welcome to IELTS Practice CLI![/bold]")
        console.print("\nThis appears to be your first time using the application.")
        console.print("Let's set up your configuration.\n")
        
        # Initialize configuration
        config = config_manager.config
        
        # Interactive setup
        console.print("[bold cyan]Step 1: LLM Provider Configuration[/bold cyan]")
        console.print("To assess your writing, we need to configure an AI language model provider.")
        console.print("Supported providers: OpenAI, Google AI (Gemini), Ollama (local)")
        
        from src.core.models import LLMProvider
        
        provider_choices = [p.value for p in LLMProvider]
        
        # Display choices
        console.print("Available providers:")
        for i, choice in enumerate(provider_choices, 1):
            console.print(f"  {i}. {choice}")
        
        while True:
            provider = typer.prompt(
                f"Select your preferred LLM provider ({'/'.join(provider_choices)})",
                default="openai"
            )
            if provider in provider_choices:
                break
            console.print(f"[red]Invalid choice. Please select from: {', '.join(provider_choices)}[/red]")
        
        config.llm_provider = LLMProvider(provider)
        
        # Get API key for cloud providers
        if provider in ["openai", "google"]:
            console.print(f"\n[yellow]You'll need an API key for {provider.title()}[/yellow]")
            
            if provider == "openai":
                console.print("Get your API key from: https://platform.openai.com/api-keys")
            elif provider == "google":
                console.print("Get your API key from: https://makersuite.google.com/app/apikey")
            
            api_key = typer.prompt("Enter your API key", hide_input=True)
            config_manager.set_api_key(config.llm_provider, api_key)
            
            # Test the connection
            console.print("\n[dim]Testing connection...[/dim]")
            from src.llm.client import LLMClient
            llm_client = LLMClient(config_manager)
            
            if asyncio.run(llm_client.test_connection()):
                display_success("✅ Connection test successful!")
            else:
                display_warning("⚠️ Connection test failed. You can reconfigure later using 'ieltscli config'")
        
        # Save initial configuration
        config_manager.save_config(config)
        
        console.print("\n[bold cyan]Step 2: Task Preferences[/bold cyan]")
        
        from src.core.models import TaskType
        task_choices = [t.value for t in TaskType]
        
        # Display choices
        console.print("Available task types:")
        for i, choice in enumerate(task_choices, 1):
            console.print(f"  {i}. {choice}")
        
        while True:
            default_task = typer.prompt(
                f"Select your default task type ({'/'.join(task_choices)})",
                default="writing_task_2"
            )
            if default_task in task_choices:
                break
            console.print(f"[red]Invalid choice. Please select from: {', '.join(task_choices)}[/red]")
        
        config.default_task_type = TaskType(default_task)
        config_manager.save_config(config)
        
        display_success("🎉 Setup complete! You're ready to start practicing.")
        console.print("\nTry these commands to get started:")
        console.print("• [cyan]ieltscli practice[/cyan] - Start a new practice session")
        console.print("• [cyan]ieltscli config --show[/cyan] - View your configuration")
        console.print("• [cyan]ieltscli --help[/cyan] - See all available commands")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        display_error(f"Setup failed: {e}")
        console.print("\nYou can run setup again later using 'ieltscli config'")


def check_dependencies() -> bool:
    """
    Check if all required dependencies are available.
    
    Returns:
        True if all dependencies are available, False otherwise
    """
    try:
        # Check critical imports
        import typer
        import rich
        import sqlalchemy
        import aiohttp
        import cryptography
        import pydantic
        
        return True
        
    except ImportError as e:
        display_error(f"Missing required dependency: {e}")
        console.print("\nPlease install dependencies using:")
        console.print("pip install -r requirements.txt")
        return False


def main() -> None:
    """Main application entry point."""
    try:
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Setup logging (basic level for startup)
        setup_logging(verbose=False)
        
        # Initialize database
        try:
            # This will create the database and tables if they don't exist
            db_info = db_manager.get_database_info()
            logging.info(f"Database initialized: {db_info.get('database_path')}")
        except Exception as e:
            display_error(f"Database initialization failed: {e}")
            sys.exit(1)
        
        # Check for first run
        if check_first_run():
            initialize_application()
            return
        
        # Run the CLI application
        cli_app()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        display_error(f"Application failed to start: {e}")
        logging.exception("Application startup failed")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            db_manager.close()
        except:
            pass


def cli_entry_point() -> None:
    """Entry point for CLI command when installed as package."""
    main()


if __name__ == "__main__":
    main()
