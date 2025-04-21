"""
Generate a C++ program
"""

from itertools import product
from string import ascii_lowercase

import math
import typer


def prefix(name: str, *args: str) -> str:
    return f"{''.join(args)}_{name}"


def postfix(name: str, *args: str) -> str:
    return f"{name}_{''.join(args)}"


FUNCTIONS = {"prefix": prefix, "postfix": postfix}


def main(name: str, count: int, kind: str) -> None:
    length = int(math.ceil(math.log(count, len(ascii_lowercase))))
    name_generator = FUNCTIONS.get(kind, prefix)
    it = product(ascii_lowercase, repeat=length)
    for i in range(count):
        print(f"int {name_generator(name, *next(it))}(void)")
        print("{")
        print(f"\treturn {i};")
        print("}\n")


if __name__ == "__main__":
    typer.run(main)
