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
        Test Setting model string name

        :return:
        :rtype:
        """

        # given
        setting = Setting.objects.get(pk=Setting.singleton_instance_id)

        # when/then
        self.assertEqual(first=str(setting), second="AA-SRP settings")

    def test_model_verbose_names(self):
        """
        Test Setting model verbose names

        :return:
        :rtype:
        """

        self.assertEqual(first=Setting._meta.verbose_name, second="Setting")
        self.assertEqual(first=Setting._meta.verbose_name_plural, second="Setting")

    def test_default_setting(self):
        """
        Test that the default settings are created

        :return:
        :rtype:
        """

        # given
        setting = Setting.get_solo()

        # then
        self.assertEqual(first=setting.pk, second=Setting.singleton_instance_id)
        self.assertEqual(first=setting.srp_team_discord_channel_id, second=None)
        self.assertEqual(first=setting.loss_value_source, second="totalValue")

    def test_set_discord_channel_id(self):
        """
        Test if the discord channel ID can be set

        :return:
        :rtype:
        """

        # given
        srp_team_discord_channel_id = 123456789
        setting = Setting.get_solo()

        # when
        setting.srp_team_discord_channel_id = srp_team_discord_channel_id
        setting.save()

        # then
        setting = Setting.get_solo()
        self.assertEqual(
            first=setting.srp_team_discord_channel_id,
            second=srp_team_discord_channel_id,
        )

    def test_set_loss_value_source(self):
        """
        Test if the loss value source can be set

        :return:
        :rtype:
        """

        # given
        loss_value_source = "fittedValue"
        setting = Setting.get_solo()

        # when
        setting.loss_value_source = loss_value_source
        setting.save()

        # then
        setting = Setting.get_solo()
        self.assertEqual(first=setting.loss_value_source, second=loss_value_source)

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
        self.assertEqual(first=setting.pk, second=Setting.singleton_instance_id)
        self.assertEqual(
            first=setting.srp_team_discord_channel_id,
            second=srp_team_discord_channel_id,
        )

    def test_setting_create_should_throw_exception(self):
        """
        Test that create method throwing the following exception
        `django.db.utils.IntegrityError`: (1062, "Duplicate entry '1' for key 'PRIMARY'")

        :return:
        :rtype:
        """

        # No pk given
        with self.assertRaises(expected_exception=IntegrityError):
            create_setting()

    def test_setting_create_with_pk_should_fail(self):
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
        settings_old = Setting.objects.get(pk=Setting.singleton_instance_id)

        # when
        Setting.objects.all().delete()

        # then
        settings = Setting.objects.all()
        settings_first = settings.first()

        # See if there is still only ONE Setting object
        self.assertEqual(first=settings.count(), second=1)

        # Check if both of our objects are identical
        self.assertEqual(first=settings_old, second=settings_first)
