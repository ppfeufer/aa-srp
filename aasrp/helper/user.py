"""
User helper
"""

# Django
from django.contrib.auth.models import User

# AA SRP
from aasrp.models import AaSrpUserSettings


def get_user_settings(user: User) -> AaSrpUserSettings:
    """
    Get a users settings or create them
    :param user:
    :return:
    """

    user_settings, _ = AaSrpUserSettings.objects.get_or_create(user=user)

    return user_settings
