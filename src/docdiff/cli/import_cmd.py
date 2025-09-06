"""Import command for applying translations."""

from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from docdiff.workflow import TranslationImporter
from docdiff.parsers import MySTParser
from docdiff.models import DocumentNode


console = Console()


def import_command(
    import_file: Path,
    target_dir: Path,
    format: Optional[str] = None,
    target_lang: str = "ja",
    create_missing: bool = True,
    overwrite_existing: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """Import translations from exported files.

    Args:
        import_file: Path to import file (JSON, XLSX, or XLIFF)
        target_dir: Target documentation directory to update
        format: Import format (auto-detected if not specified)
        target_lang: Target language code
        create_missing: Create new files for missing translations
        overwrite_existing: Overwrite existing translations
        dry_run: Preview changes without applying them
        verbose: Show detailed output
    """
    # Validate import file
    if not import_file.exists():
        console.print(f"[red]Error: Import file {import_file} does not exist[/red]")
        raise typer.Exit(1)

    # Auto-detect format from file extension
    if format is None:
        suffix = import_file.suffix.lower()
        if suffix == ".json":
            format = "json"
        elif suffix == ".csv":
            format = "csv"
        elif suffix in [".xlsx", ".xls"]:
            format = "xlsx"
        elif suffix in [".xliff", ".xlf"]:
            format = "xliff"
        else:
            console.print(
                f"[red]Error: Cannot detect format from extension '{suffix}'. Please specify --format[/red]"
            )
            raise typer.Exit(1)

    # Validate format
    valid_formats = ["json", "csv", "xlsx", "xliff"]
    if format not in valid_formats:
        console.print(
            f"[red]Error: Invalid format '{format}'. Must be one of: {', '.join(valid_formats)}[/red]"
        )
        raise typer.Exit(1)

    # Ensure target directory exists
    if not target_dir.exists():
        if create_missing:
            console.print(f"[yellow]Creating target directory: {target_dir}[/yellow]")
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            console.print(
                f"[red]Error: Target directory {target_dir} does not exist[/red]"
            )
            raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Parse existing target documents
        task = progress.add_task(
            f"Loading existing {target_lang} documents...", total=None
        )
        parser = MySTParser()
        target_nodes = []

        for md_file in target_dir.rglob("*.md"):
            if verbose:
                console.print(f"  Loading: {md_file.relative_to(target_dir)}")
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            nodes = parser.parse(content, md_file)
            # Set language for all nodes
            for node in nodes:
                node.doc_language = target_lang
            target_nodes.extend(nodes)

        progress.update(task, completed=True)
        console.print(f"[green]✓[/green] Loaded {len(target_nodes)} existing nodes")

        # Import translations
        task = progress.add_task(
            f"Importing translations from {format.upper()}...", total=None
        )
        importer = TranslationImporter()

        import_options = {
            "create_missing": create_missing,
            "overwrite_existing": overwrite_existing,
            "skip_empty": True,
        }

        if dry_run:
            console.print(
                "\n[yellow]DRY RUN MODE - No changes will be applied[/yellow]"
            )

        updated_nodes, stats = importer.import_translations(
            import_path=import_file,
            format=format,
            target_nodes=target_nodes,
            options=import_options,
        )

        progress.update(task, completed=True)

    # Display import summary
    console.print("\n[bold]Import Summary[/bold]")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="dim", width=20)
    table.add_column("Count", justify="right")

    table.add_row("Total Translations", str(stats["total"]))
    table.add_row("Applied", str(stats["applied"]))
    table.add_row("Created", str(stats["created"]))
    table.add_row("Updated", str(stats["updated"]))
    table.add_row("Skipped", str(stats["skipped"]))

    console.print(table)

    # Show errors if any
    if stats.get("errors"):
        console.print("\n[red]Errors encountered:[/red]")
        for error in stats["errors"]:
            console.print(f"  • {error}")

    # Apply changes (write files) if not dry run
    if not dry_run and stats["applied"] > 0:
        task = progress.add_task("Writing updated files...", total=None)

        # Group nodes by file
        files_to_write: Dict[Path, List[DocumentNode]] = {}
        for node in updated_nodes:
            file_path = target_dir / node.file_path.name
            if file_path not in files_to_write:
                files_to_write[file_path] = []
            files_to_write[file_path].append(node)

        # Write each file
        written_files = []
        for file_path, nodes in files_to_write.items():
            if verbose:
                console.print(f"  Writing: {file_path.relative_to(target_dir)}")

            # Sort nodes by line number
            nodes.sort(key=lambda n: n.line_number)

            # Reconstruct document content
            content_lines = []
            for node in nodes:
                content_lines.append(node.content)

            # Write file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(content_lines))

            written_files.append(file_path)

        console.print(
            f"\n[green]✓[/green] Successfully wrote {len(written_files)} files"
        )

        if verbose:
            console.print("\n[dim]Modified files:[/dim]")
            for file_path in written_files:
                console.print(f"  • {file_path.relative_to(target_dir)}")

    elif dry_run:
        console.print("\n[yellow]No changes applied (dry run mode)[/yellow]")
        console.print("Run without --dry-run to apply changes")
    else:
        console.print("\n[yellow]No translations were applied[/yellow]")

    # Provide next steps
    if stats["applied"] > 0 and not dry_run:
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  1. Review the updated files")
        console.print("  2. Run 'docdiff compare' to verify coverage")
        console.print("  3. Build your documentation to test the translations")
