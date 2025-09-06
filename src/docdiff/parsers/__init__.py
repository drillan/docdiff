"""Document parsers for docdiff."""

from docdiff.parsers.base import BaseParser
from docdiff.parsers.myst import MySTParser
from docdiff.parsers.rest import ReSTParser

__all__ = ["BaseParser", "MySTParser", "ReSTParser"]
