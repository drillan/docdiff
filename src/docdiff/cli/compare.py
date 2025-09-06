"""Compare command for advanced document comparison."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from docdiff.cache import CacheManager
from docdiff.parsers import MySTParser
from docdiff.compare import ComparisonEngine, MetadataView
from docdiff.compare.reporters import MarkdownReporter


console = Console()


def compare_command(
    source_dir: Path,
    target_dir: Path,
    source_lang: str = "en",
    target_lang: str = "ja",
    output_report: Optional[Path] = None,
    html_report: bool = False,
    view: str = "summary",
    verbose: bool = False,
) -> None:
    """Compare documents between source and target directories.
    
    Args:
        source_dir: Source documentation directory
        target_dir: Target documentation directory
        source_lang: Source language code
        target_lang: Target language code
        output_report: Optional path for JSON report output
        html_report: Generate HTML report
        verbose: Show detailed output
    """
    # Validate directories
    if not source_dir.exists():
        console.print(f"[red]Error: Source directory {source_dir} does not exist[/red]")
        raise typer.Exit(1)
    
    if not target_dir.exists():
        console.print(f"[red]Error: Target directory {target_dir} does not exist[/red]")
        raise typer.Exit(1)
    
    # Initialize cache manager
    cache_manager = CacheManager()
    cache_manager.initialize()
    
    # Parse documents with progress
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
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            nodes = parser.parse(content, md_file)
            # Set language for all nodes
            for node in nodes:
                node.doc_language = source_lang
            source_nodes.extend(nodes)
        
        progress.update(task, completed=True)
        console.print(f"[green]✓[/green] Parsed {len(source_nodes)} nodes from {source_lang} documents")
        
        # Parse target documents
        task = progress.add_task(f"Parsing {target_lang} documents...", total=None)
        target_nodes = []
        
        for md_file in target_dir.rglob("*.md"):
            if verbose:
                console.print(f"  Parsing: {md_file.relative_to(target_dir)}")
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            nodes = parser.parse(content, md_file)
            # Set language for all nodes
            for node in nodes:
                node.doc_language = target_lang
            target_nodes.extend(nodes)
        
        progress.update(task, completed=True)
        console.print(f"[green]✓[/green] Parsed {len(target_nodes)} nodes from {target_lang} documents")
        
        # Perform comparison
        task = progress.add_task("Comparing documents...", total=None)
        engine = ComparisonEngine()
        result = engine.compare(source_nodes, target_nodes, source_lang, target_lang)
        progress.update(task, completed=True)
    
    # Display based on view option
    metadata_view = MetadataView(console)
    
    if view == "tree":
        metadata_view.display_tree_view(result)
    elif view == "metadata":
        metadata_view.display_metadata_groups(result)
    elif view == "side-by-side":
        metadata_view.display_side_by_side(result)
    elif view == "stats":
        metadata_view.display_metadata_stats(result)
    else:  # Default summary view
        console.print("\n[bold]Translation Coverage Summary[/bold]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="dim", width=20)
        table.add_column("Value", justify="right")
        
        coverage = result.coverage_stats
        table.add_row("Overall Coverage", f"{coverage['overall']:.1%}")
        table.add_row("Total Nodes", str(coverage['counts']['total']))
        table.add_row("Translated", str(coverage['counts']['translated']))
        table.add_row("Missing", str(coverage['counts']['missing']))
        table.add_row("Fuzzy Matches", str(coverage['counts'].get('fuzzy', 0)))
        
        console.print(table)
    
    # Show structure differences
    if result.structure_diff:
        console.print("\n[bold]Structure Differences by Type[/bold]")
        
        struct_table = Table(show_header=True, header_style="bold cyan")
        struct_table.add_column("Node Type", style="dim")
        struct_table.add_column("Source", justify="right")
        struct_table.add_column("Target", justify="right")
        struct_table.add_column("Difference", justify="right")
        
        for node_type, stats in result.structure_diff.items():
            diff = stats.get('diff', stats['source'] - stats['target'])
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            struct_table.add_row(
                node_type,
                str(stats['source']),
                str(stats['target']),
                diff_str
            )
        
        console.print(struct_table)
    
    # Show missing translations (top 10)
    missing_nodes = [m for m in result.mappings if m.mapping_type == 'missing']
    if missing_nodes and verbose:
        console.print("\n[bold]Missing Translations (Top 10)[/bold]")
        
        missing_table = Table(show_header=True, header_style="bold yellow")
        missing_table.add_column("File", style="dim")
        missing_table.add_column("Line", justify="right")
        missing_table.add_column("Type")
        missing_table.add_column("Content (Preview)", width=40)
        
        for mapping in missing_nodes[:10]:
            node = mapping.source_node
            content_preview = node.content[:50] + "..." if len(node.content) > 50 else node.content
            missing_table.add_row(
                str(node.file_path.relative_to(source_dir)),
                str(node.line_number),
                node.type.value,
                content_preview
            )
        
        console.print(missing_table)
        
        if len(missing_nodes) > 10:
            console.print(f"\n... and {len(missing_nodes) - 10} more missing translations")
    
    # Save report based on file extension
    if output_report:
        output_report.parent.mkdir(parents=True, exist_ok=True)
        
        if output_report.suffix.lower() == '.md':
            # Generate Markdown report
            # Determine style from filename (e.g., report.github.md)
            style = 'detailed'
            if 'github' in output_report.stem.lower():
                style = 'github'
            elif 'compact' in output_report.stem.lower():
                style = 'compact'
            
            reporter = MarkdownReporter(style=style)
            markdown_content = reporter.generate(result, include_badges=True)
            output_report.write_text(markdown_content, encoding='utf-8')
            console.print(f"\n[green]✓[/green] Markdown report ({style}) saved to: {output_report}")
        else:
            # Default to JSON
            with open(output_report, 'w', encoding='utf-8') as f:
                import json
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            console.print(f"\n[green]✓[/green] JSON report saved to: {output_report}")
    
    # Generate HTML report
    if html_report:
        reports_dir = cache_manager.get_reports_dir()
        html_path = reports_dir / f"comparison_{source_lang}_{target_lang}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(result.generate_html_report())
        
        console.print(f"[green]✓[/green] HTML report saved to: {html_path}")
    
    # Exit with appropriate code
    if result.coverage_stats['overall'] < 0.5:
        console.print("\n[red]⚠ Warning: Translation coverage is below 50%[/red]")
        raise typer.Exit(1)