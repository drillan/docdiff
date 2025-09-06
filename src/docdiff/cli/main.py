"""Main CLI entry point for docdiff."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from docdiff import __version__
from docdiff.cli.parse import parse_command
from docdiff.cli.simple_compare import simple_compare_command
from docdiff.cli.status import status_command
from docdiff.cli.compare import compare_command
from docdiff.cli.export import export_command
from docdiff.cli.import_cmd import import_command

app = typer.Typer(
    name="docdiff",
    help="Document structure analysis and translation management tool.",
    add_completion=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
    ),
) -> None:
    """docdiff - Document structure analysis and translation management tool."""
    if version:
        console.print(f"docdiff version {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


@app.command()
def parse(
    project_dir: Path = typer.Argument(
        ...,
        help="Path to the Sphinx project directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    db_path: Path = typer.Option(
        None,
        "--db",
        "-d",
        help="Path to the database file (default: project_dir/.docdiff.db)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Parse a Sphinx project and extract document structure."""
    parse_command(project_dir, db_path, verbose)


@app.command()
def status(
    project_dir: Path = typer.Argument(
        ...,
        help="Path to the Sphinx project directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    db_path: Path = typer.Option(
        None,
        "--db",
        "-d",
        help="Path to the database file (default: project_dir/.docdiff.db)",
    ),
    target_lang: str = typer.Option(
        None,
        "--lang",
        "-l",
        help="Target language to check status for",
    ),
) -> None:
    """Show translation status for a project."""
    status_command(project_dir, db_path, target_lang)


@app.command()
def simple_compare(
    source: Path = typer.Argument(
        ...,
        help="Source directory path",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    target: Path = typer.Argument(
        ...,
        help="Target directory path",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_file: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional JSON output file",
    ),
) -> None:
    """Compare document structure between two directories."""
    simple_compare_command(source, target, output_file)


@app.command()
def compare(
    source_dir: Path = typer.Argument(
        ...,
        help="Source documentation directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    target_dir: Path = typer.Argument(
        ...,
        help="Target documentation directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    source_lang: str = typer.Option(
        "en",
        "--source-lang",
        "-s",
        help="Source language code",
    ),
    target_lang: str = typer.Option(
        "ja",
        "--target-lang",
        "-t",
        help="Target language code",
    ),
    output_report: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="JSON report output path",
    ),
    html_report: bool = typer.Option(
        False,
        "--html",
        help="Generate HTML report",
    ),
    view: str = typer.Option(
        "summary",
        "--view",
        help="Display view: summary/tree/metadata/side-by-side/stats",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Advanced document comparison with translation coverage analysis."""
    compare_command(
        source_dir, target_dir, source_lang, target_lang,
        output_report, html_report, view, verbose
    )


@app.command()
def export(
    source_dir: Path = typer.Argument(
        ...,
        help="Source documentation directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    target_dir: Path = typer.Argument(
        ...,
        help="Target documentation directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_file: Path = typer.Argument(
        ...,
        help="Output file path",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Export format (json, csv, xlsx, xliff)",
    ),
    source_lang: str = typer.Option(
        "en",
        "--source-lang",
        "-s",
        help="Source language code",
    ),
    target_lang: str = typer.Option(
        "ja",
        "--target-lang",
        "-t",
        help="Target language code",
    ),
    include_missing: bool = typer.Option(
        True,
        "--include-missing/--no-include-missing",
        help="Include missing translations",
    ),
    include_outdated: bool = typer.Option(
        False,
        "--include-outdated/--no-include-outdated",
        help="Include outdated translations",
    ),
    include_context: bool = typer.Option(
        False,
        "--include-context/--no-include-context",
        help="Include context information",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Export translation tasks to various formats."""
    export_command(
        source_dir, target_dir, output_file, format,
        source_lang, target_lang, include_missing,
        include_outdated, include_context, verbose
    )


@app.command(name="import")
def import_cmd(
    import_file: Path = typer.Argument(
        ...,
        help="Import file path (JSON, XLSX, or XLIFF)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    target_dir: Path = typer.Argument(
        ...,
        help="Target documentation directory",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Import format (auto-detected if not specified)",
    ),
    target_lang: str = typer.Option(
        "ja",
        "--target-lang",
        "-t",
        help="Target language code",
    ),
    create_missing: bool = typer.Option(
        True,
        "--create-missing/--no-create-missing",
        help="Create new files for missing translations",
    ),
    overwrite_existing: bool = typer.Option(
        False,
        "--overwrite/--no-overwrite",
        help="Overwrite existing translations",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without applying them",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """Import translations from exported files."""
    import_command(
        import_file, target_dir, format, target_lang,
        create_missing, overwrite_existing, dry_run, verbose
    )


def run() -> None:
    """Run the CLI application."""
    app()
