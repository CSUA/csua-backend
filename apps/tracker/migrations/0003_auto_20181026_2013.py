# Generated by Django 2.0.6 on 2018-10-27 03:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tracker", "0002_auto_20180810_0313")]

    operations = [
        migrations.AlterField(
            model_name="computer",
            name="foreign_timestamp",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="computer",
            name="local_timestamp",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_ping",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
