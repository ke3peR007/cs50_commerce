# Generated by Django 3.1.3 on 2021-03-27 12:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_auto_20210327_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='commented_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 27, 12, 14, 39, 963615)),
        ),
    ]
