r"""The core database functionality."""

# Standard library
import logging

# Third party
from streamlit_passwordless.database import URL as URL
from streamlit_passwordless.database import Session as Session
from streamlit_passwordless.database import SessionFactory as SessionFactory
from streamlit_passwordless.database import create_session_factory as create_session_factory

# Local
from cambiato import exceptions
from cambiato.core import OperationResult

logger = logging.getLogger(__name__)


def commit(session: Session, error_msg: str = 'Error committing transaction!') -> OperationResult:
    r"""Commit a database transaction.

    session : cambiato.db.Session
        An active database session.

    error_msg : str, default 'Error committing transaction!'
        An error message to add if an exception is raised when committing the transaction.

    Returns
    -------
    result : cambiato.OperationResult
        The result of committing the transaction.
    """

    try:
        session.commit()
    except exceptions.SQLAlchemyError as e:
        long_msg = f'{error_msg}\n{e!s}'
        logger.error(long_msg)
        result = OperationResult(ok=False, short_msg=error_msg, long_msg=long_msg)
        session.rollback()
    else:
        result = OperationResult()

    return result
