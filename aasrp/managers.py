"""
SRP Manager
This module contains custom managers for handling SRP (Ship Replacement Program) requests and settings.
"""

# Standard Library
import json
import re
from typing import Any
from urllib.parse import urlsplit

# Third Party
import requests
from httpx2 import Response

# Django
from django.db import models
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA SRP
from aasrp.app_settings import killboard_settings
from aasrp.constants import KILLBOARD_DATA, REQUESTS_TIMEOUT, UserAgent
from aasrp.providers.applogger import AppLogger
from aasrp.providers.esi import ESIHandler, esi

# Initialize a logger with a custom tag for the AA-SRP module
logger = AppLogger(my_logger=get_extension_logger(__name__))


class SrpRequestManager(models.Manager):
    """
    Custom manager for handling SRP requests.
    Provides methods to interact with zKillboard and ESI for retrieving killmail data.
    """

    @staticmethod
    def get_killmail_id(killmail_link: str) -> str:
        """
        Extract the killmail ID from a killmail link.

        :param killmail_link: The killboard link containing the killmail ID.
        :type killmail_link: str
        :return: The extracted killmail ID.
        :rtype: str
        :raises ValueError: If the link does not contain a numeric killmail ID.
        """

        parts = urlsplit(killmail_link).path.split("/")
        kill_id = next(
            (
                value
                for segment, value in zip(parts, parts[1:])
                if segment in ("kill", "killmails")
                and value.isascii()
                and value.isdecimal()
            ),
            None,
        )

        if kill_id is None:
            raise ValueError(_("Invalid link. Please post a link to a kill mail."))

        return kill_id

    @staticmethod
    def _get_killmail_info_from_zkill_json(
        zkill_json: list[dict[str, Any]], killmail_id: str
    ) -> dict[str, Any]:
        """
        Extract killmail information from zKillboard's JSON response.

        :param zkill_json: The JSON response from zKillboard.
        :type zkill_json: str
        :param killmail_id: The ID of the killmail to extract.
        :type killmail_id: str
        :return: The killmail information.
        :rtype: dict
        """

        logger.debug(
            f"Extracting killmail info for kill ID {killmail_id} from zKillboard JSON response: {zkill_json}"
        )

        try:
            result = next(
                (
                    killmail
                    for killmail in zkill_json
                    if killmail.get("killmail_id") == int(killmail_id)
                ),
                None,
            )

            if not result:
                raise ValueError(
                    _(
                        "No kill mail information found in zKillboard's API response. "
                        "Try again in an hour or two, or check the kill mail link."
                    )
                )

            killmail_hash = result.get("zkb", {}).get("hash")

            if not killmail_hash:
                raise ValueError(
                    _(
                        "No kill mail hash found in zKillboard's API response. "
                        "Try again in an hour or two, or check the kill mail link."
                    )
                )

            return result
        except ValueError:
            # Propagate ValueError from missing data/hash as-is
            raise
        except Exception as exc:
            # Any other unexpected exception
            raise ValueError(_("Invalid Kill ID or Hash.")) from exc

    @staticmethod
    def get_zkillboard_data(kill_id: str) -> dict | None:
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
                timeout=REQUESTS_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning(f"Error fetching kill mail details: {exc}", exc_info=True)
            raise ValueError(
                _(
                    "zKillboard is not responding at the moment. "
                    "Please try again in an hour."
                )
            ) from exc

        try:
            result_killmails = response.json()
        except json.JSONDecodeError as ex:
            # Response could not be parsed as JSON
            logger.warning(
                f"zKillboard API returned a non-parsable JSON for kill ID {kill_id}: {response.text[:200]}"
            )
            raise ValueError(
                _("zKillboard API returned an unparseable response")
            ) from ex

        return SrpRequestManager._get_killmail_info_from_zkill_json(
            result_killmails, killmail_id=kill_id
        )

    @staticmethod
    def get_killmail_data(
        killmail_link: str, loss_value_field: str
    ) -> dict[str, int | Any]:
        """
        Retrieve detailed killmail data, including ship type, loss value, and victim ID.

        :param killmail_link: The link to the killmail, from which the kill ID will be extracted.
        :type killmail_link: str
        :param loss_value_field: The field name for the loss value in the zKillboard data.
        :type loss_value_field: str
        :return: A tuple containing the ship type ID, loss value, and victim character ID.
                    - `ship_type_id`: The ID of the ship type involved in the killmail.
                    - `loss_value`: The value of the loss as retrieved from zKillboard.
                    - `victim_id`: The character ID of the victim in the killmail.
        :rtype: dict[str, int | float | None]
        """

        killmail_id = SrpRequestManager.get_killmail_id(killmail_link=killmail_link)
        zkillboard_post_esi = killboard_settings("zkillboard_post_esi")
        logger.debug("zKillboard Post ESI Settings: %s", zkillboard_post_esi)

        base_url_match = re.match(zkillboard_post_esi["base_url_regex"], killmail_link)

        if base_url_match:
            logger.debug(
                f"Kill ID {killmail_id}: ESI killmail link. Posting to zKillboard for data retrieval."
            )

            # Remove the regex-matched base URL prefix from the killmail link.
            zkill_post = killmail_link[base_url_match.end() :]

            try:
                response = requests.post(
                    url=zkillboard_post_esi["api_url"] + zkill_post,
                    headers={
                        "User-Agent": UserAgent.REQUESTS.value,
                        "Content-Type": "application/json",
                    },
                    timeout=REQUESTS_TIMEOUT,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                logger.warning(
                    f"Error fetching kill mail details: {exc}", exc_info=True
                )

                raise ValueError(
                    _(
                        "zKillboard is not responding at the moment. "
                        "Please try again in an hour."
                    )
                ) from exc

            try:
                result_killmails = response.json()

                logger.debug(
                    f"Kill ID {killmail_id}: zKillboard post response: {response.status_code} - {result_killmails.get('package')}"
                )
            except json.JSONDecodeError as ex:
                # Response could not be parsed as JSON
                logger.warning(
                    f"zKillboard API returned a non-parsable JSON for kill ID {killmail_id}: {response.text}"
                )

                raise ValueError(
                    _("zKillboard API returned an unparseable response")
                ) from ex

            zkillboard_data = SrpRequestManager._get_killmail_info_from_zkill_json(
                result_killmails.get("package"), killmail_id
            )
        else:
            logger.debug(
                f"Kill ID {killmail_id}: Non-ESI killmail link. Fetching data directly from zKillboard."
            )

            zkillboard_data = SrpRequestManager.get_zkillboard_data(kill_id=killmail_id)

        logger.debug(
            f"Kill ID {killmail_id}: zKillboard data retrieved: {zkillboard_data}"
        )

        # if (
        #     esi_killmail := ESIHandler.result(
        #         operation=esi.client.Killmails.GetKillmailsKillmailIdKillmailHash(
        #             killmail_id=killmail_id,
        #             killmail_hash=zkillboard_data.get("zkb", {}).get("hash"),
        #         ),
        #         use_etag=False,
        #     )
        # ) is None:
        #     raise ValueError(
        #         _(
        #             "Unable to fetch kill mail details from ESI. "
        #             "Please try again in an hour."
        #         )
        #     )

        # victim_id = esi_killmail.victim.character_id
        # ship_type_id = esi_killmail.victim.ship_type_id
        victim_id = zkillboard_data.get("victim", {}).get("character_id")
        ship_type_id = zkillboard_data.get("victim", {}).get("ship_type_id")
        ship_value = zkillboard_data.get("zkb", {}).get(loss_value_field, 0)

        logger.debug(
            f"Kill ID {killmail_id}: Victim ID = {victim_id}, Ship type = {ship_type_id}, Loss value = {ship_value}"
        )

        return {
            "killmail_id": killmail_id,
            "ship_type_id": ship_type_id,
            "ship_value": ship_value,
            "victim_id": victim_id,
        }

    @staticmethod
    def get_insurance_for_ship_type(ship_type_id: int) -> Response | None:
        """
        Retrieve insurance details for a given ship type ID from the ESI.

        :param ship_type_id: The ID of the ship type to fetch insurance for.
        :type ship_type_id: int
        :return: The insurance details for the ship type, or None if not found.
        :rtype: dict | None
        """

        if (
            insurance_from_esi := ESIHandler.result(
                operation=esi.client.Insurance.GetInsurancePrices(), use_etag=False
            )
        ) is None:
            logger.warning(
                f"Unable to fetch insurance prices from ESI for ship type {ship_type_id}"
            )

            return None

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

        instance = self.get_queryset().first()

        if instance is None:
            return None

        return getattr(instance, setting_key, None)

    def get_queryset(self) -> SettingQuerySet:
        """
        Retrieve the custom queryset for managing settings.

        :return: A SettingQuerySet instance.
        :rtype: SettingQuerySet
        """

        return SettingQuerySet(self.model)
