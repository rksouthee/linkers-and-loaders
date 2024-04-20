"""
LINK object format parser.
"""

from dataclasses import fields, Field
from itertools import filterfalse
from operator import attrgetter
from typing import Any, Iterable, Iterator, NamedTuple, TypeVar

from .errors import LinkError, ParseError
from .object import Segment, Symbol, Relocation, Object

MAGIC_NUMBER = "LINK"
COMMENT_LEADER = "#"

T = TypeVar("T", Segment, Symbol, Relocation)


class Line(NamedTuple):
    """
    Represents a line in an object file.
    """

    number: int
    contents: str


def is_magic_number(s: str) -> bool:
    """
    Return `True` if `s` is a valid magic number.

    :param s: the string to check.
    :return: `True` if the string is a valid magic number.
    """
    return s == MAGIC_NUMBER


def is_comment(s: str) -> bool:
    """
    Return `True` if `s` is a comment.

    :param s: the string to check.
    :return: `True` if the string is a comment.
    """
    return s.startswith(COMMENT_LEADER)


def line_iterator(lines: Iterable[str], start: int = 1) -> Iterator[Line]:
    """
    Return an iterator that.
    """
    yield from map(
        Line._make,
        filterfalse(
            lambda line: is_comment(line[1]),
            enumerate(map(str.strip, lines), start=start),
        ),
    )


def validate_magic_number(line: Line) -> None:
    """
    Check if the line is a magic number.

    :param line: the line to check.
    :raises ParseError: if the line is not a valid magic number.
    """
    if not is_magic_number(line.contents):
        raise ParseError(line.number, f"invalid magic number (expected {MAGIC_NUMBER})")


def parse_count(s: str) -> int:
    """
    Parse an integer from a string.

    :param s: the string to parse.
    :return: the integer value parsed.
    :raises ValueError: if the string cannot be parsed as a decimal integer.
    :raises ValueError: if the integer value is negative.
    """
    n = int(s)
    if n < 0:
        raise ValueError(f"count cannot be negative: '{s}'")
    return n


def parse_counts(s: str) -> tuple[int, int, int]:
    """
    Parse the space separated counts.

    :param s: the line to parse.
    :raises ValueError: if there are not enough values.
    :raises ValueError: if there are too many values.
    :raises ValueError: if any value is not an integer.
    :raises ValueError: if any value is negative.
    :return: a tuple of non-negative integer counts.
    """
    nsegs, nsyms, nrels = tuple(map(parse_count, s.split()))
    return nsegs, nsyms, nrels


def validate_counts(line: Line) -> tuple[int, int, int]:
    """
    Return the counts.

    :param line: the line to parse.
    :raises ParseError: if there is an error parsing the counts (see `parse_counts`)
    :return: a tuple of non-negative integer counts.
    """
    try:
        return parse_counts(line.contents)
    except ValueError as err:
        raise ParseError(line.number, str(err)) from err


def next_line(lines: Iterator[Line], message: str) -> Line:
    """
    Get the next line from `lines`.

    :param lines: an iterator of lines.
    :param message: the error message to use if there are no more lines.
    :raises LinkError: if there are no more lines left.
    :return: the next line.
    """
    try:
        return next(lines)
    except StopIteration:
        raise LinkError(message) from None


def parse_member(s: str, field: Field[int | str]) -> int | str:
    """
    Parse data class field member from a string.

    Integers are parsed as hexadecimal, otherwise the values should be a string.

    :param s: the string to parse.
    :param field: the data class field.
    :raises ValueError: if the field is an integer and `s` isn't a valid hexadecimal literal.
    :return: the parse value.
    """
    if field.type is int:
        return int(s, base=16)
    return s


def parse_item_from_str(s: str, cls: type[T]) -> T:
    """
    Parse a data class from a string.

    :param s: the string to parse.
    :param cls: tyhe type of the dataclass.
    :return: the parsed dataclass.
    """
    init_args: list[Any] = []
    for part, member in zip(s.split(), filter(attrgetter("init"), fields(cls))):
        init_args.append(parse_member(part, member))
    return cls(*init_args)


def parse_item(line: Line, cls: type[T]) -> T:
    """
    Parse an item from the given line.

    :param line: the line containing the definition.
    :param cls: the type to be parsed.
    :return: a `cls` instance representing the parsed object.
    :raises ParseError: if there was an error parsing the object.
    """
    try:
        return parse_item_from_str(line.contents, cls)
    except ValueError as err:
        raise ParseError(line.number, f"failed to parse {cls.__name__.lower()}: {err}") from err


def parse_lines(lines: Iterator[Line], n: int, cls: type[T]) -> Iterator[T]:
    """
    Try and parse a number of objects for a particular definition.

    :param lines: an iterator of lines containing the object definitions.
    :param n: the number of objects to parse.
    :param cls: the type to be parsed.
    :raises ParseError: if there was an error parsing an object definition.
    :raises LinkError: if there was not enough lines.
    """
    for _ in range(n):
        line = next_line(lines, f"expected {cls.__name__.lower()} definition")
        yield parse_item(line, cls)


def parse_data(line: Line, seg: Segment) -> None:
    """
    Parse the segment data.

    :param line: the line containing the segment data.
    :param seg: the segment.
    :raises ParseError: if we failed to parse the data.
    """
    try:
        seg.data = bytes.fromhex(line.contents)
    except ValueError as err:
        raise ParseError(line.number, f"failed to parse data for '{seg.name}': {err}") from err


def parse_segment_data(lines: Iterator[Line], segs: list[Segment]) -> None:
    """
    Parse the data for each of the segments that have the data present.

    :param lines: the lines containing the segment data.
    :param segs: the list of segments to check if each needs data.
    :raises ParseError: if there was an error parsing the segment data.
    """
    for seg in filter(lambda seg: "P" in seg.flags and seg.size > 0, segs):
        parse_data(next_line(lines, f"expected data for '{seg.name}'"), seg)


def parse_object_from_iter(lines: Iterator[Line], name: str) -> Object:
    """
    Parse an object from an iterator of lines.

    :param lines: an iterator of lines.
    :param name: the name of the object file.
    :return: the parsed object file.
    """
    validate_magic_number(next_line(lines, "expected magic number"))
    nsegs, nsyms, nrels = validate_counts(next_line(lines, "expected counts"))
    segs = list(parse_lines(lines, nsegs, Segment))
    syms = list(parse_lines(lines, nsyms, Symbol))
    rels = list(parse_lines(lines, nrels, Relocation))
    parse_segment_data(lines, segs)
    return Object(name, segs, syms, rels)


def parse_object_from_lines(lines: Iterable[str], name: str) -> Object:
    """
    Parse an object from an iterable of strings.

    :param lines: an iterable of strings.
    :param name: the name of the object file.
    :return: the parsed Object.
    """
    return parse_object_from_iter(line_iterator(lines), name)


def parse_object_from_str(s: str, name: str) -> Object:
    """
    Parse an object from a string.

    :param s: the string containing the object definition.
    :param name: the name of the object file.
    :return: the parsed Object.
    """
    return parse_object_from_lines(s.splitlines(), name)
