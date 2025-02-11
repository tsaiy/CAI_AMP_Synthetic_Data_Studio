# app/migrations/alembic_manager.py
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from pathlib import Path
import os
from sqlalchemy import create_engine

class AlembicMigrationManager:
    def __init__(self, db_path: str = None):
        """Initialize Alembic with the same database path as DatabaseManager"""
        self.app_path = Path(__file__).parent.parent
        
        if db_path is None:
            db_path = self.app_path.parent / "metadata.db"
        self.db_path = db_path
        
        # Initialize Alembic config
        self.alembic_cfg = Config(str(self.app_path / "alembic.ini"))
        self.alembic_cfg.set_main_option('script_location', str(self.app_path / "alembic"))
        self.alembic_cfg.set_main_option('sqlalchemy.url', f'sqlite:///{db_path}')
        
        # Create engine for version checks
        self.engine = create_engine(f'sqlite:///{db_path}')

    async def get_db_version(self) -> str:
        """Get current database version"""
        with self.engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()

    async def handle_database_upgrade(self) -> tuple[bool, str]:
        """
        Handle database migrations carefully to avoid disrupting existing data
        """
        try:
            # First check if alembic_version table exists
            try:
                version = await self.get_db_version()
                if version is None:
                    # Database exists but no alembic version - stamp current
                    command.stamp(self.alembic_cfg, "head")
                    return True, "Existing database stamped with current version"
            except Exception:
                # No alembic_version table - stamp current
                command.stamp(self.alembic_cfg, "head")
                return True, "Existing database stamped with current version"
            
            # Now check for and apply any new migrations
            script = ScriptDirectory.from_config(self.alembic_cfg)
            head_revision = script.get_current_head()
            
            if version != head_revision:
                command.upgrade(self.alembic_cfg, "head")
                return True, "Database schema updated successfully"
            
            return True, "Database schema is up to date"

        except Exception as e:
            return False, f"Error during database upgrade: {str(e)}"