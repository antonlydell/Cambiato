r"""The page controller of the order page."""

# Third party
import streamlit as st

# Local
from cambiato.app.components.forms.create_order_form import create_order_form
from cambiato.app.translations import Order
from cambiato.database import Session


def controller(session: Session, translation: Order) -> None:
    r"""Render the order page.

    Parameters
    ----------
    session : cambiato.db.Session
        An active database session.

    translation : cambiato.app.translations.Order
        The translations for the order page.
    """

    st.title(translation.page_title)

    create_order_form(
        session=session,
        order_types=[],
        order_statuses=[],
        facilities=[],
        locations=[],
        checklists=[],
        technicians=[],
        translation=translation.create_order_form,
    )
