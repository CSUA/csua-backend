# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-11-06 00:39


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db_data", "0005_sponsor")]

    operations = [
        migrations.AddField(
            model_name="officer",
            name="root_staff",
            field=models.BooleanField(default=False),
        )
    ]
