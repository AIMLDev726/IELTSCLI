"""
Input handling for IELTS CLI application with multi-line markdown support.
"""

import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from ..core.models import PracticeSession
from ..utils import display_info, display_warning, display_error


class InputHandler:
    """Handles multi-line input with markdown support and time tracking."""
    
    def __init__(self, console: Console):
        """
        Initialize input handler.
        
        Args:
            console: Rich Console instance
        """
        self.console = console
        self.submission_keywords = ["SUBMIT", "submit", "DONE", "done", "FINISH", "finish"]
        self.cancel_keywords = ["CANCEL", "cancel", "QUIT", "quit", "EXIT", "exit"]
    
    def get_multi_line_input(
        self, 
        prompt: str = "Enter your response: ",
        session_info: Optional[PracticeSession] = None,
        time_limit_minutes: Optional[int] = None,
        show_word_count: bool = True,
        show_time: bool = True
    ) -> str:
        """
        Get multi-line input from user with live feedback.
        
        Args:
            prompt: Input prompt to display
            session_info: Optional session information for context
            time_limit_minutes: Optional time limit for input
            show_word_count: Show live word count
            show_time: Show elapsed time
            
        Returns:
            User input content
            
        Raises:
            KeyboardInterrupt: If user cancels input
        """
        self.console.print(f"\n[bold cyan]{prompt}[/bold cyan]")
        self._display_input_instructions()
        
        lines = []
        start_time = datetime.now()
        
        # Calculate end time if time limit is set
        end_time = None
        if time_limit_minutes:
            end_time = start_time + timedelta(minutes=time_limit_minutes)
        
        # Start input collection with feedback
        try:
            result = self._collect_input_with_feedback(
                lines, start_time, end_time, show_word_count, show_time, session_info
            )
            
            # Check if we got any content
            if not result.strip():
                self.console.print("[yellow]No content entered. Please try again.[/yellow]")
                return ""
            
            # Show final summary
            word_count = len(result.split())
            self.console.print(f"[green]✅ Response captured ({word_count} words)[/green]")
            
            return result
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Input cancelled by user[/yellow]")
            raise
        except EOFError:
            # Handle Ctrl+D (Unix) / Ctrl+Z (Windows)
            if lines:
                result = '\n'.join(lines)
                word_count = len(result.split())
                self.console.print(f"\n[green]Input completed with EOF signal ({word_count} words)[/green]")
                return result
            else:
                self.console.print("\n[yellow]No input provided[/yellow]")
                return ""
    
    def _collect_input_with_feedback(
        self,
        lines: List[str],
        start_time: datetime,
        end_time: Optional[datetime],
        show_word_count: bool,
        show_time: bool,
        session_info: Optional[PracticeSession]
    ) -> str:
        """
        Collect input with live feedback display.
        
        Args:
            lines: List to collect input lines
            start_time: When input started
            end_time: When input should end (optional)
            show_word_count: Show word count
            show_time: Show elapsed time
            session_info: Session information
            
        Returns:
            Collected input as string
        """
        # Simple input collection without live feedback layout
        # The layout was causing display issues, so we'll use a simpler approach
        self.console.print("[dim]Start typing your response. Type 'SUBMIT' on a new line when finished:[/dim]")
        
        try:
            while True:
                # Check time limit
                if end_time and datetime.now() > end_time:
                    self.console.print("\n[red]⏰ Time limit reached![/red]")
                    break
                
                try:
                    # Show simple prompt for each line
                    if not lines:
                        line = input(">> ")
                    else:
                        line = input("   ")
                    
                    # Check for submission keywords
                    if line.strip() in self.submission_keywords:
                        self.console.print("\n[green]✅ Response submitted[/green]")
                        break
                    
                    # Check for cancellation keywords
                    if line.strip() in self.cancel_keywords:
                        self.console.print("\n[yellow]❌ Input cancelled[/yellow]")
                        raise KeyboardInterrupt()
                    
                    # Add line to collection
                    lines.append(line)
                    
                    # Show word count every few lines
                    if len(lines) % 5 == 0 and show_word_count:
                        current_text = '\n'.join(lines)
                        word_count = len(current_text.split()) if current_text.strip() else 0
                        self.console.print(f"[dim]Words so far: {word_count}[/dim]")
                    
                except EOFError:
                    # Handle Ctrl+D/Ctrl+Z
                    self.console.print("\n[green]✅ Input completed with EOF signal[/green]")
                    break
                except KeyboardInterrupt:
                    # Handle Ctrl+C
                    raise
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]❌ Input cancelled[/yellow]")
            raise
        
        return '\n'.join(lines)
    
    def _update_feedback(
        self,
        layout: Layout,
        lines: List[str],
        start_time: datetime,
        end_time: Optional[datetime],
        show_word_count: bool,
        show_time: bool,
        session_info: Optional[PracticeSession]
    ) -> None:
        """
        Update feedback display in background thread.
        
        Args:
            layout: Rich layout to update
            lines: Current input lines
            start_time: Input start time
            end_time: Input end time (optional)
            show_word_count: Show word count
            show_time: Show elapsed time
            session_info: Session information
        """
        while True:
            try:
                # Calculate current statistics
                current_text = '\n'.join(lines)
                word_count = len(current_text.split()) if current_text.strip() else 0
                char_count = len(current_text)
                line_count = len(lines)
                
                # Calculate time information
                elapsed = datetime.now() - start_time
                elapsed_str = self._format_time_delta(elapsed)
                
                # Create feedback content
                feedback_content = []
                
                if show_word_count:
                    # Word count with color coding
                    word_color = "white"
                    if session_info and session_info.task_prompt and session_info.task_prompt.word_limit:
                        word_limit = session_info.task_prompt.word_limit
                        if word_count < word_limit * 0.8:
                            word_color = "yellow"
                        elif word_count > word_limit * 1.2:
                            word_color = "red"
                        else:
                            word_color = "green"
                        
                        feedback_content.append(f"[{word_color}]Words: {word_count} / {word_limit}[/{word_color}]")
                    else:
                        feedback_content.append(f"[{word_color}]Words: {word_count}[/{word_color}]")
                    
                    feedback_content.append(f"Characters: {char_count}")
                    feedback_content.append(f"Lines: {line_count}")
                
                if show_time:
                    feedback_content.append(f"Elapsed: {elapsed_str}")
                    
                    if end_time:
                        remaining = end_time - datetime.now()
                        if remaining.total_seconds() > 0:
                            remaining_str = self._format_time_delta(remaining)
                            
                            # Color code remaining time
                            if remaining.total_seconds() < 300:  # Less than 5 minutes
                                time_color = "red"
                            elif remaining.total_seconds() < 600:  # Less than 10 minutes
                                time_color = "yellow"
                            else:
                                time_color = "green"
                            
                            feedback_content.append(f"[{time_color}]Remaining: {remaining_str}[/{time_color}]")
                        else:
                            feedback_content.append("[red]⏰ Time's up![/red]")
                
                # Update input area
                input_instruction = Text("Type your response (SUBMIT when done, CANCEL to quit):")
                input_instruction.stylize("dim")
                layout["input_area"].update(Panel(input_instruction, border_style="dim"))
                
                # Update feedback area
                if feedback_content:
                    feedback_text = " | ".join(feedback_content)
                    feedback_panel = Panel(
                        Align.center(Text(feedback_text)),
                        title="📊 Progress",
                        border_style="blue",
                        padding=(0, 1)
                    )
                    layout["feedback"].update(feedback_panel)
                
                time.sleep(1)  # Update every second
                
            except Exception:
                # Silently handle any errors in background thread
                break
    
    def _display_input_instructions(self) -> None:
        """Display input instructions to user."""
        instructions = """
[bold]📝 How to Enter Your Response:[/bold]

• Start typing your IELTS response line by line
• Press [green]Enter[/green] after each line to continue
• Type [yellow]'SUBMIT'[/yellow] on a new line when you're finished
• Type [red]'CANCEL'[/red] to quit without saving
• Use [cyan]Ctrl+D[/cyan] (Unix) or [cyan]Ctrl+Z[/cyan] (Windows) to submit
• Use [red]Ctrl+C[/red] to cancel

[dim]💡 Tip: Write your complete essay/letter/report, then type SUBMIT when done[/dim]
        """
        
        panel = Panel(
            instructions.strip(),
            title="ℹ️ Input Instructions",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def get_simple_input(self, prompt: str, default: str = None) -> str:
        """
        Get simple single-line input.
        
        Args:
            prompt: Input prompt
            default: Default value
            
        Returns:
            User input
        """
        return Prompt.ask(prompt, default=default)
    
    def get_confirmation(self, prompt: str, default: bool = True) -> bool:
        """
        Get yes/no confirmation from user.
        
        Args:
            prompt: Confirmation prompt
            default: Default response
            
        Returns:
            User confirmation
        """
        from rich.prompt import Confirm
        return Confirm.ask(prompt, default=default)
    
    def get_choice(self, prompt: str, choices: List[str], default: str = None) -> str:
        """
        Get choice from list of options.
        
        Args:
            prompt: Choice prompt
            choices: List of valid choices
            default: Default choice
            
        Returns:
            Selected choice
        """
        return Prompt.ask(prompt, choices=choices, default=default)
    
    def get_number(self, prompt: str, min_value: int = None, max_value: int = None, default: int = None) -> int:
        """
        Get numeric input with validation.
        
        Args:
            prompt: Input prompt
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            default: Default value
            
        Returns:
            Validated number
        """
        from rich.prompt import IntPrompt
        
        while True:
            try:
                value = IntPrompt.ask(prompt, default=default)
                
                if min_value is not None and value < min_value:
                    display_error(f"Value must be at least {min_value}")
                    continue
                
                if max_value is not None and value > max_value:
                    display_error(f"Value must be at most {max_value}")
                    continue
                
                return value
                
            except (ValueError, TypeError):
                display_error("Please enter a valid number")
    
    def _format_time_delta(self, delta: timedelta) -> str:
        """
        Format time delta for display.
        
        Args:
            delta: Time delta to format
            
        Returns:
            Formatted time string
        """
        total_seconds = int(delta.total_seconds())
        
        if total_seconds < 0:
            return "00:00"
        
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def display_input_summary(self, content: str) -> None:
        """
        Display summary of user input.
        
        Args:
            content: Input content to summarize
        """
        if not content.strip():
            display_warning("No content to summarize")
            return
        
        # Calculate statistics
        word_count = len(content.split())
        char_count = len(content)
        line_count = len(content.split('\n'))
        
        # Create summary table
        from rich.table import Table
        
        summary_table = Table(show_header=False, box=None, padding=(0, 1))
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Word Count", str(word_count))
        summary_table.add_row("Character Count", str(char_count))
        summary_table.add_row("Line Count", str(line_count))
        
        # Display preview of content (first 100 characters)
        preview = content[:100]
        if len(content) > 100:
            preview += "..."
        
        summary_table.add_row("Preview", f'"{preview}"')
        
        panel = Panel(
            summary_table,
            title="📝 Input Summary",
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(panel)
    
    def handle_paste_input(self, content: str) -> str:
        """
        Handle pasted content (if detected).
        
        Args:
            content: Pasted content
            
        Returns:
            Processed content
        """
        # Detect if content might be pasted (multiple lines at once)
        if '\n' in content and len(content.split('\n')) > 10:
            self.console.print("[yellow]📋 Large content detected (possibly pasted)[/yellow]")
            
            if self.get_confirmation("Process this content as your response?"):
                return content
            else:
                display_info("Content discarded. Please type your response manually.")
                return ""
        
        return content
