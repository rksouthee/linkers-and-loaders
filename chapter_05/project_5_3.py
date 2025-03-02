"""
Project 5.3
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
    link_group,
    make_default_groups,
)
from .project_5_2 import find_seg_index, resolve_symbols


def resolve_common_symbols(syms: Iterable[Symbol], seg: Segment, index: int) -> None:
    """
    Resolve common symbols.

    This function will resolve common symbols by assigning them to the next available address in the common segment.

    :param syms: An iterable of symbols.
    :param seg: The common segment.
    :param index: The index of the common segment.
    """
    addr = seg.base
    for sym in filter(lambda sym: "U" in sym.type, syms):
        size = sym.value
        sym.value = roundup(addr, 0x4)
        sym.seg = index
        sym.type = "D"
        addr += size
        assert addr <= seg.end


def link(objs: list[Object], path: Path) -> Object:
    """
    Link a list of objects.

    :param objs: The list of objects to link.
    :param path: The path to write the linked object to.
    :return: The linked object.
    """
    symtab = create_symbol_table(iter_syms(objs))
    common_seg = create_common_segment(symtab.values())
    names = group_segments_by_name(chain(iter_segs(objs), [common_seg]))
    types = group_segments_by_type(names, make_default_groups())
    segs: list[Segment] = []
    segs.extend(link_group(types["text"], names, 0x1000, "RP"))
    segs.extend(link_group(types["data"], names, roundup(segs[-1].end, 0x1000), "RWP"))
    segs.extend(link_group(types["bss"], names, segs[-1].end, "RW"))
    resolve_symbols(symtab.values(), segs)
    resolve_common_symbols(
        symtab.values(), common_seg, find_seg_index(segs, common_seg.name)
    )
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
