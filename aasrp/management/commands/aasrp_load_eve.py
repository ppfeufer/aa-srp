import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand

from aasrp import __title__
from aasrp.constants import EVE_CATEGORY_ID_SHIP
from aasrp.utils import LoggerAddTag


logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    help = "Preloads data required for this app from ESI"

    def handle(self, *args, **options):
        """
        start the eve type import
        :param args:
        :param options:
        """

        call_command(
            "eveuniverse_load_types",
            __title__,
            "--category_id",
            str(EVE_CATEGORY_ID_SHIP),
        )
