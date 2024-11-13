# Django
from django.test import TestCase

# AA SRP
from aasrp.models import FleetType


class TestFleetType(TestCase):
    """
    Tests for FleetType model
    """

    def test_model_string_name(self):
        """
        Test FleetType model string names

        :return:
        :rtype:
        """

        expected_model_name = "Test Fleet Type"
        fleet_type = FleetType(name=expected_model_name)
        fleet_type.save()

        self.assertEqual(first=str(fleet_type), second=expected_model_name)

    def test_model_verbose_names(self):
        """
        Test FleetType model verbose names

        :return:
        :rtype:
        """

        self.assertEqual(first=FleetType._meta.verbose_name, second="Fleet type")
        self.assertEqual(
            first=FleetType._meta.verbose_name_plural, second="Fleet types"
        )

    def test_add_new_fleet_type(self):
        """
        Test adding a new FleetType

        :return:
        :rtype:
        """

        # given
        fleet_type = FleetType(name="Test Fleet Type")

        # when
        fleet_type.save()

        # then
        self.assertEqual(first=fleet_type.name, second="Test Fleet Type")
