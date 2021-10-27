"""
SRP Manager
"""

import requests

from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from allianceauth.services.hooks import get_extension_logger

from aasrp import __title__
from aasrp.constants import USERAGENT, ZKILLBOARD_API_URL
from aasrp.models import AaSrpRequest, AaSrpRequestStatus
from aasrp.providers import esi
from aasrp.utils import LoggerAddTag

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class AaSrpManager:
    """
    AaSrpManager
    """

    @staticmethod
    def get_kill_id(killboard_link: str):
        """
        get killmail ID from zKillboard link
        :param killboard_link:
        :return:
        """

        num_set = "0123456789"
        kill_id = "".join(c for c in killboard_link if c in num_set)

        return kill_id

    @staticmethod
    def get_kill_data(kill_id: str):
        """
        get kill data from zKillboard
        :param kill_id:
        :return:
        """

        url = f"{ZKILLBOARD_API_URL}killID/{kill_id}/"

        headers = {
            "User-Agent": USERAGENT,
            "Content-Type": "application/json",
        }

        try:
            request_result = requests.get(url, headers=headers)
            result = request_result.json()[0]
        except IndexError:
            raise ValueError("Invalid Kill ID")

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
        returns the number of open SRP requests for given user
        or None if user has no permission
        """

        if user.has_perm("aasrp.manage_srp") or user.has_perm(
            "aasrp.manage_srp_requests"
        ):
            return AaSrpRequest.objects.filter(
                request_status=AaSrpRequestStatus.PENDING
            ).count()

        return None

    @staticmethod
    def get_insurance_for_ship_type(ship_type_id: int):
        """
        getting insurance for a given ship type ID from ESI
        :param ship_type_id:
        :type ship_type_id:
        """

        insurance_prices = esi.client.Insurance.get_insurance_prices().result()

        for insurance in insurance_prices:
            if insurance["type_id"] == ship_type_id:
                return insurance

        return None
