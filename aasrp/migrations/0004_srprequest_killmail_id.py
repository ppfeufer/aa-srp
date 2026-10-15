# Django
from django.db import migrations, models

# Largest value a PositiveBigIntegerField can hold on all supported databases
MAX_KILLMAIL_ID = 9223372036854775807


def _parse_killmail_id(killboard_link: str) -> int | None:
    """
    Extract the kill mail ID from a killboard link.

    Mirrors SrpRequestManager.get_kill_id() at the time of writing, so existing
    requests get the same ID that new submissions are checked against.

    :param killboard_link: The killboard link
    :type killboard_link: str
    :return: The kill mail ID, or None if it can't be determined
    :rtype: int | None
    """

    # Extract all digits from the killboard link to determine the killmail ID.
    digits = "".join(c for c in killboard_link if c in "0123456789")

    if not digits or int(digits) > MAX_KILLMAIL_ID:
        return None

    return int(digits)


def _backfill_killmail_id(apps, schema_editor):
    """
    Populate killmail_id for existing SRP requests.

    If a kill mail has more than one SRP request, only the oldest one gets the ID,
    so the unique constraint can be added. The others are kept and listed.

    :param apps:
    :type apps:
    :param schema_editor:
    :type schema_editor:
    :return:
    :rtype:
    """

    srp_request_model = apps.get_model("aasrp", "SrpRequest")
    db_alias = schema_editor.connection.alias
    seen_killmail_ids = set()
    to_update = []
    duplicates = []
    unparsable = []

    # Iterate over all existing SRP requests to backfill the killmail_id field.
    for srp_request in (
        srp_request_model.objects.using(db_alias)
        .order_by("pk")
        .only("pk", "request_code", "killboard_link")
        .iterator()
    ):
        killmail_id = _parse_killmail_id(srp_request.killboard_link)

        if killmail_id is None:
            unparsable.append(srp_request)
        elif killmail_id in seen_killmail_ids:
            duplicates.append(srp_request)
        else:
            seen_killmail_ids.add(killmail_id)
            srp_request.killmail_id = killmail_id
            to_update.append(srp_request)

    srp_request_model.objects.using(db_alias).bulk_update(
        to_update, ["killmail_id"], batch_size=500
    )

    # Check for duplicates and unparsable killboard links and print debug information.
    if duplicates:
        print(
            f"\n  {len(duplicates)} SRP request(s) are duplicates of an older request "
            "for the same kill mail and were left without a kill mail ID:"
        )

        for srp_request in duplicates:
            print(f"    {srp_request.request_code}: {srp_request.killboard_link}")

    # Check for unparsable killboard links and print debug information.
    if unparsable:
        print(
            f"\n  {len(unparsable)} SRP request(s) have no kill mail ID in their "
            "killboard link and were left without one:"
        )

        for srp_request in unparsable:
            print(f"    {srp_request.request_code}: {srp_request.killboard_link}")


class Migration(migrations.Migration):

    dependencies = [
        ("aasrp", "0003_alliance_auth_proxy_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="srprequest",
            name="killmail_id",
            field=models.PositiveBigIntegerField(
                blank=True, default=None, null=True, verbose_name="Kill mail ID"
            ),
        ),
        migrations.RunPython(
            code=_backfill_killmail_id,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="srprequest",
            name="killmail_id",
            field=models.PositiveBigIntegerField(
                blank=True,
                default=None,
                null=True,
                unique=True,
                verbose_name="Kill mail ID",
            ),
        ),
    ]
