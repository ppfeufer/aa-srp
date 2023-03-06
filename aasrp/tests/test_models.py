# Django
from django.test import TestCase

# AA SRP
from aasrp.tests.utils import create_fleettype


class TestFleetType(TestCase):
    """
    Tests for FleetType model
    """

    def test_model_string_names(self):
        """
        Test model string names
        :return:
        """

        topic = create_fleettype(name="Test Fleet Type")

        self.assertEqual(str(topic), "Test Fleet Type")
