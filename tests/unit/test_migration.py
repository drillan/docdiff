"""Tests for database migration system."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from docdiff.database.connection import DatabaseConnection
from docdiff.database.migrate import MigrationRunner


class TestMigrationRunner:
    """Test MigrationRunner class."""

    def test_init_creates_migration_table(self):
        """Test that initialization creates the migration table."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        conn = DatabaseConnection(db_path)
        conn.connect()

        # Create runner
        _ = MigrationRunner(conn)

        # Check table exists
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
        )
        tables = list(result)
        assert len(tables) == 1
        assert tables[0]["name"] == "schema_migrations"

        conn.close()
        db_path.unlink()

    def test_get_applied_migrations_empty(self):
        """Test getting applied migrations when none exist."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        conn = DatabaseConnection(db_path)
        conn.connect()

        runner = MigrationRunner(conn)
        migrations = runner.get_applied_migrations()

        assert migrations == []

        conn.close()
        db_path.unlink()

    def test_get_applied_migrations_with_data(self):
        """Test getting applied migrations with existing data."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        conn = DatabaseConnection(db_path)
        conn.connect()

        runner = MigrationRunner(conn)

        # Add some migrations
        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            ("001", "2024-01-01T00:00:00"),
        )
        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            ("002", "2024-01-02T00:00:00"),
        )
        conn.commit()

        migrations = runner.get_applied_migrations()
        assert migrations == ["001", "002"]

        conn.close()
        db_path.unlink()

    def test_apply_migration_invalid_filename(self):
        """Test applying migration with invalid filename."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        conn = DatabaseConnection(db_path)
        conn.connect()

        runner = MigrationRunner(conn)

        # Create invalid migration file
        invalid_file = Path("invalid_migration.py")

        with pytest.raises(ValueError, match="Invalid migration filename"):
            runner.apply_migration(invalid_file)

        conn.close()
        db_path.unlink()

    def test_apply_migration_already_applied(self, capsys):
        """Test applying migration that's already applied."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        conn = DatabaseConnection(db_path)
        conn.connect()

        runner = MigrationRunner(conn)

        # Mark migration as applied
        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            ("001", "2024-01-01T00:00:00"),
        )
        conn.commit()

        # Create migration file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix="001_test_", delete=False
        ) as mig_file:
            mig_file.write("def upgrade(conn): pass")
            migration_path = Path(mig_file.name)

        runner.apply_migration(migration_path)

        captured = capsys.readouterr()
        assert "✓ Migration 001 already applied" in captured.out

        conn.close()
        db_path.unlink()
        migration_path.unlink()

    @patch("importlib.util.spec_from_file_location")
    def test_apply_migration_success(self, mock_spec_from_file, capsys):
        """Test successfully applying a migration."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        conn = DatabaseConnection(db_path)
        conn.connect()

        runner = MigrationRunner(conn)

        # Mock the migration module
        mock_module = MagicMock()
        mock_module.upgrade = MagicMock()

        mock_spec = MagicMock()
        mock_spec.loader = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        # Mock module_from_spec
        with patch("importlib.util.module_from_spec", return_value=mock_module):
            # Create migration file
            migration_path = Path("001_test_migration.py")

            runner.apply_migration(migration_path)

            # Check upgrade was called
            mock_module.upgrade.assert_called_once_with(conn)

            # Check migration was recorded
            migrations = runner.get_applied_migrations()
            assert "001" in migrations

            captured = capsys.readouterr()
            assert "✓ Applied migration 001" in captured.out

        conn.close()
        db_path.unlink()

    def test_run_all_no_directory(self, capsys):
        """Test running all migrations when directory doesn't exist."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        conn = DatabaseConnection(db_path)
        conn.connect()

        runner = MigrationRunner(conn)

        # Run with non-existent directory
        runner.run_all(Path("/nonexistent/migrations"))

        captured = capsys.readouterr()
        assert "No migrations directory found" in captured.out

        conn.close()
        db_path.unlink()

    def test_run_all_no_migrations(self, capsys):
        """Test running all migrations when none exist."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        with tempfile.TemporaryDirectory() as tmpdir:
            conn = DatabaseConnection(db_path)
            conn.connect()

            runner = MigrationRunner(conn)

            # Run with empty directory
            runner.run_all(Path(tmpdir))

            captured = capsys.readouterr()
            assert "No migrations found" in captured.out

            conn.close()

        db_path.unlink()
