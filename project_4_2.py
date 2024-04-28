"""
Project 4.2
"""

from collections import defaultdict
from typing import Iterable

import typer

from linker import Object, roundup
from project_4_1 import main, _link_segments, _group_segments
import project_4_1


def _find_common_block_syms(objects: Iterable[Object]) -> dict[str, int]:
    """
    Find all undefined symbols.

    :param objects: a sequence of objects to can for undefined symbols.
    :return: a dictionary of symbol names to common block size.
    """
    common_blocks: dict[str, int] = defaultdict(int)
    for obj in objects:
        for sym in obj.syms:
            if sym.type == "U" and sym.value > 0:
                common_blocks[sym.name] = max(common_blocks[sym.name], sym.value)
    return common_blocks


def _calculate_common_block_size(objects: Iterable[Object], size: int, alignment: int) -> int:
    """
    Calculate the common block size for the objects.

    :param objects: a sequence of objects to scan for undefined symbols.
    :param size: base size to start from.
    :param alignment: object alignment.
    :return: the new size.
    """
    for value in _find_common_block_syms(objects).values():
        size = roundup(size, alignment)
        size += value
    return size


def link(objects: list[Object], name: str) -> Object:
    """
    Link objects together.

    :param objects: list of input objects.
    :param name: name of the output object.
    :return: the linked object.
    """
    segments = _group_segments(objects)
    text = _link_segments(segments, ".text", 0x1000, "R", 0x4)
    data = _link_segments(segments, ".data", roundup(text.base + text.size, 0x1000), "RW", 0x4)
    bss = _link_segments(segments, ".bss", roundup(data.base + data.size, 0x4), "RW", 0x4)
    bss.size = _calculate_common_block_size(objects, bss.size, 0x4)
    return Object(name, [text, data, bss], [], [])


if __name__ == "__main__":
    project_4_1.link = link
    typer.run(main)
