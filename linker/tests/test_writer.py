import pytest

from linker.object import Segment, Symbol, Relocation, Object
from linker.writer import dump_item, dump_object, dump_segment_data


def test_dump_segment() -> None:
    seg = Segment(".text", 0x1017, 0x340, "RP")
    assert dump_item(seg) == ".text 1017 340 RP"


def test_dump_symbol() -> None:
    sym = Symbol("main", 0, 1, "D")
    assert dump_item(sym) == "main 0 1 D"


def test_dump_relocation() -> None:
    rel = Relocation(26, 1, 0, "R8")
    assert dump_item(rel) == "1a 1 0 R8"


def test_dump_segment_data() -> None:
    segs = [Segment(".bss", 0, 100, "RP"), Segment(".data", 100, 4, "RWP")]
    segs[1].data = b"\xde\xad\xbe\xef"
    assert list(dump_segment_data(segs)) == ["deadbeef"]


@pytest.fixture
def main() -> Object:
    segs = [
        Segment(".text", 0, 0x1017, "R"),
        Segment(".data", 0x2000, 0x320, "RW"),
        Segment(".bss", 0x2320, 0x50, "RW"),
    ]
    syms = [Symbol("main", 0, 1, "D"), Symbol("wiggleroom", 0x100, 0, "U")]
    rels: list[Relocation] = []
    return Object("main", segs, syms, rels)


def test_dump_object(main: Object) -> None:
    assert (
        dump_object(main)
        == """LINK
3 2 0
.text 0 1017 R
.data 2000 320 RW
.bss 2320 50 RW
main 0 1 D
wiggleroom 100 0 U"""
    )
