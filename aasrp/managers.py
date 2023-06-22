"""
SRP Manager
"""

# Third Party
import requests

# Django
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.constants import USERAGENT, ZKILLBOARD_API_URL
from aasrp.providers import esi

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class SrpManager:
    """
    AaSrpManager
    """

    @staticmethod
    def get_kill_id(killboard_link: str):
        """
        Get killmail ID from zKillboard link
        :param killboard_link:
        :return:
        """

        num_set = "0123456789"
        kill_id = "".join(c for c in killboard_link if c in num_set)

        return kill_id

    @staticmethod
    def get_kill_data(kill_id: str):
        """
        Get kill data from zKillboard
        :param kill_id:
        :return:
        """

        url = f"{ZKILLBOARD_API_URL}killID/{kill_id}/"

        headers = {
            "User-Agent": USERAGENT,
            "Content-Type": "application/json",
        }

        try:
            request_result = requests.get(url, headers=headers, timeout=5)
            result = request_result.json()[0]
        except IndexError as exc:
            raise ValueError("Invalid Kill ID") from exc

        if result:
            killmail_id = result["killmail_id"]
            killmail_hash = result["zkb"]["hash"]

            esi_killmail = esi.client.Killmails.get_killmails_killmail_id_killmail_hash(
                killmail_id=killmail_id, killmail_hash=killmail_hash
            ).result()
        else:
            raise ValueError("Invalid Kill ID")

        if esi_killmail:
            ship_type = esi_killmail["victim"]["ship_type_id"]
            logger.debug(f"Ship type for kill ID {kill_id} is {ship_type}")
            ship_value = result["zkb"]["totalValue"]

            logger.debug(f"Total loss value for kill id {kill_id} is {ship_value}")

            victim_id = esi_killmail["victim"]["character_id"]

            return ship_type, ship_value, victim_id

        raise ValueError(_("Invalid Kill ID or Hash."))

    @staticmethod
    def pending_requests_count_for_user(user: User):
        """
        Returns the number of open SRP requests for given user
        or None if user has no permission
        """

        # AA SRP
        from aasrp.models import SrpRequest

        if user.has_perm("aasrp.manage_srp") or user.has_perm(
            "aasrp.manage_srp_requests"
        ):
            return SrpRequest.objects.filter(
                request_status=SrpRequest.Status.PENDING
            ).count()

        return None

    @staticmethod
    def get_insurance_for_ship_type(ship_type_id: int):
        """
        Getting insurance for a given ship type ID from ESI
        :param ship_type_id:
        :type ship_type_id:
        """

        insurance_prices = esi.client.Insurance.get_insurance_prices().result()

        for insurance in insurance_prices:
            if insurance["type_id"] == ship_type_id:
                return insurance

        return None


class SettingQuerySet(models.QuerySet):
    """
    SettingQuerySet
    """

    def delete(self):
        """
        Delete action

        Override:   We don't allow deletion here, so we make sure the object
                    is saved again and not deleted
        :return:
        """

        return super().update()


class SettingManager(models.Manager):
    """
    SettingManager
    """

    def get_setting(self, setting_key: str) -> str:
        """
        Return the value for given setting key
        :param setting_key:
        :return:
        """

        return getattr(self.first(), setting_key)

    def get_queryset(self):
        """
        Get a Setting queryset
        :return:
        """

        return SettingQuerySet(self.model)
