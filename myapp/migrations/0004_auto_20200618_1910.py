# Generated by Django 3.0.7 on 2020-06-18 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_auto_20200615_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='city',
            field=models.CharField(choices=[('WS', 'Windsor'), ('CG', 'Calgary'), ('MR', 'Montreal'), ('VC', 'Vancouver')], default='WS', max_length=2),
        ),
    ]
