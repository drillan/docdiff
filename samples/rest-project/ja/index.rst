.. _main-index:

====================================
技術ドキュメントサンプル
====================================

技術ドキュメントのサンプルプロジェクトへようこそ。このドキュメントは
様々なreStructuredText機能を実演し、ドキュメント解析と翻訳追跡のための
テストスイートとして機能します。

.. note::

   これはdocdiffツールのreStructuredText解析機能をテストするために
   設計されたサンプルプロジェクトです。

.. _index-introduction:

はじめに
========

このドキュメントでは以下をカバーしています：

* 基本的なreStructuredText構文
* 高度なフォーマット機能
* APIドキュメント構造
* 相互参照機能

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

主な機能
--------

システムは以下を提供します：

* **高速処理**: 最適化された解析アルゴリズム
* **正確な分析**: 包括的な構造検出
* **柔軟な出力**: 複数のエクスポート形式
* **翻訳サポート**: 多言語ドキュメント

.. _system-requirements:

システム要件
============

.. _index-minimum-requirements:

最小要件
--------

.. list-table:: システム要件
   :widths: 30 70
   :header-rows: 1

   * - コンポーネント
     - 要件
   * - Python
     - 3.8以上
   * - メモリ
     - 最小4GB RAM
   * - ストレージ
     - 100MBの空き容量
   * - OS
     - Linux、macOS、またはWindows

.. _index-installation:

インストール
------------

pipを使用したインストール::

   pip install docdiff

またはcondaを使用::

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

関連項目
========

* :ref:`system-requirements`
* :ref:`index-getting-started`
* :ref:`index-project-overview`
* :doc:`quickstart`
* :doc:`advanced`
* :doc:`api/index`

.. _index-external-resources:

外部リソース
------------

* `reStructuredTextドキュメント <https://docutils.sourceforge.io/rst.html>`_
* `Sphinxドキュメント <https://www.sphinx-doc.org/>`_

.. _index-contact:

お問い合わせ
============

ご質問やサポートについて：

* メール: support@example.com
* GitHub: https://github.com/example/project

.. footer::

   Copyright 2024 Example Corp. All rights reserved.