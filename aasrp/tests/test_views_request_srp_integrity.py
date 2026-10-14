"""
Tests for the integrity of SRP request creation in aasrp/views/general.py
"""

# Standard Library
from contextlib import redirect_stdout
from http import HTTPStatus
from importlib import import_module
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

# Third Party
from eve_sde.models import ItemType

# Django
from django.apps import apps as django_apps
from django.contrib.messages import get_messages
from django.db import DatabaseError, IntegrityError, connection
from django.test import Client
from django.urls import reverse
from django.utils import timezone

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# AA SRP
from aasrp.models import Insurance, RequestComment, Setting, SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user, random_id

migration_0004 = import_module("aasrp.migrations.0004_srprequest_killmail_id")


class TestRequestSrpSaveIntegrity(BaseTestCase):
    """
    SRP request creation must be all-or-nothing, and a killmail can only have one SRP request.
    """

    KILLMAIL_ID = 987654321
    KILLBOARD_LINK = f"https://zkillboard.com/kill/{KILLMAIL_ID}/"

    @classmethod
    def setUpTestData(cls):
        """
        Set up a user owning the victim character, a ship type and an active SRP link.

        :return:
        :rtype:
        """

        cls.victim_id = random_id()
        cls.user = create_fake_user(
            character_id=cls.victim_id,
            character_name="Integrity Victim",
            permissions=["aasrp.basic_access"],
        )
        cls.user.character_ownerships.get_or_create(
            character=EveCharacter.objects.get(character_id=cls.victim_id)
        )
        cls.ship = ItemType.objects.create(id=587, name="Rifter")
        cls.srp_link = SrpLink.objects.create(
            srp_name="Integrity Fleet",
            srp_code="INTEGRITY001",
            srp_status=SrpLink.Status.ACTIVE,
            creator=cls.user,
            fleet_time=timezone.now(),
        )

        setting = Setting.get_solo()
        setting.loss_value_source = "totalValue"
        setting.save()

    def setUp(self):
        """
        Mock upstream lookups and use a client that returns 500 responses instead of raising.

        :return:
        :rtype:
        """

        self.client = Client(raise_request_exception=False)
        self.client.force_login(self.user)

        kill_data_patcher = patch(
            "aasrp.managers.SrpRequestManager.get_kill_data",
            return_value={
                "ship_type_id": self.ship.id,
                "ship_value": 1000000,
                "victim_id": self.victim_id,
            },
        )
        self.mock_get_kill_data = kill_data_patcher.start()
        self.addCleanup(kill_data_patcher.stop)

        insurance_patcher = patch(
            "aasrp.managers.SrpRequestManager.get_insurance_for_ship_type",
            return_value=SimpleNamespace(
                levels=[
                    SimpleNamespace(name="Basic", cost=100.0, payout=1000.0),
                    SimpleNamespace(name="Platinum", cost=500.0, payout=5000.0),
                ]
            ),
        )
        insurance_patcher.start()
        self.addCleanup(insurance_patcher.stop)

        notify_patcher = patch("aasrp.views.general.notify_srp_team")
        notify_patcher.start()
        self.addCleanup(notify_patcher.stop)

    def _post_killmail(self, client=None):
        return (client or self.client).post(
            reverse("aasrp:request_srp", args=[self.srp_link.srp_code]),
            data={
                "killboard_link": self.KILLBOARD_LINK,
                "additional_info": "Lost it in fleet",
            },
        )

    def _requests_for_killmail(self):
        return SrpRequest.objects.filter(
            killboard_link__icontains=f"/kill/{self.KILLMAIL_ID}"
        )

    def test_valid_submission_creates_request_with_insurance(self):
        """
        Control: without failures, a submission creates one request with comments and insurance.

        :return:
        :rtype:
        """

        self._post_killmail()

        srp_request = self._requests_for_killmail().get()
        self.assertEqual(
            RequestComment.objects.filter(srp_request=srp_request).count(), 2
        )
        self.assertEqual(Insurance.objects.filter(srp_request=srp_request).count(), 2)

    def test_failed_save_leaves_no_partial_request(self):
        """
        A failure on the last write must roll back the SrpRequest and its comments.

        :return:
        :rtype:
        """

        with patch.object(
            Insurance.objects,
            "bulk_create",
            side_effect=DatabaseError("simulated failure"),
        ):
            self._post_killmail()

        self.assertFalse(self._requests_for_killmail().exists())
        self.assertFalse(
            RequestComment.objects.filter(
                srp_request__killboard_link__icontains=f"/kill/{self.KILLMAIL_ID}"
            ).exists()
        )

    def test_pilot_can_resubmit_after_failed_save(self):
        """
        After a failed save, resubmitting the same killmail must not be rejected as a duplicate.

        :return:
        :rtype:
        """

        with patch.object(
            Insurance.objects,
            "bulk_create",
            side_effect=DatabaseError("simulated failure"),
        ):
            self._post_killmail()

        self._post_killmail()

        srp_requests = self._requests_for_killmail()
        self.assertEqual(srp_requests.count(), 1)
        self.assertEqual(
            Insurance.objects.filter(srp_request=srp_requests.get()).count(), 2
        )

    def test_concurrent_submissions_create_only_one_request(self):
        """
        Two submissions that both pass the duplicate check must not create two requests.

        The second submission runs to completion after the first one has passed form
        validation, but before it writes to the database.

        :return:
        :rtype:
        """

        kill_data = self.mock_get_kill_data.return_value
        second_client = Client(raise_request_exception=False)
        second_client.force_login(self.user)

        def submit_concurrently(*args, **kwargs):
            self.mock_get_kill_data.side_effect = None
            self._post_killmail(client=second_client)

            return kill_data

        self.mock_get_kill_data.side_effect = submit_concurrently

        response = self._post_killmail()

        self.assertEqual(self._requests_for_killmail().count(), 1)
        self.assertNotEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn(
            "There is already an SRP request for this kill mail.",
            [str(message) for message in get_messages(response.wsgi_request)][0],
        )

    def test_integrity_error_without_duplicate_is_not_swallowed(self):
        """
        An IntegrityError not caused by a duplicate kill mail must not be reported as one.

        :return:
        :rtype:
        """

        with (
            patch.object(
                RequestComment.objects,
                "bulk_create",
                side_effect=IntegrityError("simulated failure"),
            ),
            self.assertLogs("django.request", level="ERROR"),
        ):
            response = self._post_killmail()

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertFalse(self._requests_for_killmail().exists())


