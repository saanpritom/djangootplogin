# Generated by Django 2.2 on 2019-11-04 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomUsers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userauthmodel',
            name='username',
            field=models.CharField(max_length=11, verbose_name='Username'),
        ),
    ]