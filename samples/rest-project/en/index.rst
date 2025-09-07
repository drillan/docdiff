.. _main-index:

====================================
Technical Documentation Sample
====================================

Welcome to our technical documentation sample project. This documentation
demonstrates various reStructuredText features and serves as a test suite
for documentation parsing and translation tracking.

.. note::

   This is a sample project designed to test the docdiff tool's
   reStructuredText parsing capabilities.

.. _index-introduction:

Introduction
============

This documentation covers:

* Basic reStructuredText syntax
* Advanced formatting features
* API documentation structure
* Cross-referencing capabilities

.. _index-getting-started:

Getting Started
===============

To begin using this documentation:

1. Read the :doc:`quickstart` guide
2. Explore :doc:`advanced` features
3. Check the :doc:`api/index` for detailed reference

.. tip::

   Use the search function to quickly find specific topics.

.. _index-project-overview:

Project Overview
================

.. _index-architecture:

Architecture
------------

Our system follows a modular architecture:

.. code-block:: text

   ┌─────────────┐     ┌─────────────┐
   │   Parser    │────▶│  Analyzer   │
   └─────────────┘     └─────────────┘
          │                    │
          ▼                    ▼
   ┌─────────────┐     ┌─────────────┐
   │   Storage   │     │   Reporter  │
   └─────────────┘     └─────────────┘

.. _index-key-features:

Key Features
------------

The system provides:

* **Fast Processing**: Optimized parsing algorithms
* **Accurate Analysis**: Comprehensive structure detection
* **Flexible Output**: Multiple export formats
* **Translation Support**: Multi-language documentation

.. _system-requirements:

System Requirements
===================

.. _index-minimum-requirements:

Minimum Requirements
--------------------

.. list-table:: System Requirements
   :widths: 30 70
   :header-rows: 1

   * - Component
     - Requirement
   * - Python
     - 3.8 or higher
   * - Memory
     - 4GB RAM minimum
   * - Storage
     - 100MB free space
   * - OS
     - Linux, macOS, or Windows

.. _index-installation:

Installation
------------

Install using pip::

   pip install docdiff

Or using conda::

   conda install -c conda-forge docdiff

.. _index-quick-example:

Quick Example
=============

Here's a simple example of parsing a document:

.. code-block:: python
   :caption: Basic usage example
   :linenos:

   from docdiff import Parser
   
   # Initialize parser
   parser = Parser()
   
   # Parse document
   with open('document.rst', 'r') as f:
       content = f.read()
   
   nodes = parser.parse(content)
   
   # Process nodes
   for node in nodes:
       print(f"{node.type}: {node.content[:50]}...")

.. _index-mathematical-expressions:

Mathematical Expressions
========================

The parser supports mathematical notation:

.. math::

   E = mc^2

For inline math, use :math:`\alpha + \beta = \gamma`.

More complex equations:

.. math::
   :name: eq:gaussian

   f(x) = \frac{1}{\sigma\sqrt{2\pi}} 
          e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}

.. _index-see-also:

See Also
========

* :ref:`system-requirements`
* :ref:`index-getting-started`
* :ref:`index-project-overview`
* :doc:`quickstart`
* :doc:`advanced`
* :doc:`api/index`

.. _index-external-resources:

External Resources
------------------

* `reStructuredText Documentation <https://docutils.sourceforge.io/rst.html>`_
* `Sphinx Documentation <https://www.sphinx-doc.org/>`_

.. _index-contact:

Contact
=======

For questions or support:

* Email: support@example.com
* GitHub: https://github.com/example/project

.. footer::

   Copyright 2024 Example Corp. All rights reserved.