"""
Database operations and session management for IELTS CLI application.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import aiosqlite
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from .models import (
    Base, SessionModel, CriteriaAssessmentModel, UserStatsModel, 
    ErrorLogModel, ConfigBackupModel,
    session_model_to_practice_session, practice_session_to_session_model
)
from ..core.models import PracticeSession, SessionStats, ErrorLog
from ..utils import get_app_data_dir, display_error, display_warning, format_duration

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Exception raised for database-related errors."""
    pass


class DatabaseManager:
    """Manages SQLite database operations for IELTS CLI application."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default path.
        """
        if db_path is None:
            app_dir = get_app_data_dir()
            self.db_path = app_dir / "ieltscli.db"
        else:
            self.db_path = Path(db_path)
        
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create SQLAlchemy engine and session factory
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            connect_args={"check_same_thread": False}
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database tables and indexes."""
        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Run any migrations if needed
            self._run_migrations()
            
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def _run_migrations(self) -> None:
        """Run database migrations for schema updates."""
        try:
            # Check if we need to run any migrations
            # This is a placeholder for future schema changes
            pass
        except Exception as e:
            logger.warning(f"Migration failed: {e}")
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close database connections."""
        try:
            self.engine.dispose()
        except Exception as e:
            logger.warning(f"Error closing database: {e}")
    
    # Session-related operations
    def save_session(self, practice_session: PracticeSession) -> None:
        """
        Save or update a practice session.
        
        Args:
            practice_session: PracticeSession to save
            
        Raises:
            DatabaseError: If save operation fails
        """
        db_session = self.get_session()
        try:
            # Convert to database model
            session_model = practice_session_to_session_model(practice_session)
            
            # Check if session already exists
            existing = db_session.query(SessionModel).filter_by(
                session_id=practice_session.session_id
            ).first()
            
            if existing:
                # Update existing session
                for key, value in session_model.__dict__.items():
                    if not key.startswith('_') and key != 'id':
                        setattr(existing, key, value)
                db_session.merge(existing)
            else:
                # Add new session
                db_session.add(session_model)
            
            # Save criteria assessments if present
            if practice_session.assessment and practice_session.assessment.criteria_scores:
                # Remove existing criteria assessments
                db_session.query(CriteriaAssessmentModel).filter_by(
                    session_id=practice_session.session_id
                ).delete()
                
                # Add new criteria assessments
                for criteria in practice_session.assessment.criteria_scores:
                    criteria_model = CriteriaAssessmentModel(
                        session_id=practice_session.session_id,
                        criterion_name=criteria.criterion_name,
                        score=criteria.score,
                        feedback=criteria.feedback,
                        strengths=criteria.strengths,
                        areas_for_improvement=criteria.areas_for_improvement
                    )
                    db_session.add(criteria_model)
            
            db_session.commit()
            
        except SQLAlchemyError as e:
            db_session.rollback()
            raise DatabaseError(f"Failed to save session: {e}")
        finally:
            db_session.close()
    
    def get_session_by_id(self, session_id: str) -> Optional[PracticeSession]:
        """
        Get a practice session by ID.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            PracticeSession if found, None otherwise
        """
        db_session = self.get_session()
        try:
            session_model = db_session.query(SessionModel).filter_by(
                session_id=session_id
            ).first()
            
            if session_model:
                return session_model_to_practice_session(session_model)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
        finally:
            db_session.close()
    
    def get_recent_sessions(
        self, 
        limit: int = 10, 
        status_filter: List[str] = None
    ) -> List[PracticeSession]:
        """
        Get recent practice sessions.
        
        Args:
            limit: Maximum number of sessions to return
            status_filter: List of status values to filter by
            
        Returns:
            List of recent practice sessions
        """
        db_session = self.get_session()
        try:
            query = db_session.query(SessionModel).order_by(
                SessionModel.created_at.desc()
            )
            
            if status_filter:
                query = query.filter(SessionModel.status.in_(status_filter))
            
            session_models = query.limit(limit).all()
            
            sessions = []
            for model in session_models:
                session = session_model_to_practice_session(model)
                if session:
                    sessions.append(session)
            
            return sessions
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get recent sessions: {e}")
            return []
        finally:
            db_session.close()
    
    def get_all_user_sessions(self) -> List[PracticeSession]:
        """
        Get all user sessions.
        
        Returns:
            List of all user sessions
        """
        db_session = self.get_session()
        try:
            session_models = db_session.query(SessionModel).order_by(
                SessionModel.created_at.asc()
            ).all()
            
            sessions = []
            for model in session_models:
                session = session_model_to_practice_session(model)
                if session:
                    sessions.append(session)
            
            return sessions
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get all sessions: {e}")
            return []
        finally:
            db_session.close()
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a practice session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        db_session = self.get_session()
        try:
            deleted_count = db_session.query(SessionModel).filter_by(
                session_id=session_id
            ).delete()
            
            db_session.commit()
            return deleted_count > 0
            
        except SQLAlchemyError as e:
            db_session.rollback()
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
        finally:
            db_session.close()
    
    def get_sessions_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PracticeSession]:
        """
        Get sessions within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of sessions in date range
        """
        db_session = self.get_session()
        try:
            session_models = db_session.query(SessionModel).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at <= end_date
            ).order_by(SessionModel.created_at.desc()).all()
            
            sessions = []
            for model in session_models:
                session = session_model_to_practice_session(model)
                if session:
                    sessions.append(session)
            
            return sessions
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get sessions by date range: {e}")
            return []
        finally:
            db_session.close()
    
    # Statistics operations
    def calculate_user_statistics(self) -> SessionStats:
        """
        Calculate comprehensive user statistics.
        
        Returns:
            SessionStats object with calculated statistics
        """
        db_session = self.get_session()
        try:
            # Get all sessions
            all_sessions = self.get_all_user_sessions()
            
            # Create and update statistics
            stats = SessionStats()
            stats.update_stats(all_sessions)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate user statistics: {e}")
            return SessionStats()
        finally:
            db_session.close()
    
    def save_user_statistics(self, stats: SessionStats) -> None:
        """
        Save user statistics to database.
        
        Args:
            stats: SessionStats to save
        """
        db_session = self.get_session()
        try:
            stats_model = UserStatsModel(
                total_sessions=stats.total_sessions,
                completed_sessions=stats.completed_sessions,
                average_score=stats.average_score,
                best_score=stats.best_score,
                improvement_trend=stats.improvement_trend,
                # Map task type distribution
                writing_task_2_count=stats.task_type_distribution.get('writing_task_2', 0),
                writing_task_1_count=stats.task_type_distribution.get('writing_task_1_academic', 0) + 
                                    stats.task_type_distribution.get('writing_task_1_general', 0),
            )
            
            db_session.add(stats_model)
            db_session.commit()
            
        except SQLAlchemyError as e:
            db_session.rollback()
            logger.error(f"Failed to save user statistics: {e}")
        finally:
            db_session.close()
    
    # Error logging
    def log_error(self, error_log: ErrorLog) -> None:
        """
        Log an error to the database.
        
        Args:
            error_log: ErrorLog to save
        """
        db_session = self.get_session()
        try:
            error_model = ErrorLogModel(
                error_id=error_log.error_id,
                error_type=error_log.error_type,
                error_message=error_log.error_message,
                error_context=error_log.context,
                timestamp=error_log.timestamp,
                user_action=error_log.user_action,
                resolved=error_log.resolved
            )
            
            db_session.add(error_model)
            db_session.commit()
            
        except SQLAlchemyError as e:
            db_session.rollback()
            logger.error(f"Failed to log error: {e}")
        finally:
            db_session.close()
    
    def get_recent_errors(self, limit: int = 20) -> List[ErrorLog]:
        """
        Get recent error logs.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error logs
        """
        db_session = self.get_session()
        try:
            error_models = db_session.query(ErrorLogModel).order_by(
                ErrorLogModel.timestamp.desc()
            ).limit(limit).all()
            
            errors = []
            for model in error_models:
                error_log = ErrorLog(
                    error_id=model.error_id,
                    error_type=model.error_type,
                    error_message=model.error_message,
                    context=model.error_context or {},
                    timestamp=model.timestamp,
                    user_action=model.user_action,
                    resolved=model.resolved
                )
                errors.append(error_log)
            
            return errors
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get recent errors: {e}")
            return []
        finally:
            db_session.close()
    
    # Maintenance operations
    def cleanup_old_sessions(self, days_old: int = 90) -> int:
        """
        Clean up old sessions older than specified days.
        
        Args:
            days_old: Number of days old to consider for cleanup
            
        Returns:
            Number of sessions deleted
        """
        db_session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            deleted_count = db_session.query(SessionModel).filter(
                SessionModel.created_at < cutoff_date,
                SessionModel.status.in_(['cancelled', 'error'])
            ).delete()
            
            db_session.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old sessions")
            
            return deleted_count
            
        except SQLAlchemyError as e:
            db_session.rollback()
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
        finally:
            db_session.close()
    
    def vacuum_database(self) -> None:
        """Vacuum the database to reclaim space and optimize performance."""
        try:
            # Use raw connection for VACUUM command
            with self.engine.raw_connection() as conn:
                conn.execute("VACUUM")
            
            logger.info("Database vacuumed successfully")
            
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information and statistics.
        
        Returns:
            Dictionary with database info
        """
        db_session = self.get_session()
        try:
            # Get table counts
            session_count = db_session.query(SessionModel).count()
            criteria_count = db_session.query(CriteriaAssessmentModel).count()
            error_count = db_session.query(ErrorLogModel).count()
            
            # Get database file size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return {
                "database_path": str(self.db_path),
                "database_size_mb": round(db_size / (1024 * 1024), 2),
                "session_count": session_count,
                "criteria_assessment_count": criteria_count,
                "error_log_count": error_count,
                "created_at": datetime.fromtimestamp(self.db_path.stat().st_ctime).isoformat() if self.db_path.exists() else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}
        finally:
            db_session.close()
    
    def backup_database(self, backup_path: str = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for backup file. If None, creates in app data dir.
            
        Returns:
            Path to the backup file
            
        Raises:
            DatabaseError: If backup fails
        """
        try:
            if backup_path is None:
                app_dir = get_app_data_dir()
                backup_dir = app_dir / "backups"
                backup_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"ieltscli_backup_{timestamp}.db"
            
            # Copy database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Database backed up to {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            raise DatabaseError(f"Failed to backup database: {e}")
    
    def restore_database(self, backup_path: str) -> None:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Raises:
            DatabaseError: If restore fails
        """
        try:
            import shutil
            
            # Close current connections
            self.close()
            
            # Restore database file
            shutil.copy2(backup_path, self.db_path)
            
            # Reinitialize
            self.__init__(str(self.db_path))
            
            logger.info(f"Database restored from {backup_path}")
            
        except Exception as e:
            raise DatabaseError(f"Failed to restore database: {e}")


class AsyncSessionManager:
    """Async wrapper for database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize async session manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    async def save_session(self, practice_session: PracticeSession) -> None:
        """Async save session."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.db_manager.save_session, practice_session)
    
    async def get_session(self, session_id: str) -> Optional[PracticeSession]:
        """Async get session."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.db_manager.get_session_by_id, session_id)
    
    async def get_recent_sessions(self, limit: int = 10) -> List[PracticeSession]:
        """Async get recent sessions."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.db_manager.get_recent_sessions, limit)
    
    async def get_all_user_sessions(self) -> List[PracticeSession]:
        """Async get all user sessions."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.db_manager.get_all_user_sessions)
    
    async def delete_session(self, session_id: str) -> bool:
        """Async delete session."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.db_manager.delete_session, session_id)
    
    async def calculate_user_statistics(self) -> SessionStats:
        """Async calculate user statistics."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.db_manager.calculate_user_statistics)


# Global database manager instance
db_manager = DatabaseManager()
session_manager = AsyncSessionManager(db_manager)
