from pathlib import Path

import pytest

from linker import Object, Segment, Symbol

from project_5_3 import link


@pytest.fixture
def main() -> Object:
    return Object(
        "main",
        [
            Segment(".text", 0, 0x230, "RP"),
            Segment(".data", 0x1000, 0x123, "RWP"),
            Segment(".bss", 0x1124, 0x31a, "RW")
        ],
        [
            Symbol("main", 0x20, 0, "D"),
            Symbol("val", 0x1034, 1, "D"),
            Symbol("junk", 0x83a, 0, "U"),
        ],
        []
        )


@pytest.fixture
def mass() -> Object:
    return Object(
        "mass",
        [
            Segment(".text", 0, 0x1138, "RP"),
            Segment(".debug", 0x1138, 0x12, "RP"),
            Segment(".data", 0x2000, 0x23, "RWP"),
            Segment(".bss", 0x2024, 0x31af, "RW"),
        ],
        [
            Symbol("add", 0x1013, 0, "D"),
            Symbol("g_name", 0x113d, 1, "D"),
            Symbol("junk", 0x1ac, 0, "U"),
        ],
        []
        )


def test_link(main: Object, mass: Object) -> None:
    obj = link([main, mass], Path("a.lk"))
    assert obj.syms[0].name == "main"
    assert obj.syms[0].value == 0x1020
    assert obj.syms[0].seg == 0
    assert obj.syms[1].name == "val"
    assert obj.syms[1].value == 0x3034
    assert obj.syms[1].seg == 2
    assert obj.syms[3].name == "add"
    assert obj.syms[3].value == 0x2243
    assert obj.syms[3].seg == 0
    assert obj.syms[4].name == "g_name"
    assert obj.syms[4].value == 0x236d
    assert obj.syms[4].seg == 1
    assert obj.syms[2].name == "junk"
    assert obj.syms[2].value == 0x6614
    assert obj.syms[2].seg == 4
    assert obj.syms[2].type == "D"
