"""Models for document comparison."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from docdiff.models import DocumentNode, TranslationPair


@dataclass
class NodeMapping:
    """Represents a mapping between source and target nodes."""
    
    source_node: DocumentNode
    target_node: Optional[DocumentNode]
    similarity: float
    mapping_type: str  # 'exact', 'fuzzy', 'missing'
    
    def is_translated(self) -> bool:
        """Check if this mapping represents a translated node."""
        return self.target_node is not None
    
    def needs_translation(self) -> bool:
        """Check if this node needs translation."""
        return self.mapping_type == 'missing' or (
            self.mapping_type == 'fuzzy' and self.similarity < 0.95
        )


@dataclass
class ComparisonResult:
    """Complete comparison results."""
    
    # Structure comparison
    structure_diff: Dict[str, Any]
    
    # Content comparison  
    content_changes: List[Dict[str, Any]]
    
    # Translation analysis
    translation_pairs: List[TranslationPair]
    coverage_stats: Dict[str, float]
    
    # Node mappings
    mappings: List[NodeMapping]
    
    # Metadata
    source_lang: str = "en"
    target_lang: str = "ja"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'metadata': {
                'source_lang': self.source_lang,
                'target_lang': self.target_lang,
                'timestamp': self.timestamp.isoformat(),
                'total_mappings': len(self.mappings)
            },
            'structure_diff': self.structure_diff,
            'content_changes': self.content_changes,
            'coverage': self.coverage_stats,
            'summary': {
                'exact_matches': len([m for m in self.mappings if m.mapping_type == 'exact']),
                'fuzzy_matches': len([m for m in self.mappings if m.mapping_type == 'fuzzy']),
                'missing': len([m for m in self.mappings if m.mapping_type == 'missing']),
                'needs_translation': len([m for m in self.mappings if m.needs_translation()])
            }
        }
    
    def generate_html_report(self) -> str:
        """Generate HTML report of comparison results."""
        # Simplified HTML generation without jinja2 dependency
        coverage_pct = round(self.coverage_stats.get('overall', 0) * 100, 1)
        
        missing_count = len([m for m in self.mappings if m.mapping_type == 'missing'])
        fuzzy_count = len([m for m in self.mappings if m.mapping_type == 'fuzzy'])
        exact_count = len([m for m in self.mappings if m.mapping_type == 'exact'])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Translation Comparison Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ margin: 20px 0; padding: 15px; background: #fff; border: 1px solid #ddd; }}
                .progress {{ width: 100%; height: 30px; background: #e0e0e0; border-radius: 15px; }}
                .progress-bar {{ height: 100%; background: #4CAF50; border-radius: 15px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-box {{ flex: 1; padding: 15px; background: #f9f9f9; border-radius: 5px; text-align: center; }}
                .missing {{ color: #d32f2f; }}
                .fuzzy {{ color: #f57c00; }}
                .exact {{ color: #388e3c; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
                th {{ background: #f5f5f5; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Translation Comparison Report</h1>
                <p><strong>Source:</strong> {self.source_lang} | <strong>Target:</strong> {self.target_lang}</p>
                <p><strong>Generated:</strong> {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metric">
                <h2>Overall Translation Coverage: {coverage_pct}%</h2>
                <div class="progress">
                    <div class="progress-bar" style="width: {coverage_pct}%"></div>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-box exact">
                    <h3>Exact Matches</h3>
                    <p style="font-size: 2em;">{exact_count}</p>
                </div>
                <div class="stat-box fuzzy">
                    <h3>Fuzzy Matches</h3>
                    <p style="font-size: 2em;">{fuzzy_count}</p>
                </div>
                <div class="stat-box missing">
                    <h3>Missing</h3>
                    <p style="font-size: 2em;">{missing_count}</p>
                </div>
            </div>
            
            <h2>Structure Analysis</h2>
            <table>
                <tr>
                    <th>Node Type</th>
                    <th>Source Count</th>
                    <th>Target Count</th>
                    <th>Coverage</th>
                </tr>
        """
        
        for node_type, data in self.structure_diff.items():
            coverage = data.get('coverage', 0)
            html += f"""
                <tr>
                    <td>{node_type}</td>
                    <td>{data.get('source', 0)}</td>
                    <td>{data.get('target', 0)}</td>
                    <td>{coverage:.1f}%</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Translation Details</h2>
            <p>Total source nodes: {}</p>
            <p>Nodes needing translation: {}</p>
            <p>Nodes with changes: {}</p>
        </body>
        </html>
        """.format(
            len(self.mappings),
            len([m for m in self.mappings if m.needs_translation()]),
            len(self.content_changes)
        )
        
        return html