"""
Project 4.1
"""

import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import typer

from linker import Object, Segment, roundup, read_object, write_object
from linker.errors import LinkError


def _group_segments(objects: Iterable[Object]) -> dict[str, list[Segment]]:
    """
    Group segments by name.

    :param objects: a sequence of objects to get segments from.
    :return: a dictionary where the key is the segment name and the value a list of segments.
    """
    segments = defaultdict(list)
    for obj in objects:
        for seg in obj.segs:
            segments[seg.name].append(seg)
    return segments


def _link_segments(segments: dict[str, list[Segment]], name: str, base: int, flags: str, alignment: int) -> Segment:
    """
    Link segments together.

    :param segments: a dictionary of names to segments.
    :param name: name of the segments to link together.
    :param base: the base address of the segment.
    :param flags: the segment flags.
    :param alignment: the alignment of the combined segments.
    :return: the linked segment.
    """
    result = Segment(name, base, 0, flags)
    for segment in segments[name]:
        result.size = roundup(result.size, alignment)
        segment.base = result.base + result.size
        result.size += segment.size
    return result


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
    return Object(name, [text, data, bss], [], [])


def main(infiles: list[Path], outfile: Path) -> None:
    """
    Link objects together to a linked object file.

    :param infiles: list of paths to object files.
    :param outfile: path to the output file.
    """
    try:
        objects = list(map(read_object, infiles))
        write_object(link(objects, outfile.stem), outfile)
    except (LinkError, FileNotFoundError) as err:
        sys.exit(str(err))


if __name__ == "__main__":
    typer.run(main)
