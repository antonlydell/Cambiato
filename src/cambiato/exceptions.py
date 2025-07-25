r"""The exception hierarchy of Cambiato."""

# Standard library
from typing import Any

# Third party
from sqlalchemy.exc import SQLAlchemyError as SQLAlchemyError


class CambiatoError(Exception):
    r"""The base Exception of Cambiato.

    Parameters
    ----------
    message : str
        The error message.

    data : Any, default None
        Optional extra data to include in the exception.

    e : Exception or None, default None
        The parent exception that is being wrapped and is
        used to extract additional error information from.

    Attributes
    ----------
    message : str
        The error message of the `message` parameter.

    name : str
        The name of the exception.

    parent_exception : Exception or None
        The wrapped parent exception if provided.

    parent_exception_name : str or None
        The name with module path of `parent_exception`.

    parent_message : str or None
        The error message of the parent exception.

    parent_full_message : str or None
        The full error message of the parent exception.
    """

    def __init__(self, message: str, data: Any = None, e: Exception | None = None) -> None:
        self.message = message
        self.data = data
        self.name = self.__class__.__name__

        if e is not None:
            self.parent_exception: Exception | None = e
            self.parent_exception_name: str | None = f'{e.__module__}.{e.__class__.__name__}'
            self.parent_full_message: str | None = str(e)
        else:
            self.parent_exception = None
            self.parent_exception_name = None
            self.parent_full_message = None

        if getattr(self, 'parent_message', None) is None:
            self.parent_message = None if e is None else self._get_parent_error_message(e=e)

        super().__init__(message)

    @staticmethod
    def _get_parent_error_message(e: Exception) -> Any:
        r"""Get the error message of the parent exception."""

        try:
            return e.args[0]
        except IndexError:
            return None

    @property
    def displayable_message(self) -> str:
        r"""An error message that is safe to display to the user."""

        return self.message

    @property
    def detailed_message(self) -> str:
        r"""An error message with more details.

        It may contain more sensitive data that should not be displayed to the user.
        It is useful to log this message.
        """

        return (
            f'Message : {self.message}\n'
            f'Parent Exception : {self.parent_exception_name}\n'
            f'Parent Full Message :{self.parent_full_message}'
        )


class ConfigError(CambiatoError):
    """Errors related to the configuration of Cambiato."""


class ConfigFileNotFoundError(ConfigError):
    """If the config file cannot be found."""


class ParseConfigError(ConfigError):
    """If the config file cannot be parsed correctly."""
