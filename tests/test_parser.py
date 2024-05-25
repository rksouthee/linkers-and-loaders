import re

import pytest

from linker.errors import ParseError, LinkError
from linker.object import Segment, Symbol
from linker.parser import (
    is_magic_number,
    is_comment,
    line_iterator,
    Line,
    validate_magic_number,
    parse_counts,
    validate_counts,
    next_line,
    parse_object_from_str,
    parse_item,
    parse_data,
    parse_segment_data,
)


@pytest.mark.parametrize(
    "line,expected",
    [
        ("link", False),
        ("LINK\n", False),
        (" LINK", False),
        ("LINK#1", False),
        ("LINK", True),
    ],
)
def test_is_magic_number(line: str, expected: bool) -> None:
    assert is_magic_number(line) == expected


@pytest.mark.parametrize(
    "line,expected",
    [
        ("# 1 2 3", True),
        (" #123", False),
        ("#123\n", True),
        ("LINK#", False),
    ],
)
def test_is_comment(line: str, expected: bool) -> None:
    assert is_comment(line) == expected


@pytest.fixture
def main() -> str:
    return """LINK
3 2 0
# segments: name base length flags
# this uses the common convention that text starts at zero,
# data starts on the next page after text, bss starts at the
# next word after data
#
# for the moment, there's no data
.text 0    1017 R
.data 2000 320  RW
.bss  2320 50   RW
# symbols
main 0 1 D
wiggleroom 100 0 U"""


def test_line_iterator(main: str) -> None:
    lines = main.splitlines()
    assert list(line_iterator(lines)) == [
        Line(1, "LINK"),
        Line(2, "3 2 0"),
        Line(9, ".text 0    1017 R"),
        Line(10, ".data 2000 320  RW"),
        Line(11, ".bss  2320 50   RW"),
        Line(13, "main 0 1 D"),
        Line(14, "wiggleroom 100 0 U"),
    ]


def test_next_line() -> None:
    lines = ["LINK"]
    it = line_iterator(lines)
    assert next_line(it, "") == Line(1, "LINK")
    with pytest.raises(LinkError):
        next_line(it, "")


def test_invalid_magic_number() -> None:
    line = Line(3, "lINK")
    with pytest.raises(ParseError) as excinfo:
        validate_magic_number(line)
    assert str(excinfo.value) == "invalid magic number (expected LINK)"
    assert excinfo.value.lineno == 3


def test_valid_magic_number() -> None:
    validate_magic_number(Line(3, "LINK"))


@pytest.mark.parametrize(
    "line,error",
    [
        ("1 2", "not enough values to unpack (expected 3, got 2)"),
        ("1 2 3 4", "too many values to unpack (expected 3)"),
        ("abc 3 4", "invalid literal for int() with base 10: 'abc'"),
        ("1    -32 4", "count cannot be negative: '-32'"),
    ],
)
def test_parse_counts_invalid(line: str, error: str) -> None:
    with pytest.raises(ValueError, match=re.escape(error)):
        parse_counts(line)


@pytest.mark.parametrize("line,expected", [("1 2 3", (1, 2, 3))])
def test_parse_counts_valid(line: str, expected: tuple[int, int, int]) -> None:
    assert parse_counts(line) == expected


def test_validate_counts() -> None:
    line = Line(8, "1 -2 3")
    with pytest.raises(ParseError, match=re.escape("")):
        validate_counts(line)
    line = Line(9, "1 2 3")
    assert validate_counts(line) == (1, 2, 3)


def test_parse_item() -> None:
    with pytest.raises(ParseError, match=re.escape("failed to parse segment: ")):
        parse_item(Line(19, ".text jeep 1017 R"), Segment)


def test_parse_data() -> None:
    line = Line(8, "deadbeef")
    seg = Segment(".text", 0, 0x4, "RP")
    parse_data(line, seg)
    assert seg.data == b"\xde\xad\xbe\xef"

    line = Line(12, "fast")
    with pytest.raises(
        ParseError, match=re.escape("failed to parse data for '.text': ")
    ):
        parse_data(line, seg)


def test_parse_segment_data() -> None:
    lines = [Line(3, "deadbeef"), Line(4, "1234")]
    segs = [
        Segment(".text", 0, 0x4, "RP"),
        Segment(".bss", 0x10, 0x123, "RW"),
        Segment(".data", 0x200, 0x2, "RWP"),
    ]
    parse_segment_data(iter(lines), segs)
    assert segs[0].data == b"\xde\xad\xbe\xef"
    assert segs[2].data == b"\x12\x34"


def test_parse_object_from_str(main: str) -> None:
    obj = parse_object_from_str(main, "main")
    assert obj.name == "main"
    assert obj.segs == [
        Segment(".text", 0, 0x1017, "R"),
        Segment(".data", 0x2000, 0x320, "RW"),
        Segment(".bss", 0x2320, 0x50, "RW"),
    ]
    assert obj.syms == [Symbol("main", 0, 1, "D"), Symbol("wiggleroom", 0x100, 0, "U")]
    assert not obj.rels
