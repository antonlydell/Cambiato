r"""User authentication and authorization."""

# Standard library
from enum import IntEnum

# Third party
import streamlit as st
import streamlit_passwordless as stp
from streamlit_passwordless import AdminRole as AdminRole
from streamlit_passwordless import SuperUserRole as SuperUserRole
from streamlit_passwordless import UserRole as UserRole
from streamlit_passwordless import ViewerRole as ViewerRole
from streamlit_passwordless import authorized as authorized

# Local
from cambiato import exceptions
from cambiato.app.session_state import (
    AUTHENTICATED,
    USER_AUTHORIZED_PERMISSIONS,
    USER_UNAUTHORIZED_PERMISSIONS,
)
from cambiato.models import User


class Permission(IntEnum):
    r"""Permissions for users to perform certain operations.

    Members
    -------
    ORDERS_EDIT
        A user is allowed to edit orders.
    """

    ORDERS_EDIT = 1


permission_mapping = {Permission.ORDERS_EDIT: UserRole}


def has_permission(user: User, permission: Permission) -> bool:
    r"""Check if the `user` has specified `permission`.

    Parameters
    ----------
    user : cambiato.models.User
        The user for which to check for permissions.

    permission : cambiato.app.auth.Permission
        The permission to validate.

    Returns
    -------
    bool
        True if the user has specified `permission` and False otherwise.

    Raises
    ------
    cambiato.CambiatoError
        If `permission` is not mapped to a user role.
    """

    authorized_permissions = st.session_state.get(USER_AUTHORIZED_PERMISSIONS, set())
    if permission in authorized_permissions:
        return True

    unauthorized_permissions = st.session_state.get(USER_UNAUTHORIZED_PERMISSIONS, set())
    if permission in unauthorized_permissions:
        return False

    role = permission_mapping.get(permission)
    if role is None:
        raise exceptions.CambiatoError(f'Permission {permission!r} is not mapped to a role!')

    has_permission = user.is_authorized(role=role)

    if has_permission:
        authorized_permissions.add(permission)
        st.session_state[USER_AUTHORIZED_PERMISSIONS] = authorized_permissions
    else:
        unauthorized_permissions.add(permission)
        st.session_state[USER_UNAUTHORIZED_PERMISSIONS] = unauthorized_permissions

    return has_permission


def authenticated(user: User | None = None) -> bool:
    r"""Check if the current user is authenticated.

    Parameters
    ----------
    user : streamlit_passwordless.User or None, default None
        The user for which to check the authentication status.
        The default option is to fetch the current user from the
        session state.
    """

    if st.session_state.get(AUTHENTICATED, False) is True:
        return True

    user = stp.get_current_user() if user is None else user

    return user is not None and user.is_authenticated
