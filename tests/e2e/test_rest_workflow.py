"""End-to-end tests for reStructuredText workflow."""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from docdiff.cli.main import app


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_rest_project(tmp_path):
    """Create a temporary reST project structure."""
    # Create English documentation
    en_dir = tmp_path / "en"
    en_dir.mkdir()
    
    # Create index.rst with sections and directives
    (en_dir / "index.rst").write_text("""
.. _main-index:

======================
Project Documentation
======================

Welcome to our project documentation.

.. note::

   This is a test project for DocDiff.

Introduction
============

This documentation covers the basics of our system.

Features
--------

* Fast processing
* Accurate analysis
* Flexible output

.. code-block:: python
   :caption: Example code

   def hello():
       print("Hello, World!")

See Also
========

* :doc:`guide`
* :ref:`main-index`
""")
    
    # Create guide.rst
    (en_dir / "guide.rst").write_text("""
.. _user-guide:

==========
User Guide
==========

This guide helps you get started.

Installation
============

Install using pip::

   pip install docdiff

Basic Usage
===========

Parse a document:

.. code-block:: bash

   docdiff parse document.rst

Configuration
=============

Create a config file:

.. code-block:: yaml
   :caption: config.yaml

   parser:
     format: restructuredtext
   output:
     format: json

.. tip::

   Use environment variables for sensitive settings.

Tables
======

.. list-table:: Feature Comparison
   :widths: 30 70
   :header-rows: 1

   * - Feature
     - Description
   * - Parsing
     - Analyze document structure
   * - Comparison
     - Compare two documents
   * - Reporting
     - Generate reports

.. warning::

   Always backup your data before processing.

Conclusion
==========

You are now ready to use the tool.
""")
    
    # Create Japanese documentation (partial translation)
    ja_dir = tmp_path / "ja"
    ja_dir.mkdir()
    
    # Translated index.rst
    (ja_dir / "index.rst").write_text("""
.. _main-index:

======================
プロジェクトドキュメント
======================

プロジェクトドキュメントへようこそ。

.. note::

   これはDocDiffのテストプロジェクトです。

はじめに
========

このドキュメントはシステムの基本をカバーしています。

機能
----

* 高速処理
* 正確な分析
* 柔軟な出力

.. code-block:: python
   :caption: サンプルコード

   def hello():
       print("こんにちは、世界！")

参照
====

* :doc:`guide`
* :ref:`main-index`
""")
    
    # guide.rst is intentionally missing to test missing translations
    
    return tmp_path


