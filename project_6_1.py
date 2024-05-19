from pathlib import Path
from typing import Iterable, Iterator

import typer

from linker import Symbol, Object, write_object, read_object
from linker.errors import LinkError


def defined_syms(obj: Object) -> Iterator[Symbol]:
    for sym in obj.syms:
        if "D" in sym.type:
            yield sym


def add_syms(syms: dict[str, Object], obj: Object) -> None:
    for sym in defined_syms(obj):
        if sym.name in syms:
            raise LinkError("multiply defined symbol")
        syms[sym.name] = obj


def create_library(objs: list[Object], path: Path) -> None:
    syms: dict[str, Object] = {}
    for obj in objs:
        add_syms(syms, obj)
    map_lines: list[str] = []
    for obj in objs:
        write_object(obj, path / obj.name)
        map_lines.append(obj.name + ' ' + ' '.join(map(lambda sym: sym.name, defined_syms(obj))))
    with open(path / "MAP", mode="w", encoding="ascii") as fh:
        fh.write("\n".join(map_lines))


if __name__ == "__main__":
    def main(inputs: list[Path], output: Path) -> None:
        try:
            if output.exists():
                raise LinkError("directory already exists")
            output.mkdir()
            create_library(list(map(read_object, inputs)), output)
        except LinkError as err:
            print(f"fatal error: {err}")
    typer.run(main)
