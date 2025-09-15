"""
SRP Manager
"""

# Standard Library
from typing import Any

# Third Party
import requests

# Django
from django.db import models

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.constants import KILLBOARD_DATA, UserAgent
from aasrp.providers import esi

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


class SrpRequestManager(models.Manager):
    """
    SrpRequestManager
    """

    @staticmethod
    def get_kill_id(killboard_link: str) -> str:
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
    def get_zkillboard_data(kill_id: str) -> dict:
        """
        Get killmail hash from zKillboard

        :param kill_id:
        :type kill_id:
        :return:
        :rtype:
        """

        zkillboard_api_url = KILLBOARD_DATA["zKillboard"]["api_url"]
        killmail_api_url = f"{zkillboard_api_url}killID/{kill_id}/"

        try:
            response = requests.get(
                url=killmail_api_url,
                headers={
                    "User-Agent": UserAgent.REQUESTS.value,
                    "Content-Type": "application/json",
                },
                timeout=5,
            )
            response.raise_for_status()
            result_killmails = response.json()

            result = next(
                (
                    killmail
                    for killmail in result_killmails
                    if killmail.get("killmail_id") == int(kill_id)
                ),
                None,
            )

            if not result:
                raise ValueError(
                    "No kill mail information found in zKillboard's API response."
                )

            killmail_hash = result.get("zkb", {}).get("hash")

            if not killmail_hash:
                raise ValueError(
                    "No kill mail hash found in zKillboard's API response."
                )

            return result

        except (requests.HTTPError, requests.Timeout) as exc:
            logger.warning(f"Error fetching kill mail details: {exc}", exc_info=True)

            raise ValueError(str(exc)) from exc
        except Exception as exc:
            raise ValueError("Invalid Kill ID or Hash.") from exc

    @staticmethod
    def get_kill_data(killmail_id: str, loss_value_field: str) -> tuple[int, int, int]:
        """
        Get kill data from zKillboard

        :param killmail_id:
        :type killmail_id:
        :param loss_value_field:
        :type loss_value_field:
        :return:
        :rtype:
        """

        zkillboard_data = SrpRequestManager.get_zkillboard_data(kill_id=killmail_id)

        esi_killmail = esi.client.Killmails.GetKillmailsKillmailIdKillmailHash(
            killmail_id=killmail_id,
            killmail_hash=zkillboard_data.get("zkb", {}).get("hash"),
        ).result()

        logger.info(
            f"Fetched kill mail details for Kill ID {killmail_id} from ESI: {esi_killmail}"
        )

        ship_type = esi_killmail.victim.ship_type_id
        ship_value = zkillboard_data.get("zkb", {}).get(loss_value_field, 0)
        victim_id = esi_killmail.victim.character_id

        logger.debug(
            f"Kill ID {killmail_id}: Ship type = {ship_type}, Loss value = {ship_value}"
        )

        return ship_type, ship_value, victim_id

    @staticmethod
    def get_insurance_for_ship_type(ship_type_id: int) -> dict | None:
        """
        Getting insurance for a given ship type ID from ESI

        :param ship_type_id:
        :type ship_type_id:
        :return:
        :rtype:
        """

        insurance = next(
            (
                i
                for i in list(esi.client.Insurance.GetInsurancePrices().result())
                if i.type_id == ship_type_id
            ),
            None,
        )

        return insurance


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

    def get_setting(self, setting_key: str) -> Any:
        """
        Return the value for given setting key

        :param setting_key:
        :type setting_key:
        :return:
        :rtype:
        """

        return getattr(self.first(), setting_key)

    def get_queryset(self) -> SettingQuerySet:
        """
        Get a Setting queryset

        :return:
        :rtype:
        """

        return SettingQuerySet(self.model)
