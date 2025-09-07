"""Unit tests for import command."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
import typer

from docdiff.cli.import_cmd import import_command
from docdiff.models import DocumentNode


@pytest.fixture
def mock_console():
    """Mock Rich console."""
    with patch("docdiff.cli.import_cmd.console") as mock:
        yield mock


@pytest.fixture
def mock_progress():
    """Mock Rich progress."""
    with patch("docdiff.cli.import_cmd.Progress") as mock:
        progress_instance = MagicMock()
        progress_instance.__enter__ = MagicMock(return_value=progress_instance)
        progress_instance.__exit__ = MagicMock(return_value=None)
        mock.return_value = progress_instance
        yield progress_instance


@pytest.fixture
def mock_parser():
    """Mock MyST parser."""
    with patch("docdiff.cli.import_cmd.MySTParser") as mock:
        parser_instance = MagicMock()
        parser_instance.parse.return_value = []
        mock.return_value = parser_instance
        yield parser_instance


@pytest.fixture
def mock_importer():
    """Mock TranslationImporter."""
    with patch("docdiff.cli.import_cmd.TranslationImporter") as mock:
        importer_instance = MagicMock()
        importer_instance.import_translations.return_value = (
            [],
            {
                "total": 0,
                "applied": 0,
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "errors": [],
            },
        )
        mock.return_value = importer_instance
        yield importer_instance


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary test files."""
    # Create import file
    import_file = tmp_path / "translations.json"
    import_file.write_text(json.dumps({"test": "data"}))

    # Create target directory
    target_dir = tmp_path / "docs"
    target_dir.mkdir()

    return import_file, target_dir


class TestImportCommandValidation:
    """Test import command validation."""

    def test_import_file_not_exists(self, mock_console):
        """Test error when import file doesn't exist."""
        with pytest.raises(typer.Exit) as exc_info:
            import_command(
                import_file=Path("nonexistent.json"),
                target_dir=Path("."),
            )
        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called_with(
            "[red]Error: Import file nonexistent.json does not exist[/red]"
        )

    def test_auto_detect_json_format(
        self, temp_files, mock_importer, mock_parser, mock_progress
    ):
        """Test auto-detection of JSON format."""
        import_file, target_dir = temp_files
        import_command(
            import_file=import_file,
            target_dir=target_dir,
            format=None,
        )
        mock_importer.import_translations.assert_called_once()
        call_args = mock_importer.import_translations.call_args
        assert call_args[1]["format"] == "json"

    def test_auto_detect_csv_format(self, tmp_path, mock_console):
        """Test auto-detection of CSV format."""
        import_file = tmp_path / "translations.csv"
        import_file.write_text("header1,header2")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        with patch("docdiff.cli.import_cmd.TranslationImporter") as mock_imp:
            importer = MagicMock()
            importer.import_translations.return_value = (
                [],
                {"total": 0, "applied": 0, "created": 0, "updated": 0, "skipped": 0},
            )
            mock_imp.return_value = importer

            with patch("docdiff.cli.import_cmd.MySTParser"):
                with patch("docdiff.cli.import_cmd.Progress"):
                    import_command(
                        import_file=import_file,
                        target_dir=target_dir,
                        format=None,
                    )

            call_args = importer.import_translations.call_args
            assert call_args[1]["format"] == "csv"

    def test_auto_detect_xlsx_format(self, tmp_path, mock_console):
        """Test auto-detection of Excel format."""
        for ext in [".xlsx", ".xls"]:
            import_file = tmp_path / f"translations{ext}"
            import_file.write_text("")
            target_dir = tmp_path / "docs"
            target_dir.mkdir(exist_ok=True)

            with patch("docdiff.cli.import_cmd.TranslationImporter") as mock_imp:
                importer = MagicMock()
                importer.import_translations.return_value = (
                    [],
                    {
                        "total": 0,
                        "applied": 0,
                        "created": 0,
                        "updated": 0,
                        "skipped": 0,
                    },
                )
                mock_imp.return_value = importer

                with patch("docdiff.cli.import_cmd.MySTParser"):
                    with patch("docdiff.cli.import_cmd.Progress"):
                        import_command(
                            import_file=import_file,
                            target_dir=target_dir,
                            format=None,
                        )

                call_args = importer.import_translations.call_args
                assert call_args[1]["format"] == "xlsx"

    def test_auto_detect_xliff_format(self, tmp_path, mock_console):
        """Test auto-detection of XLIFF format."""
        for ext in [".xliff", ".xlf"]:
            import_file = tmp_path / f"translations{ext}"
            import_file.write_text("")
            target_dir = tmp_path / "docs"
            target_dir.mkdir(exist_ok=True)

            with patch("docdiff.cli.import_cmd.TranslationImporter") as mock_imp:
                importer = MagicMock()
                importer.import_translations.return_value = (
                    [],
                    {
                        "total": 0,
                        "applied": 0,
                        "created": 0,
                        "updated": 0,
                        "skipped": 0,
                    },
                )
                mock_imp.return_value = importer

                with patch("docdiff.cli.import_cmd.MySTParser"):
                    with patch("docdiff.cli.import_cmd.Progress"):
                        import_command(
                            import_file=import_file,
                            target_dir=target_dir,
                            format=None,
                        )

                call_args = importer.import_translations.call_args
                assert call_args[1]["format"] == "xliff"

    def test_unknown_extension_error(self, tmp_path, mock_console):
        """Test error for unknown file extension."""
        import_file = tmp_path / "translations.unknown"
        import_file.write_text("")

        with pytest.raises(typer.Exit) as exc_info:
            import_command(
                import_file=import_file,
                target_dir=Path("."),
                format=None,
            )
        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called_with(
            "[red]Error: Cannot detect format from extension '.unknown'. Please specify --format[/red]"
        )

    def test_invalid_format_specified(self, temp_files, mock_console):
        """Test error for invalid format specification."""
        import_file, target_dir = temp_files

        with pytest.raises(typer.Exit) as exc_info:
            import_command(
                import_file=import_file,
                target_dir=target_dir,
                format="invalid",
            )
        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called_with(
            "[red]Error: Invalid format 'invalid'. Must be one of: json, csv, xlsx, xliff[/red]"
        )

    def test_target_dir_not_exists_without_create(self, tmp_path, mock_console):
        """Test error when target directory doesn't exist and create_missing is False."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "nonexistent"

        with pytest.raises(typer.Exit) as exc_info:
            import_command(
                import_file=import_file,
                target_dir=target_dir,
                create_missing=False,
            )
        assert exc_info.value.exit_code == 1
        assert mock_console.print.called
        # Check that error message contains target directory path
        call_args = mock_console.print.call_args_list[-1][0][0]
        assert "does not exist" in call_args

    def test_target_dir_created_when_missing(
        self, tmp_path, mock_console, mock_importer, mock_parser, mock_progress
    ):
        """Test target directory is created when create_missing is True."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "new_docs"

        assert not target_dir.exists()

        import_command(
            import_file=import_file,
            target_dir=target_dir,
            create_missing=True,
        )

        assert target_dir.exists()
        # Check warning message
        mock_console.print.assert_any_call(
            f"[yellow]Creating target directory: {target_dir}[/yellow]"
        )


