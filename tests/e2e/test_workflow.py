"""End-to-end tests for complete docdiff workflow."""

import json
import csv
import tempfile
from pathlib import Path
from typing import Dict, Any
import subprocess
import time

import pytest
from click.testing import CliRunner

from docdiff.cli.main import app
from docdiff.cache import CacheManager
from docdiff.parsers import MySTParser
from docdiff.compare import ComparisonEngine
from docdiff.workflow import TranslationExporter, TranslationImporter


class TestCompleteWorkflow:
    """Test the complete docdiff workflow from parsing to import."""
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        # Create source documents (English)
        en_dir = tmp_path / "docs" / "en"
        en_dir.mkdir(parents=True)
        
        (en_dir / "index.md").write_text("""# Project Documentation

## Introduction

This is a test project for E2E testing.

### Features

- Feature 1: Basic functionality
- Feature 2: Advanced features
- Feature 3: Integration support

## Getting Started

To get started with this project:

```python
def hello():
    print("Hello, World!")
```

### Installation

Run the following command:

```bash
pip install test-project
```

## API Reference

See the API documentation for details.
""")
        
        (en_dir / "guide.md").write_text("""# User Guide

## Basic Usage

This guide covers basic usage patterns.

### Configuration

Configure the system with:

```yaml
config:
  setting1: value1
  setting2: value2
```

### Examples

Here are some examples:

```python
# Example 1
result = process_data(input)
print(result)
```

## Advanced Topics

Advanced usage patterns and best practices.
""")
        
        # Create partial target documents (Japanese)
        ja_dir = tmp_path / "docs" / "ja"
        ja_dir.mkdir(parents=True)
        
        (ja_dir / "index.md").write_text("""# プロジェクトドキュメント

## はじめに

これはE2Eテスト用のテストプロジェクトです。

### 機能

- 機能1: 基本機能
- 機能2: 高度な機能

## 始め方

このプロジェクトを始めるには：

```python
def hello():
    print("Hello, World!")
```
""")
        
        # Intentionally leave guide.md missing to test missing translations
        
        return tmp_path
    
    @pytest.fixture
    def cache_manager(self, temp_project):
        """Create and initialize cache manager."""
        manager = CacheManager(temp_project)
        manager.initialize()
        return manager
    
    def test_full_workflow_cli(self, temp_project):
        """Test complete workflow using CLI commands."""
        runner = CliRunner()
        
        # Change to project directory
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_project)
        
        try:
            # Step 1: Parse source documents
            result = runner.invoke(app, [
                'parse', 
                str(temp_project / 'docs' / 'en')
            ])
            assert result.exit_code == 0
            assert 'Parsed' in result.output
            
            # Step 2: Parse target documents
            result = runner.invoke(app, [
                'parse',
                str(temp_project / 'docs' / 'ja')
            ])
            assert result.exit_code == 0
            
            # Step 3: Compare documents
            comparison_output = temp_project / 'comparison.json'
            result = runner.invoke(app, [
                'compare',
                str(temp_project / 'docs' / 'en'),
                str(temp_project / 'docs' / 'ja'),
                '--output', str(comparison_output)
            ])
            # Allow exit code 1 (coverage < 50% warning)
            assert result.exit_code in [0, 1]
            assert 'Translation Coverage Summary' in result.output
            assert comparison_output.exists()
            
            # Verify comparison results
            with open(comparison_output) as f:
                comparison_data = json.load(f)
            assert 'metadata' in comparison_data
            assert comparison_data['metadata']['source_lang'] == 'en'
            assert comparison_data['metadata']['target_lang'] == 'ja'
            
            # Step 4: Export for translation (CSV format)
            export_csv = temp_project / 'translations.csv'
            result = runner.invoke(app, [
                'export',
                str(temp_project / 'docs' / 'en'),
                str(temp_project / 'docs' / 'ja'),
                str(export_csv),
                '--format', 'csv'
            ])
            assert result.exit_code == 0
            assert export_csv.exists()
            
            # Verify CSV content
            with open(export_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            assert len(rows) > 0
            assert 'Source' in rows[0]
            assert 'Target' in rows[0]
            
            # Step 5: Export for translation (JSON format)
            export_json = temp_project / 'translations.json'
            result = runner.invoke(app, [
                'export',
                str(temp_project / 'docs' / 'en'),
                str(temp_project / 'docs' / 'ja'),
                str(export_json),
                '--format', 'json',
                '--include-context'
            ])
            assert result.exit_code == 0
            assert export_json.exists()
            
            # Verify JSON content
            with open(export_json) as f:
                export_data = json.load(f)
            assert 'translations' in export_data
            assert len(export_data['translations']) > 0
            
            # Step 6: Simulate translation by modifying JSON
            for trans in export_data['translations'][:3]:  # Translate first 3 items
                if not trans['target']:
                    trans['target'] = f"翻訳済み: {trans['source'][:20]}..."
            
            modified_json = temp_project / 'translations_modified.json'
            with open(modified_json, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Step 7: Import translations (dry run first)
            result = runner.invoke(app, [
                'import',
                str(modified_json),
                str(temp_project / 'docs' / 'ja'),
                '--dry-run'
            ])
            assert result.exit_code == 0
            assert 'DRY RUN MODE' in result.output
            
            # Step 8: Generate HTML report
            result = runner.invoke(app, [
                'compare',
                str(temp_project / 'docs' / 'en'),
                str(temp_project / 'docs' / 'ja'),
                '--html'
            ])
            assert result.exit_code in [0, 1]
            assert 'HTML report saved' in result.output
            
            # Verify HTML report exists
            reports_dir = temp_project / '.docdiff' / 'reports'
            html_files = list(reports_dir.glob('*.html'))
            assert len(html_files) > 0
            
        finally:
            os.chdir(original_cwd)
    
    def test_workflow_with_api(self, temp_project, cache_manager):
        """Test workflow using Python API directly."""
        # Step 1: Parse documents
        parser = MySTParser()
        source_nodes = []
        target_nodes = []
        
        # Parse source documents
        en_dir = temp_project / 'docs' / 'en'
        for md_file in en_dir.glob('*.md'):
            content = md_file.read_text()
            nodes = parser.parse(content, md_file)
            for node in nodes:
                node.doc_language = 'en'
            source_nodes.extend(nodes)
        
        # Parse target documents
        ja_dir = temp_project / 'docs' / 'ja'
        for md_file in ja_dir.glob('*.md'):
            content = md_file.read_text()
            nodes = parser.parse(content, md_file)
            for node in nodes:
                node.doc_language = 'ja'
            target_nodes.extend(nodes)
        
        assert len(source_nodes) > 0
        assert len(target_nodes) > 0
        assert len(source_nodes) > len(target_nodes)  # Some translations missing
        
        # Step 2: Compare
        engine = ComparisonEngine()
        result = engine.compare(source_nodes, target_nodes, 'en', 'ja')
        
        assert result.coverage_stats['overall'] < 1.0  # Not fully translated
        assert result.coverage_stats['overall'] > 0.0  # Some translations exist
        assert len(result.mappings) == len(source_nodes)
        
        # Check mapping types
        mapping_types = [m.mapping_type for m in result.mappings]
        assert 'missing' in mapping_types  # Some missing translations
        assert 'exact' in mapping_types or 'fuzzy' in mapping_types  # Some matches
        
        # Step 3: Export
        exporter = TranslationExporter()
        
        # Export to JSON
        json_path = temp_project / 'export_test.json'
        exporter.export(
            result,
            format='json',
            output_path=json_path,
            options={'include_missing': True, 'include_context': True}
        )
        assert json_path.exists()
        
        # Export to CSV
        csv_path = temp_project / 'export_test.csv'
        exporter.export(
            result,
            format='csv',
            output_path=csv_path,
            options={'include_missing': True}
        )
        assert csv_path.exists()
        
        # Step 4: Import
        importer = TranslationImporter()
        
        # Create simulated translations
        with open(json_path) as f:
            data = json.load(f)
        
        # Modify some translations
        modified_count = 0
        for trans in data['translations']:
            if not trans['target'] and modified_count < 5:
                trans['target'] = f"テスト翻訳: {trans['id'][:8]}"
                modified_count += 1
        
        # Save modified translations
        modified_path = temp_project / 'import_test.json'
        with open(modified_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Import translations
        updated_nodes, stats = importer.import_translations(
            import_path=modified_path,
            format='json',
            target_nodes=target_nodes,
            options={'create_missing': True}
        )
        
        assert stats['total'] > 0
        assert stats['created'] == modified_count
        assert len(updated_nodes) >= len(target_nodes)
        
        # Step 5: Verify HTML report generation
        html_report = result.generate_html_report()
        assert '<html>' in html_report
        assert 'Translation Coverage' in html_report
        assert f"{result.coverage_stats['overall']*100:.1f}%" in html_report
    
    def test_performance_metrics(self, temp_project):
        """Test performance with real documents."""
        parser = MySTParser()
        
        # Parse actual project documentation
        docs_en = Path('docs/en')
        docs_ja = Path('docs/ja')
        
        if not docs_en.exists() or not docs_ja.exists():
            pytest.skip("Real documentation not available")
        
        # Measure parsing performance
        start_time = time.time()
        
        source_nodes = []
        for md_file in docs_en.rglob('*.md'):
            content = md_file.read_text()
            nodes = parser.parse(content, md_file)
            source_nodes.extend(nodes)
        
        parse_time = time.time() - start_time
        
        # Performance assertions
        assert len(source_nodes) > 100  # Substantial number of nodes
        assert parse_time < 5.0  # Should parse in under 5 seconds
        
        # Measure comparison performance
        target_nodes = []
        for md_file in docs_ja.rglob('*.md'):
            if md_file.exists():
                content = md_file.read_text()
                nodes = parser.parse(content, md_file)
                target_nodes.extend(nodes)
        
        engine = ComparisonEngine()
        
        start_time = time.time()
        result = engine.compare(source_nodes, target_nodes, 'en', 'ja')
        compare_time = time.time() - start_time
        
        # Performance assertions
        assert compare_time < 10.0  # Should compare in under 10 seconds
        assert result.coverage_stats['counts']['total'] == len(source_nodes)
        
        # Log performance metrics
        print(f"\nPerformance Metrics:")
        print(f"  Nodes parsed: {len(source_nodes)}")
        print(f"  Parse time: {parse_time:.2f}s")
        print(f"  Compare time: {compare_time:.2f}s")
        print(f"  Nodes/second: {len(source_nodes)/parse_time:.0f}")
    
    def test_error_recovery(self, temp_project):
        """Test error handling and recovery."""
        runner = CliRunner()
        
        # Test with non-existent directory
        result = runner.invoke(app, [
            'compare',
            '/non/existent/path',
            '/another/bad/path'
        ])
        assert result.exit_code != 0
        assert 'Error' in result.output or 'does not exist' in result.output
        
        # Test with invalid format
        result = runner.invoke(app, [
            'export',
            str(temp_project / 'docs' / 'en'),
            str(temp_project / 'docs' / 'ja'),
            str(temp_project / 'output.xyz'),
            '--format', 'invalid'
        ])
        assert result.exit_code != 0
        assert 'Invalid format' in result.output
        
        # Test import with corrupted JSON
        bad_json = temp_project / 'bad.json'
        bad_json.write_text('{"invalid": json content}')
        
        result = runner.invoke(app, [
            'import',
            str(bad_json),
            str(temp_project / 'docs' / 'ja')
        ])
        assert result.exit_code != 0
    
    def test_cache_management(self, temp_project, cache_manager):
        """Test cache directory structure and management."""
        # Verify directory structure
        assert cache_manager.cache_dir.exists()
        assert cache_manager.reports_dir.exists()
        assert cache_manager.config_file.exists()
        
        # Test cache operations
        cache_path = cache_manager.get_cache_path('test', 'en')
        assert cache_path.parent == cache_manager.cache_dir
        assert cache_path.name == 'en_test.db'
        
        # Create dummy cache files
        (cache_manager.cache_dir / 'test1.db').touch()
        (cache_manager.cache_dir / 'test2.db').touch()
        
        # Test cache clearing
        removed = cache_manager.clear_cache()
        assert removed >= 2
        assert not (cache_manager.cache_dir / 'test1.db').exists()
        assert not (cache_manager.cache_dir / 'test2.db').exists()
        
        # Test report path generation
        report_path = cache_manager.get_report_path('test_report.html', timestamp=False)
        assert report_path.parent == cache_manager.reports_dir
        assert report_path.name == 'test_report.html'
        
        # Test config management
        config = cache_manager.get_config()
        assert 'project' in config
        assert config['project']['source_lang'] == 'en'
        assert 'ja' in config['project']['target_langs']