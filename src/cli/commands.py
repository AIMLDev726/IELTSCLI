"""
CLI commands for IELTS practice application using Typer.
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.config import ConfigManager
from ..core.models import TaskType, LLMProvider, BandScore, TaskPrompt, PracticeSession, UserResponse
from ..core.session import SessionManager
from ..storage.database import db_manager, session_manager
from ..llm.client import LLMClient
from ..assessment.analyzer import ResponseAnalyzer
from ..utils import display_error, display_success, display_warning, display_info, format_duration
from .interface import IELTSInterface
from .input_handler import InputHandler

# Initialize console and CLI app
console = Console()
app = typer.Typer(
    name="ieltscli",
    help="IELTS Practice CLI - AI-powered writing assessment tool",
    add_completion=False,
    rich_markup_mode="rich"
)

# Global state
config_manager = ConfigManager()
session_mgr = None  # Will be initialized when needed
input_handler = InputHandler(console)
interface = IELTSInterface(console)


def _create_quick_session(task_type: TaskType, custom_prompt: str = None, time_limit: int = None) -> PracticeSession:
    """Create a quick practice session with default prompts (no LLM needed)."""
    import uuid
    from datetime import datetime
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Default prompts for each task type
    default_prompts = {
        TaskType.WRITING_TASK_2: """Some people believe that children should be allowed to stay at home and play until they are six or seven years old. Others believe that it is important for young children to go to school as soon as possible.

What do you think are the advantages of attending school from a young age?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.""",
        
        TaskType.WRITING_TASK_1_ACADEMIC: """The chart below shows the results of a survey about people's coffee and tea buying and drinking habits in five Australian cities.

Summarise the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.""",
        
        TaskType.WRITING_TASK_1_GENERAL: """You recently bought a piece of equipment for your kitchen but it did not work. You phoned the shop but no action was taken.

Write a letter to the shop manager. In your letter:
• describe the problem with the equipment
• explain what happened when you phoned the shop
• say what you would like the manager to do

