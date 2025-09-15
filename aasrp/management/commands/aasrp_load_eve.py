"""
Preloads data required for this app from ESI.

This script defines a Django management command that preloads data required for the application
from the EVE Swagger Interface (ESI). It imports EVE types related to ships and supports an optional
`--noinput` argument to suppress user prompts.
"""

# Standard Library
import logging

# Django
from django.core.management import call_command
from django.core.management.base import BaseCommand

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from eveuniverse.constants import EveCategoryId

# AA SRP
from aasrp import __title__

# Initialize a logger with a custom tag for the AA SRP module
logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    """
    Django management command for preloading required data from ESI.

    This command loads EVE types related to ships into the database. It supports an optional
    `--noinput` argument to suppress user prompts during execution.
    """

    help = "Preloads data required for this app from ESI"

    def add_arguments(self, parser):
        """
        Add command-line arguments to the parser.

        :param parser: The argument parser instance.
        :type parser: argparse.ArgumentParser
        """
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        """
        Execute the command to start the EVE type import.

        This method constructs the parameters for the `eveuniverse_load_types` command
        and executes it. If the `--noinput` option is provided, it adds the corresponding
        flag to the command.

        :param args: Positional arguments passed to the command.
        :type args: tuple
        :param options: Keyword arguments passed to the command.
        :type options: dict
        """
        # Define the base parameters for the `eveuniverse_load_types` command
        params = [
            "eveuniverse_load_types",
            __title__,
            "--category_id",
            str(EveCategoryId.SHIP.value),
        ]

        # Add the `--noinput` flag if specified in the options
        if options["noinput"]:
            params.append("--noinput")

        # Call the `eveuniverse_load_types` command with the constructed parameters
        call_command(*params)
