"""
SRP Manager
"""

# pylint: disable=cyclic-import

# Third Party
import requests

# Django
from django.contrib.auth.models import User
from django.db import models

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
        :type killboard_link:
        :return:
        :rtype:
        """

        num_set = "0123456789"
        kill_id = "".join(c for c in killboard_link if c in num_set)

        return kill_id

    @staticmethod
    def get_kill_data(kill_id: str):
        """
        Get kill data from zKillboard

        :param kill_id:
        :type kill_id:
        :return:
        :rtype:
        """

        url = f"{ZKILLBOARD_API_URL}killID/{kill_id}/"
        headers = {"User-Agent": USERAGENT, "Content-Type": "application/json"}
        request_result = requests.get(url=url, headers=headers, timeout=5)

        try:
            request_result.raise_for_status()
        except requests.HTTPError as exc:
            error_str = str(exc)

            logger.warning(
                msg=f"Unable to get killmail details from zKillboard. Error: {error_str}",
                exc_info=True,
            )

            raise ValueError(error_str) from exc
        except requests.Timeout as exc:
            error_str = str(exc)

            logger.warning(msg="Connection to zKillboard timed out …")

            raise ValueError(error_str) from exc

        result = request_result.json()[0]

        try:
            killmail_id = result["killmail_id"]
            killmail_hash = result["zkb"]["hash"]

            esi_killmail = esi.client.Killmails.get_killmails_killmail_id_killmail_hash(
                killmail_id=killmail_id, killmail_hash=killmail_hash
            ).result()
        except Exception as exc:
            raise ValueError("Invalid Kill ID or Hash.") from exc

        ship_type = esi_killmail["victim"]["ship_type_id"]
        ship_value = result["zkb"]["totalValue"]

        logger.debug(msg=f"Ship type for kill ID {kill_id} is {ship_type}")
        logger.debug(msg=f"Total loss value for kill id {kill_id} is {ship_value}")

        victim_id = esi_killmail["victim"]["character_id"]

        return ship_type, ship_value, victim_id

    @staticmethod
    def pending_requests_count_for_user(user: User):
        """
        Returns the number of open SRP requests for given user
        or None if user has no permission

        :param user:
        :type user:
        :return:
        :rtype:
        """

        # AA SRP
        from aasrp.models import SrpRequest  # pylint: disable=import-outside-toplevel

        if user.has_perm(perm="aasrp.manage_srp") or user.has_perm(
            perm="aasrp.manage_srp_requests"
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
        :return:
        :rtype:
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

        Override:
            We don't allow deletion here, so we make sure the object
            is saved again and not deleted

        :return:
        :rtype:
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
        :type setting_key:
        :return:
        :rtype:
        """

        return getattr(self.first(), setting_key)

    def get_queryset(self):
        """
        Get a Setting queryset

        :return:
        :rtype:
        """

        return SettingQuerySet(self.model)