class TestImportCommandExecution:
    """Test import command execution."""

    def test_load_existing_documents(
        self, tmp_path, mock_parser, mock_importer, mock_progress
    ):
        """Test loading existing target documents."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        # Create some markdown files
        (target_dir / "doc1.md").write_text("# Doc 1")
        (target_dir / "subdir").mkdir()
        (target_dir / "subdir" / "doc2.md").write_text("# Doc 2")

        # Mock parser to return nodes
        mock_nodes = [
            MagicMock(spec=DocumentNode, doc_language="en"),
            MagicMock(spec=DocumentNode, doc_language="en"),
        ]
        mock_parser.parse.return_value = mock_nodes

        import_command(
            import_file=import_file,
            target_dir=target_dir,
            target_lang="ja",
        )

        # Verify parser was called for each .md file
        assert mock_parser.parse.call_count == 2

        # Verify language was set on nodes
        for node in mock_nodes:
            assert node.doc_language == "ja"

    def test_verbose_output(
        self, temp_files, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test verbose output during import."""
        import_file, target_dir = temp_files
        (target_dir / "test.md").write_text("# Test")

        import_command(
            import_file=import_file,
            target_dir=target_dir,
            verbose=True,
        )

        # Check verbose output
        calls = [str(call[0][0]) for call in mock_console.print.call_args_list]
        assert any("Loading: test.md" in call for call in calls)

    def test_dry_run_mode(
        self, temp_files, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test dry run mode doesn't apply changes."""
        import_file, target_dir = temp_files

        mock_importer.import_translations.return_value = (
            [MagicMock(spec=DocumentNode)],
            {"total": 10, "applied": 5, "created": 2, "updated": 3, "skipped": 5},
        )

        import_command(
            import_file=import_file,
            target_dir=target_dir,
            dry_run=True,
        )

        # Check dry run messages
        mock_console.print.assert_any_call(
            "\n[yellow]DRY RUN MODE - No changes will be applied[/yellow]"
        )
        mock_console.print.assert_any_call(
            "\n[yellow]No changes applied (dry run mode)[/yellow]"
        )
        mock_console.print.assert_any_call("Run without --dry-run to apply changes")

    def test_import_with_errors(
        self, temp_files, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test handling of import errors."""
        import_file, target_dir = temp_files

        mock_importer.import_translations.return_value = (
            [],
            {
                "total": 10,
                "applied": 3,
                "created": 1,
                "updated": 2,
                "skipped": 5,
                "errors": ["Error 1", "Error 2"],
            },
        )

        import_command(
            import_file=import_file,
            target_dir=target_dir,
        )

        # Check error display
        mock_console.print.assert_any_call("\n[red]Errors encountered:[/red]")
        mock_console.print.assert_any_call("  • Error 1")
        mock_console.print.assert_any_call("  • Error 2")

    def test_write_updated_files(
        self, tmp_path, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test writing updated files after import."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        # Create mock nodes to be written
        mock_nodes = [
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc1.md"),
                line_number=1,
                content="# Updated Title",
            ),
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc1.md"),
                line_number=3,
                content="Updated content",
            ),
        ]

        mock_importer.import_translations.return_value = (
            mock_nodes,
            {"total": 2, "applied": 2, "created": 0, "updated": 2, "skipped": 0},
        )

        with patch("builtins.open", mock_open()) as mock_file:
            import_command(
                import_file=import_file,
                target_dir=target_dir,
                dry_run=False,
            )

            # Verify file was written
            mock_file.assert_called()
            handle = mock_file()
            handle.write.assert_called_once_with("# Updated Title\n\nUpdated content")

    def test_write_files_verbose(
        self, tmp_path, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test verbose output when writing files."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        mock_nodes = [
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc1.md"),
                line_number=1,
                content="Content",
            ),
        ]

        mock_importer.import_translations.return_value = (
            mock_nodes,
            {"total": 1, "applied": 1, "created": 0, "updated": 1, "skipped": 0},
        )

        with patch("builtins.open", mock_open()):
            import_command(
                import_file=import_file,
                target_dir=target_dir,
                verbose=True,
                dry_run=False,
            )

            # Check verbose output for modified files
            mock_console.print.assert_any_call("\n[dim]Modified files:[/dim]")
            # The exact path output varies, just check it was called
            assert any(
                "doc1.md" in str(call) for call in mock_console.print.call_args_list
            )

    def test_no_translations_applied(
        self, temp_files, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test message when no translations are applied."""
        import_file, target_dir = temp_files

        mock_importer.import_translations.return_value = (
            [],
            {"total": 10, "applied": 0, "created": 0, "updated": 0, "skipped": 10},
        )

        import_command(
            import_file=import_file,
            target_dir=target_dir,
            dry_run=False,
        )

        mock_console.print.assert_any_call(
            "\n[yellow]No translations were applied[/yellow]"
        )

    def test_next_steps_displayed(
        self, tmp_path, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test next steps are displayed after successful import."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        mock_nodes = [
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc1.md"),
                line_number=1,
                content="Content",
            ),
        ]

        mock_importer.import_translations.return_value = (
            mock_nodes,
            {"total": 1, "applied": 1, "created": 0, "updated": 1, "skipped": 0},
        )

        with patch("builtins.open", mock_open()):
            import_command(
                import_file=import_file,
                target_dir=target_dir,
                dry_run=False,
            )

            # Check next steps
            mock_console.print.assert_any_call("\n[cyan]Next steps:[/cyan]")
            mock_console.print.assert_any_call("  1. Review the updated files")
            mock_console.print.assert_any_call(
                "  2. Run 'docdiff compare' to verify coverage"
            )
            mock_console.print.assert_any_call(
                "  3. Build your documentation to test the translations"
            )


class TestImportOptions:
    """Test import command options."""

    def test_import_options_passed(
        self, temp_files, mock_parser, mock_importer, mock_progress
    ):
        """Test that import options are correctly passed to importer."""
        import_file, target_dir = temp_files

        import_command(
            import_file=import_file,
            target_dir=target_dir,
            create_missing=True,
            overwrite_existing=True,
        )

        call_args = mock_importer.import_translations.call_args
        options = call_args[1]["options"]
        assert options["create_missing"] is True
        assert options["overwrite_existing"] is True
        assert options["skip_empty"] is True

    def test_target_language_setting(
        self, temp_files, mock_parser, mock_importer, mock_progress
    ):
        """Test target language is set on nodes."""
        import_file, target_dir = temp_files
        (target_dir / "test.md").write_text("# Test")

        mock_nodes = [MagicMock(spec=DocumentNode) for _ in range(3)]
        mock_parser.parse.return_value = mock_nodes

        import_command(
            import_file=import_file,
            target_dir=target_dir,
            target_lang="fr",
        )

        # Verify language was set
        for node in mock_nodes:
            assert node.doc_language == "fr"

    def test_summary_table_display(
        self, temp_files, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test import summary table is displayed."""
        import_file, target_dir = temp_files

        stats = {
            "total": 100,
            "applied": 75,
            "created": 25,
            "updated": 50,
            "skipped": 25,
        }

        mock_importer.import_translations.return_value = ([], stats)

        with patch("docdiff.cli.import_cmd.Table") as mock_table_class:
            mock_table = MagicMock()
            mock_table_class.return_value = mock_table

            import_command(
                import_file=import_file,
                target_dir=target_dir,
            )

            # Verify table was created and populated
            mock_table.add_row.assert_any_call("Total Translations", "100")
            mock_table.add_row.assert_any_call("Applied", "75")
            mock_table.add_row.assert_any_call("Created", "25")
            mock_table.add_row.assert_any_call("Updated", "50")
            mock_table.add_row.assert_any_call("Skipped", "25")

            # Verify table was printed
            mock_console.print.assert_any_call(mock_table)


class TestFileWriting:
    """Test file writing functionality."""

    def test_create_parent_directories(
        self, tmp_path, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test that parent directories are created when writing files."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        # Node with nested path
        mock_nodes = [
            MagicMock(
                spec=DocumentNode,
                file_path=Path("subdir/nested/doc.md"),
                line_number=1,
                content="Content",
            ),
        ]

        mock_importer.import_translations.return_value = (
            mock_nodes,
            {"total": 1, "applied": 1, "created": 1, "updated": 0, "skipped": 0},
        )

        # Mock file operations to verify parent directory creation
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch("builtins.open", mock_open()):
                import_command(
                    import_file=import_file,
                    target_dir=target_dir,
                    dry_run=False,
                )

                # Verify mkdir was called with parents=True
                mock_mkdir.assert_called_with(parents=True, exist_ok=True)

    def test_sort_nodes_by_line_number(
        self, tmp_path, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test that nodes are sorted by line number before writing."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        # Create nodes in wrong order
        mock_nodes = [
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc.md"),
                line_number=5,
                content="Line 5",
            ),
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc.md"),
                line_number=1,
                content="Line 1",
            ),
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc.md"),
                line_number=3,
                content="Line 3",
            ),
        ]

        mock_importer.import_translations.return_value = (
            mock_nodes,
            {"total": 3, "applied": 3, "created": 0, "updated": 3, "skipped": 0},
        )

        with patch("builtins.open", mock_open()) as mock_file:
            import_command(
                import_file=import_file,
                target_dir=target_dir,
                dry_run=False,
            )

            # Verify content was written in sorted order
            handle = mock_file()
            handle.write.assert_called_once_with("Line 1\n\nLine 3\n\nLine 5")

    def test_multiple_files_written(
        self, tmp_path, mock_console, mock_parser, mock_importer, mock_progress
    ):
        """Test writing multiple files from imported nodes."""
        import_file = tmp_path / "translations.json"
        import_file.write_text("{}")
        target_dir = tmp_path / "docs"
        target_dir.mkdir()

        # Nodes for different files
        mock_nodes = [
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc1.md"),
                line_number=1,
                content="Doc 1 content",
            ),
            MagicMock(
                spec=DocumentNode,
                file_path=Path("doc2.md"),
                line_number=1,
                content="Doc 2 content",
            ),
        ]

        mock_importer.import_translations.return_value = (
            mock_nodes,
            {"total": 2, "applied": 2, "created": 0, "updated": 2, "skipped": 0},
        )

        file_contents = {}

        def mock_open_side_effect(path, mode, encoding=None):
            mock_file = MagicMock()
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)

            def write_content(content):
                file_contents[str(path)] = content

            mock_file.write = write_content
            return mock_file

        with patch("builtins.open", side_effect=mock_open_side_effect):
            import_command(
                import_file=import_file,
                target_dir=target_dir,
                dry_run=False,
            )

            # Verify both files were written
            assert len(file_contents) == 2
            assert file_contents.get(str(target_dir / "doc1.md")) == "Doc 1 content"
            assert file_contents.get(str(target_dir / "doc2.md")) == "Doc 2 content"

            # Verify success message
            mock_console.print.assert_any_call(
                "\n[green]✓[/green] Successfully wrote 2 files"
            )
