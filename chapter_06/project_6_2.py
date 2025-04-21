from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing_extensions import Annotated
from typing import Iterator, Iterable

import typer
from linker import Object, Segment, write_object, Symbol, read_object, roundup
from linker.errors import LinkError

from chapter_04.project_4_3 import (
    create_common_segment,
    create_symbol_table,
    group_segments_by_name,
    group_segments_by_type,
    iter_syms,
    iter_segs,
    link_group,
    make_default_groups,
)


def is_undefined_symbol(symbol: Symbol) -> bool:
    return "U" in symbol.type


def is_defined_symbol(symbol: Symbol) -> bool:
    return "D" in symbol.type


def iter_undefined_symbols(symbols: Iterable[Symbol]) -> Iterator[Symbol]:
    return filter(is_undefined_symbol, symbols)


def split_objects_and_libraries(
    paths: Iterable[Path],
) -> tuple[list[Object], list[Path]]:
    objects: list[Object] = []
    directories: list[Path] = []
    for path in paths:
        if path.is_dir():
            directories.append(path)
        else:
            objects.append(read_object(path))
    return objects, directories


def add_symbols(symtab: dict[str, Symbol], symbols: Iterable[Symbol]) -> None:
    for symbol in symbols:
        existing_symbol = symtab.get(symbol.name)
        if existing_symbol:
            if is_defined_symbol(existing_symbol):
                if is_defined_symbol(symbol):
                    raise LinkError(f"multiply defined symbol: {symbol.name}")
            elif is_defined_symbol(symbol):
                symtab[symbol.name] = symbol


@dataclass
class Module:
    name: str
    symbols: list[str]


def read_map(library: Path) -> list[Module]:
    modules: list[Module] = []
    with open(library / "MAP", mode="r", encoding="ascii") as fh:
        for line in fh:
            parts = line.split()
            modules.append(Module(parts[0], parts[1:]))
    return modules


def resolve_undefined_symbols(symtab: dict[str, Symbol], libs: Iterable[Path]) -> list[Object]:
    objects: list[Object] = []
    while True:
        added = False
        for lib in libs:
            modules = read_map(lib)
            for module in modules:
                for symbol in module.symbols:
                    existing_symbol = symtab.get(symbol)
                    if existing_symbol and is_undefined_symbol(existing_symbol):
                        path = lib / module.name
                        obj = read_object(path)
                        add_symbols(symtab, obj.syms)
                        objects.append(obj)
                        added = True
                        break
        if not added:
            break
    return objects


def link(inputs: Iterable[Path], path: Path) -> Object:
    objs, libs = split_objects_and_libraries(inputs)
    symtab = create_symbol_table(iter_syms(objs))
    objs.extend(resolve_undefined_symbols(symtab, libs))
    common_seg = create_common_segment(symtab.values())
    names = group_segments_by_name(chain(iter_segs(objs), [common_seg]))
    types = group_segments_by_type(names, make_default_groups())
    segs: list[Segment] = []
    segs.extend(link_group(types["text"], names, 0x1000, "RP"))
    segs.extend(link_group(types["data"], names, roundup(segs[-1].end, 0x1000), "RWP"))
    return Object(path.stem, segs, list(symtab.values()), [])


if __name__ == "__main__":  # pragma: no cover

    def main(
        inputs: list[Path],
        output: Annotated[Path, typer.Option(help="output object file")],
    ) -> None:
        """
        Link a list of objects and libraries.

        :param inputs: The list of objects/libraries to link.
        :param output: The path to write the linked object to.
        """
        write_object(link(inputs, output), output)

    typer.run(main)
