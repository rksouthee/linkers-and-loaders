from pathlib import Path

import pytest

from linker import roundup, read_object, write_object, Object, Segment
from linker.writer import dump_object


def test_roundup_to_zero() -> None:
    with pytest.raises(ZeroDivisionError, match="integer modulo by zero"):
        roundup(123, 0)


@pytest.mark.parametrize(
    "val,multiple,expected",
    [
        (0, 5, 0),
        (4, 5, 5),
        (5, 5, 5),
    ],
)
def test_roundup(val: int, multiple: int, expected: int) -> None:
    assert roundup(val, multiple) == expected


@pytest.fixture
def main() -> Object:
    segs = [
        Segment(".text", 0, 0x1017, "R"),
        Segment(".data", 0x2000, 0x320, "RW"),
        Segment(".bss", 0x2320, 0x100, "RW"),
    ]
    return Object("main", segs, [], [])


def test_read_object(tmp_path: Path, main: Object) -> None:
    contents = dump_object(main)
    path = (tmp_path / main.name).with_suffix(".lk")
    path.write_text(contents)
    assert read_object(path) == main


def test_write_object(tmp_path: Path, main: Object) -> None:
    path = (tmp_path / main.name).with_suffix(".lk")
    write_object(main, path)
    assert (
        path.read_text()
        == """LINK
3 0 0
.text 0 1017 R
.data 2000 320 RW
.bss 2320 100 RW"""
    )
