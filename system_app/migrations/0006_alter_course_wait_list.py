# Generated by Django 4.1.5 on 2023-01-24 19:47

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_app', '0005_course_wait_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='wait_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), default=list, size=None),
        ),
    ]