Write at least 150 words."""
    }
    
    # Get default time limits and word requirements
    default_time_limits = {
        TaskType.WRITING_TASK_2: 40,
        TaskType.WRITING_TASK_1_ACADEMIC: 20,
        TaskType.WRITING_TASK_1_GENERAL: 20
    }
    
    word_requirements = {
        TaskType.WRITING_TASK_2: (250, 350),
        TaskType.WRITING_TASK_1_ACADEMIC: (150, 200),
        TaskType.WRITING_TASK_1_GENERAL: (150, 200)
    }
    
    # Use custom prompt or default
    prompt_text = custom_prompt or default_prompts.get(task_type, default_prompts[TaskType.WRITING_TASK_2])
    time_limit = time_limit or default_time_limits.get(task_type, 40)
    word_min, word_max = word_requirements.get(task_type, (250, 350))
    
    # Create task prompt
    task_prompt = TaskPrompt(
        task_type=task_type,
        prompt_text=prompt_text,
        time_limit=time_limit,
        word_count_min=word_min,
        word_count_max=word_max
    )
    
    # Create session
    session = PracticeSession(
        session_id=session_id,
        task_prompt=task_prompt,
        user_response=UserResponse(text="[No response yet]", word_count=0),  # Initialize placeholder response
        status="in_progress",  # Changed from "created" to valid status
        quick_mode=True,  # This is a quick session
        time_limit_minutes=time_limit,  # Set time limit if provided
        created_at=datetime.now()
    )
    
    return session


@app.command("config")
def config_command(
    set_key: Optional[str] = typer.Option(None, "--set", "-s", help="Set a configuration key"),
    set_value: Optional[str] = typer.Option(None, "--value", "-v", help="Value to set"),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    reset: bool = typer.Option(False, "--reset", help="Reset configuration to defaults"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Set LLM provider (openai, google, ollama)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Set API key for the provider"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Set model name")
):
    """Configure IELTS CLI settings, API keys, and LLM providers."""
    
    try:
        if reset:
            if Confirm.ask("Are you sure you want to reset all configuration?"):
                config_manager.reset_config()
                display_success("Configuration reset to defaults")
            return
        
        if show:
            interface.display_configuration(config_manager.config)
            return
        
        # Handle provider configuration
        if provider:
            provider_enum = None
            try:
                provider_enum = LLMProvider(provider.lower())
            except ValueError:
                display_error(f"Invalid provider. Choose from: {[p.value for p in LLMProvider]}")
                raise typer.Exit(1)
            
            config = config_manager.config
            config.llm_provider = provider_enum
            
            # Set API key if provided
            if api_key:
                config_manager.set_api_key(provider_enum, api_key)
                display_success(f"API key set for {provider_enum.value}")
            
            # Set model if provided
            if model:
                current_model_config = config.get_current_model_config()
                current_model_config.model = model
            
            config_manager.save_config(config)
            display_success(f"LLM provider set to {provider_enum.value}")
            
            # Test the configuration
            if api_key:
                with console.status("Testing LLM configuration..."):
                    llm_client = LLMClient(config_manager)
                    if asyncio.run(llm_client.test_connection()):
                        display_success("LLM connection test successful")
                    else:
                        display_warning("LLM connection test failed. Please check your API key and settings.")
            
            return
        
        # Handle generic key-value setting
        if set_key and set_value:
            config = config_manager.config
            
            # Map common configuration keys
            key_mappings = {
                "task_type": ("default_task_type", lambda x: TaskType(x)),
                "auto_save": ("user_preferences.save_sessions", lambda x: x.lower() == "true"),
                "detailed_feedback": ("detailed_feedback", lambda x: x.lower() == "true"),
                "word_limit_strict": ("word_limit_strict", lambda x: x.lower() == "true"),
                "session_timeout": ("session_timeout_minutes", int),
                "theme": ("theme", str),
                "model_temperature": ("model_config.temperature", float)
            }
            
            if set_key in key_mappings:
                attr_path, converter = key_mappings[set_key]
                try:
                    value = converter(set_value)
                    
                    # Handle nested attributes
                    if '.' in attr_path:
                        obj_path, attr_name = attr_path.rsplit('.', 1)
                        obj = getattr(config, obj_path)
                        setattr(obj, attr_name, value)
                    else:
                        setattr(config, attr_path, value)
                    
                    config_manager.save_config(config)
                    display_success(f"Set {set_key} = {set_value}")
                    
                except (ValueError, AttributeError) as e:
                    display_error(f"Invalid value for {set_key}: {e}")
                    raise typer.Exit(1)
            else:
                display_error(f"Unknown configuration key: {set_key}")
                display_info("Available keys: " + ", ".join(key_mappings.keys()))
                raise typer.Exit(1)
            
            return
        
        # Show interactive configuration menu
        interface.interactive_configuration(config_manager)
        
    except Exception as e:
        display_error(f"Configuration error: {e}")
        raise typer.Exit(1)


@app.command("practice")
def practice_command(
    task_type: Optional[str] = typer.Option(None, "--type", "-t", help="Task type (writing_task_1_academic, writing_task_1_general, writing_task_2)"),
    topic: Optional[str] = typer.Option(None, "--topic", help="Specific topic or prompt"),
    time_limit: Optional[int] = typer.Option(None, "--time", help="Time limit in minutes"),
    resume: Optional[str] = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    quick: bool = typer.Option(False, "--quick", "-q", help="Quick practice mode (no assessment)")
):
    """Start a new IELTS writing practice session."""
    
    try:
        config = config_manager.config
        
        # Initialize LLM client and session manager
        llm_client = LLMClient(config_manager)
        session_mgr = SessionManager(llm_client)
        
        # Resume existing session
        if resume:
            session = asyncio.run(session_manager.load_session(resume))
            if not session:
                display_error(f"Session {resume} not found")
                raise typer.Exit(1)
            
            display_info(f"Resuming session: {session.session_id}")
            interface.display_session_info(session)
            
            # Continue the session
            return _run_practice_session(session, config, resume_mode=True)
        
        # Determine task type
        task_type_enum = None
        if task_type:
            try:
                task_type_enum = TaskType(task_type.lower())
            except ValueError:
                display_error(f"Invalid task type. Choose from: {[t.value for t in TaskType]}")
                raise typer.Exit(1)
        else:
            task_type_enum = config.default_task_type
        
        # Create new session
        with console.status("Creating new practice session..."):
            if quick:
                # For quick mode, use a default prompt instead of LLM generation
                session = _create_quick_session(task_type_enum, topic, time_limit)
            else:
                # Initialize session manager with LLM client for full mode
                llm_client = LLMClient(config_manager)
                session_mgr = SessionManager(llm_client)
                session = asyncio.run(session_mgr.create_session(task_type_enum, topic))
        
        display_success(f"Created new practice session: {session.session_id}")
        interface.display_session_info(session)
        
        # Start the practice session
        return _run_practice_session(session, config)
        
    except KeyboardInterrupt:
        display_warning("Practice session cancelled by user")
        raise typer.Exit(0)
    except Exception as e:
        display_error(f"Failed to start practice session: {e}")
        raise typer.Exit(1)


def _run_practice_session(session, config, resume_mode=False):
    """Run a practice session with input handling and assessment."""
    
    try:
        # Display prompt and instructions
        interface.display_task_prompt(session)
        
        if not resume_mode:
            session.start_session()
        
        # Get user response
        if not session.user_response or not session.user_response.text or session.user_response.text == "[No response yet]":
            console.print("\n[bold]Enter your response below.[/bold]")
            console.print("[dim]Type your response and press Ctrl+D (Unix) or Ctrl+Z (Windows) when finished.[/dim]")
            console.print("[dim]Or type 'SUBMIT' on a new line to submit your response.[/dim]\n")
            
            response_content = input_handler.get_multi_line_input(
                prompt="Your response: ",
                session_info=session,
                time_limit_minutes=session.time_limit_minutes
            )
            
            if not response_content.strip():
                display_warning("No response provided. Session saved for later.")
                asyncio.run(session_manager.save_session(session))
                return
            
            # Update session with response
            session.submit_response(response_content)
            
            # Auto-save if enabled
            if config.user_preferences.save_sessions:
                asyncio.run(session_manager.save_session(session))
        
        # Skip assessment in quick mode
        if session.quick_mode:
            display_info("Quick mode: Skipping assessment")
            session.complete_session()
            asyncio.run(session_manager.save_session(session))
            interface.display_session_summary(session)
            return
        
        # Perform assessment
        with console.status("Analyzing your response..."):
            llm_client = LLMClient(config_manager)
            analyzer = ResponseAnalyzer(llm_client)
            
            assessment = asyncio.run(analyzer.analyze_response(
                session.task_prompt,
                session.user_response,
                session.task_prompt.task_type  # Get task_type from task_prompt
            ))
        
        if assessment:
            session.set_assessment(assessment)
            session.complete_session()
            
            # Save final session
            asyncio.run(session_manager.save_session(session))
            
            # Display results
            interface.display_assessment_results(assessment)
            interface.display_session_summary(session)
            
            display_success(f"Practice session completed! Overall band score: {assessment.overall_band_score}")
        else:
            display_error("Assessment failed. Session saved without assessment.")
            asyncio.run(session_manager.save_session(session))
    
    except KeyboardInterrupt:
        display_warning("Session interrupted. Saving progress...")
        asyncio.run(session_manager.save_session(session))
        raise typer.Exit(0)
    except Exception as e:
        display_error(f"Session error: {e}")
        # Try to save session before exiting
        try:
            asyncio.run(session_manager.save_session(session))
        except:
            pass
        raise typer.Exit(1)


@app.command("sessions")
def sessions_command(
    list_all: bool = typer.Option(False, "--all", "-a", help="List all sessions"),
    recent: int = typer.Option(10, "--recent", "-r", help="Number of recent sessions to show"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    delete: Optional[str] = typer.Option(None, "--delete", "-d", help="Delete session by ID"),
    details: Optional[str] = typer.Option(None, "--details", help="Show session details by ID"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export sessions to file")
):
    """Manage practice sessions."""
    
    try:
        # Delete session
        if delete:
            if Confirm.ask(f"Are you sure you want to delete session {delete}?"):
                success = asyncio.run(session_manager.delete_session(delete))
                if success:
                    display_success(f"Session {delete} deleted")
                else:
                    display_error(f"Failed to delete session {delete}")
            return
        
        # Show session details
        if details:
            session = asyncio.run(session_manager.load_session(details))
            if session:
                interface.display_session_details(session)
            else:
                display_error(f"Session {details} not found")
            return
        
        # Export sessions
        if export:
            sessions = asyncio.run(session_manager.get_all_sessions())
            interface.export_sessions(sessions, export)
            return
        
        # List sessions
        status_filter = [status] if status else None
        
        if list_all:
            sessions = asyncio.run(session_manager.get_all_sessions())
        else:
            sessions = db_manager.get_recent_sessions(limit=recent, status_filter=status_filter)
        
        if not sessions:
            display_info("No sessions found")
            return
        
        interface.display_sessions_table(sessions)
        
    except Exception as e:
        display_error(f"Session management error: {e}")
        raise typer.Exit(1)


@app.command("stats")
def stats_command(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed statistics"),
    period: Optional[str] = typer.Option(None, "--period", "-p", help="Time period (week, month, year)"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export stats to file")
):
    """Display user statistics and progress analytics."""
    
    try:
        with console.status("Calculating statistics..."):
            stats = db_manager.calculate_user_statistics()
        
        if period:
            # Filter stats by time period
            end_date = datetime.now()
            if period == "week":
                start_date = end_date - timedelta(weeks=1)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                display_error("Invalid period. Use: week, month, year")
                raise typer.Exit(1)
            
            sessions = db_manager.get_sessions_by_date_range(start_date, end_date)
            stats.update_stats(sessions)
        
        # Display statistics
        interface.display_user_statistics(stats, detailed=detailed)
        
        # Export if requested
        if export:
            interface.export_statistics(stats, export)
            display_success(f"Statistics exported to {export}")
        
    except Exception as e:
        display_error(f"Statistics error: {e}")
        raise typer.Exit(1)


@app.command("test")
def test_command(
    connection: bool = typer.Option(False, "--connection", "-c", help="Test LLM connection"),
    config: bool = typer.Option(False, "--config", help="Test configuration"),
    database: bool = typer.Option(False, "--database", "-d", help="Test database connection"),
    all: bool = typer.Option(False, "--all", "-a", help="Run all tests")
):
    """Test system components and connections."""
    
    try:
        if all or connection:
            console.print("\n[bold]Testing LLM connection...[/bold]")
            with console.status("Connecting to LLM..."):
                llm_client = LLMClient(config_manager)
                success = asyncio.run(llm_client.test_connection())
            
            if success:
                display_success("LLM connection test passed")
            else:
                display_error("LLM connection test failed")
        
        if all or config:
            console.print("\n[bold]Testing configuration...[/bold]")
            try:
                config = config_manager.config
                display_success("Configuration loaded successfully")
                interface.display_configuration(config)
            except Exception as e:
                display_error(f"Configuration test failed: {e}")
        
        if all or database:
            console.print("\n[bold]Testing database connection...[/bold]")
            try:
                db_info = db_manager.get_database_info()
                display_success("Database connection successful")
                interface.display_database_info(db_info)
            except Exception as e:
                display_error(f"Database test failed: {e}")
        
        if not any([connection, config, database, all]):
            display_info("No test specified. Use --help to see available tests.")
    
    except Exception as e:
        display_error(f"Test error: {e}")
        raise typer.Exit(1)


@app.command("maintenance")
def maintenance_command(
    cleanup: bool = typer.Option(False, "--cleanup", help="Clean up old sessions"),
    vacuum: bool = typer.Option(False, "--vacuum", help="Vacuum database"),
    backup: Optional[str] = typer.Option(None, "--backup", "-b", help="Create database backup"),
    restore: Optional[str] = typer.Option(None, "--restore", "-r", help="Restore from backup"),
    info: bool = typer.Option(False, "--info", "-i", help="Show database information")
):
    """Database maintenance operations."""
    
    try:
        if cleanup:
            if Confirm.ask("Clean up old cancelled/error sessions (older than 90 days)?"):
                with console.status("Cleaning up old sessions..."):
                    deleted = db_manager.cleanup_old_sessions()
                display_success(f"Cleaned up {deleted} old sessions")
        
        if vacuum:
            with console.status("Vacuuming database..."):
                db_manager.vacuum_database()
            display_success("Database vacuumed successfully")
        
        if backup:
            with console.status("Creating database backup..."):
                backup_path = db_manager.backup_database(backup)
            display_success(f"Database backed up to: {backup_path}")
        
        if restore:
            if Confirm.ask(f"Restore database from {restore}? This will overwrite current data."):
                with console.status("Restoring database..."):
                    db_manager.restore_database(restore)
                display_success("Database restored successfully")
        
        if info:
            db_info = db_manager.get_database_info()
            interface.display_database_info(db_info)
        
        if not any([cleanup, vacuum, backup, restore, info]):
            display_info("No maintenance operation specified. Use --help to see available operations.")
    
    except Exception as e:
        display_error(f"Maintenance error: {e}")
        raise typer.Exit(1)


@app.command("version")
def version_command():
    """Show version information."""
    interface.display_version_info()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config_file: Optional[str] = typer.Option(None, "--config", help="Custom configuration file")
):
    """
    IELTS Practice CLI - AI-powered writing assessment tool.
    
    An intelligent command-line application for IELTS writing practice with
    AI-powered assessment and feedback.
    """
    
    if version:
        interface.display_version_info()
        raise typer.Exit()
    
    # Set up logging level based on verbose flag
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Load custom config file if specified
    if config_file:
        try:
            config_manager.load_config_file(config_file)
        except Exception as e:
            display_error(f"Failed to load config file {config_file}: {e}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()
