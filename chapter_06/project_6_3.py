import sys
from pathlib import Path
from typing import Iterator
from typing_extensions import Annotated

import typer
from linker import Object, Symbol, read_object
from linker.writer import dump_object
from linker.errors import LinkError


def update_symbol_table(symbol_table: dict[str, Symbol], obj: Object) -> None:
    for sym in obj.syms:
        if "D" in sym.type:
            assert sym.name not in symbol_table
            symbol_table[sym.name] = sym


def iter_defined_symbols(obj: Object) -> Iterator[Symbol]:
    for sym in obj.syms:
        if "D" in sym.type:
            yield sym


def dump_module(offsets: dict[str, tuple[int, int]], obj: Object) -> str:
    offset = offsets[obj.name]
    parts = [str(offset[0]), str(offset[1])]
    for sym in iter_defined_symbols(obj):
        parts.append(sym.name)
    return " ".join(parts) + "\n"


def create_library(objects: list[Object], output: Path) -> None:
    lines = [f"LIBRARY {len(objects)} {0:08x}\n"]
    offset = len(lines[0])
    symbol_table: dict[str, Symbol] = {}
    module_offsets: dict[str, tuple[int, int]] = {}
    for obj in objects:
        update_symbol_table(symbol_table, obj)
        obj_str = dump_object(obj) + "\n"
        module_offsets[obj.name] = (offset, len(obj_str))
        offset += len(obj_str)
        lines.append(obj_str)

    lines[0] = f"LIBRARY {len(objects)} {offset:08x}\n"
    for obj in objects:
        mod_str = dump_module(module_offsets, obj)
        offset += len(mod_str)
        lines.append(mod_str)

    with open(output, mode="w", encoding="ascii") as fh:
        fh.writelines(lines)


if __name__ == "__main__":

    def main(
        inputs: list[Path],
        output: Annotated[Path, typer.Option(help="output directory path")],
    ) -> None:
        """
        Link the input objects into a library.

        :param inputs: The input objects.
        :param output: The output directory.
        """
        try:
            if output.exists():
                raise LinkError("library already exists")
            create_library(list(map(read_object, inputs)), output)
        except LinkError as err:
            sys.exit(f"error: {err}")

    typer.run(main)
