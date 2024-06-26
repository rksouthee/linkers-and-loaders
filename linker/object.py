"""
Defines the type for the object format and the various sections such as segments, symbols and relocations.
"""

from dataclasses import dataclass, field
from typing import Optional

MAGIC_NUMBER = "LINK"


@dataclass
class Segment:
    """
    Segment definition.

    The base is the address where the segment logically starts. The size is the length in bytes of the segment, this
    should match the length of the `data` if "P" is in the flags.
    """

    name: str
    base: int
    size: int
    flags: str
    data: bytes = field(init=False, default=b"")
    oldbase: int = field(init=False, compare=False)

    def __post_init__(self) -> None:
        self.oldbase = self.base

    @property
    def end(self) -> int:
        """
        Return the address of the end of the segment.

        The address is based of the 'base'.

        :return: the end of the segment.
        """
        return self.base + self.size


@dataclass
class Symbol:
    """
    Symbol definition.

    The `seg` field is the segment number relative to which the symbol is defined (0 for absolute or undefined
    symbols).  The `type` is a string of letters that includes D for defined or U for undefined.
    """

    name: str
    value: int
    seg: int
    type: str
    obj: Optional["Object"] = field(init=False, default=None, compare=False)


@dataclass
class Relocation:
    """
    Relocation definition.

    `loc` is the location to be relocated, `seg` is the segment within which the locationis found, `ref` is the segment
    number of symbol number to be relocated there, and `type` is an architecture-dependent relocation type.
    """

    loc: int
    seg: int
    ref: int
    type: str


@dataclass
class Object:
    """
    Object definition.
    """

    name: str
    segs: list[Segment]
    syms: list[Symbol]
    rels: list[Relocation]

    def __post_init__(self) -> None:
        for sym in self.syms:
            sym.obj = self
