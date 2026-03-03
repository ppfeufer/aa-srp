# Django
from django.db import migrations


def on_migrate(apps, schema_editor):
    """
    Create default settings on migration
    :param apps:
    :param schema_editor:
    :return:
    """

    Setting = apps.get_model("aasrp", "Setting")
    db_alias = schema_editor.connection.alias

    Setting.objects.using(db_alias).create(pk=1)


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
