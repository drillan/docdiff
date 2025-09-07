"""Cache management system for docdiff - Phase 2 implementation."""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import yaml
from docdiff.utils.path_utils import safe_relative_to


class CacheManager:
    """Simple and direct cache management without legacy support."""

    def __init__(self, project_root: Optional[Path] = None):
        """Direct initialization - no fallbacks or compatibility checks."""
        self.project_root = project_root or self._find_project_root()
        self.base_dir = self.project_root / ".docdiff"
        self.cache_dir = self.base_dir / "cache"
        self.reports_dir = self.base_dir / "reports"
        self.config_file = self.base_dir / "config.yml"

    def _find_project_root(self, start_path: Optional[Path] = None) -> Path:
        """Find project root by looking for .git or pyproject.toml."""
        current = (start_path or Path.cwd()).resolve()

        while current != current.parent:
            if (
                (current / ".git").exists()
                or (current / "pyproject.toml").exists()
                or (current / ".docdiff").exists()
            ):
                return current
            current = current.parent

        # Fallback to current directory
        return Path.cwd()

    def initialize(self) -> None:
        """Create fresh directory structure - no migration."""
        # Simple, direct creation
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Create config only if missing
        if not self.config_file.exists():
            self._create_default_config()

        # Update .gitignore once
        self._update_gitignore()

    def _create_default_config(self) -> None:
        """Create default configuration file."""
        config = {
            "version": "1.0",
            "project": {
                "source_lang": "en",
                "target_langs": ["ja"],
                "source_dir": "docs/en",
                "target_dirs": {"ja": "docs/ja"},
            },
            "cache": {"location": ".docdiff/cache", "auto_clean": False},
            "comparison": {
                "similarity_threshold": 0.8,
                "ignore_patterns": ["_build/", "*.pyc", "__pycache__/"],
            },
        }

        with open(self.config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def _update_gitignore(self) -> None:
        """Update .gitignore with docdiff patterns."""
        gitignore = self.project_root / ".gitignore"

        patterns_to_add = [
            "",
            "# docdiff generated files",
            ".docdiff/cache/",
            ".docdiff/reports/",
            "*.db",
            "comparison*.json",
            "",
            "# Keep configuration",
            "!.docdiff/config.yml",
        ]

        # Check if patterns already exist
        if gitignore.exists():
            content = gitignore.read_text()
            if ".docdiff/cache/" in content:
                return  # Already configured

        # Add patterns
        with open(gitignore, "a") as f:
            f.write("\n".join(patterns_to_add))
            f.write("\n")

    def get_cache_path(self, name: str, lang: Optional[str] = None) -> Path:
        """Get cache file path with optional language prefix."""
        if lang:
            name = f"{lang}_{name}"
        if not name.endswith(".db"):
            name += ".db"
        return self.cache_dir / name

    def get_report_path(self, name: str, timestamp: bool = True) -> Path:
        """Get report file path with optional timestamp."""
        if timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = name.rsplit(".", 1) if "." in name else (name, "json")
            name = f"{base}_{ts}.{ext}"
        return self.reports_dir / name

    def clear_cache(self) -> int:
        """Clear all cache files - no questions asked."""
        # Breaking change: No confirmation, just delete
        removed = 0
        for cache_file in self.cache_dir.glob("*.db"):
            cache_file.unlink()
            removed += 1
        return removed

    def clear_reports(self) -> int:
        """Clear all report files."""
        removed = 0
        for report_file in self.reports_dir.glob("*"):
            if report_file.is_file():
                report_file.unlink()
                removed += 1
        return removed

    def get_config(self) -> Dict[str, Any]:
        """Load configuration from config.yml."""
        if not self.config_file.exists():
            self._create_default_config()

        with open(self.config_file) as f:
            return yaml.safe_load(f)

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to config.yml."""
        with open(self.config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def get_default_db_path(self, parse_dir: Path) -> Path:
        """Get default database path for a given directory."""
        # Extract meaningful name from path
        # docs/en -> docs_en.db
        # docs/ja -> docs_ja.db
        rel_path = (
            safe_relative_to(parse_dir, self.project_root)
            if parse_dir.is_absolute()
            else parse_dir
        )
        db_name = "_".join(rel_path.parts) + ".db"
        return self.cache_dir / db_name

    def get_cache_dir(self) -> Path:
        """Get the cache directory path.

        Returns:
            Path to the cache directory
        """
        return self.cache_dir

    def get_reports_dir(self) -> Path:
        """Get the reports directory path.

        Returns:
            Path to the reports directory
        """
        return self.reports_dir
