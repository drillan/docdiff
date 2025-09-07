.. _quickstart-guide:

===============
Quick Start Guide
===============

This guide covers the essential features you need to get started quickly.
Follow along to learn the basics of our system.

.. contents:: Table of Contents
   :local:
   :depth: 2

.. _quickstart-installation:

Installation
============

.. _quickstart-prerequisites:

Prerequisites
-------------

Before installing, ensure you have:

* Python 3.8 or higher
* pip package manager
* Git (for development installation)

.. _quickstart-basic-installation:

Basic Installation
------------------

The simplest way to install is via pip::

   pip install docdiff

To verify the installation::

   docdiff --version

.. _quickstart-development-installation:

Development Installation
------------------------

For development work, clone and install in editable mode:

.. code-block:: bash
   :caption: Development setup
   :emphasize-lines: 3

   git clone https://github.com/example/docdiff.git
   cd docdiff
   pip install -e .  # This is the important line
   
.. _quickstart-configuration:

Configuration
=============

.. _quickstart-initial-setup:

Initial Setup
-------------

Create a configuration file:

.. code-block:: yaml
   :caption: config.yaml
   :name: basic-config

   # Basic configuration
   parser:
     format: restructuredtext
     strict: false
   
   output:
     format: json
     pretty: true
   
   cache:
     enabled: true
     directory: ~/.docdiff/cache

.. _quickstart-environment-variables:

Environment Variables
---------------------

You can also use environment variables:

.. list-table:: Environment Variables
   :widths: 25 25 50
   :header-rows: 1

   * - Variable
     - Default
     - Description
   * - DOCDIFF_CONFIG
     - ./config.yaml
     - Path to configuration file
   * - DOCDIFF_CACHE
     - ~/.docdiff
     - Cache directory location
   * - DOCDIFF_LOG_LEVEL
     - INFO
     - Logging level (DEBUG, INFO, WARNING, ERROR)

.. _quickstart-basic-usage:

Basic Usage
===========

.. _quickstart-parsing-documents:

Parsing Documents
-----------------

Parse a single document::

   docdiff parse document.rst

Parse a directory::

   docdiff parse /path/to/docs/

.. note::

   The parser automatically detects the document format based on
   file extension (.rst for reStructuredText, .md for Markdown).

.. _quickstart-comparing-documents:

Comparing Documents
-------------------

Compare two versions:

.. code-block:: bash

   docdiff compare old.rst new.rst

Compare directories:

.. code-block:: bash

   docdiff compare docs/v1/ docs/v2/

.. _quickstart-working-with-lists:

Working with Lists
==================

.. _quickstart-bullet-lists:

Bullet Lists
------------

Simple bullet list:

* First item
* Second item
* Third item with a longer description
  that spans multiple lines
* Fourth item

Nested bullet list:

* Main item 1

  * Sub-item 1.1
  * Sub-item 1.2
  
* Main item 2

  * Sub-item 2.1
    
    * Sub-sub-item 2.1.1
    * Sub-sub-item 2.1.2

.. _quickstart-numbered-lists:

Numbered Lists
--------------

Simple numbered list:

1. First step
2. Second step
3. Third step

With sub-items:

1. Preparation

   a. Gather materials
   b. Read instructions
   c. Set up workspace

2. Execution

   a. Follow step-by-step guide
   b. Monitor progress
   c. Make adjustments as needed

3. Cleanup

   a. Store tools
   b. Document results

.. _quickstart-definition-lists:

Definition Lists
----------------

Parser
    A component that analyzes document structure

Analyzer
    Processes parsed nodes to extract information

Reporter
    Generates human-readable output from analysis

.. _quickstart-code-examples:

Code Examples
=============

.. _quickstart-inline-code:

Inline Code
-----------

Use ``inline code`` for short snippets like ``variable_name`` or ``function()``.

.. _quickstart-code-blocks:

Code Blocks
-----------

Python example:

.. code-block:: python
   :linenos:
   :emphasize-lines: 4,5

   def fibonacci(n):
       """Calculate nth Fibonacci number."""
       if n <= 1:
           return n  # Base case
       return fibonacci(n-1) + fibonacci(n-2)  # Recursive case
   
   # Example usage
   for i in range(10):
       print(f"F({i}) = {fibonacci(i)}")

JavaScript example:

.. code-block:: javascript
   :caption: async-example.js

   async function fetchData(url) {
       try {
           const response = await fetch(url);
           const data = await response.json();
           return data;
       } catch (error) {
           console.error('Error:', error);
           throw error;
       }
   }

.. _quickstart-literal-blocks:

Literal Blocks
--------------

Simple literal block using double colon::

   This is a literal block.
   All whitespace is preserved.
       Including indentation.

