# Generated by Django 4.0.2 on 2022-04-17 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0013_backgroundprocess'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.CharField(max_length=200)),
                ('instrumentToken', models.CharField(max_length=200)),
            ],
        ),
    ]