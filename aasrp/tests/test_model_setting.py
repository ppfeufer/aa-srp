"""
Tests for model Setting
"""

# Django
from django.db.utils import IntegrityError
from django.test import TestCase

# AA SRP
from aasrp.models import Setting
from aasrp.tests.utils import create_setting


class TestSetting(TestCase):
    """
    Testing the Setting model
    """

    def test_model_string_name(self):
        """
        Test model string name

        :return:
        :rtype:
        """

        # given
        setting = Setting.objects.get(pk=1)

        # when/then
        self.assertEqual(first=str(setting), second="AA-SRP Settings")

    def test_setting_save(self):
        """
        Test if there can't be another setting created
        and the existing setting is changed instead

        :return:
        :rtype:
        """

        # given
        srp_team_discord_channel_id = 45698741256
        setting = Setting(pk=2, srp_team_discord_channel_id=srp_team_discord_channel_id)
        setting.save()

        # then
        self.assertEqual(first=setting.pk, second=1)
        self.assertEqual(
            first=setting.srp_team_discord_channel_id,
            second=srp_team_discord_channel_id,
        )

    def test_setting_create(self):
        """
        Test that create method throwing the following exception
        django.db.utils.IntegrityError: (1062, "Duplicate entry '1' for key 'PRIMARY'")

        :return:
        :rtype:
        """

        # No pk given
        with self.assertRaises(expected_exception=IntegrityError):
            create_setting()

    def test_setting_create_with_pk(self):
        """
        Test that create method throwing the following exception no matter the given pk
        django.db.utils.IntegrityError: (1062, "Duplicate entry '1' for key 'PRIMARY'")

        :return:
        :rtype:
        """

        # Set pk=2
        with self.assertRaises(expected_exception=IntegrityError):
            create_setting(pk=2)

    def test_cannot_be_deleted(self):
        """
        Test that the settings object cannot be deleted

        :return:
        :rtype:
        """

        # given
        settings_old = Setting.objects.get(pk=1)

        # when
        Setting.objects.all().delete()

        # then
        settings = Setting.objects.all()
        settings_first = settings.first()

        # See if there is still only ONE Setting object
        self.assertEqual(first=settings.count(), second=1)

        # Check if both of our objects are identical
        self.assertEqual(first=settings_old, second=settings_first)

    def test_srp_team_discord_channel_id_is_not_mandatory(self):
        """
        Test that we get None when the Discord Channel ID field is empty

        :return:
        :rtype:
        """

        # given
        setting = Setting()
        setting.save()

        # then
        self.assertEqual(first=setting.pk, second=1)
        self.assertEqual(first=setting.srp_team_discord_channel_id, second=None)
