from datetime import datetime

from django.db import migrations, models
from django.db.migrations.operations.special import RunPython


def date_to_datetime(apps, schema_editor):
    Event = apps.get_model("db_data", "Event")
    for event in Event.objects.all():
        d = event.date
        event.start_time = datetime(year=d.year, month=d.month, day=d.day)
        event.save()


class Migration(migrations.Migration):
    dependencies = [("db_data", "0020_auto_20200728_2346")]

    operations = [
        migrations.AddField(
            model_name="event", name="start_time", field=models.DateTimeField(null=True)
        ),
        migrations.AddField(
            model_name="event", name="end_time", field=models.DateTimeField(null=True)
        ),
        migrations.RunPython(date_to_datetime),
        migrations.RemoveField(model_name="event", name="date"),
        migrations.RemoveField(model_name="event", name="time"),
    ]
