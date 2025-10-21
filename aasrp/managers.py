"""
SRP Manager
This module contains custom managers for handling SRP (Ship Replacement Program) requests and settings.
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

# Initialize a logger with a custom tag for the AA-SRP module
logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


class SrpRequestManager(models.Manager):
    """
    Custom manager for handling SRP requests.
    Provides methods to interact with zKillboard and ESI for retrieving killmail data.
    """

    @staticmethod
    def get_kill_id(killboard_link: str) -> str:
        """
        Extract the killmail ID from a killboard link.

        :param killboard_link: The killboard link containing the killmail ID.
        :type killboard_link: str
        :return: The extracted killmail ID.
        :rtype: str
        """

        num_set = "0123456789"
        kill_id = "".join(c for c in killboard_link if c in num_set)

        return kill_id

    @staticmethod
    def get_zkillboard_data(kill_id: str) -> dict:
        """
        Retrieve killmail data from the zKillboard API.

        :param kill_id: The ID of the killmail to fetch.
        :type kill_id: str
        :return: The killmail data retrieved from zKillboard.
        :rtype: dict
        :raises ValueError: If no data or hash is found in the API response.
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
        Retrieve detailed killmail data, including ship type, loss value, and victim ID.

        :param killmail_id: The ID of the killmail to fetch.
        :type killmail_id: str
        :param loss_value_field: The field name for the loss value in the zKillboard data.
        :type loss_value_field: str
        :return: A tuple containing the ship type ID, loss value, and victim character ID.
        :rtype: tuple[int, int, int]
        """

        zkillboard_data = SrpRequestManager.get_zkillboard_data(kill_id=killmail_id)

        esi_killmail = esi.client.Killmails.GetKillmailsKillmailIdKillmailHash(
            killmail_id=killmail_id,
            killmail_hash=zkillboard_data.get("zkb", {}).get("hash"),
        ).result(force_refresh=True)

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
        Retrieve insurance details for a given ship type ID from the ESI.

        :param ship_type_id: The ID of the ship type to fetch insurance for.
        :type ship_type_id: int
        :return: The insurance details for the ship type, or None if not found.
        :rtype: dict | None
        """

        insurance_from_esi = esi.client.Insurance.GetInsurancePrices().result(
            force_refresh=True
        )

        insurance = next(
            (i for i in insurance_from_esi if i.type_id == ship_type_id),
            None,
        )

        return insurance


class SettingQuerySet(models.QuerySet):
    """
    Custom queryset for managing settings.
    Overrides the delete method to prevent deletion of settings.
    """

    def delete(self):
        """
        Override the delete method to prevent deletion of settings.
        Instead, the object is updated and not deleted.

        :return: The result of the update operation.
        :rtype: int
        """

        return super().update()


class SettingManager(models.Manager):
    """
    Custom manager for handling application settings.
    Provides methods to retrieve and manage settings.
    """

    def get_setting(self, setting_key: str) -> Any:
        """
        Retrieve the value of a specific setting by its key.

        :param setting_key: The key of the setting to retrieve.
        :type setting_key: str
        :return: The value of the setting.
        :rtype: Any
        """

        return getattr(self.first(), setting_key)

    def get_queryset(self) -> SettingQuerySet:
        """
        Retrieve the custom queryset for managing settings.

        :return: A SettingQuerySet instance.
        :rtype: SettingQuerySet
        """

        return SettingQuerySet(self.model)
