from pathlib import Path

import typer

from linker import Object, parse_object_from_lines, dump_object


def read_object(path: Path) -> Object:
    with open(path, mode="r", encoding="ascii") as file:
        return parse_object_from_lines(file, path.stem)


def write_object(obj: Object, path: Path) -> None:
    with open(path, mode="w", encoding="ascii") as file:
        file.write(dump_object(obj))


def main(infile: Path, outfile: Path) -> None:
    write_object(read_object(infile), outfile)


typer.run(main)
