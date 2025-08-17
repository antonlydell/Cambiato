r"""The page controller of the order page."""

# Standard library
from zoneinfo import ZoneInfo

# Third party
import streamlit as st

# Local
from cambiato.app.components.buttons import create_order_button
from cambiato.app.components.selectors import utility_pills_selector
from cambiato.app.database import (
    get_all_checklists_cached,
    get_all_facilities_cached,
    get_all_order_statuses_cached,
    get_all_order_types_cached,
    get_all_technicians_cached,
    get_all_utilities_cached,
)
from cambiato.database import Session
from cambiato.models.dataframe import ChecklistDataFrameModel, FacilityDataFrameModel
from cambiato.translations import Database, Order, create_translation_mapping


def controller(
    session: Session,
    order_translation: Order,
    db_translation: Database,
    tz: ZoneInfo,
    user_id: str | None,
) -> None:
    r"""Render the order page.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    order_translation : cambiato.translations.Order
        The translations for the order page.

    db_translation: cambiato.translations.Database
        Translations for default database objects.

    tz : zoneinfo.ZoneInfo
        The timezone where the application is used.

    user : str or None
        The ID of the signed in user. None if the user is not signed in.
    """

    st.title(order_translation.page_title)

    utilities = get_all_utilities_cached(
        _session=session, translation=create_translation_mapping(db_translation.utility)
    )

    selected_utility = utility_pills_selector(
        label='Utility', utilities=utilities, default=0, label_visibility='collapsed'
    )

    technicians = get_all_technicians_cached(_session=session)

    if selected_utility:
        utility_ids = (selected_utility,)
        facilities = get_all_facilities_cached(_session=session, utility_ids=utility_ids)
        checklists = get_all_checklists_cached(_session=session, utility_ids=utility_ids)
        create_order_button_disabled = False
    else:
        utility_ids = None
        facilities = FacilityDataFrameModel()
        checklists = ChecklistDataFrameModel()
        create_order_button_disabled = True

    order_types = get_all_order_types_cached(
        _session=session,
        utility_ids=utility_ids,
        translation=create_translation_mapping(db_translation.order_type),
    )
    order_statuses = get_all_order_statuses_cached(
        _session=session,
        utility_ids=utility_ids,
        translation=create_translation_mapping(db_translation.order_status),
    )

    create_order_button(
        label=order_translation.create_order_button.label,
        disabled=create_order_button_disabled,
        session=session,
        order_types=order_types,
        order_statuses=order_statuses,
        facilities=facilities,
        checklists=checklists,
        technicians=technicians,
        translation=order_translation.create_order_form,
        tz=tz,
        user_id=user_id,
        help_text=order_translation.create_order_button.help_text,
    )
