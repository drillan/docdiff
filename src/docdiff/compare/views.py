"""Rich view formatters for comparison results."""

from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text

from docdiff.compare.models import ComparisonResult, NodeMapping
from docdiff.models import DocumentNode, NodeType


@dataclass
class MetadataGroup:
    """Group of nodes with the same metadata."""
    key: str  # label, name, or caption
    value: str  # actual metadata value
    source_nodes: List[DocumentNode]
    target_nodes: List[DocumentNode]
    coverage: float


class MetadataView:
    """Rich display formatter for metadata-based comparison views."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def display_tree_view(self, result: ComparisonResult) -> None:
        """Display hierarchical tree view of document structure."""
        tree = Tree("📚 Document Structure Comparison")
        
        # Group mappings by file
        file_groups = self._group_by_file(result.mappings)
        
        for file_path, mappings in file_groups.items():
            file_branch = tree.add(f"📁 {file_path}")
            
            # Build hierarchical structure
            hierarchy = self._build_hierarchy(mappings)
            self._add_hierarchy_to_tree(file_branch, hierarchy, 0)
        
        self.console.print(tree)
    
    def display_metadata_groups(self, result: ComparisonResult) -> None:
        """Display comparison grouped by metadata (label, name, caption)."""
        # Group by labels
        label_groups = self._group_by_metadata(result.mappings, 'label')
        name_groups = self._group_by_metadata(result.mappings, 'name')
        caption_groups = self._group_by_metadata(result.mappings, 'caption')
        
        # Display label-based groups
        if label_groups:
            self.console.print("\n[bold cyan]Label-based Mappings:[/bold cyan]")
            self.console.print("━" * 60)
            for label, mappings in label_groups.items():
                self._display_metadata_group(label, mappings, "label")
        
        # Display name-based groups
        if name_groups:
            self.console.print("\n[bold cyan]Name-based Mappings:[/bold cyan]")
            self.console.print("━" * 60)
            for name, mappings in name_groups.items():
                self._display_metadata_group(name, mappings, "name")
        
        # Display caption-based groups
        if caption_groups:
            self.console.print("\n[bold cyan]Caption-based Mappings:[/bold cyan]")
            self.console.print("━" * 60)
            for caption, mappings in caption_groups.items():
                self._display_metadata_group(caption, mappings, "caption")
    
    def display_side_by_side(self, result: ComparisonResult, max_items: int = 20) -> None:
        """Display side-by-side comparison table."""
        table = Table(title="Side-by-Side Comparison", show_lines=True)
        
        table.add_column("Source (EN)", width=40, style="cyan")
        table.add_column("Target (JA)", width=40, style="yellow")
        table.add_column("Status", width=15, justify="center")
        table.add_column("Match", width=10, justify="center")
        
        for i, mapping in enumerate(result.mappings[:max_items]):
            source_text = self._format_node_text(mapping.source_node)
            target_text = self._format_node_text(mapping.target_node) if mapping.target_node else "[red]MISSING[/red]"
            
            status = self._get_status_icon(mapping)
            match_pct = f"{mapping.similarity*100:.0f}%" if mapping.target_node else "0%"
            
            # Color code the match percentage
            if mapping.similarity >= 0.95:
                match_style = "green"
            elif mapping.similarity >= 0.8:
                match_style = "yellow"
            else:
                match_style = "red"
            
            table.add_row(
                source_text,
                target_text,
                status,
                f"[{match_style}]{match_pct}[/{match_style}]"
            )
        
        if len(result.mappings) > max_items:
            table.add_row(
                f"... and {len(result.mappings) - max_items} more items",
                "", "", ""
            )
        
        self.console.print(table)
    
    def display_metadata_stats(self, result: ComparisonResult) -> None:
        """Display statistics grouped by metadata."""
        self.console.print("\n[bold magenta]Metadata Coverage Report[/bold magenta]")
        self.console.print("=" * 60)
        
        # Calculate stats by label
        label_stats = self._calculate_metadata_stats(result.mappings, 'label')
        if label_stats:
            self._display_metadata_stat_table("By Label", label_stats)
        
        # Calculate stats by name
        name_stats = self._calculate_metadata_stats(result.mappings, 'name')
        if name_stats:
            self._display_metadata_stat_table("By Name Attribute", name_stats)
        
        # Calculate stats by caption
        caption_stats = self._calculate_metadata_stats(result.mappings, 'caption')
        if caption_stats:
            self._display_metadata_stat_table("By Caption", caption_stats)
    
    def _group_by_file(self, mappings: List[NodeMapping]) -> Dict[str, List[NodeMapping]]:
        """Group mappings by source file path."""
        groups = defaultdict(list)
        for mapping in mappings:
            if hasattr(mapping.source_node, 'file_path'):
                file_name = mapping.source_node.file_path.name
                groups[file_name].append(mapping)
        return dict(groups)
    
    def _group_by_metadata(self, mappings: List[NodeMapping], attr: str) -> Dict[str, List[NodeMapping]]:
        """Group mappings by metadata attribute (label, name, caption)."""
        groups = defaultdict(list)
        for mapping in mappings:
            value = getattr(mapping.source_node, attr, None)
            if value:
                groups[value].append(mapping)
        return dict(groups)
    
    def _build_hierarchy(self, mappings: List[NodeMapping]) -> Dict[int, List[NodeMapping]]:
        """Build hierarchical structure based on section levels."""
        hierarchy = defaultdict(list)
        
        # Sort by line number
        sorted_mappings = sorted(mappings, key=lambda m: m.source_node.line_number)
        
        current_level = 0
        level_stack = [0]
        
        for mapping in sorted_mappings:
            node = mapping.source_node
            
            if node.type == NodeType.SECTION and hasattr(node, 'level'):
                current_level = node.level
                # Update level stack
                while len(level_stack) > current_level:
                    level_stack.pop()
                if len(level_stack) < current_level:
                    level_stack.append(current_level)
            
            hierarchy[current_level].append(mapping)
        
        return dict(hierarchy)
    
    def _add_hierarchy_to_tree(self, parent: Tree, hierarchy: Dict[int, List[NodeMapping]], level: int) -> None:
        """Recursively add hierarchical nodes to tree."""
        if level not in hierarchy:
            return
        
        for mapping in hierarchy[level]:
            node_text = self._format_tree_node(mapping)
            child = parent.add(node_text)
            
            # Add children if this is a section
            if mapping.source_node.type == NodeType.SECTION:
                self._add_hierarchy_to_tree(child, hierarchy, level + 1)
    
    def _format_tree_node(self, mapping: NodeMapping) -> str:
        """Format a node for tree display."""
        node = mapping.source_node
        icon = self._get_node_icon(node.type)
        status = self._get_status_icon(mapping)
        
        # Build node text
        text = f"{icon} {node.content[:50]}..." if len(node.content) > 50 else f"{icon} {node.content}"
        
        # Add metadata
        metadata_parts = []
        if node.label:
            metadata_parts.append(f"[dim]label: {node.label}[/dim]")
        if node.name:
            metadata_parts.append(f"[dim]name: {node.name}[/dim]")
        if hasattr(node, 'caption') and node.caption:
            metadata_parts.append(f"[dim]caption: {node.caption}[/dim]")
        
        if metadata_parts:
            text += f" [{', '.join(metadata_parts)}]"
        
        # Add status
        text += f" {status}"
        
        # Add coverage for sections
        if node.type == NodeType.SECTION and mapping.target_node:
            text += f" [cyan]({mapping.similarity*100:.0f}%)[/cyan]"
        
        return text
    
    def _get_node_icon(self, node_type: NodeType) -> str:
        """Get icon for node type."""
        icons = {
            NodeType.SECTION: "📄",
            NodeType.PARAGRAPH: "📝",
            NodeType.CODE_BLOCK: "💻",
            NodeType.LIST: "📋",
            NodeType.LIST_ITEM: "•",
            NodeType.TABLE: "📊",
            NodeType.FIGURE: "🖼️",
            NodeType.MATH_BLOCK: "🔢",
            NodeType.ADMONITION: "⚠️",
        }
        return icons.get(node_type, "📄")
    
    def _get_status_icon(self, mapping: NodeMapping) -> str:
        """Get status icon for mapping."""
        if mapping.mapping_type == 'exact':
            return "[green]✅[/green]"
        elif mapping.mapping_type == 'fuzzy':
            if mapping.similarity >= 0.95:
                return "[yellow]⚠️[/yellow]"
            else:
                return "[orange1]⚠️[/orange1]"
        else:
            return "[red]❌[/red]"
    
    def _format_node_text(self, node: Optional[DocumentNode]) -> str:
        """Format node content for display."""
        if not node:
            return ""
        
        text = node.content[:80] if len(node.content) > 80 else node.content
        
        # Add metadata hints
        metadata = []
        if node.label:
            metadata.append(f"[dim]:{node.label}[/dim]")
        if node.name:
            metadata.append(f"[dim]@{node.name}[/dim]")
        
        if metadata:
            text += "\n" + " ".join(metadata)
        
        return text
    
    def _display_metadata_group(self, key: str, mappings: List[NodeMapping], metadata_type: str) -> None:
        """Display a single metadata group."""
        # Calculate coverage
        translated = sum(1 for m in mappings if m.target_node)
        total = len(mappings)
        coverage = (translated / total * 100) if total > 0 else 0
        
        # Determine overall status
        if coverage == 100:
            status = "[green]✅ Complete[/green]"
        elif coverage > 0:
            status = f"[yellow]⚠️ Partial ({coverage:.0f}%)[/yellow]"
        else:
            status = "[red]❌ Missing[/red]"
        
        # Display header
        self.console.print(f"\n[bold][{metadata_type}: {key}][/bold] {status}")
        
        # Display mappings
        for mapping in mappings:
            source_preview = mapping.source_node.content[:60]
            if mapping.target_node:
                target_preview = mapping.target_node.content[:60]
                match_info = f"[green]→[/green] {target_preview}"
            else:
                match_info = "[red]→ (not translated)[/red]"
            
            self.console.print(f"  {source_preview}")
            self.console.print(f"  {match_info}")
    
    def _calculate_metadata_stats(self, mappings: List[NodeMapping], attr: str) -> Dict[str, Tuple[int, int, float]]:
        """Calculate statistics for each metadata value."""
        stats = defaultdict(lambda: [0, 0])  # [translated, total]
        
        for mapping in mappings:
            value = getattr(mapping.source_node, attr, None)
            if value:
                stats[value][1] += 1  # total
                if mapping.target_node:
                    stats[value][0] += 1  # translated
        
        # Calculate percentages
        result = {}
        for key, (translated, total) in stats.items():
            percentage = (translated / total * 100) if total > 0 else 0
            result[key] = (translated, total, percentage)
        
        return result
    
    def _display_metadata_stat_table(self, title: str, stats: Dict[str, Tuple[int, int, float]]) -> None:
        """Display statistics table for metadata."""
        self.console.print(f"\n[bold]{title}:[/bold]")
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Metadata", width=30)
        table.add_column("Translated", justify="right", width=12)
        table.add_column("Total", justify="right", width=8)
        table.add_column("Coverage", justify="right", width=12)
        table.add_column("Progress", width=20)
        
        # Sort by coverage percentage
        sorted_stats = sorted(stats.items(), key=lambda x: x[1][2], reverse=True)
        
        for key, (translated, total, percentage) in sorted_stats:
            # Color code based on percentage
            if percentage == 100:
                style = "green"
                status = "✅"
            elif percentage >= 50:
                style = "yellow"
                status = "⚠️"
            else:
                style = "red"
                status = "❌"
            
            # Create progress bar
            bar_width = 15
            filled = int(percentage / 100 * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            table.add_row(
                f"{key}",
                str(translated),
                str(total),
                f"[{style}]{percentage:.1f}%[/{style}] {status}",
                f"[{style}]{bar}[/{style}]"
            )
        
        self.console.print(table)