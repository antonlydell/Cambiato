r"""The create order form component."""

# Standard library
from collections.abc import Sequence
from enum import StrEnum

# Third party
import streamlit as st

# Local
from cambiato.app.components import keys
from cambiato.app.components.core import BannerContainerMapping, process_form_validation_errors
from cambiato.app.session_state import CREATE_ORDER_FORM_VALIDATION_ERRORS
from cambiato.app.translations import CreateOrderForm, CreateOrderFormValidationMessage
from cambiato.database import Session
from cambiato.database.models import (
    Checklist,
    Facility,
    Location,
    Order,
    OrderStatus,
    OrderType,
    User,
)


class FormField(StrEnum):
    r"""The fields of the create order form to validate."""

    SCHEDULED_START_TIME = 'scheduled_start_time'
    SCHEDULED_END_TIME = 'scheduled_end_time'


def _validate_form(translation: CreateOrderFormValidationMessage) -> None:
    r"""Validate the input fields of the create order form.

    Parameters
    ----------
    translation : cambiato.app.translation.CreateOrderFormValidationMessage
        The translations for the validation errors.
    """

    validation_errors = {}

    start_time = st.session_state[keys.CREATE_ORDER_FORM_SCHEDULED_START_TIME_INPUT]
    end_time = st.session_state[keys.CREATE_ORDER_FORM_SCHEDULED_END_TIME_INPUT]

    if start_time is None and end_time is None:
        pass

    elif start_time is None and end_time is not None:
        validation_errors[FormField.SCHEDULED_START_TIME] = translation.start_time_no_end_time

    elif start_time is not None and end_time is None:
        validation_errors[FormField.SCHEDULED_END_TIME] = translation.end_time_no_start_time

    elif start_time >= end_time:
        validation_errors[FormField.SCHEDULED_START_TIME] = (
            translation.start_time_geq_end_time.format(start_time=start_time, end_time=end_time)
        )

    else:
        pass

    st.session_state[CREATE_ORDER_FORM_VALIDATION_ERRORS] = validation_errors


def create_order_form(
    session: Session,
    order_types: Sequence[OrderType],
    order_statuses: Sequence[OrderStatus],
    facilities: Sequence[Facility],
    locations: Sequence[Location],
    checklists: Sequence[Checklist],
    technicians: Sequence[User],
    translation: CreateOrderForm,
    border: bool = True,
    title: bool = True,
    key: str = keys.CREATE_ORDER_FORM,
) -> Order | None:
    r"""Render the form for creating an order.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    order_types : Sequence[cambiato.db.models.OrderType]
        The selectable order types of the order to create.

    order_statuses : Sequence[cambiato.db.models.OrderStatus]
        The selectable order statuses of the order to create.

    facilities : Sequence[cambiato.db.models.Facility]
        The selectable facilities that can be assigned to the order.

    locations : Sequence[cambiato.db.models.Location]
        The selectable locations that can be assigned to the order.

    checklists : Sequence[cambiato.db.models.Checklist]
        The selectable checklists that can be assigned to the order.

    technicians : Sequence[cambiato.db.models.User]
        The selectable technicians that can be assigned to the order.

    translation : cambiato.app.translations.CreateOrderForm
        The language translations for the form.

    border : bool, default True
        True if a border should be rendered around the form and False for no border.

    title : bool, default True
        True if the title of the form should be rendered.
        Useful for removing the title if rendering the form in a dialog frame.

    key : str, default cambiato.app.components.keys.CREATE_ORDER_FORM
        The unique identifier of the form in the session state.
    """

    banner_container_mapping: BannerContainerMapping = {}

    with st.form(key=key, border=border):
        if title:
            st.markdown(f'### {translation.title}')

        order_type_id = st.selectbox(
            label=translation.order_type_id_label,
            placeholder=translation.order_type_id_placeholder,
            options=order_types,
            disabled=not bool(order_types),
            key=keys.CREATE_ORDER_FORM_ORDER_TYPE_SELECTBOX,
        )
        order_status_id = st.selectbox(
            label=translation.order_status_id_label,
            placeholder=translation.order_status_id_placeholder,
            options=order_statuses,
            disabled=not bool(order_statuses),
            key=keys.CREATE_ORDER_FORM_ORDER_STATUS_SELECTBOX,
        )
        facility_id = st.selectbox(
            label=translation.facility_id_label,
            placeholder=translation.facility_id_placeholder,
            options=facilities,
            index=None,
            disabled=not bool(facilities),
            key=keys.CREATE_ORDER_FORM_FACILITY_SELECTBOX,
        )
        location_id = st.selectbox(
            label=translation.location_id_label,
            placeholder=translation.location_id_placeholder,
            options=locations,
            index=None,
            disabled=not bool(locations),
            key=keys.CREATE_ORDER_FORM_LOCATION_SELECTBOX,
        )
        checklist_id = st.selectbox(
            label=translation.checklist_id_label,
            placeholder=translation.checklist_id_placeholder,
            options=checklists,
            index=None,
            disabled=not bool(checklists),
            key=keys.CREATE_ORDER_FORM_CHECKLIST_SELECTBOX,
        )
        ext_id = st.text_input(
            label=translation.ext_id_label,
            placeholder=translation.ext_id_placeholder,
            key=keys.CREATE_ORDER_FORM_EXT_ID_TEXT_INPUT,
        )
        technician_id = st.selectbox(
            label=translation.technician_id_label,
            placeholder=translation.technician_id_placeholder,
            options=technicians,
            index=None,
            disabled=not bool(technicians),
            key=keys.CREATE_ORDER_FORM_TECHNICIAN_SELECTBOX,
        )

        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            scheduled_start_at = st.date_input(
                label=translation.scheduled_date,
                value=None,
                format='YYYY-MM-DD',
                key=keys.CREATE_ORDER_FORM_SCHEDULED_DAY_DATE_INPUT,
            )
        with mid_col:
            banner_container_mapping[FormField.SCHEDULED_START_TIME] = st.empty()
            scheduled_start_at_time = st.time_input(
                label=translation.scheduled_start_at,
                value=None,
                key=keys.CREATE_ORDER_FORM_SCHEDULED_START_TIME_INPUT,
            )
        with right_col:
            banner_container_mapping[FormField.SCHEDULED_END_TIME] = st.empty()
            scheduled_end_time = st.time_input(
                label=translation.scheduled_end_at,
                value=None,
                key=keys.CREATE_ORDER_FORM_SCHEDULED_END_TIME_INPUT,
            )

        clicked = st.form_submit_button(
            label=translation.submit_button_label,
            type='primary',
            on_click=_validate_form,
            kwargs={'translation': translation.validation_messages},
        )

        if not clicked:
            return None

        if validation_errors := st.session_state.get(CREATE_ORDER_FORM_VALIDATION_ERRORS, {}):
            process_form_validation_errors(
                validation_errors=validation_errors,
                banner_container_mapping=banner_container_mapping,
            )
            st.session_state[CREATE_ORDER_FORM_VALIDATION_ERRORS] = {}

            return None

        return None
