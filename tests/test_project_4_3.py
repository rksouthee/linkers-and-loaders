import re
from pathlib import Path

import pytest

from linker import Object, Symbol, Segment
from linker.errors import LinkError

from projects.project_4_3 import (
    make_default_groups,
    iter_segs,
    iter_syms,
    get_group,
    group_segments_by_name,
    group_segments_by_type,
    group_symbols_by_name,
    partition_symbols,
    reduce_symbol,
    create_common_segment,
    create_symbol_table,
    link,
)


@pytest.fixture
def main() -> Object:
    segs = [
        Segment(".text", 0, 2, "RP"),
        Segment(".data", 0x1000, 1, "RWP"),
        Segment(".bss", 0x1004, 3, "RW"),
    ]
    segs[0].data = b"hi"
    segs[1].data = b"y"
    syms = [
        Symbol("main", 0, 1, "D"),
        Symbol("ptr", 0, 2, "D"),
        Symbol("items", 10, 0, "U"),
    ]
    return Object("main", segs, syms, [])


@pytest.fixture
def calif() -> Object:
    return Object("calif", [], [], [])


@pytest.fixture
def mass() -> Object:
    return Object("mass", [], [], [])


@pytest.fixture
def newyork() -> Object:
    return Object("newyork", [], [], [])


@pytest.fixture
def objs(main: Object, calif: Object, mass: Object, newyork: Object) -> list[Object]:
    return [main, calif, mass, newyork]


def test_iter_segs(objs: list[Object]) -> None:
    assert list(iter_segs(objs)) == objs[0].segs


def test_iter_syms(objs: list[Object]) -> None:
    assert list(iter_syms(objs)) == objs[0].syms


@pytest.mark.parametrize(
    "flags,expected",
    [
        ("RWP", "data"),
        ("RP", "text"),
        ("R", "bss"),
        ("RW", "bss"),
    ],
)
def test_get_group(flags: str, expected: str) -> None:
    assert get_group(flags) == expected


def test_group_segments_by_name(objs: list[Object]) -> None:
    segs = group_segments_by_name(iter_segs(objs))
    assert segs == {
        ".text": [objs[0].segs[0]],
        ".data": [objs[0].segs[1]],
        ".bss": [objs[0].segs[2]],
    }


def test_group_segments_by_type(objs: list[Object]) -> None:
    segs = group_segments_by_name(iter_segs(objs))
    groups = group_segments_by_type(segs, make_default_groups())
    assert groups == {
        "text": [".text"],
        "data": [".data"],
        "bss": [".bss", ".common"],
    }


def test_group_segments_by_type_empty() -> None:
    names: dict[str, list[Segment]] = {".text": [], ".debug": []}
    groups = group_segments_by_type(names, make_default_groups())
    assert groups == {"text": [".text"], "data": [".data"], "bss": [".bss", ".common"]}


def test_group_segments_by_type_mismatch() -> None:
    seg = Segment(".text", 0, 10, "RW")
    names = {seg.name: [seg]}
    with pytest.raises(LinkError, match=re.escape(".text type mismatch (expected text, got bss)")):
        group_segments_by_type(names, make_default_groups())


def test_group_segments_by_type_nondefault() -> None:
    seg = Segment(".debug", 0, 10, "RP")
    names = {seg.name: [seg]}
    types = group_segments_by_type(names, make_default_groups())
    assert types == {
        "text": [".text", ".debug"],
        "data": [".data"],
        "bss": [".bss", ".common"],
    }


def test_group_symbols_by_name(objs: list[Object]) -> None:
    syms = group_symbols_by_name(iter_syms(objs))
    assert syms == {
        "main": [objs[0].syms[0]],
        "ptr": [objs[0].syms[1]],
        "items": [objs[0].syms[2]],
    }


def test_partition_symbols(main: Object) -> None:
    d, u = partition_symbols(main.syms)
    assert d == [main.syms[0], main.syms[1]]
    assert u == [main.syms[2]]


def test_reduce_symbol_multiply_defined() -> None:
    syms = [
        Symbol("main", 0, 0, "D"),
        Symbol("main", 0, 0, "D"),
        Symbol("main", 0, 0, "U"),
    ]
    with pytest.raises(LinkError, match=re.escape("multiply defined symbol")):
        reduce_symbol(syms)


def test_reduce_symbol_defined() -> None:
    syms = [
        Symbol("main", 0, 0, "U"),
        Symbol("main", 0, 0, "D"),
        Symbol("main", 0, 0, "U"),
    ]
    assert reduce_symbol(syms) == syms[1]


def test_reduce_symbol_common() -> None:
    syms = [
        Symbol("main", 0x20, 0, "U"),
        Symbol("main", 0x18, 0, "U"),
        Symbol("main", 0xA, 0, "U"),
    ]
    assert reduce_symbol(syms) == syms[0]


def test_reduce_symbol_undefined() -> None:
    with pytest.raises(LinkError, match=re.escape("undefined symbol")):
        reduce_symbol([])


def test_create_common_segment(objs: list[Object]) -> None:
    seg = create_common_segment(iter_syms(objs))
    assert seg == Segment(".common", 0, 0xA, "RW")


def test_create_symbol_table(objs: list[Object]) -> None:
    syms = create_symbol_table(iter_syms(objs))
    assert syms == {
        "main": objs[0].syms[0],
        "ptr": objs[0].syms[1],
        "items": objs[0].syms[2],
    }


def test_link(objs: list[Object]) -> None:
    obj = link(objs, Path("out.lk"))
    assert obj.segs == [
        Segment(".text", 0x1000, 2, "RP"),
        Segment(".data", 0x2000, 1, "RWP"),
        Segment(".bss", 0x2004, 3, "RW"),
        Segment(".common", 0x2008, 0xA, "RW"),
    ]
    assert not obj.syms
    assert not obj.rels
