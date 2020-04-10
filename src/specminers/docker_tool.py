# -*- coding: utf-8 -*-
"""
This module provides the Tool interface that is implemented by all
specification mining tools that are supported by this package.
"""
__all__ = ('DockerTool',)

from typing import ClassVar
import abc
import contextlib

from loguru import logger
import docker

from .tool import Tool


class DockerTool(Tool, abc.ABC):
    """An interface to a specification mining tool.

    Class Attributes
    ----------------
    IMAGE: str
        The name of the Docker image that provides the tool.
    _DOCKER_DIRECTORY: str
        The directory that provides the build context when building the image.
    """
    IMAGE: ClassVar[str]
    _DOCKER_DIRECTORY: ClassVar[str]

    @classmethod
    def is_installed(cls) -> bool:
        """Checks whether this tool is installed."""
        with contextlib.closing(docker.from_env()) as docker_client:
            try:
                docker_client.images.get(cls.IMAGE)
            except docker.errors.ImageNotFound:
                return False
            return True

    @classmethod
    def install(cls, force_reinstall: bool = False) -> None:
        """Ensures that this tool is installed.

        Parameters
        ----------
        force_reinstall: bool
            If :code:`True`, the image for this tool will be rebuilt
            regardless of whether or not it already exists.
        """
        if cls.is_installed() and not force_reinstall:
            return
        with contextlib.closing(docker.from_env()) as docker_client:
            logger.debug(f'building tool image [{cls.IMAGE}]')
            image, _ = docker_client.images.build(path=cls._DOCKER_DIRECTORY,
                                                  tag=cls.IMAGE,
                                                  pull=True)
            logger.debug(f'built tool image [{cls.IMAGE}]')
