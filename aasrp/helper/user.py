"""
User helper module.

This module provides utility functions for working with user-related data in the AA SRP application.
"""

# Django
from django.db.models import QuerySet

# Alliance Auth
from allianceauth.authentication.models import User
from allianceauth.eveonline.models import EveCharacter
from esi.models import Token

# AA SRP
from aasrp.constants import ESI_SCOPE_UI_OPEN_WINDOW
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


def get_pending_requests_count_for_user(user: User) -> int | None:
    """
    Retrieve the count of pending SRP (Ship Replacement Program) requests for the current user.

    :param user: The user object for whom to count pending SRP requests.
    :type user: User
    :return: The count of pending SRP requests for the user, or None if there are no pending requests.
    :rtype: int | None
    """

    return SrpRequest.pending_requests_count_for_user(user=user)


def get_ui_characters_for_user(user: User) -> QuerySet[EveCharacter]:
    """
    Retrieve the characters of a user that can be used to open windows in the EVE client.

    Only characters owned by the user, with a token holding the UI scope, are returned.

    :param user: The user object for whom to retrieve the characters.
    :type user: User
    :return: A queryset of EveCharacter objects.
    :rtype: QuerySet[EveCharacter]
    """

    character_ids = (
        Token.objects.filter(user=user)
        .require_scopes([ESI_SCOPE_UI_OPEN_WINDOW])
        .values_list("character_id", flat=True)
    )

    return EveCharacter.objects.filter(
        character_ownership__user=user, character_id__in=list(character_ids)
    ).order_by("character_name")


def get_ui_token_for_user(user: User, character: EveCharacter | None) -> Token | None:
    """
    Retrieve a valid UI token for the given character, owned by the given user.

    :param user: The user object who owns the token.
    :type user: User
    :param character: The character to get the token for.
    :type character: EveCharacter | None
    :return: A valid token, or None if there is none.
    :rtype: Token | None
    """

    if character is None:
        return None

    return (
        Token.objects.filter(user=user, character_id=character.character_id)
        .require_scopes([ESI_SCOPE_UI_OPEN_WINDOW])
        .require_valid()
        .first()
    )
