# Generated by Django 5.0.4 on 2024-04-14 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='is_private',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
