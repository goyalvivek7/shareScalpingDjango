# Generated by Django 4.0.2 on 2022-03-06 05:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='logged_in_client',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