.. _quickstart-admonitions:

Admonitions
===========

.. _quickstart-information-notes:

Information Notes
-----------------

.. note::

   This is a note providing additional information that might be
   helpful but isn't critical to understanding.

.. tip::

   Here's a helpful tip that can save you time or improve your workflow.

.. _quickstart-warnings-and-cautions:

Warnings and Cautions
---------------------

.. warning::

   This is a warning about potential issues or problems you might encounter.

.. caution::

   Exercise caution when performing this operation as it may have
   unintended consequences.

.. danger::

   This action is dangerous and could result in data loss or system damage.

.. _quickstart-other-admonitions:

Other Admonitions
-----------------

.. important::

   This information is important for proper system operation.

.. attention::

   Pay special attention to this information.

.. hint::

   This might help you solve a common problem.

.. error::

   This describes an error condition and how to resolve it.

.. _quickstart-tables:

Tables
======

.. _quickstart-simple-table:

Simple Table
------------

.. table:: Feature Comparison
   :widths: auto

   ===============  =========  =========  =========
   Feature          Basic      Pro        Enterprise
   ===============  =========  =========  =========
   Users            5          50         Unlimited
   Storage          10GB       100GB      1TB
   Support          Email      Phone      24/7
   API Access       No         Yes        Yes
   Custom Domain    No         Yes        Yes
   ===============  =========  =========  =========

.. _quickstart-csv-table:

CSV Table
---------

.. csv-table:: Performance Metrics
   :header: "Operation", "Time (ms)", "Memory (MB)", "CPU (%)"
   :widths: 30, 20, 20, 20

   "Parse", "45", "12.3", "25"
   "Analyze", "120", "45.6", "60"
   "Generate", "30", "8.9", "15"
   "Export", "15", "5.2", "10"

.. _quickstart-list-table:

List Table
----------

.. list-table:: Command Options
   :widths: 15 30 55
   :header-rows: 1
   :stub-columns: 1

   * - Option
     - Type
     - Description
   * - -v, --verbose
     - flag
     - Enable verbose output
   * - -o, --output
     - string
     - Specify output file path
   * - -f, --format
     - choice
     - Output format (json, yaml, xml)
   * - --config
     - path
     - Path to configuration file

.. _quickstart-cross-references:

Cross-References
================

.. _quickstart-internal-links:

Internal Links
--------------

* See the :ref:`quickstart-guide` (this page)
* Check :ref:`basic-config` for configuration details
* Review :ref:`main-index` for the complete index

.. _quickstart-document-links:

Document Links
--------------

* Read the :doc:`index` page
* Explore :doc:`advanced` features
* API documentation in :doc:`api/index`

.. _quickstart-footnotes:

Footnotes
=========

This is a sentence with a footnote [#f1]_.

You can also use numbered footnotes [#]_ which are automatically numbered.

Citations are similar but use a different syntax [CIT2024]_.

.. [#f1] This is the footnote text that appears at the bottom.

.. [#] This footnote is automatically numbered.

.. [CIT2024] Example Citation, "Title of Work", 2024.

.. _quickstart-images-and-figures:

Images and Figures
==================

.. _quickstart-simple-image:

Simple Image
------------

.. image:: _static/diagram.png
   :alt: System Architecture Diagram
   :width: 400px
   :align: center

.. _quickstart-figure-with-caption:

Figure with Caption
-------------------

.. figure:: _static/diagram.png
   :alt: Detailed system architecture
   :width: 500px
   :align: center
   :name: fig-architecture

   **Figure 1:** Complete system architecture showing all components
   and their interactions. Notice the bidirectional data flow.

.. _quickstart-substitutions:

Substitutions
=============

.. |project| replace:: DocDiff
.. |version| replace:: 1.0.0
.. |date| date::

This documentation is for |project| version |version|, generated on |date|.

.. _quickstart-raw-output:

Raw Output
==========

.. raw:: html

   <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
       <strong>HTML Note:</strong> This content is only visible in HTML output.
   </div>

.. _quickstart-include-files:

Include Files
=============

You can include other files:

.. commented out as the file doesn't exist
   .. include:: ../README.rst
      :start-line: 10
      :end-line: 20

.. _quickstart-summary:

Summary
=======

You've now learned the basics of:

1. Installation and configuration
2. Basic document operations
3. Various text formatting options
4. Code blocks and examples
5. Tables and lists
6. Cross-references and links
7. Admonitions and notes

.. _quickstart-next-steps:

Next Steps
----------

* Try the :doc:`advanced` guide for more features
* Explore the :doc:`api/reference` for detailed API documentation
* Join our community forum for support

----

*Last updated: January 2024*