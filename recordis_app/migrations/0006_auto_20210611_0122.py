# Generated by Django 3.2.4 on 2021-06-11 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordis_app', '0005_auto_20210610_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifytoken',
            name='access_token',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='spotifytoken',
            name='refresh_token',
            field=models.CharField(max_length=250),
        ),
    ]
