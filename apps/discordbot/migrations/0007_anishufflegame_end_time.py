# Generated by Django 2.2.28 on 2023-02-02 22:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("discordbot", "0006_anishufflegame")]

    operations = [
        migrations.AddField(
            model_name="anishufflegame",
            name="end_time",
            field=models.DateTimeField(null=True),
        )
    ]
