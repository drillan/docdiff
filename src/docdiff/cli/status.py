"""Status command implementation."""

from pathlib import Path
from typing import Dict, Optional

import typer
from rich.console import Console
from rich.table import Table

from docdiff.database import (
    DatabaseConnection,
    NodeRepository,
    TranslationRepository,
)
from docdiff.models import NodeType, TranslationStatus

console = Console()


def status_command(
    project_dir: Path,
    db_path: Optional[Path] = None,
    target_lang: Optional[str] = None,
) -> None:
    """Show translation status for a project.

    Args:
        project_dir: Path to the Sphinx project
        db_path: Path to the database file
        target_lang: Target language to check status for
    """
    # Set default database path
    if db_path is None:
        db_path = project_dir / ".docdiff.db"

    if not db_path.exists():
        console.print(
            f"[red]Database not found at {db_path}[/red]\n"
            f"Please run 'docdiff parse' first."
        )
        raise typer.Exit(1)

    console.print(f"[bold]Project:[/bold] {project_dir}")
    console.print(f"[bold]Database:[/bold] {db_path}")
    if target_lang:
        console.print(f"[bold]Target Language:[/bold] {target_lang}")

    # Connect to database
    conn = DatabaseConnection(db_path)
    conn.connect()

    node_repo = NodeRepository(conn)
    trans_repo = TranslationRepository(conn)

    # Get all files
    all_files = set()
    for file_path in project_dir.rglob("*.md"):
        all_files.add(file_path)
    for file_path in project_dir.rglob("*.rst"):
        all_files.add(file_path)

    # Create summary table
    table = Table(title="Translation Status Summary")
    table.add_column("File", style="cyan")
    table.add_column("Nodes", justify="right")

    if target_lang:
        table.add_column("Pending", justify="right", style="yellow")
        table.add_column("Translated", justify="right", style="green")
        table.add_column("Reviewed", justify="right", style="blue")
        table.add_column("Outdated", justify="right", style="red")

    total_nodes = 0
    total_pending = 0
    total_translated = 0
    total_reviewed = 0
    total_outdated = 0

    for file_path in sorted(all_files):
        nodes = node_repo.find_by_file(file_path)
        node_count = len(nodes)
        total_nodes += node_count

        if node_count == 0:
            continue

        row = [str(file_path.relative_to(project_dir)), str(node_count)]

        if target_lang:
            pending = 0
            translated = 0
            reviewed = 0
            outdated = 0

            for node in nodes:
                units = trans_repo.find_by_source_node(node.id)
                target_units = [u for u in units if u.target_lang == target_lang]

                if not target_units:
                    pending += 1
                else:
                    unit = target_units[0]
                    if unit.status == TranslationStatus.PENDING:
                        pending += 1
                    elif unit.status == TranslationStatus.TRANSLATED:
                        translated += 1
                    elif unit.status == TranslationStatus.REVIEWED:
                        reviewed += 1
                    elif unit.status == TranslationStatus.OUTDATED:
                        outdated += 1

            total_pending += pending
            total_translated += translated
            total_reviewed += reviewed
            total_outdated += outdated

            row.extend(
                [
                    str(pending) if pending > 0 else "-",
                    str(translated) if translated > 0 else "-",
                    str(reviewed) if reviewed > 0 else "-",
                    str(outdated) if outdated > 0 else "-",
                ]
            )

        table.add_row(*row)

    # Add totals row
    if target_lang:
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_nodes}[/bold]",
            f"[bold]{total_pending}[/bold]",
            f"[bold]{total_translated}[/bold]",
            f"[bold]{total_reviewed}[/bold]",
            f"[bold]{total_outdated}[/bold]",
        )
    else:
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_nodes}[/bold]",
        )

    console.print("\n")
    console.print(table)

    # Show node type breakdown
    type_counts: Dict[NodeType, int] = {}
    for file_path in all_files:
        nodes = node_repo.find_by_file(file_path)
        for node in nodes:
            type_counts[node.type] = type_counts.get(node.type, 0) + 1

    if type_counts:
        type_table = Table(title="\nNode Type Breakdown")
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", justify="right")

        for node_type in NodeType:
            count = type_counts.get(node_type, 0)
            if count > 0:
                type_table.add_row(node_type.value, str(count))

        console.print(type_table)

    conn.close()
