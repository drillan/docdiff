"""Full comparison engine implementation for Phase 2."""

import difflib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime

from docdiff.cache import CacheManager
from docdiff.database import DatabaseConnection, NodeRepository
from docdiff.models import DocumentNode, TranslationPair, TranslationStatus
from docdiff.parsers import MySTParser, ReSTParser
from .models import ComparisonResult, NodeMapping


class ComparisonEngine:
    """Enhanced comparison engine for full document comparison."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize comparison engine.

        Args:
            cache_manager: Optional cache manager instance
        """
        self.cache_manager = cache_manager or CacheManager()
        self.cache_manager.initialize()
        self.similarity_threshold = 0.8

    def compare_projects(
        self, source_lang: str = "en", target_lang: str = "ja"
    ) -> ComparisonResult:
        """Compare entire documentation projects.

        Args:
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Complete comparison results
        """
        # Load configuration
        _ = self.cache_manager.get_config()
        # Directories are in config but not used directly here

        # Load from cache databases
        source_db = self.cache_manager.get_cache_path("docs", source_lang)
        target_db = self.cache_manager.get_cache_path("docs", target_lang)

        source_nodes = self._load_nodes_from_db(source_db)
        target_nodes = self._load_nodes_from_db(target_db)

        return self.compare(source_nodes, target_nodes, source_lang, target_lang)

    def compare_directories(
        self,
        source_dir: Path,
        target_dir: Path,
        source_lang: str = "en",
        target_lang: str = "ja",
    ) -> ComparisonResult:
        """Compare two directories directly.

        Args:
            source_dir: Source directory path
            target_dir: Target directory path
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Complete comparison results
        """
        # Parse directories
        source_nodes = self._parse_directory(source_dir)
        target_nodes = self._parse_directory(target_dir)

        return self.compare(source_nodes, target_nodes, source_lang, target_lang)

    def compare(
        self,
        source_nodes: List[DocumentNode],
        target_nodes: List[DocumentNode],
        source_lang: str = "en",
        target_lang: str = "ja",
    ) -> ComparisonResult:
        """Perform complete comparison between node sets.

        Args:
            source_nodes: List of source document nodes
            target_nodes: List of target document nodes
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Complete comparison results
        """
        # Create node mappings
        mappings = self._create_node_mappings(source_nodes, target_nodes)

        # Analyze structure
        structure_diff = self._analyze_structure(source_nodes, target_nodes)

        # Detect content changes
        content_changes = self._detect_content_changes(mappings)

        # Create translation pairs
        translation_pairs = self._create_translation_pairs(
            mappings, source_lang, target_lang
        )

        # Calculate coverage statistics
        coverage_stats = self._calculate_coverage(mappings)

        return ComparisonResult(
            structure_diff=structure_diff,
            content_changes=content_changes,
            translation_pairs=translation_pairs,
            coverage_stats=coverage_stats,
            mappings=mappings,
            source_lang=source_lang,
            target_lang=target_lang,
        )

    def _create_node_mappings(
        self, source_nodes: List[DocumentNode], target_nodes: List[DocumentNode]
    ) -> List[NodeMapping]:
        """Create mappings between source and target nodes.

        This is the core algorithm that matches nodes between languages.
        Uses content-based matching to determine translation status.
        """
        mappings = []
        target_map = self._build_node_index(target_nodes)
        used_targets: Set[str] = set()

        for source_node in source_nodes:
            # Check if there's a node with matching label/name (structural correspondence)
            structural_match = None
            if source_node.label:
                key = f"label:{source_node.label}"
                if key in target_map and target_map[key].id not in used_targets:
                    structural_match = target_map[key]
            elif source_node.name:
                key = f"name:{source_node.name}"
                if key in target_map and target_map[key].id not in used_targets:
                    structural_match = target_map[key]

            # If we found a structural match, check if it's actually translated
            if structural_match:
                # Compare content to determine if translated
                similarity = self._calculate_similarity(
                    source_node.content, structural_match.content
                )

                # If content is very similar, it's NOT translated (just copied)
                if similarity > 0.95:  # Nearly identical content
                    # Mark as missing translation
                    mappings.append(
                        NodeMapping(
                            source_node=source_node,
                            target_node=None,
                            similarity=0.0,
                            mapping_type="missing",
                        )
                    )
                else:
                    # Content is different, so it's translated
                    mappings.append(
                        NodeMapping(
                            source_node=source_node,
                            target_node=structural_match,
                            similarity=similarity,
                            mapping_type="exact" if similarity < 0.3 else "fuzzy",
                        )
                    )
                    used_targets.add(structural_match.id)
            else:
                # No structural match, try fuzzy content matching
                target_node, similarity = self._find_fuzzy_match(
                    source_node, target_nodes, used_targets
                )

                if target_node and similarity >= self.similarity_threshold:
                    # Check if it's actually translated or just similar
                    if similarity > 0.95:
                        # Too similar - probably not translated
                        mappings.append(
                            NodeMapping(
                                source_node=source_node,
                                target_node=None,
                                similarity=0.0,
                                mapping_type="missing",
                            )
                        )
                    else:
                        mappings.append(
                            NodeMapping(
                                source_node=source_node,
                                target_node=target_node,
                                similarity=similarity,
                                mapping_type="fuzzy",
                            )
                        )
                        used_targets.add(target_node.id)
                else:
                    # No match found - needs translation
                    mappings.append(
                        NodeMapping(
                            source_node=source_node,
                            target_node=None,
                            similarity=0.0,
                            mapping_type="missing",
                        )
                    )

        return mappings

    def _find_exact_match(
        self,
        source_node: DocumentNode,
        target_map: Dict[str, DocumentNode],
        used_targets: Set[str],
    ) -> Optional[DocumentNode]:
        """Find structurally corresponding node (not necessarily translated).

        This method finds the STRUCTURAL match based on labels/names,
        but does NOT determine if content is translated.
        """
        # Match by label (e.g., (section-label)=)
        # Labels are structural markers, not content
        if source_node.label:
            key = f"label:{source_node.label}"
            if key in target_map and target_map[key].id not in used_targets:
                return target_map[key]

        # Match by name attribute (e.g., :name: attribute)
        # Names are structural markers, not content
        if source_node.name:
            key = f"name:{source_node.name}"
            if key in target_map and target_map[key].id not in used_targets:
                return target_map[key]

        # Match by relative path and approximate line number
        if hasattr(source_node, "file_path") and source_node.file_path:
            # Convert docs/en/index.md -> docs/ja/index.md
            rel_path = (
                Path(*source_node.file_path.parts[2:])
                if len(source_node.file_path.parts) > 2
                else source_node.file_path
            )

            # Look for nodes at similar positions
            for line_offset in [0, -1, 1, -2, 2]:  # Check nearby lines
                key = f"position:{rel_path}:{source_node.line_number + line_offset}"
                if key in target_map and target_map[key].id not in used_targets:
                    candidate = target_map[key]
                    # Must be same type
                    if candidate.type == source_node.type:
                        # Position match also needs content check
                        return None

        return None

    def _find_fuzzy_match(
        self,
        source_node: DocumentNode,
        target_nodes: List[DocumentNode],
        used_targets: Set[str],
    ) -> Tuple[Optional[DocumentNode], float]:
        """Find best fuzzy match based on content similarity."""
        best_match = None
        best_similarity = 0.0

        for target_node in target_nodes:
            if target_node.id in used_targets:
                continue

            # Must be same type
            if target_node.type != source_node.type:
                continue

            # Calculate similarity
            similarity = self._calculate_similarity(
                source_node.content, target_node.content
            )

            # Boost similarity for nodes in corresponding files
            if self._are_corresponding_files(source_node, target_node):
                similarity *= 1.2  # 20% boost
                similarity = min(similarity, 1.0)  # Cap at 1.0

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = target_node

        return best_match, best_similarity

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using difflib."""
        if not text1 or not text2:
            return 0.0

        # Quick check for very different lengths
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
        if len_ratio < 0.3:  # If one is more than 3x longer
            return 0.0

        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def _are_corresponding_files(
        self, node1: DocumentNode, node2: DocumentNode
    ) -> bool:
        """Check if two nodes are from corresponding files in different languages."""
        if not hasattr(node1, "file_path") or not hasattr(node2, "file_path"):
            return False

        if not node1.file_path or not node2.file_path:
            return False

        # Extract filename without language directory
        # e.g., docs/en/index.md -> index.md
        file1 = (
            Path(*node1.file_path.parts[2:])
            if len(node1.file_path.parts) > 2
            else node1.file_path.name
        )
        file2 = (
            Path(*node2.file_path.parts[2:])
            if len(node2.file_path.parts) > 2
            else node2.file_path.name
        )

        return str(file1) == str(file2)

    def _build_node_index(self, nodes: List[DocumentNode]) -> Dict[str, DocumentNode]:
        """Build an index for quick node lookup."""
        node_map = {}

        for node in nodes:
            # Index by label
            if node.label:
                node_map[f"label:{node.label}"] = node

            # Index by name
            if node.name:
                node_map[f"name:{node.name}"] = node

            # Index by position
            if hasattr(node, "file_path") and node.file_path:
                rel_path = (
                    Path(*node.file_path.parts[2:])
                    if len(node.file_path.parts) > 2
                    else node.file_path
                )
                node_map[f"position:{rel_path}:{node.line_number}"] = node

        return node_map

    def _create_translation_pairs(
        self, mappings: List[NodeMapping], source_lang: str, target_lang: str
    ) -> List[TranslationPair]:
        """Create TranslationPair objects from mappings."""
        pairs = []

        for mapping in mappings:
            # Determine translation status
            if mapping.mapping_type == "missing":
                status = TranslationStatus.PENDING
            elif mapping.mapping_type == "exact":
                status = TranslationStatus.TRANSLATED
            elif mapping.similarity >= 0.95:
                status = TranslationStatus.REVIEWED
            else:
                status = TranslationStatus.OUTDATED

            pair = TranslationPair(
                source_node_id=mapping.source_node.id,
                target_node_id=mapping.target_node.id if mapping.target_node else None,
                source_language=source_lang,
                target_language=target_lang,
                status=status,
                updated_at=datetime.now(),
                similarity_score=mapping.similarity if mapping.target_node else None,
            )
            pairs.append(pair)

        return pairs

    def _calculate_coverage(self, mappings: List[NodeMapping]) -> Dict[str, Any]:
        """Calculate translation coverage statistics."""
        total = len(mappings)
        if total == 0:
            return {
                "overall": 0.0,
                "counts": {"total": 0, "translated": 0, "missing": 0},
            }

        translated = len([m for m in mappings if m.target_node is not None])
        exact = len([m for m in mappings if m.mapping_type == "exact"])
        fuzzy = len([m for m in mappings if m.mapping_type == "fuzzy"])
        missing = len([m for m in mappings if m.mapping_type == "missing"])

        return {
            "overall": translated / total,
            "exact_match": exact / total,
            "fuzzy_match": fuzzy / total,
            "missing": missing / total,
            "counts": {
                "total": total,
                "translated": translated,
                "exact": exact,
                "fuzzy": fuzzy,
                "missing": missing,
            },
        }

    def _analyze_structure(
        self, source_nodes: List[DocumentNode], target_nodes: List[DocumentNode]
    ) -> Dict[str, Any]:
        """Analyze structural differences between documents."""
        source_types: Dict[str, int] = {}
        target_types: Dict[str, int] = {}

        # Count node types
        for node in source_nodes:
            node_type = (
                node.type.value if hasattr(node.type, "value") else str(node.type)
            )
            source_types[node_type] = source_types.get(node_type, 0) + 1

        for node in target_nodes:
            node_type = (
                node.type.value if hasattr(node.type, "value") else str(node.type)
            )
            target_types[node_type] = target_types.get(node_type, 0) + 1

        # Calculate differences
        all_types = set(source_types.keys()) | set(target_types.keys())

        diff = {}
        for node_type in all_types:
            s_count = source_types.get(node_type, 0)
            t_count = target_types.get(node_type, 0)
            diff[node_type] = {
                "source": s_count,
                "target": t_count,
                "diff": t_count - s_count,
                "coverage": (t_count / s_count * 100) if s_count > 0 else 0,
            }

        return diff

    def _detect_content_changes(
        self, mappings: List[NodeMapping]
    ) -> List[Dict[str, Any]]:
        """Detect content-level changes between mapped nodes."""
        changes = []

        for mapping in mappings:
            if mapping.target_node and 0 < mapping.similarity < 1.0:
                change = {
                    "source_id": mapping.source_node.id,
                    "target_id": mapping.target_node.id,
                    "file": str(mapping.source_node.file_path)
                    if hasattr(mapping.source_node, "file_path")
                    else "unknown",
                    "line": mapping.source_node.line_number,
                    "type": mapping.source_node.type.value
                    if hasattr(mapping.source_node.type, "value")
                    else str(mapping.source_node.type),
                    "similarity": mapping.similarity,
                    "change_type": self._classify_change(mapping.similarity),
                    "source_preview": mapping.source_node.content[:100]
                    if mapping.source_node.content
                    else "",
                    "target_preview": mapping.target_node.content[:100]
                    if mapping.target_node.content
                    else "",
                }
                changes.append(change)

        return changes

    def _classify_change(self, similarity: float) -> str:
        """Classify the type of change based on similarity score."""
        if similarity >= 0.95:
            return "minor"
        elif similarity >= 0.8:
            return "moderate"
        elif similarity >= 0.5:
            return "major"
        else:
            return "rewrite"

    def _load_nodes_from_db(self, db_path: Path) -> List[DocumentNode]:
        """Load nodes from a database file."""
        if not db_path.exists():
            return []

        conn = DatabaseConnection(db_path)
        conn.connect()
        repo = NodeRepository(conn)

        # Get all nodes from database
        nodes = repo.get_all_nodes()

        conn.close()
        return nodes

    def _parse_directory(self, directory: Path) -> List[DocumentNode]:
        """Parse all documents in a directory."""
        nodes = []

        # Create parsers
        myst_parser = MySTParser()
        rest_parser = ReSTParser()

        # Find all markdown and rst files
        md_files = list(directory.rglob("*.md"))
        rst_files = list(directory.rglob("*.rst"))

        for file_path in md_files + rst_files:
            try:
                parser = myst_parser if file_path.suffix == ".md" else rest_parser

                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                file_nodes = parser.parse(content, file_path)
                nodes.extend(file_nodes)

            except Exception as e:
                print(f"Error parsing {file_path}: {e}")

        return nodes
