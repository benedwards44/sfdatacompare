# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparedata', '0002_auto_20151008_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='object_id',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
