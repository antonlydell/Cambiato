r"""The entry point of the order page."""

# Standard library
from pathlib import Path

# Third party
import streamlit as st

# Local
from cambiato.app import auth
from cambiato.app._pages import Pages
from cambiato.app.config import (
    APP_HOME_PAGE_URL,
    APP_ISSUES_PAGE_URL,
    MAINTAINER_INFO,
)
from cambiato.app.controller.order import controller
from cambiato.app.setup import cm, session_factory, translations

ORDER_PAGE_PATH = Path(__file__)

ABOUT = f"""Create and manage orders.

{MAINTAINER_INFO}
"""


@auth.authorized(redirect=Pages.SIGN_IN)
def order_page() -> None:
    r"""Render the order page."""

    st.set_page_config(
        page_title='Cambiato - Order',
        page_icon=':bookmark_tabs:',
        layout='wide',
        menu_items={
            'Get Help': APP_HOME_PAGE_URL,
            'Report a bug': APP_ISSUES_PAGE_URL,
            'About': ABOUT,
        },
        initial_sidebar_state='auto',
    )

    translation = translations[cm.default_language]

    with session_factory() as session:
        controller(session=session, translation=translation.order)


if __name__ in {'__main__', '__page__'}:
    order_page()
