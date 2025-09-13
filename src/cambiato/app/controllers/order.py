r"""The page controller of the order page."""

# Standard library
from zoneinfo import ZoneInfo

# Third party
import streamlit as st

# Local
from cambiato.app.components import ICON_INFO, create_order_button, utility_pills_selector
from cambiato.app.database import (
    get_all_checklists_cached,
    get_all_facilities_cached,
    get_all_order_statuses_cached,
    get_all_order_types_cached,
    get_all_orders_cached,
    get_all_technicians_cached,
    get_all_utilities_cached,
)
from cambiato.app.views import edit_orders_view
from cambiato.database import Session
from cambiato.models.dataframe import ChecklistDataFrameModel, FacilityDataFrameModel
from cambiato.translations import (
    Database,
    EditOrdersDataFrame,
    EditOrdersView,
    Order,
    create_translation_mapping,
)


def controller(
    session: Session,
    order_translation: Order,
    db_translation: Database,
    edit_orders_df_trans: EditOrdersDataFrame,
    edit_orders_view_trans: EditOrdersView,
    tz: ZoneInfo,
    user_id: str,
    has_edit_permission: bool = True,
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

    edit_orders_df_trans : cambiato.translations.EditOrdersDataFrame
        The translations for the order DataFrame editor component
        :func:`cambiato.app.components.edit_orders`.

    tz : zoneinfo.ZoneInfo
        The timezone where the application is used.

    user_id : str
        The ID of the signed in user.

    has_edit_permission : bool, default False
        True if the user has permission to edit orders and False otherwise.
    """

    st.title(order_translation.page_title)

    utilities = get_all_utilities_cached(
        _session=session, translation=create_translation_mapping(db_translation.utility)
    )

    left_col, right_col, _ = st.columns((3, 1, 6))
    with left_col:
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

    order_type_trans = create_translation_mapping(db_translation.order_type)
    order_types = get_all_order_types_cached(
        _session=session, utility_ids=utility_ids, translation=order_type_trans
    )

    order_status_trans = create_translation_mapping(db_translation.order_status)
    order_statuses = get_all_order_statuses_cached(
        _session=session, utility_ids=utility_ids, translation=order_status_trans
    )

    with right_col:
        create_order_button(
            label=order_translation.create_order_button.label,
            disabled=create_order_button_disabled,
            session=session,
            utility_id=selected_utility,
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

    st.divider()
    if not selected_utility:
        st.info('Please select a utility above!', icon=ICON_INFO)
        return

    orders = get_all_orders_cached(
        _session=session,
        utility_ids=utility_ids,
        order_type_trans=order_type_trans,
        order_status_trans=order_status_trans,
        tz=tz,
    )
    edit_orders_view(
        session=session,
        orders=orders,
        order_types=order_types,
        order_statuses=order_statuses,
        facilities=facilities,
        technicians=technicians,
        trans=edit_orders_view_trans,
        edit_orders_df_trans=edit_orders_df_trans,
        tz=tz,
        user_id=user_id,
        has_edit_permission=has_edit_permission,
    )
