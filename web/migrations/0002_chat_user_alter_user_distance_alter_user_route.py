# Generated by Django 5.1.3 on 2025-02-22 07:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='web.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='distance',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='route',
            field=models.JSONField(null=True),
        ),
    ]
