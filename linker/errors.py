"""
A collection of errors from linking and parsing objects.
"""


class LinkError(Exception):
    """
    Base class for link errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParseError(LinkError):
    """
    Error when parsing an object file.
    """

    lineno: int

    def __init__(self, lineno: int, message: str) -> None:
        super().__init__(message)
        self.lineno = lineno
