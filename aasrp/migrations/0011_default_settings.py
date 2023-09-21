# Django
from django.db import migrations

# Alliance Auth (External Libs)
from app_utils.app_settings import clean_setting

srp_team_discord_channel_id = clean_setting(
    name="AASRP_SRP_TEAM_DISCORD_CHANNEL", default_value=None, required_type=int
)


def on_migrate(apps, schema_editor):
    """
    Create default settings on migration
    :param apps:
    :param schema_editor:
    :return:
    """

    Setting = apps.get_model("aasrp", "Setting")
    db_alias = schema_editor.connection.alias

    Setting.objects.using(db_alias).create(
        pk=1,
        srp_team_discord_channel_id=srp_team_discord_channel_id,
    )


def on_migrate_zero(apps, schema_editor):
    """
    Remove default settings on migration to zero
    :param apps:
    :param schema_editor:
    :return:
    """

    Setting = apps.get_model("aasrp", "Setting")
    db_alias = schema_editor.connection.alias
    Setting.objects.using(db_alias).delete()


class Migration(migrations.Migration):
    """
    Run migrations
    """

    dependencies = [
        ("aasrp", "0010_model_changes"),
    ]

    operations = [migrations.RunPython(on_migrate, on_migrate_zero)]
