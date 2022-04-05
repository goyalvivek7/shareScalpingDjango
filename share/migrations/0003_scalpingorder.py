# Generated by Django 4.0.2 on 2022-04-01 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0002_user_logged_in_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScalpingOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrumentToken', models.CharField(max_length=200)),
                ('orderType', models.CharField(max_length=200)),
                ('lotQuantity', models.CharField(max_length=200)),
                ('steps', models.CharField(max_length=200)),
                ('entryDiff', models.CharField(max_length=200)),
                ('exitDiff', models.CharField(max_length=200)),
                ('startPrice', models.CharField(max_length=200)),
            ],
        ),
    ]