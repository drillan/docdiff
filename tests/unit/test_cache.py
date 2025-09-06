"""Tests for cache management system."""

from pathlib import Path
import tempfile
import shutil

import pytest

from docdiff.cache import CacheManager


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    # Create a .git directory to simulate project root
    (Path(temp_dir) / ".git").mkdir()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestCacheManager:
    """Test CacheManager functionality."""

    def test_initialization(self, temp_project_dir):
        """Test cache manager initialization."""
        cache_manager = CacheManager(temp_project_dir)
        cache_manager.initialize()

        # Check directories were created
        assert cache_manager.cache_dir.exists()
        assert cache_manager.reports_dir.exists()
        assert cache_manager.config_file.exists()

    def test_find_project_root(self, temp_project_dir):
        """Test project root detection."""
        # Create nested directory
        nested = temp_project_dir / "docs" / "en"
        nested.mkdir(parents=True)

        cache_manager = CacheManager()
        # Should find temp_project_dir as root (has .git)
        root = cache_manager._find_project_root(nested)
        assert root == temp_project_dir

    def test_get_cache_path(self, temp_project_dir):
        """Test cache path generation."""
        cache_manager = CacheManager(temp_project_dir)

        # Test without language
        path = cache_manager.get_cache_path("test")
        assert path == cache_manager.cache_dir / "test.db"

        # Test with language
        path = cache_manager.get_cache_path("docs", "en")
        assert path == cache_manager.cache_dir / "en_docs.db"

    def test_get_report_path(self, temp_project_dir):
        """Test report path generation."""
        cache_manager = CacheManager(temp_project_dir)

        # Test without timestamp
        path = cache_manager.get_report_path("report.json", timestamp=False)
        assert path == cache_manager.reports_dir / "report.json"

        # Test with timestamp
        path = cache_manager.get_report_path("report.json", timestamp=True)
        assert "report_" in str(path)
        assert path.suffix == ".json"

    def test_config_management(self, temp_project_dir):
        """Test configuration file management."""
        cache_manager = CacheManager(temp_project_dir)
        cache_manager.initialize()

        # Load default config
        config = cache_manager.get_config()
        assert config["version"] == "1.0"
        assert config["project"]["source_lang"] == "en"
        assert "ja" in config["project"]["target_langs"]

        # Modify and save config
        config["project"]["source_lang"] = "fr"
        cache_manager.save_config(config)

        # Reload and verify
        new_config = cache_manager.get_config()
        assert new_config["project"]["source_lang"] == "fr"

    def test_clear_cache(self, temp_project_dir):
        """Test cache clearing functionality."""
        cache_manager = CacheManager(temp_project_dir)
        cache_manager.initialize()

        # Create some cache files
        (cache_manager.cache_dir / "test1.db").touch()
        (cache_manager.cache_dir / "test2.db").touch()

        # Clear cache
        removed = cache_manager.clear_cache()
        assert removed == 2
        assert not list(cache_manager.cache_dir.glob("*.db"))

    def test_clear_reports(self, temp_project_dir):
        """Test report clearing functionality."""
        cache_manager = CacheManager(temp_project_dir)
        cache_manager.initialize()

        # Create some report files
        (cache_manager.reports_dir / "report1.json").touch()
        (cache_manager.reports_dir / "report2.html").touch()

        # Clear reports
        removed = cache_manager.clear_reports()
        assert removed == 2
        assert not list(cache_manager.reports_dir.glob("*"))

    def test_get_default_db_path(self, temp_project_dir):
        """Test default database path generation."""
        cache_manager = CacheManager(temp_project_dir)

        # Test with relative path
        docs_en = temp_project_dir / "docs" / "en"
        docs_en.mkdir(parents=True)

        db_path = cache_manager.get_default_db_path(docs_en)
        assert db_path == cache_manager.cache_dir / "docs_en.db"

    def test_gitignore_update(self, temp_project_dir):
        """Test .gitignore update functionality."""
        cache_manager = CacheManager(temp_project_dir)
        cache_manager.initialize()

        gitignore = temp_project_dir / ".gitignore"
        assert gitignore.exists()

        content = gitignore.read_text()
        assert ".docdiff/cache/" in content
        assert ".docdiff/reports/" in content
        assert "!.docdiff/config.yml" in content

        # Initialize again should not duplicate
        cache_manager.initialize()
        new_content = gitignore.read_text()
        assert new_content.count(".docdiff/cache/") == 1
