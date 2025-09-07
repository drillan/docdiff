================================
reStructuredText Sample Project
================================

This sample project demonstrates docdiff's support for reStructuredText documentation.
It includes various reST features and serves as a test suite for the ReSTParser.

Project Structure
=================

.. code-block:: text

   rest-project/
   ├── README.rst          # This file
   ├── en/                 # English documentation
   │   ├── index.rst      # Main page
   │   ├── quickstart.rst # Basic reST features
   │   ├── advanced.rst   # Advanced features
   │   ├── api/           # Nested structure
   │   │   ├── index.rst
   │   │   └── reference.rst
   │   └── _static/       # Static files
   │       └── diagram.png
   └── ja/                # Japanese translations
       ├── index.rst      # Partial translation
       └── quickstart.rst # Full translation

Features Covered
================

Basic Elements
--------------

* Multi-level sections with labels
* Paragraphs and line blocks
* Bullet and numbered lists
* Literal blocks and inline code

Directives
----------

* ``code-block`` with various languages
* ``figure`` and ``image``
* Admonitions (note, warning, tip, etc.)
* ``math`` for mathematical expressions
* ``toctree`` for document structure

Advanced Features
-----------------

* Cross-references (``:ref:``, ``:doc:``)
* Footnotes and citations
* Tables (list-table, csv-table)
* Include directive
* Substitutions

Testing docdiff
===============

Parse the Project
-----------------

.. code-block:: bash

   # Parse the English documentation
   docdiff parse samples/rest-project/en

   # Parse the Japanese documentation
   docdiff parse samples/rest-project/ja

Compare Translations
--------------------

.. code-block:: bash

   # Compare English and Japanese versions
   docdiff compare samples/rest-project/en samples/rest-project/ja

   # Generate a detailed report
   docdiff compare samples/rest-project/en samples/rest-project/ja \
       --format detailed --output report.md

Export for Translation
-----------------------

.. code-block:: bash

   # Export untranslated content
   docdiff export samples/rest-project/en samples/rest-project/ja \
       --format json --output tasks.json

Expected Results
================

The ReSTParser should correctly identify:

1. **Sections**: All heading levels with proper hierarchy
2. **Code Blocks**: Both literal blocks (``::`` ) and ``code-block`` directives
3. **Admonitions**: Various types with their content
4. **Figures**: With captions and metadata
5. **Cross-references**: Labels and targets

Translation Tracking
--------------------

The comparison should show:

* Fully translated documents (``quickstart.rst``)
* Partially translated documents (``index.rst``)
* Missing translations (``advanced.rst``, ``api/*``)

Notes
=====

.. note::

   This sample project uses a subset of reStructuredText features
   that are most commonly used in technical documentation.

.. warning::

   Some advanced Sphinx-specific directives may not be fully
   supported by the basic ReSTParser implementation.