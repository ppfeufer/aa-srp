"""
Unit tests for the BonusGroup model.
"""

# Django
from django.db import IntegrityError, transaction

# Alliance Auth
from allianceauth.groupmanagement.models import Group

# AA SRP
from aasrp.models import BonusGroup
from aasrp.tests import BaseTestCase


class TestBonusGroup(BaseTestCase):
    """
    Test cases for the BonusGroup model.
    """

    def test_bonus_group_string_representation_returns_group_name(self):
        """
        Test that the string representation of a BonusGroup returns the name of the associated group.

        :return:
        """

        group = Group.objects.create(name="Capital Pilots")
        bonus_group = BonusGroup.objects.create(
            group=group,
            bonus_percentage=12.5,
        )

        self.assertEqual(str(bonus_group), "Capital Pilots")

    def test_bonus_group_defaults_to_zero_percentage(self):
        """
        Test that a newly created BonusGroup defaults to a bonus percentage of 0.0.

        :return:
        """

        group = Group.objects.create(name="Capital Pilots")

        bonus_group = BonusGroup.objects.create(group=group)

        self.assertEqual(bonus_group.bonus_percentage, 0.0)

    def test_bonus_group_persists_the_configured_percentage(self):
        """
        Test that a BonusGroup persists the configured bonus percentage.

        :return:
        """

        group = Group.objects.create(name="Logistics Pilots")
        bonus_group = BonusGroup.objects.create(
            group=group,
            bonus_percentage=27.75,
        )

        bonus_group.refresh_from_db()

        self.assertEqual(bonus_group.bonus_percentage, 27.75)

    def test_bonus_group_rejects_a_second_configuration_for_the_same_group(self):
        """
        Test that a BonusGroup rejects a second configuration for the same group.

        :return:
        """
        group = Group.objects.create(name="Alliance Members")
        BonusGroup.objects.create(group=group, bonus_percentage=5.0)

        with self.assertRaises(IntegrityError), transaction.atomic():
            BonusGroup.objects.create(group=group, bonus_percentage=10.0)

    def test_bonus_group_requires_a_group(self):
        """
        Test that a BonusGroup requires an associated group.

        :return:
        """

        with self.assertRaises(IntegrityError), transaction.atomic():
            BonusGroup.objects.create(bonus_percentage=10.0)

    def test_deleting_a_group_removes_its_bonus_group_configuration(self):
        """
        Test that deleting a group also removes its associated BonusGroup configuration.

        :return:
        """

        group = Group.objects.create(name="Temporary Bonus")
        bonus_group = BonusGroup.objects.create(group=group, bonus_percentage=15.0)
        bonus_group_id = bonus_group.pk

        group.delete()

        self.assertFalse(BonusGroup.objects.filter(pk=bonus_group_id).exists())
