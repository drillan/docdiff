"""Parse command implementation."""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from docdiff.database import DatabaseConnection, NodeRepository, create_tables
from docdiff.parsers import MySTParser, ReSTParser
from docdiff.cache import CacheManager

console = Console()


def parse_command(
    project_dir: Path,
    db_path: Optional[Path] = None,
    verbose: bool = False,
) -> None:
    """Parse a Sphinx project and extract document structure.

    Args:
        project_dir: Path to the Sphinx project
        db_path: Path to the database file
        verbose: Show detailed output
    """
    # Initialize cache manager
    cache_manager = CacheManager()
    cache_manager.initialize()

    # Set default database path using cache manager
    if db_path is None:
        db_path = cache_manager.get_default_db_path(project_dir)

    console.print(f"[bold]Parsing project:[/bold] {project_dir}")
    console.print(f"[bold]Database:[/bold] {db_path}")

    # Create database connection
    conn = DatabaseConnection(db_path)
    conn.connect()
    create_tables(conn)

    # Create parsers
    myst_parser = MySTParser()
    rest_parser = ReSTParser()

    # Find all document files
    md_files = list(project_dir.rglob("*.md"))
    rst_files = list(project_dir.rglob("*.rst"))
    total_files = len(md_files) + len(rst_files)

    console.print(f"\nFound {len(md_files)} .md files and {len(rst_files)} .rst files")

    # Parse files
    node_repo = NodeRepository(conn)
    total_nodes = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Parsing files...", total=total_files)

        # Parse Markdown files
        for md_file in md_files:
            if verbose:
                console.print(f"  Parsing: {md_file.relative_to(project_dir)}")

            try:
                content = md_file.read_text(encoding="utf-8")
                nodes = myst_parser.parse(content, md_file)

                for node in nodes:
                    node_repo.save(node)
                    total_nodes += 1

                progress.advance(task)
            except Exception as e:
                console.print(f"[red]Error parsing {md_file}: {e}[/red]")
                progress.advance(task)

        # Parse RST files
        for rst_file in rst_files:
            if verbose:
                console.print(f"  Parsing: {rst_file.relative_to(project_dir)}")

            try:
                content = rst_file.read_text(encoding="utf-8")
                nodes = rest_parser.parse(content, rst_file)

                for node in nodes:
                    node_repo.save(node)
                    total_nodes += 1

                progress.advance(task)
            except Exception as e:
                console.print(f"[red]Error parsing {rst_file}: {e}[/red]")
                progress.advance(task)

    # Show summary
    console.print("\n[green]✓[/green] Parsing completed!")
    console.print(f"  Files processed: {total_files}")
    console.print(f"  Nodes extracted: {total_nodes}")
    console.print(f"  Database saved: {db_path}")

    conn.close()
