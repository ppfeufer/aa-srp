"""
User helper module.

This module provides utility functions for working with user-related data in the AA SRP application.
"""

# Django
from django.contrib.auth.models import AbstractUser, AnonymousUser, User

# AA SRP
from aasrp.models import SrpRequest, UserSetting


def get_user_settings(user: User) -> UserSetting:
    """
    Retrieve or create a user's settings.

    This function fetches the settings associated with a given user. If the settings do not exist,
    they are created automatically.

    :param user: The user object for which settings are to be retrieved or created.
    :type user: User
    :return: The user's settings object.
    :rtype: UserSetting
    """

    return UserSetting.objects.get_or_create(user=user)[0]


def get_pending_requests_count_for_user(
    user: User | AbstractUser | AnonymousUser,
) -> int | None:
    """
    Retrieve the count of pending SRP (Ship Replacement Program) requests for the current user.

    :param user: The user object for whom to count pending SRP requests.
    :type user: User
    :return: The count of pending SRP requests for the user, or None if there are no pending requests.
    :rtype: int | None
    """

    return SrpRequest.pending_requests_count_for_user(user=user)
