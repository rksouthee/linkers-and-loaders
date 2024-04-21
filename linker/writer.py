"""
Functions for dumping an object file to an ascii string.
"""
from dataclasses import fields, Field
from operator import attrgetter
from typing import cast, Iterable, Iterator, TypeVar

from .object import Object, Segment, Symbol, Relocation, MAGIC_NUMBER

T = TypeVar("T", Segment, Symbol, Relocation)


def dump_member(item: T, member: Field[int | str]) -> str:
    """
    Convert the member of an instance to a string.

    If the member is an integer then we convert the value to a hex string.

    :param item: the instance to read the member.
    :param member: the member to extract.
    :return: the string interpretation.
    """
    if member.type is int:
        return f"{getattr(item, member.name):x}"
    assert member.type is str
    return cast(str, getattr(item, member.name))


def dump_item(item: T) -> str:
    """
    Convert the item to a string interpretation.

    :param item: the item to dump.
    :return: the string interpretation of the item.
    """
    values: list[str] = []
    for member in filter(attrgetter("init"), fields(item)):
        values.append(dump_member(item, member))
    return " ".join(values)


def dump_segment_data(segs: Iterable[Segment]) -> Iterator[str]:
    """
    Dump the segment data for each segment that has data present.

    :param segs: the segments to scan.
    :return: an iterator for each of the hex strings present.
    """
    for seg in segs:
        if "P" in seg.flags and seg.data:
            yield seg.data.hex()


def dump_object(obj: Object) -> str:
    """
    Dump an object to a string.

    :param obj: the object to dump.
    :return: the string interpretation of the object.
    """
    lines = [MAGIC_NUMBER]
    lines.append(f"{len(obj.segs)} {len(obj.syms)} {len(obj.rels)}")
    lines.extend(map(dump_item, obj.segs))
    lines.extend(map(dump_item, obj.syms))
    lines.extend(map(dump_item, obj.rels))
    lines.extend(dump_segment_data(obj.segs))
    return "\n".join(lines)
