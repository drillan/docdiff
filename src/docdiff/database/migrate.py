"""Database migration tool."""

import importlib.util
import re
from datetime import datetime
from pathlib import Path
from typing import List

from docdiff.database.connection import DatabaseConnection


class MigrationRunner:
    """Runs database migrations."""

    def __init__(self, conn: DatabaseConnection):
        self.conn = conn
        self._ensure_migration_table()

    def _ensure_migration_table(self) -> None:
        """Create migration tracking table."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        result = self.conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        return [row["version"] for row in result]

    def apply_migration(self, migration_file: Path) -> None:
        """Apply a single migration."""
        # Extract version from filename (e.g., "001_add_language.py")
        match = re.match(r"(\d+)_", migration_file.name)
        if not match:
            raise ValueError(f"Invalid migration filename: {migration_file.name}")
        version = match.group(1)

        # Check if already applied
        if version in self.get_applied_migrations():
            print(f"✓ Migration {version} already applied")
            return

        # Import and run migration
        spec = importlib.util.spec_from_file_location(
            f"migration_{version}", migration_file
        )
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load migration from {migration_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Run upgrade
        module.upgrade(self.conn)

        # Record migration
        self.conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (version, datetime.now().isoformat()),
        )
        self.conn.commit()
        print(f"✓ Applied migration {version}: {migration_file.name}")

    def run_all(self, migrations_dir: Path) -> None:
        """Run all pending migrations in a directory."""
        if not migrations_dir.exists():
            print(f"No migrations directory found at {migrations_dir}")
            return

        # Get all migration files sorted by version
        migration_files = sorted(
            [f for f in migrations_dir.glob("*.py") if re.match(r"\d+_", f.name)]
        )

        if not migration_files:
            print("No migrations found")
            return

        for migration_file in migration_files:
            self.apply_migration(migration_file)

        print("All migrations applied successfully")
