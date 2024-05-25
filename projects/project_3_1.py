"""
Project 3.1
"""

import sys
from pathlib import Path

import typer

from linker import read_object, write_object
from linker.errors import LinkError


def main(infile: Path, outfile: Path) -> None:
    """
    Output object file.

    :param infile: path to the input file.
    :param outfile: path to the output file.
    """
    try:
        write_object(read_object(infile), outfile)
    except (LinkError, FileNotFoundError) as err:
        sys.exit(str(err))


typer.run(main)
