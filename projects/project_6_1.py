"""
Project 6.1
"""

import sys
from pathlib import Path
from typing import Iterator

import typer
from linker import Object, Symbol, read_object, write_object
from linker.errors import LinkError


def defined_syms(obj: Object) -> Iterator[Symbol]:
    """
    Return an iterator over the defined symbols in the object.

    :param obj: The object to examine.
    :return: An iterator over the defined symbols.
    """
    for sym in obj.syms:
        if "D" in sym.type:
            yield sym


def add_syms(syms: dict[str, Object], obj: Object) -> None:
    """
    Add the defined symbols in the object to the symbol table.

    :param syms: The symbol table.
    :param obj: The object to examine.
    :raises LinkError: If a symbol is multiply defined.
    """
    for sym in defined_syms(obj):
        if sym.name in syms:
            raise LinkError("multiply defined symbol")
        syms[sym.name] = obj


def create_library(objs: list[Object], path: Path) -> None:
    """
    Create a library from the objects.

    :param objs: The objects to link.
    :param path: The directory to write the library.
    :raises LinkError: If a symbol is multiply defined.
    """
    syms: dict[str, Object] = {}
    for obj in objs:
        add_syms(syms, obj)
    map_lines: list[str] = []
    for obj in objs:
        write_object(obj, path / obj.name)
        map_lines.append(
            obj.name + " " + " ".join(map(lambda sym: sym.name, defined_syms(obj)))
        )
    with open(path / "MAP", mode="w", encoding="ascii") as fh:
        fh.write("\n".join(map_lines))


if __name__ == "__main__":

    def main(inputs: list[Path], output: Path) -> None:
        """
        Link the input objects into a library.

        :param inputs: The input objects.
        :param output: The output directory.
        """
        try:
            if output.exists():
                raise LinkError("directory already exists")
            output.mkdir()
            create_library(list(map(read_object, inputs)), output)
        except LinkError as err:
            sys.exit(f"error: {err}")

    typer.run(main)
