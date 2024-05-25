from collections import defaultdict
from itertools import chain
from operator import attrgetter
from pathlib import Path
from typing import Iterable, Iterator, Literal, TypedDict

import typer

from linker import Object, Segment, Symbol, read_object, write_object, roundup
from linker.errors import LinkError

from .project_4_1 import link_segments


class SegmentGroup(TypedDict):
    text: list[str]
    data: list[str]
    bss: list[str]


def make_default_groups() -> SegmentGroup:
    return {"text": [".text"], "data": [".data"], "bss": [".bss", ".common"]}


def iter_segs(objs: Iterable[Object]) -> Iterator[Segment]:
    for obj in objs:
        yield from obj.segs


def iter_syms(objs: Iterable[Object]) -> Iterator[Symbol]:
    for obj in objs:
        yield from obj.syms


def get_group(flags: str) -> Literal["text", "data", "bss"]:
    if "P" not in flags:
        return "bss"
    if "W" in flags:
        return "data"
    return "text"


def group_segments_by_name(segs: Iterable[Segment]) -> dict[str, list[Segment]]:
    names = defaultdict(list)
    for seg in segs:
        names[seg.name].append(seg)
    return names


def validate_segment_types(segs: Iterable[Segment], group: str) -> None:
    for seg in segs:
        if (this_group := get_group(seg.flags)) != group:
            raise LinkError(
                f"{seg.name} type mismatch (expected {group}, got {this_group})"
            )


def types_from_groups(groups: SegmentGroup) -> Iterator[tuple[str, str]]:
    yield from ((name, "text") for name in groups["text"])
    yield from ((name, "data") for name in groups["data"])
    yield from ((name, "bss") for name in groups["bss"])


def group_segments_by_type(names: dict[str, list[Segment]], groups: SegmentGroup) -> SegmentGroup:
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
    symtab = defaultdict(list)
    for sym in syms:
        symtab[sym.name].append(sym)
    return symtab


def partition_symbols(syms: Iterable[Symbol]) -> tuple[list[Symbol], list[Symbol]]:
    d, u = [], []
    for sym in syms:
        if "D" in sym.type:
            d.append(sym)
        else:
            u.append(sym)
    return d, u


def reduce_symbol(syms: Iterable[Symbol]) -> Symbol:
    d, u = partition_symbols(syms)
    if d:
        if len(d) > 1:
            raise LinkError("multiply defined symbol")
        return d[0]
    if u:
        return max(u, key=attrgetter("value"))
    raise LinkError("undefined symbol")


def reduce_symbols(symtab: dict[str, list[Symbol]]) -> Iterator[tuple[str, Symbol]]:
    for name, syms in symtab.items():
        yield name, reduce_symbol(syms)


def create_common_segment(syms: Iterable[Symbol]) -> Segment:
    size = 0
    for sym in filter(lambda x: "D" not in x.type, syms):
        size = roundup(size, 0x4) + sym.value
    return Segment(".common", 0, size, "RW")


def create_symbol_table(syms: Iterable[Symbol]) -> dict[str, Symbol]:
    return dict(reduce_symbols(group_symbols_by_name(syms)))


def link_group(
    names: Iterable[str], segs: dict[str, list[Segment]], addr: int, flags: str
) -> Iterator[Segment]:
    for name in names:
        addr = roundup(addr, 0x4)
        seg = link_segments(segs, name, addr, flags, 0x4)
        yield seg
        addr += seg.size


def link(objs: list[Object], path: Path) -> Object:
    symtab = create_symbol_table(iter_syms(objs))
    names = group_segments_by_name(
        chain(iter_segs(objs), [create_common_segment(symtab.values())])
    )
    types = group_segments_by_type(names, make_default_groups())
    segs: list[Segment] = []
    segs.extend(link_group(types["text"], names, 0x1000, "RP"))
    segs.extend(link_group(types["data"], names, roundup(segs[-1].end, 0x1000), "RWP"))
    segs.extend(link_group(types["bss"], names, segs[-1].end, "RW"))
    return Object(path.stem, segs, [], [])


if __name__ == "__main__":  # pragma: no cover

    def main(inputs: list[Path], output: Path) -> None:
        objs = map(read_object, inputs)
        obj = link(list(objs), output)
        write_object(obj, output)

    typer.run(main)
