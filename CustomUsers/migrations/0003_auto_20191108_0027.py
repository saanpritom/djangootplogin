# Generated by Django 2.2 on 2019-11-08 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CustomUsers', '0002_auto_20191107_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userauthmodel',
            name='group',
            field=models.ForeignKey(default='650d3bdb0c8145d8a0f9cb8d56dd4afb', on_delete=django.db.models.deletion.CASCADE, related_name='user_group', to='CustomUsers.UserGroupModel'),
        ),
    ]
