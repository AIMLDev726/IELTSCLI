"""
Rich UI interface components for IELTS CLI application.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
from rich.rule import Rule
from rich.markdown import Markdown
from rich.syntax import Syntax

from ..core.models import (
    AppConfig, PracticeSession, Assessment, SessionStats, 
    TaskType, LLMProvider, BandScore, AssessmentCriteria
)
from ..core.config import ConfigManager
from ..utils import format_duration, get_app_data_dir


class IELTSInterface:
    """Rich-based UI interface for IELTS CLI application."""
    
    def __init__(self, console: Console):
        """
        Initialize interface with console.
        
        Args:
            console: Rich Console instance
        """
        self.console = console
        
        # Define color scheme
        self.colors = {
            "primary": "#2563eb",      # Blue
            "success": "#059669",      # Green
            "warning": "#d97706",      # Orange
            "error": "#dc2626",        # Red
            "info": "#0891b2",         # Cyan
            "muted": "#6b7280",        # Gray
            "accent": "#7c3aed"        # Purple
        }
        
        # Band score colors
        self.band_colors = {
            9.0: "bright_green",
            8.5: "green",
            8.0: "green",
            7.5: "yellow",
            7.0: "yellow",
            6.5: "bright_yellow",
            6.0: "bright_yellow",
            5.5: "orange1",
            5.0: "orange1",
            4.5: "red",
            4.0: "red"
        }
    
    def display_welcome(self) -> None:
        """Display welcome message and application info."""
        welcome_text = """
        [bold blue]🎯 IELTS Practice CLI[/bold blue]
        
        [italic]AI-powered writing assessment tool for IELTS preparation[/italic]
        
        • Get instant feedback on your writing
        • Track your progress over time
        • Practice with authentic IELTS tasks
        • Improve your band score with detailed analysis
        """
        
        panel = Panel(
            welcome_text,
            title="Welcome",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def display_task_prompt(self, session) -> None:
        """
        Display IELTS task prompt with formatting.
        
        Args:
            session: PracticeSession object
        """
        task_prompt = session.task_prompt
        # Task type header
        task_type_text = Text(f"IELTS {task_prompt.task_type.value.replace('_', ' ').title()}")
        task_type_text.stylize("bold blue")
        
        # Time limit - get from session if available, otherwise from task prompt
        time_limit = session.time_limit_minutes if session.time_limit_minutes else task_prompt.time_limit
        time_info = f"⏱️ Time limit: {time_limit} minutes"
        
        # Word limit info
        if task_prompt.word_count_min and task_prompt.word_count_max:
            word_info = f"📝 Word limit: {task_prompt.word_count_min}-{task_prompt.word_count_max} words"
        elif task_prompt.word_count_min:
            word_info = f"📝 Minimum words: {task_prompt.word_count_min}"
        elif task_prompt.word_count_max:
            word_info = f"📝 Maximum words: {task_prompt.word_count_max}"
        else:
            word_info = "📝 No word limit specified"
        
        # Prompt content with proper markdown rendering
        prompt_content = Markdown(task_prompt.prompt_text)
        
        # Additional instructions if available
        instructions_content = ""
        if task_prompt.instructions:
            instructions_content = Markdown("\n".join(task_prompt.instructions))
        
        # Create the panel
        panel_content = f"""
{task_type_text}

{time_info} | {word_info}

---

