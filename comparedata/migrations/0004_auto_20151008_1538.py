# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparedata', '0003_job_object_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='matching_rows_count',
            new_name='matching_rows_count_org_one',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='unmatching_rows_count',
            new_name='matching_rows_count_org_two',
        ),
        migrations.AddField(
            model_name='job',
            name='unmatching_rows_count_org_one',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='unmatching_rows_count_org_two',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
