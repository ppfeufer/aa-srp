"""
Helper for our tests
"""

# Standard Library
import re

# Third Party
from faker import Faker

# Django
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA SRP
from aasrp.models import FleetType, Setting

fake = Faker()


def create_fake_user(
    character_id: int,
    character_name: str,
    corporation_id: int = None,
    corporation_name: str = None,
    corporation_ticker: str = None,
    permissions: list[str] = None,
    **kwargs,
) -> User:
    """
    Create a fake user incl. Main character and (optional) permissions.

    :param character_id:
    :type character_id:
    :param character_name:
    :type character_name:
    :param corporation_id:
    :type corporation_id:
    :param corporation_name:
    :type corporation_name:
    :param corporation_ticker:
    :type corporation_ticker:
    :param permissions:
    :type permissions:
    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """

    username = re.sub(pattern=r"[^\w\d@\.\+-]", repl="_", string=character_name)
    user = AuthUtils.create_user(username=username)

    if not corporation_id:
        corporation_id = 2001
        corporation_name = "Wayne Technologies Inc."
        corporation_ticker = "WTE"

    alliance_id = kwargs.get("alliance_id", 3001)
    alliance_name = (
        kwargs.get("alliance_name", "Wayne Enterprises")
        if alliance_id is not None
        else ""
    )

    AuthUtils.add_main_character_2(
        user=user,
        name=character_name,
        character_id=character_id,
        corp_id=corporation_id,
        corp_name=corporation_name,
        corp_ticker=corporation_ticker,
        alliance_id=alliance_id,
        alliance_name=alliance_name,
    )

    if permissions:
        perm_objs = [
            AuthUtils.get_permission_by_name(perm=perm) for perm in permissions
        ]
        user = AuthUtils.add_permissions_to_user(perms=perm_objs, user=user)

    return user


def get_or_create_fake_user(*args, **kwargs) -> User:
    """
    Same as create_fake_user but will not fail when user already exists.

    :param args:
    :type args:
    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """

    if len(args) > 1:
        character_name = args[1]
    elif "character_name" in kwargs:
        character_name = kwargs["character_name"]
    else:
        ValueError("character_name is not defined")

    username = character_name.replace("'", "").replace(" ", "_")

    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return create_fake_user(*args, **kwargs)


def create_fleettype(**kwargs) -> FleetType:
    """
    Create a fleet type

    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """

    if "name" not in kwargs:
        kwargs["name"] = fake.name()

    return FleetType.objects.create(**kwargs)


def create_setting(**kwargs) -> Setting:
    """
    Create setting

    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """

    return Setting.objects.create(**kwargs)


def get_permission_content_type():
    """
    Get the content type for the permission.

    :return:
    :rtype:
    """

    return ContentType.objects.filter(app_label="aasrp", model="aasrp").get()