class TestKillmailIdBackfillMigration(BaseTestCase):
    """
    Test the kill mail ID backfill in migration 0004
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up a user, a ship type and an SRP link to attach SRP requests to.

        :return:
        :rtype:
        """

        cls.character_id = random_id()
        cls.user = create_fake_user(
            character_id=cls.character_id, character_name="Backfill Pilot"
        )
        cls.character = EveCharacter.objects.get(character_id=cls.character_id)
        cls.ship = ItemType.objects.create(id=587, name="Rifter")
        cls.srp_link = SrpLink.objects.create(
            srp_name="Backfill Fleet",
            srp_code="BACKFILL001",
            creator=cls.user,
            fleet_time=timezone.now(),
        )

    def _create_srp_request(self, killboard_link):
        return SrpRequest.objects.create(
            killboard_link=killboard_link,
            creator=self.user,
            character=self.character,
            ship=self.ship,
            srp_link=self.srp_link,
            post_time=timezone.now(),
        )

    def test_backfills_killmail_id_and_skips_duplicates_and_unparsable_links(self):
        """
        The oldest request for a kill mail gets the ID, later duplicates and links without an ID stay NULL.

        :return:
        :rtype:
        """

        original = self._create_srp_request("https://zkillboard.com/kill/111/")
        duplicate = self._create_srp_request("https://zkillboard.com/kill/111/")
        other = self._create_srp_request("https://eve-kill.com/kill/222")
        unparsable = self._create_srp_request("https://zkillboard.com/kill/")

        with redirect_stdout(StringIO()) as output:
            migration_0004._backfill_killmail_id(
                apps=django_apps,
                schema_editor=SimpleNamespace(connection=connection),
            )

        for srp_request in (original, duplicate, other, unparsable):
            srp_request.refresh_from_db()

        self.assertEqual(original.killmail_id, 111)
        self.assertIsNone(duplicate.killmail_id)
        self.assertEqual(other.killmail_id, 222)
        self.assertIsNone(unparsable.killmail_id)
        self.assertIn(duplicate.request_code, output.getvalue())
        self.assertIn(unparsable.request_code, output.getvalue())
