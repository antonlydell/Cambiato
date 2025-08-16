r"""Functions for working with order related models."""

# Standard library
from collections.abc import Sequence

# Third party
import pandas as pd
from sqlalchemy import or_, select

# Local
from cambiato.core import OperationResult
from cambiato.database.core import Session, commit
from cambiato.database.models import Order, OrderStatus, OrderType
from cambiato.models.dataframe import OrderStatusDataFrameModel, OrderTypeDataFrameModel
from cambiato.translations import TranslationMapping, translate_dataframe


def get_all_order_types(
    _session: Session,
    utility_ids: Sequence[int] | None = None,
    translation: TranslationMapping | None = None,
) -> OrderTypeDataFrameModel:
    r"""Get all order types from the database.

    Parameters
    ----------
    _session : cambiato.db.Session
        An active database session.

    utility_ids : Sequence[int] or None, default None
        The ID:s of the utilities to filter by in addition to the non-utility specific
        order types. If None all order types without a specified utility are included.

    translation : Mapping[int, str] or None, default None
        The translations for the names of the default order types.

    Returns
    -------
    cambiato.models.OrderTypeDataFrameModel
        The order types retrieved from the database.
    """

    c_order_type_id = OrderTypeDataFrameModel.c_order_type_id
    c_name = OrderTypeDataFrameModel.c_name

    query = select(
        OrderType.order_type_id.label(c_order_type_id), OrderType.name.label(c_name)
    ).order_by(OrderType.order_type_id)

    if utility_ids:
        query = query.where(
            or_(OrderType.utility_id.in_(utility_ids), OrderType.utility_id.is_(None))
        )
    else:
        query = query.where(OrderType.utility_id.is_(None))

    df = pd.read_sql_query(
        sql=query,
        con=_session.bind,  # type: ignore[arg-type]
        dtype={col: OrderTypeDataFrameModel.dtypes[col] for col in (c_order_type_id, c_name)},
    ).set_index(OrderTypeDataFrameModel.index_cols)

    if translation:
        df = translate_dataframe(df=df, translation=translation, columns=[c_name])

    return OrderTypeDataFrameModel(df=df)


def get_all_order_statuses(
    _session: Session,
    utility_ids: Sequence[int] | None = None,
    translation: TranslationMapping | None = None,
) -> OrderStatusDataFrameModel:
    r"""Get all order statuses from the database.

    Parameters
    ----------
    _session : cambiato.db.Session
        An active database session.

    utility_ids : Sequence[int] or None, default None
        The ID:s of the utilities to filter by in addition to the non-utility specific
        order statuses. If None all order statues without a specified utility are included.

    translation : Mapping[int, str] or None, default None
        The translations for the names of the default order statuses.

    Returns
    -------
    cambiato.models.OrderStatusThinDataFrameModel
        The order statuses retrieved from the database.
    """

    c_order_status_id = OrderStatusDataFrameModel.c_order_status_id
    c_name = OrderStatusDataFrameModel.c_name

    query = select(
        OrderStatus.order_status_id.label(c_order_status_id), OrderStatus.name.label(c_name)
    ).order_by(OrderStatus.order_status_id)

    if utility_ids:
        query = query.where(
            or_(OrderStatus.utility_id.in_(utility_ids), OrderStatus.utility_id.is_(None))
        )
    else:
        query = query.where(OrderStatus.utility_id.is_(None))

    df = pd.read_sql_query(  # type: ignore[call-overload]
        sql=query,
        con=_session.bind,
        dtype={col: OrderStatusDataFrameModel.dtypes[col] for col in (c_order_status_id, c_name)},
        dtype_backend='pyarrow',
    ).set_index(OrderStatusDataFrameModel.index_cols)

    if translation:
        df = translate_dataframe(df=df, translation=translation, columns=[c_name])

    return OrderStatusDataFrameModel(df=df)


def create_order(session: Session, order: Order) -> OperationResult:
    r"""Create a new order in the database.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    order : cambiato.db.models.Order
        The order to save to the database.

    Returns
    -------
    cambiato.OperationResult
        The result of saving the order to the database.
    """

    session.add(order)
    return commit(session=session, error_msg='Unexpected error when saving order to database!')
