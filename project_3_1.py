from pathlib import Path

import typer

from linker import read_object, write_object


def main(infile: Path, outfile: Path) -> None:
    write_object(read_object(infile), outfile)


typer.run(main)
