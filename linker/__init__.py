"""
Functions for parsing and dumping `Object`s.
"""

from .object import Object, Segment
from .utils import read_object, write_object, roundup

__all__ = ("Object", "Segment", "read_object", "write_object", "roundup")
