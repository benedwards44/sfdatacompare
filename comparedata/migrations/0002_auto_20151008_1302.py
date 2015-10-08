# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparedata', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='matching_rows_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='row_count_org_one',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='row_count_org_two',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='unmatching_rows_count',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
