"""Simple comparison command for Phase 1.5."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

from docdiff.models import DocumentNode, NodeType
from docdiff.parsers import MySTParser, ReSTParser
from docdiff.parsers.base import BaseParser
from docdiff.cache import CacheManager

console = Console()


def simple_compare_command(
    source: Path,
    target: Path,
    output_file: Optional[Path] = None,
) -> None:
    """Simple structural comparison between two document directories.

    Args:
        source: Source directory path
        target: Target directory path
        output_file: Optional JSON output file
    """
    console.print("[bold]Simple Structure Comparison[/bold]")
    console.print(f"  Source: {source}")
    console.print(f"  Target: {target}")

    # Initialize cache manager for output
    cache_manager = CacheManager()
    cache_manager.initialize()

    # Phase 1.5: Structure comparison only
    # Parse both directories
    with console.status("Parsing source documents..."):
        source_nodes = _parse_directory(source)

    with console.status("Parsing target documents..."):
        target_nodes = _parse_directory(target)

    # Simple structural comparison
    results = _compare_structure(source_nodes, target_nodes)

    # Display results
    _display_simple_results(results)

    # Save if requested
    if output_file:
        # If no path specified, use cache manager's reports directory
        if output_file.name == output_file:
            output_file = cache_manager.get_report_path(
                str(output_file), timestamp=False
            )

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"[green]✓[/green] Results saved to {output_file}")


def _parse_directory(path: Path) -> List[DocumentNode]:
    """Parse all documents in a directory."""
    nodes: List[DocumentNode] = []

    if not path.exists():
        console.print(f"[yellow]Warning:[/yellow] Directory {path} does not exist")
        return nodes

    # Create parsers
    myst_parser = MySTParser()
    rest_parser = ReSTParser()

    # Find all markdown and rst files
    md_files = list(path.rglob("*.md"))
    rst_files = list(path.rglob("*.rst"))

    all_files = md_files + rst_files
    console.print(f"Found {len(all_files)} documents to parse")

    for file_path in all_files:
        try:
            # Choose parser based on file extension
            parser: Optional[BaseParser] = None
            if file_path.suffix == ".md" and myst_parser.can_parse(file_path):
                parser = myst_parser
            elif file_path.suffix == ".rst" and rest_parser.can_parse(file_path):
                parser = rest_parser

            if parser is None:
                continue

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            file_nodes = parser.parse(content, file_path)
            nodes.extend(file_nodes)

        except Exception as e:
            console.print(f"[red]Error parsing {file_path}: {e}[/red]")

    return nodes


def _compare_structure(
    source_nodes: List[DocumentNode], target_nodes: List[DocumentNode]
) -> Dict[str, Any]:
    """Simple structural comparison."""
    # Count node types
    source_counts: Dict[str, int] = {}
    target_counts: Dict[str, int] = {}

    for node in source_nodes:
        node_type = (
            node.type.value if isinstance(node.type, NodeType) else str(node.type)
        )
        source_counts[node_type] = source_counts.get(node_type, 0) + 1

    for node in target_nodes:
        node_type = (
            node.type.value if isinstance(node.type, NodeType) else str(node.type)
        )
        target_counts[node_type] = target_counts.get(node_type, 0) + 1

    # Calculate differences
    all_types = set(source_counts.keys()) | set(target_counts.keys())
    differences = {}

    for node_type in all_types:
        s_count = source_counts.get(node_type, 0)
        t_count = target_counts.get(node_type, 0)
        differences[node_type] = {
            "source": s_count,
            "target": t_count,
            "diff": t_count - s_count,
        }

    # Find added, removed, and changed types
    added_types = [t for t in differences if differences[t]["source"] == 0]
    removed_types = [t for t in differences if differences[t]["target"] == 0]
    changed_types = [
        t
        for t in differences
        if differences[t]["diff"] != 0
        and t not in added_types
        and t not in removed_types
    ]

    return {
        "source_total": len(source_nodes),
        "target_total": len(target_nodes),
        "by_type": differences,
        "summary": {
            "added_types": added_types,
            "removed_types": removed_types,
            "changed_types": changed_types,
        },
    }


def _display_simple_results(results: Dict[str, Any]) -> None:
    """Display simple comparison results."""
    table = Table(title="Structure Comparison")
    table.add_column("Node Type", style="cyan")
    table.add_column("Source", justify="right")
    table.add_column("Target", justify="right")
    table.add_column("Difference", justify="right")

    for node_type, data in sorted(results["by_type"].items()):
        diff = data["diff"]
        if diff > 0:
            diff_str = f"+{diff}"
            style = "green"
        elif diff < 0:
            diff_str = str(diff)
            style = "red"
        else:
            diff_str = "="
            style = "white"

        table.add_row(
            node_type,
            str(data["source"]),
            str(data["target"]),
            f"[{style}]{diff_str}[/{style}]",
        )

    console.print(table)
    console.print(
        f"\n[bold]Total:[/bold] Source: {results['source_total']}, "
        f"Target: {results['target_total']}"
    )

    # Show summary
    summary = results["summary"]
    if summary["added_types"]:
        console.print(
            f"[green]Added types:[/green] {', '.join(summary['added_types'])}"
        )
    if summary["removed_types"]:
        console.print(
            f"[red]Removed types:[/red] {', '.join(summary['removed_types'])}"
        )
    if summary["changed_types"]:
        console.print(
            f"[yellow]Changed types:[/yellow] {', '.join(summary['changed_types'])}"
        )