{task_prompt.prompt_text}
"""
        
        if task_prompt.instructions:
            panel_content += f"\n\n**Additional Instructions:**\n" + "\n".join(f"• {instruction}" for instruction in task_prompt.instructions)
        
        panel = Panel(
            Markdown(panel_content),
            title="📋 Task Prompt",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def display_session_info(self, session: PracticeSession) -> None:
        """
        Display practice session information.
        
        Args:
            session: PracticeSession object
        """
        # Create session info table
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Session ID", session.session_id)
        table.add_row("Task Type", session.task_prompt.task_type.value.replace('_', ' ').title())
        table.add_row("Status", self._format_status(session.status))
        table.add_row("Created", session.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        if session.time_limit_minutes:
            table.add_row("Time Limit", f"{session.time_limit_minutes} minutes")
        
        if session.started_at:
            table.add_row("Started", session.started_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        if session.completed_at:
            table.add_row("Completed", session.completed_at.strftime("%Y-%m-%d %H:%M:%S"))
            duration = session.completed_at - session.started_at
            table.add_row("Duration", format_duration(duration.total_seconds()))
        
        panel = Panel(
            table,
            title="📊 Session Information",
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def display_assessment_results(self, assessment: Assessment) -> None:
        """
        Display assessment results with detailed feedback.
        
        Args:
            assessment: Assessment object
        """
        # Overall score panel
        overall_score = assessment.overall_band_score
        score_color = self._get_band_color(overall_score)
        
        score_text = Text(f"Overall Band Score: {overall_score}", style=f"bold {score_color}")
        score_panel = Panel(
            Align.center(score_text),
            title="🎯 Assessment Results",
            border_style=score_color,
            padding=(1, 2)
        )
        
        self.console.print(score_panel)
        
        # Criteria scores table
        if assessment.criteria_scores:
            criteria_table = Table(title="📊 Criteria Breakdown", show_lines=True)
            criteria_table.add_column("Criterion", style="cyan", min_width=20)
            criteria_table.add_column("Score", justify="center", min_width=8)
            criteria_table.add_column("Feedback", style="white", min_width=40)
            
            for criteria in assessment.criteria_scores:
                score_color = self._get_band_color(criteria.score)
                score_text = f"[{score_color}]{criteria.score}[/{score_color}]"
                
                criteria_table.add_row(
                    criteria.criterion_name.replace('_', ' ').title(),
                    score_text,
                    criteria.feedback or "No specific feedback"
                )
            
            self.console.print(criteria_table)
        
        # Detailed feedback sections
        if assessment.detailed_feedback:
            feedback_sections = [
                ("💪 Strengths", assessment.detailed_feedback.get("strengths", [])),
                ("🎯 Areas for Improvement", assessment.detailed_feedback.get("areas_for_improvement", [])),
                ("💡 Suggestions", assessment.detailed_feedback.get("suggestions", [])),
                ("📚 Examples", assessment.detailed_feedback.get("examples", []))
            ]
            
            for title, items in feedback_sections:
                if items:
                    feedback_text = "\n".join([f"• {item}" for item in items])
                    feedback_panel = Panel(
                        feedback_text,
                        title=title,
                        border_style="dim",
                        padding=(1, 2)
                    )
                    self.console.print(feedback_panel)
        
        # Overall feedback
        if assessment.overall_feedback:
            overall_panel = Panel(
                assessment.overall_feedback,
                title="📝 Overall Feedback",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(overall_panel)
        
        self.console.print()
    
    def display_session_summary(self, session: PracticeSession) -> None:
        """
        Display session summary.
        
        Args:
            session: PracticeSession object
        """
        summary_table = Table(show_header=False, box=None, padding=(0, 1))
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        # Basic session info
        summary_table.add_row("Session ID", session.session_id)
        summary_table.add_row("Task Type", session.task_prompt.task_type.value.replace('_', ' ').title())
        
        # Response statistics
        if session.user_response:
            word_count = len(session.user_response.text.split())
            summary_table.add_row("Word Count", str(word_count))
            
            if session.task_prompt and (session.task_prompt.word_count_min or session.task_prompt.word_count_max):
                # Check against minimum word count
                if session.task_prompt.word_count_min and word_count < session.task_prompt.word_count_min:
                    word_status = f"[red]Below minimum ({session.task_prompt.word_count_min})[/red]"
                # Check against maximum word count
                elif session.task_prompt.word_count_max and word_count > session.task_prompt.word_count_max:
                    word_status = f"[red]Above maximum ({session.task_prompt.word_count_max})[/red]"
                else:
                    if session.task_prompt.word_count_min and session.task_prompt.word_count_max:
                        word_status = f"[green]Within range ({session.task_prompt.word_count_min}-{session.task_prompt.word_count_max})[/green]"
                    elif session.task_prompt.word_count_min:
                        word_status = f"[green]Above minimum ({session.task_prompt.word_count_min})[/green]"
                    else:
                        word_status = f"[green]Below maximum ({session.task_prompt.word_count_max})[/green]"
                
                summary_table.add_row("Word Count Status", word_status)
        
        # Time information
        if session.started_at and session.completed_at:
            duration = session.completed_at - session.started_at
            summary_table.add_row("Duration", format_duration(duration.total_seconds()))
        
        # Assessment summary
        if session.assessment:
            score_color = self._get_band_color(session.assessment.overall_band_score)
            score_text = f"[{score_color}]{session.assessment.overall_band_score}[/{score_color}]"
            summary_table.add_row("Overall Score", score_text)
        
        panel = Panel(
            summary_table,
            title="📈 Session Summary",
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def display_sessions_table(self, sessions: List[PracticeSession]) -> None:
        """
        Display sessions in a table format.
        
        Args:
            sessions: List of PracticeSession objects
        """
        table = Table(title="📚 Practice Sessions", show_lines=True)
        table.add_column("Session ID", style="cyan", min_width=8)
        table.add_column("Task Type", min_width=15)
        table.add_column("Status", justify="center", min_width=10)
        table.add_column("Score", justify="center", min_width=8)
        table.add_column("Created", min_width=16)
        table.add_column("Duration", min_width=10)
        
        for session in sessions:
            # Format session ID (show only last 8 characters)
            session_id_short = session.session_id[-8:]
            
            # Format task type
            task_type = session.task_prompt.task_type.value.replace('_', ' ').title()
            
            # Format status
            status = self._format_status(session.status)
            
            # Format score
            if session.assessment and session.assessment.overall_band_score:
                score_color = self._get_band_color(session.assessment.overall_band_score)
                score = f"[{score_color}]{session.assessment.overall_band_score}[/{score_color}]"
            else:
                score = "[dim]-[/dim]"
            
            # Format created date
            created = session.created_at.strftime("%m-%d %H:%M")
            
            # Format duration
            if session.user_response.time_taken:
                duration_str = format_duration(session.user_response.time_taken)
            elif session.started_at and session.completed_at:
                duration = session.completed_at - session.started_at
                duration_str = format_duration(duration.total_seconds())
            else:
                duration_str = "[dim]-[/dim]"
            
            table.add_row(
                session_id_short,
                task_type,
                status,
                score,
                created,
                duration_str
            )
        
        self.console.print(table)
        self.console.print()
    
    def display_session_details(self, session: PracticeSession) -> None:
        """
        Display detailed session information.
        
        Args:
            session: PracticeSession object
        """
        # Session header
        self.console.print(Rule(f"[bold blue]Session Details: {session.session_id}[/bold blue]"))
        
        # Display session info
        self.display_session_info(session)
        
        # Display task prompt
        if session.task_prompt:
            self.display_task_prompt(session)
        
        # Display user response
        if session.user_response and session.user_response.text:
            response_panel = Panel(
                session.user_response.text,
                title="📝 Your Response",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(response_panel)
        
        # Display assessment
        if session.assessment:
            self.display_assessment_results(session.assessment)
        
        # Display summary
        self.display_session_summary(session)
    
    def display_user_statistics(self, stats: SessionStats, detailed: bool = False) -> None:
        """
        Display user statistics and progress.
        
        Args:
            stats: SessionStats object
            detailed: Show detailed statistics
        """
        # Overview panel
        overview_table = Table(show_header=False, box=None, padding=(0, 1))
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="white")
        
        overview_table.add_row("Total Sessions", str(stats.total_sessions))
        overview_table.add_row("Completed Sessions", str(stats.completed_sessions))
        
        if stats.average_score:
            avg_color = self._get_band_color(stats.average_score)
            avg_text = f"[{avg_color}]{stats.average_score:.1f}[/{avg_color}]"
            overview_table.add_row("Average Score", avg_text)
        
        if stats.best_score:
            best_color = self._get_band_color(stats.best_score)
            best_text = f"[{best_color}]{stats.best_score:.1f}[/{best_color}]"
            overview_table.add_row("Best Score", best_text)
        
        overview_table.add_row("Improvement Trend", self._format_trend(stats.improvement_trend))
        
        overview_panel = Panel(
            overview_table,
            title="📊 Performance Overview",
            border_style="blue",
            padding=(0, 1)
        )
        
        self.console.print(overview_panel)
        
        # Task type distribution
        if stats.task_type_distribution:
            dist_table = Table(title="📝 Task Type Distribution")
            dist_table.add_column("Task Type", style="cyan")
            dist_table.add_column("Count", justify="center")
            dist_table.add_column("Percentage", justify="center")
            
            total = sum(stats.task_type_distribution.values())
            for task_type, count in stats.task_type_distribution.items():
                percentage = (count / total * 100) if total > 0 else 0
                dist_table.add_row(
                    task_type.replace('_', ' ').title(),
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            self.console.print(dist_table)
        
        # Detailed statistics
        if detailed and stats.score_history:
            # Score progression chart (simple text-based)
            self.console.print("\n[bold]📈 Score Progression[/bold]")
            
            for i, score in enumerate(stats.score_history[-10:], 1):  # Last 10 scores
                bar_length = int(score / 9.0 * 20)  # Scale to 20 characters
                bar = "█" * bar_length + "░" * (20 - bar_length)
                score_color = self._get_band_color(score)
                self.console.print(f"{i:2}: [{score_color}]{bar}[/{score_color}] {score:.1f}")
        
        self.console.print()
    
    def display_configuration(self, config: AppConfig) -> None:
        """
        Display current configuration.
        
        Args:
            config: AppConfig object
        """
        config_table = Table(title="⚙️ Current Configuration", show_lines=True)
        config_table.add_column("Setting", style="cyan", min_width=20)
        config_table.add_column("Value", style="white", min_width=30)
        
        # General settings
        config_table.add_row("Default Task Type", config.default_task_type.value.replace('_', ' ').title())
        config_table.add_row("LLM Provider", config.llm_provider.value.title())
        config_table.add_row("Auto Save Sessions", "✅ Yes" if config.user_preferences.save_sessions else "❌ No")
        config_table.add_row("Detailed Feedback", "✅ Yes" if config.user_preferences.show_detailed_feedback else "❌ No")
        config_table.add_row("Word Count Warnings", "✅ Yes" if config.user_preferences.word_count_warnings else "❌ No")
        
        # Model settings
        current_model_config = config.get_current_model_config()
        config_table.add_row("Model Name", current_model_config.model)
        config_table.add_row("Temperature", str(current_model_config.temperature))
        
        self.console.print(config_table)
        self.console.print()
    
    def display_database_info(self, db_info: Dict[str, Any]) -> None:
        """
        Display database information.
        
        Args:
            db_info: Database info dictionary
        """
        info_table = Table(title="🗄️ Database Information", show_lines=True)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        for key, value in db_info.items():
            if key == "error":
                info_table.add_row(key.replace('_', ' ').title(), f"[red]{value}[/red]")
            else:
                info_table.add_row(key.replace('_', ' ').title(), str(value))
        
        self.console.print(info_table)
        self.console.print()
    
    def display_version_info(self) -> None:
        """Display version and system information."""
        version_info = """
        [bold blue]IELTS Practice CLI[/bold blue]
        
        Version: 1.0.0
        Author: AI Assistant
        License: MIT
        
        [dim]Built with Python, Typer, Rich, and SQLAlchemy[/dim]
        """
        
        panel = Panel(
            version_info,
            title="📋 Version Information",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def interactive_configuration(self, config_manager: ConfigManager) -> None:
        """
        Interactive configuration menu.
        
        Args:
            config_manager: ConfigManager instance
        """
        config = config_manager.config
        
        self.console.print("[bold]⚙️ Interactive Configuration[/bold]\n")
        
        # LLM Provider configuration
        if Confirm.ask("Configure LLM provider?"):
            providers = [p.value for p in LLMProvider]
            self.console.print(f"Available providers: {', '.join(providers)}")
            
            provider_choice = Prompt.ask(
                "Select LLM provider",
                choices=providers,
                default=config.llm_provider.value
            )
            
            config.llm_provider = LLMProvider(provider_choice)
            
            # API Key
            if Confirm.ask(f"Set API key for {provider_choice}?"):
                api_key = Prompt.ask("Enter API key", password=True)
                config_manager.set_api_key(config.llm_provider, api_key)
            
            # Model name
            current_model = config.model_config.model_name
            new_model = Prompt.ask("Model name", default=current_model)
            current_model_config = config.get_current_model_config()
            current_model_config.model = new_model
        
        # Task type configuration
        if Confirm.ask("Set default task type?"):
            task_types = [t.value for t in TaskType]
            self.console.print(f"Available task types: {', '.join(task_types)}")
            
            task_choice = Prompt.ask(
                "Select default task type",
                choices=task_types,
                default=config.default_task_type.value
            )
            
            config.default_task_type = TaskType(task_choice)
        
        # Other settings
        if Confirm.ask("Configure other settings?"):
            config.user_preferences.save_sessions = Confirm.ask(
                "Auto-save sessions?",
                default=config.user_preferences.save_sessions
            )
            
            config.user_preferences.show_detailed_feedback = Confirm.ask(
                "Enable detailed feedback?",
                default=config.user_preferences.show_detailed_feedback
            )
            
            config.user_preferences.word_count_warnings = Confirm.ask(
                "Enable word count warnings?",
                default=config.user_preferences.word_count_warnings
            )
        
        # Save configuration
        config_manager.save_config(config)
        self.console.print("[green]✅ Configuration saved successfully![/green]")
    
    def export_sessions(self, sessions: List[PracticeSession], filename: str) -> None:
        """
        Export sessions to file.
        
        Args:
            sessions: List of sessions to export
            filename: Output filename
        """
        try:
            export_data = []
            for session in sessions:
                session_data = {
                    "session_id": session.session_id,
                    "task_type": session.task_prompt.task_type.value,
                    "status": session.status,
                    "created_at": session.created_at.isoformat(),
                    "started_at": session.started_at.isoformat() if session.started_at else None,
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                    "task_prompt": {
                        "prompt": session.task_prompt.prompt_text,
                        "task_type": session.task_prompt.task_type.value,
                        "time_limit_minutes": session.time_limit_minutes,
                        "word_count_min": session.task_prompt.word_count_min,
                        "word_count_max": session.task_prompt.word_count_max
                    } if session.task_prompt else None,
                    "user_response": {
                        "content": session.user_response.text,
                        "word_count": session.user_response.word_count,
                        "submitted_at": session.user_response.submitted_at.isoformat()
                    } if session.user_response else None,
                    "assessment": {
                        "overall_band_score": session.assessment.overall_band_score,
                        "overall_feedback": session.assessment.overall_feedback,
                        "criteria_scores": [
                            {
                                "criterion_name": criteria.criterion_name,
                                "score": criteria.score,
                                "feedback": criteria.feedback
                            }
                            for criteria in session.assessment.criteria_scores
                        ]
                    } if session.assessment else None
                }
                export_data.append(session_data)
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ Exported {len(sessions)} sessions to {filename}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]")
    
    def export_statistics(self, stats: SessionStats, filename: str) -> None:
        """
        Export statistics to file.
        
        Args:
            stats: SessionStats object
            filename: Output filename
        """
        try:
            stats_data = {
                "total_sessions": stats.total_sessions,
                "completed_sessions": stats.completed_sessions,
                "average_score": stats.average_score,
                "best_score": stats.best_score,
                "improvement_trend": stats.improvement_trend,
                "task_type_distribution": stats.task_type_distribution,
                "score_history": stats.score_history,
                "monthly_progress": stats.monthly_progress,
                "exported_at": datetime.now().isoformat()
            }
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ Statistics exported to {filename}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]")
    
    def _format_status(self, status: str) -> str:
        """Format session status with colors."""
        status_colors = {
            "created": "blue",
            "in_progress": "yellow",
            "completed": "green",
            "cancelled": "red",
            "error": "red"
        }
        
        color = status_colors.get(status, "white")
        return f"[{color}]{status.title()}[/{color}]"
    
    def _format_trend(self, trend: float) -> str:
        """Format improvement trend with indicators."""
        if trend > 0.1:
            return f"[green]↗ +{trend:.2f}[/green]"
        elif trend < -0.1:
            return f"[red]↘ {trend:.2f}[/red]"
        else:
            return f"[yellow]→ {trend:.2f}[/yellow]"
    
    def _get_band_color(self, score: float) -> str:
        """Get color for band score."""
        # Find the closest band score
        for band_score in sorted(self.band_colors.keys(), reverse=True):
            if score >= band_score:
                return self.band_colors[band_score]
        
        return "red"  # Default for very low scores
