"""Sphinx-specific features for docdiff.

This module provides functionality for integrating with Sphinx documentation projects,
including glossary extraction, cross-reference tracking, and internationalization support.
"""

from .glossary import GlossaryExtractor, GlossaryTerm, TermReference
from .project import SphinxProject, detect_sphinx_project
from .references import Reference, ReferenceDatabase, ReferenceType

__all__ = [
    "GlossaryExtractor",
    "GlossaryTerm",
    "TermReference",
    "SphinxProject",
    "detect_sphinx_project",
    "Reference",
    "ReferenceDatabase",
    "ReferenceType",
]
