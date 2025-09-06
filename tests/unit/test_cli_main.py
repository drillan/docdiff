"""Tests for CLI main module."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from docdiff.cli.main import app


class TestCLIMain:
    """Test CLI main functions."""

    def test_version_callback(self):
        """Test version callback."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        # Version exits with code 0 after showing version
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    @patch("docdiff.cli.main.parse_command")
    def test_parse_command(self, mock_parse_command):
        """Test parse command."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test directory
            test_dir = Path("test_project")
            test_dir.mkdir()

            result = runner.invoke(app, ["parse", str(test_dir)])

            assert result.exit_code == 0
            mock_parse_command.assert_called_once()

            # Check arguments
            call_args = mock_parse_command.call_args[0]
            assert call_args[0].name == "test_project"
            assert call_args[1] is None  # db_path
            assert call_args[2] is False  # verbose

    @patch("docdiff.cli.main.parse_command")
    def test_parse_command_with_options(self, mock_parse_command):
        """Test parse command with options."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test directory
            test_dir = Path("test_project")
            test_dir.mkdir()

            result = runner.invoke(
                app, ["parse", str(test_dir), "--db", "custom.db", "--verbose"]
            )

            assert result.exit_code == 0
            mock_parse_command.assert_called_once()

            # Check arguments
            call_args = mock_parse_command.call_args[0]
            assert call_args[0].name == "test_project"
            assert call_args[1] == Path("custom.db")
            assert call_args[2] is True  # verbose

    @patch("docdiff.cli.main.status_command")
    def test_status_command(self, mock_status_command):
        """Test status command."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test directory
            test_dir = Path("test_project")
            test_dir.mkdir()

            result = runner.invoke(app, ["status", str(test_dir)])

            assert result.exit_code == 0
            mock_status_command.assert_called_once()

            # Check arguments
            call_args = mock_status_command.call_args[0]
            assert call_args[0].name == "test_project"
            assert call_args[1] is None  # db_path
            assert call_args[2] is None  # target_lang

    @patch("docdiff.cli.main.status_command")
    def test_status_command_with_options(self, mock_status_command):
        """Test status command with options."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test directory
            test_dir = Path("test_project")
            test_dir.mkdir()

            result = runner.invoke(
                app, ["status", str(test_dir), "--db", "custom.db", "--lang", "ja"]
            )

            assert result.exit_code == 0
            mock_status_command.assert_called_once()

            # Check arguments
            call_args = mock_status_command.call_args[0]
            assert call_args[0].name == "test_project"
            assert call_args[1] == Path("custom.db")
            assert call_args[2] == "ja"  # target_lang

    @patch("docdiff.cli.main.simple_compare_command")
    def test_simple_compare_command(self, mock_simple_compare_command):
        """Test simple_compare command."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create test directories
            source_dir = Path("source")
            source_dir.mkdir()
            target_dir = Path("target")
            target_dir.mkdir()

            result = runner.invoke(
                app, ["simple-compare", str(source_dir), str(target_dir)]
            )

            assert result.exit_code == 0
            mock_simple_compare_command.assert_called_once()

            # Check arguments
            call_args = mock_simple_compare_command.call_args[0]
            assert call_args[0].name == "source"
            assert call_args[1].name == "target"
            assert call_args[2] is None  # output_file

    @patch("docdiff.cli.main.simple_compare_command")
    def test_simple_compare_command_with_output(self, mock_simple_compare_command):
        """Test simple_compare command with output option."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create test directories
            source_dir = Path("source")
            source_dir.mkdir()
            target_dir = Path("target")
            target_dir.mkdir()

            result = runner.invoke(
                app,
                [
                    "simple-compare",
                    str(source_dir),
                    str(target_dir),
                    "--output",
                    "result.json",
                ],
            )

            assert result.exit_code == 0
            mock_simple_compare_command.assert_called_once()

            # Check arguments
            call_args = mock_simple_compare_command.call_args[0]
            assert call_args[0].name == "source"
            assert call_args[1].name == "target"
            assert call_args[2] == Path("result.json")

    def test_help_message(self):
        """Test help message."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Document structure analysis" in result.output
        assert "parse" in result.output
        assert "status" in result.output
        assert "simple-compare" in result.output

    def test_invalid_command(self):
        """Test invalid command."""
        runner = CliRunner()
        result = runner.invoke(app, ["invalid-command"])

        assert result.exit_code != 0
        # Check for typer error message
        assert (
            "No such command" in result.output
            or "Error" in result.output
            or result.exit_code == 2
        )