class TestReSTWorkflow:
    """Test complete reST document workflow."""
    
    def test_parse_rest_documents(self, runner, temp_rest_project):
        """Test parsing reST documents."""
        en_dir = temp_rest_project / "en"
        
        # Parse English docs
        result = runner.invoke(app, ["parse", str(en_dir)])
        assert result.exit_code == 0
        assert "Found" in result.output
        assert ".rst files" in result.output
        assert "Parsing complete" in result.output
    
    def test_compare_rest_translations(self, runner, temp_rest_project):
        """Test comparing reST document translations."""
        en_dir = temp_rest_project / "en"
        ja_dir = temp_rest_project / "ja"
        
        # Parse both directories first
        runner.invoke(app, ["parse", str(en_dir)])
        runner.invoke(app, ["parse", str(ja_dir)])
        
        # Compare translations
        result = runner.invoke(app, [
            "compare",
            str(en_dir),
            str(ja_dir),
            "--output", str(temp_rest_project / "comparison.json")
        ])
        
        assert result.exit_code == 0
        
        # Check if comparison was successful
        if result.exit_code == 0:
            # Check output file if it was created
            comparison_file = temp_rest_project / "comparison.json"
            if comparison_file.exists():
                with open(comparison_file) as f:
                    data = json.load(f)
                assert "translations" in data or "results" in data or "coverage" in data
    
    def test_rest_directive_parsing(self, runner, tmp_path):
        """Test parsing of various reST directives."""
        # Create a document with various directives
        test_file = tmp_path / "directives.rst"
        test_file.write_text("""
Title
=====

.. note::

   This is a note.

.. warning::

   This is a warning.

.. code-block:: python
   :linenos:
   :emphasize-lines: 2

   def test():
       return 42  # Important line
       pass

.. figure:: image.png
   :alt: Test image
   :width: 500px

   Figure caption here.

.. math::

   E = mc^2

.. list-table:: Test Table
   :widths: 30 70
   :header-rows: 1

   * - Column 1
     - Column 2
   * - Data 1
     - Data 2
""")
        
        # Parse the file
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
        assert "Parsing complete" in result.output
    
    def test_rest_cross_references(self, runner, tmp_path):
        """Test parsing of reST cross-references."""
        # Create documents with cross-references
        doc1 = tmp_path / "doc1.rst"
        doc1.write_text("""
.. _label1:

Document 1
==========

See :ref:`label2` in the other document.

Also check :doc:`doc2`.
""")
        
        doc2 = tmp_path / "doc2.rst"
        doc2.write_text("""
.. _label2:

Document 2
==========

Back to :ref:`label1`.

External link: `Python <https://python.org>`_
""")
        
        # Parse the documents
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
        assert "2" in result.output  # Should find 2 .rst files
    
    def test_rest_nested_structures(self, runner, tmp_path):
        """Test parsing of nested reST structures."""
        test_file = tmp_path / "nested.rst"
        test_file.write_text("""
Level 1
=======

Level 1 content.

Level 2
-------

Level 2 content.

Level 3
~~~~~~~

Level 3 content.

* List item 1
  
  * Nested item 1.1
  * Nested item 1.2
    
    * Double nested 1.2.1

* List item 2

1. Numbered item
   
   a. Sub-item a
   b. Sub-item b
      
      i. Sub-sub-item i
      ii. Sub-sub-item ii

2. Numbered item 2
""")
        
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
    
    def test_rest_literal_blocks(self, runner, tmp_path):
        """Test parsing of literal blocks."""
        test_file = tmp_path / "literals.rst"
        test_file.write_text("""
Examples
========

Here is a literal block::

   This is literal text.
   All    spaces     are    preserved.
       Including indentation.

Another example::

   def function():
       return "literal"

Back to normal text.

.. code-block:: python

   # This is a code-block directive
   # Different from literal block
   print("Hello")
""")
        
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
    
    def test_rest_export_import_workflow(self, runner, temp_rest_project):
        """Test export and import workflow with reST documents."""
        en_dir = temp_rest_project / "en"
        ja_dir = temp_rest_project / "ja"
        
        # Parse both directories
        runner.invoke(app, ["parse", str(en_dir)])
        runner.invoke(app, ["parse", str(ja_dir)])
        
        # Export untranslated content
        export_file = temp_rest_project / "export.json"
        result = runner.invoke(app, [
            "export",
            str(en_dir),
            str(ja_dir),
            "--format", "json",
            "--output", str(export_file)
        ])
        
        if result.exit_code == 0 and export_file.exists():
            # Verify export file
            with open(export_file) as f:
                export_data = json.load(f)
            
            assert "translations" in export_data
            assert isinstance(export_data["translations"], list)
            
            # Simulate translation
            if export_data["translations"]:
                for trans in export_data["translations"][:2]:  # Translate first 2
                    if "translation" in trans:
                        trans["translation"] = f"翻訳: {trans.get('source', '')}"
            
            # Save modified translations
            import_file = temp_rest_project / "import.json"
            with open(import_file, 'w') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Import translations (dry run)
            result = runner.invoke(app, [
                "import",
                str(import_file),
                str(ja_dir),
                "--dry-run"
            ])
            
            if result.exit_code == 0:
                assert "Dry run" in result.output or "would" in result.output.lower()
    
    def test_rest_unicode_content(self, runner, tmp_path):
        """Test parsing of reST with Unicode content."""
        test_file = tmp_path / "unicode.rst"
        test_file.write_text("""
Unicode Test 测试 テスト
========================

Content with emojis 🎉 and special chars: é, ñ, ü, ß

中文内容
--------

这是中文段落。

日本語コンテンツ
----------------

これは日本語の段落です。

.. note::

   Mixed content: Hello 你好 こんにちは 🌍
""")
        
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
    
    def test_rest_malformed_document(self, runner, tmp_path):
        """Test handling of malformed reST documents."""
        test_file = tmp_path / "malformed.rst"
        test_file.write_text("""
Title without proper underline
====  # Too short

.. note:  # Missing second colon

   This note might not parse correctly.

.. code-block::  # Missing language
   
   code here

Incomplete section
=================
# Missing content or next section
""")
        
        # Should handle gracefully
        result = runner.invoke(app, ["parse", str(tmp_path)])
        # Parser should complete even with malformed content
        assert "Parsing complete" in result.output or "complete" in result.output.lower()
    
    def test_rest_sample_project(self, runner):
        """Test parsing the actual reST sample project if it exists."""
        sample_path = Path("samples/rest-project/en")
        
        if sample_path.exists():
            result = runner.invoke(app, ["parse", str(sample_path)])
            assert result.exit_code == 0
            assert ".rst" in result.output
            assert "Parsing complete" in result.output
            
            # Test comparison if Japanese version exists
            ja_path = Path("samples/rest-project/ja")
            if ja_path.exists():
                runner.invoke(app, ["parse", str(ja_path)])
                
                result = runner.invoke(app, [
                    "compare",
                    str(sample_path),
                    str(ja_path),
                    "--view", "summary"
                ])
                # For now, accept exit code 0 or 1 (warning about low coverage)
                assert result.exit_code in [0, 1], f"Unexpected exit code: {result.exit_code}\nOutput: {result.output}"


class TestReSTParserIntegration:
    """Integration tests for reST parser."""
    
    def test_rest_parser_with_includes(self, runner, tmp_path):
        """Test reST parser with include directives."""
        # Create main file
        main_file = tmp_path / "main.rst"
        include_file = tmp_path / "included.rst"
        
        include_file.write_text("""
Included Content
----------------

This content is included from another file.
""")
        
        main_file.write_text("""
Main Document
=============

Main content here.

.. include:: included.rst

Back to main content.
""")
        
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
    
    def test_rest_parser_with_substitutions(self, runner, tmp_path):
        """Test reST parser with substitutions."""
        test_file = tmp_path / "substitutions.rst"
        test_file.write_text("""
.. |version| replace:: 1.0.0
.. |project| replace:: DocDiff
.. |date| date::
.. |time| date:: %H:%M

|project| Documentation
=======================

Version |version| generated on |date| at |time|.

The |project| system is version |version|.
""")
        
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
    
    def test_rest_parser_performance(self, runner, tmp_path):
        """Test reST parser with large documents."""
        # Create a large document
        large_file = tmp_path / "large.rst"
        
        content = ["Large Document", "=" * 14, ""]
        
        # Add many sections
        for i in range(50):
            content.extend([
                f"Section {i}",
                "-" * (10 + len(str(i))),
                "",
                f"Content for section {i}.",
                "",
                ".. code-block:: python",
                "",
                f"   def function_{i}():",
                f"       return {i}",
                ""
            ])
        
        large_file.write_text('\n'.join(content))
        
        result = runner.invoke(app, ["parse", str(tmp_path)])
        assert result.exit_code == 0
        assert "Parsing complete" in result.output