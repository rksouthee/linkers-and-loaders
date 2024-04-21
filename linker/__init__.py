"""
Functions for parsing and dumping `Object`s.
"""

from .object import Object
from .parser import parse_object_from_lines
from .writer import dump_object

__all__ = (
    "Object",
    "parse_object_from_lines",
    "dump_object",
)
