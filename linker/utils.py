"""
Some helper functions.
"""

from pathlib import Path

from .errors import LinkError, ParseError
from .object import Object
from .parser import parse_object_from_lines
from .writer import dump_object


def roundup(val: int, multiple: int) -> int:
    """
    Round value to next multiple.

    :param val: value to round up.
    :param multiple: multiple to round up to.
    :return: the rounded up value.
    """
    rem = val % multiple
    if rem != 0:
        val += multiple - rem
    return val


def read_object(path: Path) -> Object:
    """
    Read object from file.

    :param path: path to the object file.
    :return: the parsed object file.
    :raises FileNotFoundError: if the path doesn't exist.
    :raises LinkError: if there is an error parsing the file.
    """
    with open(path, mode="r", encoding="ascii") as file:
        try:
            return parse_object_from_lines(file, path.stem)
        except ParseError as err:
            raise LinkError(f"{path}:{err.lineno}: error: {err}") from err
        except LinkError as err:
            raise LinkError(f"{path}: error: {err}") from err


def write_object(obj: Object, path: Path) -> None:
    """
    Write object to file.

    :param obj: the object to write.
    :param path: the output path.
    """
    with open(path, mode="w", encoding="ascii") as file:
        file.write(dump_object(obj))
