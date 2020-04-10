# -*- coding: utf-8 -*-
"""
This module provides the Tool interface that is implemented by all
specification mining tools that are supported by this package.
"""
__all__ = ('Tool',)

import abc


class Tool(abc.ABC):
    """An interface to a specification mining tool."""
    @abc.abstractmethod
    @classmethod
    def install(cls, force_reinstall: bool = True) -> None:
        """Performs any necessary installation steps for this tool.

        Parameters
        ----------
        force_reinstall: bool
            If :code:`True`, the image for this tool will be rebuilt
            regardless of whether or not it already exists.
        """
        ...

    @abc.abstractmethod
    @classmethod
    def is_installed(cls) -> bool:
        """Determines whether or not this tool has been installed."""
        ...
