"""Export command for translation tasks."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from docdiff.parsers import MySTParser
from docdiff.compare import ComparisonEngine
from docdiff.workflow import TranslationExporter


console = Console()


def export_command(
    source_dir: Path,
    target_dir: Path,
    output_file: Path,
    format: str = "json",
    source_lang: str = "en",
    target_lang: str = "ja",
    include_missing: bool = True,
    include_outdated: bool = False,
    include_context: bool = False,
    batch_size: int = 2000,
    context_window: int = 3,
    glossary_file: Optional[Path] = None,
    verbose: bool = False,
) -> None:
    """Export translation tasks to various formats.

    Args:
        source_dir: Source documentation directory
        target_dir: Target documentation directory
        output_file: Output file path
        format: Export format (json, xlsx, xliff)
        source_lang: Source language code
        target_lang: Target language code
        include_missing: Include missing translations
        include_outdated: Include outdated translations
        include_context: Include context information
        batch_size: Target batch size for AI translation (tokens)
        context_window: Number of surrounding nodes for context
        glossary_file: Path to glossary file for terminology consistency
        verbose: Show detailed output
    """
    # Validate format
    valid_formats = ["json", "csv", "xlsx", "xliff"]
    if format not in valid_formats:
        console.print(
            f"[red]Error: Invalid format '{format}'. Must be one of: {', '.join(valid_formats)}[/red]"
        )
        raise typer.Exit(1)

    # Validate directories
    if not source_dir.exists():
        console.print(f"[red]Error: Source directory {source_dir} does not exist[/red]")
        raise typer.Exit(1)

    if not target_dir.exists():
        console.print(f"[red]Error: Target directory {target_dir} does not exist[/red]")
        raise typer.Exit(1)

    # Set appropriate file extension if not provided
    if output_file.suffix == "":
        if format == "json":
            output_file = output_file.with_suffix(".json")
        elif format == "csv":
            output_file = output_file.with_suffix(".csv")
        elif format == "xlsx":
            output_file = output_file.with_suffix(".xlsx")
        elif format == "xliff":
            output_file = output_file.with_suffix(".xliff")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Parse source documents
        task = progress.add_task(f"Parsing {source_lang} documents...", total=None)
        parser = MySTParser()
        source_nodes = []

        for md_file in source_dir.rglob("*.md"):
            if verbose:
                console.print(f"  Parsing: {md_file.relative_to(source_dir)}")
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            nodes = parser.parse(content, md_file)
            # Set language for all nodes
            for node in nodes:
                node.doc_language = source_lang
            source_nodes.extend(nodes)

        progress.update(task, completed=True)
        console.print(
            f"[green]✓[/green] Parsed {len(source_nodes)} nodes from {source_lang} documents"
        )

        # Parse target documents
        task = progress.add_task(f"Parsing {target_lang} documents...", total=None)
        target_nodes = []

        for md_file in target_dir.rglob("*.md"):
            if verbose:
                console.print(f"  Parsing: {md_file.relative_to(target_dir)}")
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            nodes = parser.parse(content, md_file)
            # Set language for all nodes
            for node in nodes:
                node.doc_language = target_lang
            target_nodes.extend(nodes)

        progress.update(task, completed=True)
        console.print(
            f"[green]✓[/green] Parsed {len(target_nodes)} nodes from {target_lang} documents"
        )

        # Perform comparison
        task = progress.add_task("Comparing documents...", total=None)
        engine = ComparisonEngine()
        result = engine.compare(source_nodes, target_nodes, source_lang, target_lang)
        progress.update(task, completed=True)

        # Export translations
        task = progress.add_task(f"Exporting to {format.upper()}...", total=None)
        exporter = TranslationExporter()

        export_options = {
            "include_missing": include_missing,
            "include_outdated": include_outdated,
            "include_context": include_context,
            "batch_size": batch_size,
            "context_window": context_window,
            "glossary_file": glossary_file,
            "verbose": verbose,
        }

        output_path = exporter.export(
            result=result,
            format=format,
            output_path=output_file,
            options=export_options,
        )

        progress.update(task, completed=True)

    # Display export summary
    console.print("\n[green]✓[/green] Export completed successfully!")
    console.print(f"  Output file: {output_path}")

    # Count exported items
    missing_count = sum(1 for m in result.mappings if m.mapping_type == "missing")
    outdated_count = sum(
        1 for m in result.mappings if m.mapping_type == "fuzzy" and m.similarity < 0.95
    )

    exported_count = 0
    if include_missing:
        exported_count += missing_count
    if include_outdated:
        exported_count += outdated_count

    console.print(f"  Exported items: {exported_count}")

    if format == "xlsx":
        console.print(
            "\n[cyan]Tip:[/cyan] Open the Excel file and fill in the 'Target' column with translations"
        )
    elif format == "xliff":
        console.print(
            "\n[cyan]Tip:[/cyan] Import this XLIFF file into your CAT tool for translation"
        )
    elif format == "json":
        console.print(
            "\n[cyan]Tip:[/cyan] Use 'docdiff import' to apply translations from this file"
        )

    if verbose:
        console.print("\n[dim]Export options:[/dim]")
        console.print(f"  Include missing: {include_missing} ({missing_count} items)")
        console.print(
            f"  Include outdated: {include_outdated} ({outdated_count} items)"
        )
        console.print(f"  Include context: {include_context}")
        console.print(f"  Batch size: {batch_size} tokens")
        console.print(f"  Context window: {context_window} nodes")
        if glossary_file:
            console.print(f"  Glossary file: {glossary_file}")
