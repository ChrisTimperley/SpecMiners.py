# -*- coding: utf-8 -*-
__all__ = ('LineLoader',)

from typing import Callable, Generic, IO, Iterator, List, TypeVar
import abc
import itertools

from loguru import logger
import attr

T = TypeVar('T')


@attr.s(auto_attribs=True)
class LineBuffer:
    _source: Iterator[str]

    @classmethod
    def for_file(cls, filename: str) -> Iterator['LineBuffer']:
        with open(filename, 'r') as fh:
            lines = map(lambda l: l.strip('\n'), fh)
            yield LineBuffer(lines)

    def prepend(self, line: str) -> None:
        """Prepends a line to the front of the buffer."""
        self._source = itertools.chain([line], self._source)

    def peek(self) -> str:
        """Peeks at the next line in the buffer.

        Raises
        ------
        StopIteration
            If the buffer is empty.
        """
        line = next(self._source)
        self.prepend(line)
        return line

    def pop(self) -> str:
        """Pops the next line from the buffer.

        Raises
        ------
        StopIteration
            If the buffer is empty.
        """
        return next(self._source)


class LineLoader(Generic[T]):
    lines: LineBuffer

    @classmethod
    def from_file(cls, filename: str, **kwargs) -> T:
        logger.trace(f'loading from file [{filename}] using [{cls.__name__}]')
        with open(filename, 'r') as fh:
            return cls.from_file_handle(fh, **kwargs)

    @classmethod
    def from_file_handle(cls, fh: IO[str], **kwargs) -> T:
        lines: Iterable[str] = \
            filter(lambda l: l, map(lambda l: l.strip('\n'), fh))
        return cls.from_lines(lines)

    @classmethod
    def from_lines(cls, lines: Iterator[str], **kwargs) -> T:
        assert not isinstance(lines, LineBuffer)
        line_buffer = LineBuffer(lines)
        return cls.from_line_buffer(line_buffer, **kwargs)

    @classmethod
    def from_line_buffer(cls, lines: LineBuffer, **kwargs) -> T:
        return cls(lines=lines, **kwargs).load()

    @abc.abstractmethod
    def lookup(self, name: str):
        ...

    def has_finished(self) -> bool:
        """Determines whether the loader has finished."""
        return False

    def read_line(self, line: str) -> None:
        """Attempts to read the next line."""
        if not line:
            return
        logger.trace(f'parsing line: {line}')
        arguments: List[str] = line.split(' ')
        self.lookup(arguments[0])(*arguments[1:])

    def read(self) -> None:
        while not self.has_finished():
            try:
                line = self.lines.pop()
            except StopIteration:
                break
            self.read_line(line)
        logger.trace(f'reader finished: {self}')

    @abc.abstractmethod
    def build(self) -> T:
        ...

    def load(self) -> T:
        self.read()
        return self.build()
