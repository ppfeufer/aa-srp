"""
Preloads data required for this app from ESI
"""

# Standard Library
import logging

# Django
from django.core.management import call_command
from django.core.management.base import BaseCommand

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.constants import EVE_CATEGORY_ID_SHIP

logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    """
    Pre-loading required data
    """

    help = "Preloads data required for this app from ESI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        """
        Start the eve type import
        :param args:
        :param options:
        """

        params = [
            "eveuniverse_load_types",
            __title__,
            "--category_id",
            str(EVE_CATEGORY_ID_SHIP),
        ]

        if options["noinput"]:
            params.append("--noinput")

        call_command(*params)
