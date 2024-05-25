"""
Project 4.3
"""

from collections import defaultdict
from itertools import chain
from operator import attrgetter
from pathlib import Path
from typing import Iterable, Iterator, Literal

import typer

from linker import Object, Segment, Symbol, read_object, write_object, roundup
from linker.errors import LinkError
from linker.utils import SegmentGroup

from .project_4_1 import link_segments


def make_default_groups() -> SegmentGroup:
    """
    Create a SegmentGroup with the core segments.
    """
    return {"text": [".text"], "data": [".data"], "bss": [".bss", ".common"]}


def iter_segs(objs: Iterable[Object]) -> Iterator[Segment]:
    """
    Return an iterator over all the segments.
    """
    for obj in objs:
        yield from obj.segs


def iter_syms(objs: Iterable[Object]) -> Iterator[Symbol]:
    """
    Return an iterator over all the symbols.
    """
    for obj in objs:
        for sym in obj.syms:
            sym.obj = obj
            yield sym


def get_group(flags: str) -> Literal["text", "data", "bss"]:
    """
    Get the group of a segment based on its flags.
    """
    if "P" not in flags:
        return "bss"
    if "W" in flags:
        return "data"
    return "text"


def group_segments_by_name(segs: Iterable[Segment]) -> dict[str, list[Segment]]:
    """
    Group segments by name.
    """
    names = defaultdict(list)
    for seg in segs:
        names[seg.name].append(seg)
    return names


def validate_segment_types(segs: Iterable[Segment], group: str) -> None:
    """
    Validate that the segments are of the correct type.
    """
    for seg in segs:
        if (this_group := get_group(seg.flags)) != group:
            raise LinkError(f"{seg.name} type mismatch (expected {group}, got {this_group})")


def types_from_groups(groups: SegmentGroup) -> Iterator[tuple[str, str]]:
    """
    Yield the segment name and type.
    """
    yield from ((name, "text") for name in groups["text"])
    yield from ((name, "data") for name in groups["data"])
    yield from ((name, "bss") for name in groups["bss"])


def group_segments_by_type(names: dict[str, list[Segment]], groups: SegmentGroup) -> SegmentGroup:
    """
    Group segments by type.
    """
    types = dict(types_from_groups(groups))
    for name, segs in names.items():
        if not segs:
            continue
        if name not in types:
            group = get_group(segs[0].flags)
            types[name] = group
            groups[group].append(name)
        validate_segment_types(segs, types[name])
    return groups


def group_symbols_by_name(syms: Iterable[Symbol]) -> dict[str, list[Symbol]]:
    """
    Group symbols by name.
    """
    symtab = defaultdict(list)
    for sym in syms:
        symtab[sym.name].append(sym)
    return symtab


def partition_symbols(syms: Iterable[Symbol]) -> tuple[list[Symbol], list[Symbol]]:
    """
    Partition symbols in to defined and undefined.

    :param syms: The list of symbols to partition.
    :return: A tuple containing the defined and undefined symbols.
    """
    d, u = [], []
    for sym in syms:
        if "D" in sym.type:
            d.append(sym)
        else:
            u.append(sym)
    return d, u


def reduce_symbol(syms: Iterable[Symbol]) -> Symbol:
    """
    Reduce a list of symbols to a single symbol.

    :param syms: The list of symbols to reduce.
    :return: The reduced symbol.
    """
    d, u = partition_symbols(syms)
    if d:
        if len(d) > 1:
            raise LinkError("multiply defined symbol")
        return d[0]
    if u:
        return max(u, key=attrgetter("value"))
    raise LinkError("undefined symbol")


def reduce_symbols(symtab: dict[str, list[Symbol]]) -> Iterator[tuple[str, Symbol]]:
    """
    Reduce a symbol table.

    :param symtab: The symbol table to reduce.
    :return: An iterator over the reduced symbols.
    """
    for name, syms in symtab.items():
        yield name, reduce_symbol(syms)


def create_common_segment(syms: Iterable[Symbol]) -> Segment:
    """
    Create a common segment from a list of symbols.

    :param syms: The list of symbols.
    :return: The common segment.
    """
    size = 0
    for sym in filter(lambda x: "D" not in x.type, syms):
        size = roundup(size, 0x4) + sym.value
    return Segment(".common", 0, size, "RW")


def create_symbol_table(syms: Iterable[Symbol]) -> dict[str, Symbol]:
    """
    Create a symbol table.

    :param syms: The list of symbols.
    :return: The symbol table.
    """
    return dict(reduce_symbols(group_symbols_by_name(syms)))


def link_group(names: Iterable[str], segs: dict[str, list[Segment]], addr: int, flags: str) -> Iterator[Segment]:
    """
    Link a group of segments.

    :param names: The names of the segments to link.
    :param segs: The segments to link.
    :param addr: The address to link the segments at.
    :param flags: The flags to link the segments with.
    :return: An iterator over the linked segments.
    """
    for name in names:
        addr = roundup(addr, 0x4)
        seg = link_segments(segs, name, addr, flags, 0x4)
        yield seg
        addr += seg.size


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
    return Object(path.stem, segs, [], [])


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
