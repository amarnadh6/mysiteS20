# Generated by Django 3.0.7 on 2020-07-15 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_auto_20200621_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='interested',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='stages',
            field=models.PositiveIntegerField(default=3),
        ),
    ]
