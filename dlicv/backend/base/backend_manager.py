# This file is modified from `mmdepoly` 
# https://github.com/open-mmlab/mmdeploy/blob/main/mmdeploy/backend/base/backend_manager.py
import importlib
from abc import ABCMeta
from typing import Callable, Optional, Sequence

from .base_backend import BaseBackend


class BaseBackendManager(metaclass=ABCMeta):
    """Abstract interface of backend manager. 
    """

    @classmethod
    def build_backend(cls,
                      backend_files: Sequence[str],
                      device_type: str = 'cpu',
                      device_id: int = 0,
                      input_names: Optional[Sequence[str]] = None,
                      output_names: Optional[Sequence[str]] = None,
                      **kwargs) -> BaseBackend:
        """Build the backend for the backend model.
        Args:
            backend_files (Sequence[str]): Backend files.
            device_type (str): A string specifying device type. 
                Defaults to 'cpu'.
            device_id (int): A number specifying device id. Defaults to 0.
            input_names (Optional[Sequence[str]], optional): input names.
                Defaults to None.
            output_names (Optional[Sequence[str]], optional): output names.
                Defaults to None.
        """
        raise NotImplementedError(
            f'build_backend has not been implemented for "{cls.__name__}"')

    @classmethod
    def is_available(cls, with_custom_ops: bool = False) -> bool:
        """Check whether backend is installed.
        Args:
            with_custom_ops (bool): check custom ops exists.
        Returns:
            bool: True if backend package is installed.
        """
        raise NotImplementedError(
            f'is_available has not been implemented for "{cls.__name__}"')

    @classmethod
    def get_version(cls) -> str:
        """Get the version of the backend."""
        raise NotImplementedError(
            f'get_version has not been implemented for "{cls.__name__}"')

    @classmethod
    def check_env(cls, log_callback: Callable = lambda _: _) -> str:
        """Check current environment.
        Returns:
            str: Info about the environment.
        """
        try:
            available = cls.is_available()
            if available:
                try:
                    backend_version = cls.get_version()
                except NotImplementedError:
                    backend_version = 'Unknown'
            else:
                backend_version = 'None'

            info = f'{cls.backend_name}:\t{backend_version}'
        except Exception:
            info = f'{cls.backend_name}:\tCheckFailed'

        log_callback(info)
        return info


class BackendManagerRegistry:
    """backend manager registry."""

    def __init__(self):
        self._module_dict = {}

    def register(self, name: str, enum_name: Optional[str] = None):
        """register backend manager.
        Args:
            name (str): name of the backend
            enum_name (Optional[str], optional): enum name of the backend.
                if not given, the upper case of name would be used.
        """
        from dlicv.utils import get_root_logger
        logger = get_root_logger()

        if enum_name is None:
            enum_name = name.upper()

        def wrap_manager(cls):

            from dlicv.utils import Backend

            if not hasattr(Backend, enum_name):
                from aenum import extend_enum
                extend_enum(Backend, enum_name, name)
                logger.info(f'Registry new backend: {enum_name} = {name}.')

            if name in self._module_dict:
                logger.info(
                    f'Backend manager of `{name}` has already been registered.'
                )

            self._module_dict[name] = cls

            cls.backend_name = name

            return cls

        return wrap_manager

    def find(self, name: str) -> BaseBackendManager:
        """Find the backend manager with name.
        Args:
            name (str): backend name.
        Returns:
            BaseBackendManager: backend manager of the given backend.
        """
        # try import backend if backend is in `backend`
        importlib.import_module('dlicv.backend.' + name)
        return self._module_dict.get(name, None)


BACKEND_MANAGERS = BackendManagerRegistry()


def get_backend_manager(name: str) -> BaseBackendManager:
    """Get backend manager.
    Args:
        name (str): name of the backend.
    Returns:
        BaseBackendManager: The backend manager of given name
    """
    from enum import Enum
    if isinstance(name, Enum):
        name = name.value
    return BACKEND_MANAGERS.find(name)
