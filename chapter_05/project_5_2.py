"""
Project 5.2
"""

from itertools import chain
from pathlib import Path
from typing import Iterable

import typer
from linker import Object, Segment, Symbol, read_object, roundup, write_object

from chapter_04.project_4_3 import (
    create_common_segment,
    create_symbol_table,
    group_segments_by_name,
    group_segments_by_type,
    iter_segs,
    iter_syms,
    make_default_groups,
    link_group,
)


def find_seg_index(segs: Iterable[Segment], name: str) -> int:
    """
    Find the index of a segment by name.

    :param segs: The segments.
    :param name: The name of the segment.
    :return: The index of the segment.
    """
    for idx, seg in enumerate(segs):
        if seg.name == name:
            return idx
    return -1


def resolve_sym(sym: Symbol, segs: list[Segment]) -> None:
    """
    Resolve a symbol.

    :param sym: The symbol to resolve.
    :param segs: The segments.
    """
    assert sym.obj is not None
    seg = sym.obj.segs[sym.seg]
    offset = seg.base - seg.oldbase
    sym.value += offset
    sym.seg = find_seg_index(segs, seg.name)


def resolve_symbols(syms: Iterable[Symbol], segs: list[Segment]) -> None:
    """
    Resolve all the symbols.

    :param syms: The symbols.
    :param segs: The segments.
    """
    for sym in filter(lambda sym: "D" in sym.type, syms):
        resolve_sym(sym, segs)


def link(objs: list[Object], path: Path) -> Object:
    """
    Link a list of objects.

    :param objs: The list of objects to link.
    :param path: The path to write the linked object to.
    :return: The linked object.
    """
    symtab = create_symbol_table(iter_syms(objs))
    names = group_segments_by_name(chain(iter_segs(objs), [create_common_segment(symtab.values())]))
    types = group_segments_by_type(names, make_default_groups())
    segs: list[Segment] = []
    segs.extend(link_group(types["text"], names, 0x1000, "RP"))
    segs.extend(link_group(types["data"], names, roundup(segs[-1].end, 0x1000), "RWP"))
    segs.extend(link_group(types["bss"], names, segs[-1].end, "RW"))
    resolve_symbols(symtab.values(), segs)
    return Object(path.stem, segs, list(symtab.values()), [])


if __name__ == "__main__":  # pragma: no cover

    def main(inputs: list[Path], output: Path) -> None:
        """
        Link a list of objects.

        :param inputs: The list of objects to link.
        :param output: The path to write the linked object to.
        """
        objs = map(read_object, inputs)
        obj = link(list(objs), output)
        write_object(obj, output)

    typer.run(main)
